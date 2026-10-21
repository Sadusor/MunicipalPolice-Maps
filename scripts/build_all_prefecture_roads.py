#!/usr/bin/env python3
"""Generate 51 prefecture road packs from official-like regional-unit geometry and Geofabrik OSM.
Only publishes after all polygons match expected IDs and every generated pack passes limits.
Coverage: named OSM highway segments, not all possible roads.
"""
import argparse
import collections
import gzip
import hashlib
import json
import math
import os
import re
import unicodedata
from pathlib import Path

# 51 traditional prefectures; grouping modern regional units where geography changed.
# Unit IDs are supplied by the independently sourced GeoJSON inventory.
GROUPS = {
 "Αιτωλοακαρνανίας": ["0701"],
 "Αργολίδας": ["1001"], "Αρκαδίας": ["1002"], "Άρτας": ["0401"],
 "Αττικής": ["0901","0902","0903","0904","0905","0906","0907","0908"],
 "Αχαΐας": ["0702"], "Βοιωτίας": ["0801"], "Γρεβενών": ["0301"],
 "Δράμας": ["0101"], "Δωδεκανήσου": ["1203","1204","1206","1211"],
 "Έβρου": ["0102"], "Ευβοίας": ["0802"], "Ευρυτανίας": ["0803"],
 "Ζακύνθου": ["0601"], "Ηλείας": ["0703"], "Ημαθίας": ["0201"],
 "Ηρακλείου": ["1301"], "Θεσπρωτίας": ["0402"], "Θεσσαλονίκης": ["0202"],
 "Ιωαννίνων": ["0403"], "Καβάλας": ["0103","0104"],
 "Καρδίτσας": ["0501"], "Καστοριάς": ["0302"], "Κέρκυρας": ["0603"],
 "Κεφαλληνίας": ["0602","0604"], "Κιλκίς": ["0203"], "Κοζάνης": ["0303"],
 "Κορινθίας": ["1003"],
 "Κυκλάδων": ["1201","1202","1205","1207","1208","1209","1210","1212","1213"],
 "Λακωνίας": ["1004"], "Λάρισας": ["0502"], "Λασιθίου": ["1302"],
 "Λέσβου": ["1101","1103"], "Λευκάδας": ["0605"],
 "Μαγνησίας": ["0503","0504"], "Μεσσηνίας": ["1005"], "Ξάνθης": ["0105"],
 "Πέλλας": ["0204"], "Πιερίας": ["0205"], "Πρέβεζας": ["0404"],
 "Ρεθύμνης": ["1303"], "Ροδόπης": ["0106"], "Σάμου": ["1102","1104"],
 "Σερρών": ["0206"], "Τρικάλων": ["0505"], "Φθιώτιδας": ["0804"],
 "Φλώρινας": ["0304"], "Φωκίδας": ["0805"], "Χαλκιδικής": ["0207"],
 "Χανίων": ["1304"], "Χίου": ["1105"]
}

def slug(s):
    s=unicodedata.normalize("NFKD",s)
    s="".join(c for c in s if not unicodedata.combining(c))
    translit={"Α":"a","Β":"v","Γ":"g","Δ":"d","Ε":"e","Ζ":"z","Η":"i","Θ":"th",
      "Ι":"i","Κ":"k","Λ":"l","Μ":"m","Ν":"n","Ξ":"x","Ο":"o","Π":"p",
      "Ρ":"r","Σ":"s","Τ":"t","Υ":"y","Φ":"f","Χ":"ch","Ψ":"ps","Ω":"o"}
    s="".join(translit.get(c.upper(),c.lower()) for c in s)
    return re.sub(r"-+","-",re.sub(r"[^a-z0-9]+","-",s)).strip("-")

def build(pbf,boundaries,out,tag):
    import osmium
    from shapely.geometry import shape, Point
    from shapely.ops import unary_union
    from shapely.strtree import STRtree
    b=json.loads(boundaries.read_text(encoding="utf-8"))
    by_id={str(f["properties"]["id"]).zfill(4):shape(f["geometry"]) for f in b["features"]}
    assigned=[id for members in GROUPS.values() for id in members]
    assert len(GROUPS)==51, "Prefecture selector mismatch"
    assert len(assigned)==len(set(assigned))==len(by_id)==74, "Boundary IDs missing, changed or overlapping"
    assert set(assigned)==set(by_id), "Boundary data inventory changed; review before publish"
    names=list(GROUPS)
    geoms=[unary_union([by_id[id] for id in GROUPS[name]]) for name in names]
    assert all(not g.is_empty and g.is_valid for g in geoms), "Invalid boundary geometry"
    tree=STRtree(geoms)
    out.mkdir(parents=True,exist_ok=True)
    writers={}
    paths={}
    counts=collections.Counter()
    try:
        for name in names:
            path=out/(slug(name)+".tsv.gz")
            paths[name]=path
            writers[name]=gzip.open(path,"wt",encoding="utf-8",compresslevel=6,newline="\n")
            writers[name].write("# © OpenStreetMap contributors; ODbL https://www.openstreetmap.org/copyright\n")

        class Roads(osmium.SimpleHandler):
            def way(self,way):
                name=way.tags.get("name")
                if not way.tags.get("highway") or not name or any(c in name for c in "\t\r\n") or len(name)>200:
                    return
                nodes=[(n.location.lat,n.location.lon) for n in way.nodes if n.location.valid()]
                for (lat1,lon1),(lat2,lon2) in zip(nodes,nodes[1:]):
                    mid=Point((lon1+lon2)/2,(lat1+lat2)/2)
                    candidates=tree.query(mid)
                    for idx in candidates:
                        index=int(idx)
                        if not geoms[index].covers(mid):
                            continue
                        region=names[index]
                        counts[region]+=1
                        assert counts[region]<=2_000_000, "Excess segments: "+region
                        writers[region].write(f"{name}\t{lat1:.7f}\t{lon1:.7f}\t{lat2:.7f}\t{lon2:.7f}\n")
                        break
        Roads().apply_file(str(pbf),locations=True)
    finally:
        for w in writers.values(): w.close()
    manifest={"schema":1,"regions":[]}
    print("REGIONS>",len(names))
    for name in names:
        p=paths[name]
        size=p.stat().st_size
        n=counts[name]
        print("REGION>",name,"ROWS>",n,"BYTES>",size)
        if n<100 or size>32*1024*1024: raise RuntimeError(f"Region {name} invalid: {n} segments / {size} bytes")
        digest=hashlib.sha256(p.read_bytes()).hexdigest()
        manifest["regions"].append({
            "id":slug(name),"name":name,
            "url":"https://github.com/Sadusor/MunicipalPolice-Maps/releases/download/"+tag+"/"+p.name,
            "bytes":size,"sha256":digest})
    (out/"catalogue.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("COMPLETE_PACKS_VALIDATED>",len(manifest["regions"]))
if __name__=="__main__":
    a=argparse.ArgumentParser()
    a.add_argument("--pbf",type=Path,required=True)
    a.add_argument("--boundaries",type=Path,required=True)
    a.add_argument("--output",type=Path,required=True)
    a.add_argument("--tag",required=True)
    x=a.parse_args()
    build(x.pbf,x.boundaries,x.output,x.tag)
