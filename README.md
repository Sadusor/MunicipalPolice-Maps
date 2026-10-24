# MunicipalPolice Maps — public road-only datasets

This repository distributes **only** offline street-index datasets and a machine-readable region catalogue for MunicipalPolice. It contains no Android source, accounts, incident records, photographs, contact details or signing credentials.

## Status
A nationwide Greece SQLite gzip road bundle is publicly distributed in release `greece-bundle-v1`; see [licensing, provenance and checksums](docs/GREECE_BUNDLE_LICENSE_AND_PROVENANCE.md). Regional TSV catalogue packs have not yet been verified/published. `catalogue.json` intentionally contains an empty list. The Android app must report **not available** until a real verified package has been published.

## Road pack contract
* One pack per Greek prefecture/administrative unit (Νομός), using checked geographical boundaries — **not** postcode-number ranges.
* Gzip-compressed UTF-8 `.tsv.gz`, each non-comment row: `street_name\tlat1\tlon1\tlat2\tlon2`. The app checks rows and installs validated datasets offline.
* Catalogue uses `{"schema":1,"regions":[{"id":"...","name":"Αιτωλοακαρνανίας","url":"https://.../roads-v1/...tsv.gz","bytes":12345,"sha256":"64_hex_digits"}]}`. Region names must match Android selector options. Never publish placeholder URLs or fake hashes.
* Publish pack files as GitHub Releases assets with versioned release tags. Compute exact file bytes and SHA-256, and validate the data and boundary before updating catalogue.
* Coverage describes **roads mapped in OpenStreetMap**, not a guarantee that every road exists. Display attribution: © OpenStreetMap contributors (ODbL). Ensure license and attribution requirements are met when producing and redistributing regional databases.
* Public HTTPS catalogue: https://raw.githubusercontent.com/Sadusor/MunicipalPolice-Maps/main/catalogue.json

First test target: Αιτωλοακαρνανίας, including Ναύπακτος (30300), to be produced from a verified OSM extract with a reviewed regional boundary.

Do not upload data from the private MunicipalPolice repositories.
