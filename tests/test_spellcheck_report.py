import copy
import hashlib
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from spellcheck_report import main, prepare_report, snapshot_catalogs


class SpellcheckReportTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.catalog = self.root / 'tutorial' / 'guide.po'
        self.catalog.parent.mkdir()
        self.catalog.write_text('msgid "Source"\nmsgstr "Błont"\n', encoding='utf-8')
        with patch(
            'spellcheck_report.revision', side_effect=['translations', 'cpython']
        ):
            self.snapshot = snapshot_catalogs(self.root, self.root)
        self.finding = {
            'msgctxt': None,
            'msgid': 'Source',
            'msgid_plural': '',
            'msgstr_sha256': 'translation-digest',
            'words': ['Błont'],
        }
        self.raw = {
            'schema_version': 1,
            'status': 'complete',
            'created_at': '2026-11-21T00:00:00+00:00',
            'language': 'pl_PL,pl_SJP',
            'checker': {'pospell': '1.3', 'hunspell': 'test'},
            'catalogs': {
                'tutorial/guide.po': {
                    'source_sha256': 'temporary-po-digest',
                    'findings': [self.finding],
                },
            },
        }

    def prepare(self, raw=None):
        return prepare_report(
            self.raw if raw is None else raw,
            self.snapshot,
            docs_version='3.15',
            repository='python/python-docs-pl',
            run_url='https://github.com/python/python-docs-pl/actions/runs/123',
        )

    def test_original_checksum_survives_temporary_po_update(self):
        original = hashlib.sha256(self.catalog.read_bytes()).hexdigest()
        self.catalog.write_text('# temporary changes\n', encoding='utf-8')
        result = self.prepare()
        catalog = result['catalogs']['tutorial/guide.po']
        self.assertEqual(catalog['source_sha256'], original)
        self.assertEqual(catalog['scanned_sha256'], 'temporary-po-digest')
        self.assertEqual(catalog['findings'], [self.finding])
        self.assertEqual(result['language'], 'pl')
        self.assertEqual(result['dictionaries'], ['pl_PL', 'pl_SJP'])
        self.assertEqual(result['translations_revision'], 'translations')
        self.assertEqual(result['cpython_revision'], 'cpython')
        self.assertEqual(result['checker'], self.raw['checker'])

    def test_clean_scanned_catalogs_are_kept_but_unscanned_ones_are_not_added(self):
        raw = copy.deepcopy(self.raw)
        raw['catalogs']['tutorial/guide.po']['findings'] = []
        self.snapshot['catalogs']['unscanned.po'] = 'unscanned-digest'
        raw['catalogs']['new.po'] = {'source_sha256': 'new', 'findings': []}
        result = self.prepare(raw)
        self.assertEqual(set(result['catalogs']), {'tutorial/guide.po'})
        self.assertEqual(result['catalogs']['tutorial/guide.po']['findings'], [])

    def test_error_report_is_not_promoted_to_complete(self):
        self.raw.update(status='error', error='Hunspell failed')
        result = self.prepare()
        self.assertEqual(result['status'], 'error')
        self.assertEqual(result['error'], 'Hunspell failed')

    def test_unsupported_or_invalid_reports_are_rejected(self):
        for field, value in [('schema_version', 2), ('status', 'success')]:
            with self.subTest(field=field), self.assertRaises(ValueError):
                self.prepare({**self.raw, field: value})

    def test_cli_adds_metadata_and_preserves_non_ascii_findings(self):
        raw = self.root / 'pospell.json'
        state = self.root / 'snapshot.json'
        output = self.root / 'spellcheck.json'
        raw.write_text(json.dumps(self.raw), encoding='utf-8')
        state.write_text(json.dumps(self.snapshot), encoding='utf-8')
        with (
            patch.dict(
                os.environ,
                {
                    'GITHUB_REPOSITORY': 'python/python-docs-pl',
                    'GITHUB_SERVER_URL': 'https://github.com',
                    'GITHUB_RUN_ID': '123',
                },
            ),
            patch(
                'sys.argv',
                [
                    'spellcheck_report.py',
                    'prepare',
                    '--input',
                    str(raw),
                    '--snapshot',
                    str(state),
                    '--docs-version',
                    '3.15',
                    '--output',
                    str(output),
                ],
            ),
        ):
            main()
        result = json.loads(output.read_text(encoding='utf-8'))
        self.assertEqual(result, self.prepare())
        self.assertIn('Błont', output.read_text(encoding='utf-8'))

    def test_missing_pospell_report_cannot_become_a_clean_report(self):
        output = self.root / 'spellcheck.json'
        with (
            patch(
                'sys.argv',
                [
                    'spellcheck_report.py',
                    'prepare',
                    '--input',
                    str(self.root / 'missing.json'),
                    '--snapshot',
                    str(self.root / 'snapshot.json'),
                    '--docs-version',
                    '3.15',
                    '--output',
                    str(output),
                ],
            ),
            self.assertRaises(FileNotFoundError),
        ):
            main()
        self.assertFalse(output.exists())
