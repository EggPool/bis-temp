# Codename "Concrete"

Goal: Faster bootstrap and catchup after a downtime.


## What
Concrete are group of blocks, under an optimized and compact binary format.

Each concrete batch could store 10k blocks for instance (around 10 Mb, vs 34 Mb in json, native bis format)

Having these elements means 
- less network load (:3) vs native format
- can be pre-computed (no cpu to extract, just have to serve, can be sync over the net to CDN)
- each concrete batch can have a hash that is stored on chain - safety
- hns can host and provide them (very fast // download of the bootstrap from hns, then assembling and final check)

## Internals

Uses google protobuff as binary format for storage and transmission

Stores in binary instead of hex or b64, where possible
