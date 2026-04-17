#!/usr/bin/python3

import json
import sqlite3
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml


# DB fields:
# platform, status, test, subtest, files, note
def parse_documents(fobj):
    for doc in yaml.safe_load_all(fobj):
        platform = doc["platform"]
        test = doc.get("name")
        if subtests := doc.get("subtests"):
            for subtest in subtests:
                # each subtest
                files = json.dumps(subtest["files"]) if "files" in subtest else None
                yield (
                    platform,
                    subtest.get("status"),
                    test,
                    subtest.get("name"),
                    files,
                    subtest.get("note"),
                )
        # test itself
        files = json.dumps(doc["files"]) if "files" in doc else None
        yield (
            platform,
            doc.get("status"),
            test,
            None,
            files,
            doc.get("note"),
        )


if len(sys.argv) != 3:
    print(f"usage: {sys.argv[0]} results.yaml results.sqlite.gz")
    sys.exit(1)

_, results_yaml, results_sqlite = sys.argv

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

    with open(results_yaml, mode="rb") as res_in:
        db_cur.executemany(
            "INSERT INTO results VALUES(?,?,?,?,?,?)",
            parse_documents(res_in),
        )

    db_conn.commit()
    db_conn.close()

    with open(results_sqlite, "wb") as gz_out:
        subprocess.run(
            ("gzip", "-9"),
            stdin=tmpf.fileno(),
            stdout=gz_out.fileno(),
        )
