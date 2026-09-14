import filecmp
import os
import stat
import tempfile
import unittest
import zipfile
from pathlib import Path

from zip_recompress import zip_recompress


class TestZipRecompress(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

        self.src = self.root / "input.zip"
        self.recompressed = self.root / "recompressed.zip"
        self.recompressed_again = self.root / "recompressed-again.zip"

        self.compression = zipfile.ZIP_STORED
        self.compresslevel = None
        self._create_test_zip()

    def tearDown(self):
        self.tmp.cleanup()

    def _create_test_zip(self):
        """Create a small archive with files, a directory and permissions."""
        with zipfile.ZipFile(
            self.src,
            "w",
            compression=self.compression,
            compresslevel=self.compresslevel,
        ) as z:
            z.comment = b"test archive"

            directory = zipfile.ZipInfo("directory/")
            directory.external_attr = (
                stat.S_IFDIR | 0o755
            ) << 16
            z.writestr(directory, b"")

            executable = zipfile.ZipInfo("directory/executable")
            executable.external_attr = (
                stat.S_IFREG | 0o755
            ) << 16
            z.writestr(executable, b"#!/bin/sh\necho hello\n")

            regular = zipfile.ZipInfo("directory/regular.txt")
            regular.external_attr = (
                stat.S_IFREG | 0o644
            ) << 16
            z.writestr(regular, b"hello world\n")

            z.writestr("empty", b"")

    def test_recompression_preserves_data(self):
        zip_recompress(
            self.src,
            self.recompressed,
            zipfile.ZIP_DEFLATED,
            6,
        )

        with zipfile.ZipFile(self.src) as original, \
                zipfile.ZipFile(self.recompressed) as result:

            self.assertEqual(
                set(original.namelist()),
                set(result.namelist()),
            )

            for name in original.namelist():
                self.assertEqual(
                    original.read(name),
                    result.read(name),
                    name,
                )

    def test_recompression_preserves_archive_comment(self):
        zip_recompress(
            self.src,
            self.recompressed,
            zipfile.ZIP_DEFLATED,
            6,
        )

        with zipfile.ZipFile(self.src) as original, \
                zipfile.ZipFile(self.recompressed) as result:

            self.assertEqual(original.comment, result.comment)

    def test_recompression_preserves_metadata(self):
        zip_recompress(
            self.src,
            self.recompressed,
            zipfile.ZIP_DEFLATED,
            6,
        )

        with zipfile.ZipFile(self.src) as original, \
                zipfile.ZipFile(self.recompressed) as result:

            self.assertEqual(
                len(original.infolist()),
                len(result.infolist()),
            )

            for old, new in zip(
                original.infolist(),
                result.infolist(),
            ):
                self.assertEqual(old.filename, new.filename)
                self.assertEqual(old.date_time, new.date_time)
                self.assertEqual(old.external_attr, new.external_attr)
                self.assertEqual(old.create_system, new.create_system)
                self.assertEqual(old.create_version, new.create_version)
                self.assertEqual(old.extract_version, new.extract_version)
                self.assertEqual(old.flag_bits, new.flag_bits)
                self.assertEqual(old.extra, new.extra)
                self.assertEqual(old.comment, new.comment)

    def test_recompression_is_idempotent(self):
        compression = zipfile.ZIP_DEFLATED

        zip_recompress(
            self.src,
            self.recompressed,
            compression,
            6,
        )

        zip_recompress(
            self.recompressed,
            self.recompressed_again,
            compression,
            6,
        )

        self.assertTrue(
            filecmp.cmp(
                self.recompressed,
                self.recompressed_again,
                shallow=False,
            )
        )

    def test_recompression_is_reversible(self):
        """Recompressing A -> B -> A must preserve the original data/metadata."""
        zip_recompress(
            self.src,
            self.recompressed,
            zipfile.ZIP_DEFLATED,
            6,
        )

        zip_recompress(
            self.recompressed,
            self.recompressed_again,
            self.compression,
            self.compresslevel,
        )


if __name__ == "__main__":
    unittest.main()
