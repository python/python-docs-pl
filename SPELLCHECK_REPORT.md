# Spellcheck reports

The spellcheck workflow publishes a `spellcheck-pl` Actions artifact containing
`spellcheck.json`. It uses pospell's JSON report from
[PR #24](https://git.afpy.org/AFPy/pospell/pulls/24), installed from the
[`feat/json-reports` branch on maciek's fork](https://git.afpy.org/maciek/pospell/src/branch/feat/json-reports)
until a release includes that feature.
Normal text diagnostics remain in the job log. Spelling findings still produce
a failing step, but the job is advisory by default. The report is prepared and
uploaded even when that step fails.

## Schema version 1

The report preserves pospell's `schema_version`, `status`, `created_at`, `checker`
and findings. `spellcheck_report.py` adds or adapts:

- `language`: `pl`, the translation language expected by consumers.
- `dictionaries`: pospell's dictionary names, currently `pl_PL` and `pl_SJP`.
- `repository`: the GitHub repository name, such as `python/python-docs-pl`.
- `docs_version`: the documentation branch checked, such as `3.15`.
- `run_url`: the Actions run URL.
- `translations_revision` and `cpython_revision`: the checked-out Git commits.
- `catalogs`: resources keyed by POSIX paths relative to the translation root,
  such as `tutorial/guide.po`.

Each catalog contains:

- `source_sha256`: SHA-256 of the original PO file, recorded before the temporary
  `sphinx-intl update`. Consumers compare it with their repository checkout to
  determine whether coverage is current.
- `scanned_sha256`: pospell's SHA-256 of the temporarily updated PO file.
- `findings`: pospell's results, with `msgctxt`, `msgid`, `msgid_plural`,
  `msgstr_sha256`, and unique `words` for each affected entry.

`msgstr_sha256` hashes the checked translation as UTF-8 JSON of
`{"msgstr": entry.msgstr, "msgstr_plural": {str(k): v, ...}}`, serialized with
`ensure_ascii=False`, `sort_keys=True`, and `separators=(',', ':')`. Consumers
should match both the entry identity and this fingerprint before using a finding.

Only catalogs present both in the original checkout and in pospell's report are
published. Clean scanned catalogs retain empty `findings`; unscanned files are
not added as clean. The scan covers prose and excludes literal blocks through
the temporary gettext update. A checked catalog does not imply that every token
or plural form was checked.

`status: "complete"` means the scan finished, including scans that found spelling
issues. `status: "error"` means it failed, and its findings must not be used as
complete coverage. Failures before pospell can write its JSON, or failures during
report preparation, leave no artifact. Missing reports mean unavailable coverage.

`potodo-docs-priority` downloads the artifact separately. It validates the source
run, selects complete reports for its requested branch, and checks local entry
identities and fingerprints. This workflow requires no dispatch to that project.
