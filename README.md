# zip-recompress

This is a simple CLI utility that takes a zip file and creates a new one with
the new compression.

It aims for two main features

1. Environment agnostic. For a given input file the output file should be
   identical even when run on different systems.
2. Streaming. The unpacked archive should not need to be stored in full as
   intermediate step (either on disk or memory).

## Installation

1. Get the source (git clone or download archive and unpack)
2. `pip install .`

## Usage
```bash
zip-recompress --help
```
