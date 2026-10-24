# Nationwide Greece road bundle — license and provenance

## Public release

Version: `greece-bundle-v1`  
Public manifest: https://github.com/Sadusor/MunicipalPolice-Maps/releases/download/greece-bundle-v1/greece_roads.json  
Database asset: https://github.com/Sadusor/MunicipalPolice-Maps/releases/download/greece-bundle-v1/greece_roads.sqlite.gz

Public manifest retrieved by the project owner on 2026-10-24:

| Field | Value |
| --- | --- |
| `schema` | `1` |
| `file` | `greece_roads.sqlite` |
| `road_segments` | `3228275` |
| `bytes` (uncompressed) | `445685760` |
| `sha256` (uncompressed) | `88345b58b4db99ef39b7f7a96f31920b01aa4537c179f26ffe380c59b2673cc4` |
| `gzip_bytes` | `125193558` |
| `gzip_sha256` | `bb4da070452832013105e1a3e20e7cbdcc826ca7abe0b98fbaecbeb0664c9d74` |
| `source` | `© OpenStreetMap contributors; ODbL; Geofabrik Greece` |

The compressed SHA-256 and length match the app's previously verified original pack. The manifest's provenance assertion has **not** been independently traced to a particular Geofabrik extract timestamp or full build recipe. Do not describe that unverified aspect as audited.

## Rights and attribution

Road information originates from OpenStreetMap contributors and is licensed under the Open Database License (ODbL) 1.0. See:
- https://www.openstreetmap.org/copyright
- https://opendatacommons.org/licenses/odbl/1-0/
- https://osmfoundation.org/wiki/Attribution_Guidelines
- https://download.geofabrik.de/europe/greece.html

**© OpenStreetMap contributors. Data available under the ODbL 1.0.**

The redistributed nationwide SQLite road index is a derived database from OSM data; recipients should receive the applicable ODbL rights. Do not impose restrictions on reuse of this road database that conflict with ODbL. The Field Notebook application code, private user data and other independent resources are *not* thereby licensed as ODbL.

Geofabrik is acknowledged as the source/distributor identified in the manifest; this document does not imply endorsement by Geofabrik or OpenStreetMap.

## Redistribution review gates (not legal certification)

- [x] Release URL and provenance statement are publicly accessible in the manifest (owner test).
- [x] Manifest compressed SHA-256 matches the original local pack exactly.
- [x] Public road database made available as a versioned release asset.
- [ ] Verify completeness/validity of public compressed asset download and check both compressed and SQLite SHA-256 independently.
- [ ] Identify and archive exact source PBF version/time, extraction scripts, transformations and database schema; evaluate whether publishing the resulting database suffices for ODbL obligations in this specific case.
- [ ] Ensure attribution and license access is visible in **all** apps that use the pack and on asset distribution pages.
- [ ] Check any additional source/third-party content rights and legal requirements before claiming full legal compliance.

This page supplies attribution and a public database link; it is not a representation that the complete licensing/legal review is finished.
