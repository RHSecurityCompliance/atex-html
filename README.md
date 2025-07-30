# ATEX-HTML

This is a simple HTML UI for viewing results produced by the
[ATEX](https://github.com/RHSecurityCompliance/atex) infrastructure tooling,
specifically aimed at the `JSONAggregator` output.

The JSON-on-each-line gzipped format produced by this aggregator is then
transformed by the `json2db.py` script (located in this repo) to produce
a compressed sqlite database used by `index.html`, which also contains all
of the javascript code (due to latency optimizations).

## Usage

1. Produce some results via the ATEX `JSONAggregator`, into a pair of
   `results.json.gz` (containing results) and `files_dir` (with test-uploaded
   files a.k.a. logs).

1. Convert the JSON results to sqlite3 with:
   `./json2db.py results.json.gz results.sqlite.gz`

1. Optionally copy over `old_runs` as a directory containing temporary or old
   test runs (that were later re-run), for debugging.

1. Optionally, create `header.html` and/or `footer.html` that would be displayed
   above/below the results table.

1. Host

   * `results.sqlite.gz`
   * `files_dir`
   * `old_runs` (optional)
   * `index.html` (from this repo)
   * `sqljs` (from this repo)
   * `header.html` / `footer.html` (optional)

   on a HTTP server somewhere. This can be a "dumb" server like Python's
   `http.server` with no server-side scripting support.

1. Access the website from your browser.

## Filtering the results

The idea here is to use a sqlite3 database, loaded in-memory to a web browser,
to run custom SQL queries on the result set. As such, the only input field
visible is a SQL WHERE condition.

Since no advanced input sanitization is done (the database is transient, no harm
*can* be done by a malicious URL), one can inject additional SQL keywords between
the `WHERE` and a trailing `LIMIT`, ie. `ORDER BY`, to further tweak the output.

Columns currently cannot be hidden / changed due to how the HTML table is built
from javascript and how CSS styling is applied.

## License

Unless specified otherwise, any content within this repository is distributed
under the GNU GPLv3 license, see the [COPYING.txt](COPYING.txt) file for more.

### sql.js

Any files under the `sqljs` directory are subject to the license of the
[sql.js project](https://github.com/sql-js/sql.js/) which can be found here:
https://github.com/sql-js/sql.js/blob/master/LICENSE
