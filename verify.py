#!/usr/bin/env python3
"""Verify the news-image-20261122 entry.

Runs main.py twice into separate directories, checks the two
outputs are byte-identical, under 1 MiB, a valid 1024x1024 PNG.
"""
import hashlib
import os
import struct
import subprocess
import sys
import tempfile
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))


def run_once(outdir):
    env = dict(os.environ)
    env["MAKEFUN_OUTPUT_DIR"] = outdir
    r = subprocess.run([sys.executable, os.path.join(HERE, "main.py")],
                       env=env, capture_output=True, text=True)
    if r.returncode != 0:
        print("main.py failed:\n" + r.stdout + r.stderr)
        sys.exit(1)
    return os.path.join(outdir, "entry.png")


def png_info(path):
    with open(path, "rb") as f:
        data = f.read()
    assert data[:8] == b"\x89PNG\r\n\x1a\n", "not a PNG"
    pos = 8
    w = h = None
    while pos < len(data):
        ln = struct.unpack(">I", data[pos:pos + 4])[0]
        kind = data[pos + 4:pos + 8]
        body = data[pos + 8:pos + 8 + ln]
        crc = struct.unpack(">I", data[pos + 8 + ln:pos + 12 + ln])[0]
        assert zlib.crc32(kind + body) & 0xFFFFFFFF == crc, \
            "bad CRC in %r" % kind
        if kind == b"IHDR":
            w, h, depth, ctype = struct.unpack(">IIBB", body[:10])
            assert (depth, ctype) == (8, 2), "need 8-bit RGB"
        if kind == b"IEND":
            break
        pos += 12 + ln
    assert w is not None, "no IHDR"
    return w, h, len(data)


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def main():
    with tempfile.TemporaryDirectory() as d1, \
            tempfile.TemporaryDirectory() as d2:
        p1 = run_once(d1)
        p2 = run_once(d2)
        s1, s2 = sha(p1), sha(p2)
        print("run 1:", s1)
        print("run 2:", s2)
        assert s1 == s2, "runs differ: not deterministic"
        w, h, size = png_info(p1)
        print("size: %d bytes, dimensions: %dx%d" % (size, w, h))
        assert (w, h) == (1024, 1024), "wrong dimensions"
        assert size <= 1048576, "over 1 MiB"
    print("VERIFY OK: deterministic, valid 1024x1024 PNG, <= 1 MiB")


if __name__ == "__main__":
    main()
