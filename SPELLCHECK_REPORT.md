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
`tutorial/guide.po`. Each catalog's `source_sha256` is replaced with the checksum
of the original PO, recorded before the temporary `sphinx-intl update`. This lets
consumers compare coverage with their repository checkout. Pospell's checksum of
the temporarily updated PO is retained as `scanned_sha256`.

Only catalogs present both in the original checkout and in pospell's report are
published; unscanned files are not added as clean. The scan covers prose and
excludes literal blocks through the temporary gettext update.

`potodo-docs-priority` downloads the artifact separately. It validates the source
run, selects complete reports for its requested branch, and checks local entry
identities and fingerprints. This workflow requires no dispatch to that project.
