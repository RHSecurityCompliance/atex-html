#!/usr/bin/python3

import contextlib
import gzip
import json
import lzma
import sqlite3
import subprocess
import sys
import tempfile
from pathlib import Path


def parse_lines(fobj):
    for line in fobj:
        platform, status, test, subtest, files, note = json.loads(line)
        files = json.dumps(files) if files else None  # also does [] -> None
        yield (platform, status, test, subtest, files, note)


if len(sys.argv) != 3:
    print(f"usage: {sys.argv[0]} results.json{{.gz,.xz}} results.sqlite.gz")
    sys.exit(1)

_, results_json, results_sqlite = sys.argv

if Path(results_sqlite).exists():
    raise RuntimeError(f"{results_sqlite} already exists")

with tempfile.NamedTemporaryFile(dir="/var/tmp") as tmpf:
    db_conn = sqlite3.connect(tmpf.name)
    db_cur = db_conn.cursor()

    db_cur.execute("""
        CREATE TABLE results (
            platform    TEXT    NOT NULL,
            status      TEXT    NOT NULL,
            test        TEXT    NOT NULL,
            subtest     TEXT,
            files       JSONB,
            note        TEXT
        )
    """)

    with contextlib.ExitStack() as stack:
        if results_json.endswith(".gz"):
            res_in = stack.enter_context(gzip.open(results_json, mode="rb"))
        elif results_json.endswith(".xz"):
            res_in = stack.enter_context(lzma.open(results_json, mode="rb"))
        else:
            res_in = stack.enter_context(open(results_json, mode="rb"))

        db_cur.executemany(
            "INSERT INTO results VALUES(?,?,?,?,?,?)",
            parse_lines(res_in),
        )

    db_conn.commit()
    db_conn.close()

    with open(results_sqlite, "wb") as gz_out:
        subprocess.run(
            ("gzip", "-9"),
            stdin=tmpf.fileno(),
            stdout=gz_out.fileno(),
        )
