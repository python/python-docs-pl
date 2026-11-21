"""Adapt pospell's JSON report for translation-priority consumers."""

import argparse
import hashlib
import json
import os
import subprocess
from pathlib import Path


def revision(root: Path) -> str:
    return subprocess.check_output(
        ['git', '-C', str(root), 'rev-parse', 'HEAD'], text=True
    ).strip()


def snapshot_catalogs(translations: Path, cpython: Path) -> dict:
    """Record repository identities before sphinx-intl rewrites temporary POs."""
    return {
        'translations_revision': revision(translations),
        'cpython_revision': revision(cpython),
        'catalogs': {
            path.relative_to(translations).as_posix(): hashlib.sha256(
                path.read_bytes()
            ).hexdigest()
            for path in sorted(translations.rglob('*.po'))
        },
    }


def prepare_report(
    report: dict,
    snapshot: dict,
    *,
    docs_version: str,
    repository: str,
    run_url: str,
) -> dict:
    """Keep pospell findings intact while describing the original checkout."""
    if report.get('schema_version') != 1:
        raise ValueError('Unsupported pospell report schema')
    if report.get('status') not in {'complete', 'error'}:
        raise ValueError('Invalid pospell report status')
    return {
        **report,
        'language': 'pl',
        'dictionaries': report['language'].split(','),
        'repository': repository,
        'docs_version': docs_version,
        'run_url': run_url,
        'translations_revision': snapshot['translations_revision'],
        'cpython_revision': snapshot['cpython_revision'],
        'catalogs': {
            resource: {
                **catalog,
                'scanned_sha256': catalog['source_sha256'],
                'source_sha256': snapshot['catalogs'][resource],
            }
            for resource, catalog in report['catalogs'].items()
            # Newly created catalogs have no corresponding repository file.
            if resource in snapshot['catalogs']
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    snapshot_parser = commands.add_parser('snapshot')
    snapshot_parser.add_argument('--translations', type=Path, required=True)
    snapshot_parser.add_argument('--cpython', type=Path, required=True)
    snapshot_parser.add_argument('--output', type=Path, required=True)
    report_parser = commands.add_parser('prepare')
    report_parser.add_argument('--input', type=Path, required=True)
    report_parser.add_argument('--snapshot', type=Path, required=True)
    report_parser.add_argument('--docs-version', required=True)
    report_parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.command == 'snapshot':
        data = snapshot_catalogs(args.translations, args.cpython)
    else:
        data = prepare_report(
            json.loads(args.input.read_text(encoding='utf-8')),
            json.loads(args.snapshot.read_text(encoding='utf-8')),
            docs_version=args.docs_version,
            repository=os.environ['GITHUB_REPOSITORY'],
            run_url=(
                f'{os.environ["GITHUB_SERVER_URL"]}/'
                f'{os.environ["GITHUB_REPOSITORY"]}/actions/runs/'
                f'{os.environ["GITHUB_RUN_ID"]}'
            ),
        )
    args.output.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8'
    )


if __name__ == '__main__':
    main()
