#!/usr/bin/env python3
import argparse
import sys
import zipfile
from pathlib import Path


parser = argparse.ArgumentParser(
    prog="zip-recompress",
    description="Recompress an input zipfile into a new zipfile with given compression.",
)
parser.add_argument("-i", "--input", type=Path, required=True, help="Input zip archive")
parser.add_argument("-o", "--output", type=Path, required=True, help="Output zip archive")
parser.add_argument("-c", "--compression", default="stored", choices=["stored", "zlib", "bzip2", "lzma", "zstandard"], help="Compression method to use")
parser.add_argument("-l", "--level", default=None, type=int, help="Compression level")

COMPRESSION_METHODS = {
    "stored": zipfile.ZIP_STORED,
    "zlib": zipfile.ZIP_DEFLATED,
    "bzip2": zipfile.ZIP_BZIP2,
    "lzma": zipfile.ZIP_LZMA,
    "zstandard": zipfile.ZIP_ZSTANDARD,
}
try:
    COMPRESSION_METHODS["zstandard"] = zipfile.ZIP_ZSTANDARD
except AttributeError:
    pass


def zip_recompress(src, dst, compression, compresslevel) -> None:
    """Convert tar to uncompressed zip file."""
    with zipfile.ZipFile(src) as zsrc, zipfile.ZipFile(
        dst,
        mode="w",
        compression=compression,
        compresslevel=compresslevel,
    ) as zdst:
        zdst.comment = zsrc.comment
        for info in zsrc.infolist():
            new_info = copy(info)
            new_info.compress_type = compression
            zdst.writestr(new_info, zsrc.read(info))


def main() -> int:
    args = parser.parse_args()

    if not args.input.is_file():
        print(f"Error: Input does not exist: {args.input}", file=sys.stderr)
        return 1
    elif not zipfile.is_zipfile(args.input):
        print(f"Error: Input does not seem like a zipfile: {args.input}", file=sys.stderr)
        return 1
    if args.output.exists():
        print(f"Error: Output exists: {args.output}", file=sys.stderr)
        return 1

    compression = COMPRESSION_METHODS[args.compression]

    try:
        zip_recompress(
            src=args.input,
            dst=args.output,
            compression=compression,
            compresslevel=args.level,
        )
        return 0
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
