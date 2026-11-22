# Spellcheck reports

The spellcheck workflow publishes a `spellcheck-pl` Actions artifact containing
`spellcheck.json`. Pospell is installed from `maciek/pospell@feat/json-reports`
until a release includes JSON reports. See the
[pospell documentation](https://git.afpy.org/maciek/pospell/src/branch/feat/json-reports/README.md)
for the report schema, finding identities, translation fingerprints, and statuses.

Normal text diagnostics remain in the job log. The report is prepared and uploaded
even when spelling findings cause the check step to fail; the job is advisory by
default. If pospell cannot write its JSON or report preparation fails, no artifact
is published.

## Integration fields

`spellcheck_report.py` preserves pospell's schema-v1 findings and adds or adapts:

- `language`: `pl`, the translation language expected by consumers.
- `dictionaries`: pospell's dictionary names, currently `pl_PL` and `pl_SJP`.
- `repository`: the GitHub repository name, such as `python/python-docs-pl`.
- `docs_version`: the documentation branch checked, such as `3.15`.
- `run_url`: the Actions run URL.
- `translations_revision` and `cpython_revision`: the checked-out Git commits.

Catalog paths are relative to `locales/pl/LC_MESSAGES`, such as
`tutorial/guide.po`. Each catalog retains pospell's `source_sha256`, the checksum
of the temporarily updated PO that was scanned. `checkout_sha256` records the
original repository PO before `sphinx-intl update`, so consumers can check
freshness against their checkout.

Before the temporary update, catalogs with no matching current POT are removed
from the disposable checkout; otherwise old catalogs would retain literal blocks.
`sphinx.po` is kept separately for Sphinx's template messages. Only catalogs
present both in the original snapshot and pospell's report are published;
unscanned files are not added as clean.

The translation dashboard downloads `spellcheck-pl/spellcheck.json` and publishes
the complete report at `https://translations.python.org/spellcheck-pl.json`, or
JSON `null` when unavailable. `potodo-docs-priority` reads that public file and
checks local entry identities and translation fingerprints. Only the dashboard
needs a token for cross-repository Actions access.
