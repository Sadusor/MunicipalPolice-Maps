#!/usr/bin/env python3
"""Build one read-only, spatially indexed SQLite named-road database from Greece OSM PBF."""
import argparse, hashlib, json, os, sqlite3
from pathlib import Path

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--pbf",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--manifest",type=Path,required=True)
    args=p.parse_args()
    import osmium
    assert args.pbf.stat().st_size > 10_000_000, "OSM source missing/too small"
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.unlink(missing_ok=True)
    db=sqlite3.connect(str(args.out))
    db.executescript("""
    PRAGMA journal_mode=DELETE;
    PRAGMA synchronous=OFF;
    PRAGMA temp_store=MEMORY;
    CREATE TABLE roads (id INTEGER PRIMARY KEY, name TEXT NOT NULL,
      a REAL NOT NULL, b REAL NOT NULL, c REAL NOT NULL, d REAL NOT NULL);
    CREATE VIRTUAL TABLE roads_rtree USING rtree(id,minLat,maxLat,minLon,maxLon);
    """)
    segments=[]
    rectangles=[]
    count=0
    class Roads(osmium.SimpleHandler):
        def way(self,way):
            nonlocal count
            name=way.tags.get("name")
            highway=way.tags.get("highway")
            if not name or not highway or len(name)>200 or any(c in name for c in "\r\t\n"):
                return
            nodes=[(n.location.lat,n.location.lon) for n in way.nodes if n.location.valid()]
            for (a,b),(c,d) in zip(nodes,nodes[1:]):
                if not all(-90<=v<=90 for v in (a,c)) or not all(-180<=v<=180 for v in (b,d)):
                    continue
                count+=1
                segments.append((count,name,a,b,c,d))
                rectangles.append((count,min(a,c),max(a,c),min(b,d),max(b,d)))
                if len(segments)>=20000:
                    db.executemany("INSERT INTO roads VALUES (?,?,?,?,?,?)",segments)
                    db.executemany("INSERT INTO roads_rtree VALUES (?,?,?,?,?)",rectangles)
                    segments.clear();rectangles.clear()
    try:
        Roads().apply_file(str(args.pbf),locations=True)
        db.executemany("INSERT INTO roads VALUES (?,?,?,?,?,?)",segments)
        db.executemany("INSERT INTO roads_rtree VALUES (?,?,?,?,?)",rectangles)
        db.commit()
        if count < 50_000: raise ValueError("Too few named road segments")
        integrity=db.execute("PRAGMA integrity_check").fetchone()[0]
        if integrity!="ok": raise ValueError("SQLite integrity check failed: "+integrity)
        n=db.execute("SELECT count(*) FROM roads").fetchone()[0]
        r=db.execute("SELECT count(*) FROM roads_rtree").fetchone()[0]
        assert n==r==count
    finally:
        db.close()
    data=args.out.read_bytes()
    digest=hashlib.sha256(data).hexdigest()
    manifest={
      "schema":1,"file":args.out.name,"sha256":digest,
      "bytes":len(data),"road_segments":count,
      "source":"© OpenStreetMap contributors; ODbL; Geofabrik Greece"
    }
    args.manifest.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("NATIONWIDE_SQLITE_PASS>",len(data),"bytes",count,"named segments",digest,flush=True)

if __name__=="__main__": main()
