#!/usr/bin/env python
#
# This python file contains utility scripts to manage Python docs Polish translation.
# It has to be run inside the python-docs-pl git root directory.
#
# Inspired by django-docs-translations script by claudep.
#
# The following commands are available:
#
# * fetch: fetch translations from transifex.com and strip source lines from the
#          files.
# * recreate_tx_config: recreate configuration for all resources.
# * warn_about_files_to_delete: lists files that are not available upstream
# * generate_commit_msg: generates commit message with co-authors
# * fetch_glossary: download Polish terminology as a Hunspell personal dictionary

import csv
import io
import os
import re
import sys
import time
import unicodedata
from argparse import ArgumentParser
from collections.abc import Iterable
from contextlib import chdir
from dataclasses import dataclass
from pathlib import Path
from subprocess import CalledProcessError, call, run
from tempfile import TemporaryDirectory
from typing import Self
from warnings import warn

import requests
from polib import POFile, pofile
from transifex.api import transifex_api
from transifex.api.jsonapi.exceptions import JsonApiException

LANGUAGE = 'pl'
PROJECT_SLUG = 'python-newest'
VERSION = '3.14'
GLOSSARY_ID = 'o:python-doc:g:python_global'


def fetch():
    """
    Fetch translations from Transifex, remove source lines.
    """
    if (code := call('tx --version', shell=True)) != 0:
        sys.stderr.write('The Transifex client app is required.\n')
        sys.exit(code)
    lang = LANGUAGE
    _call(f'tx pull -l {lang} --minimum-perc=1 --force --skip')
    for file in Path().rglob('*.po'):
        _call(f'msgcat --no-location -o {file} {file}')


def _download_glossary(token: str, *, max_wait: float = 300) -> str:
    transifex_api.setup(auth=token)
    # The SDK supports new API resource types before adding dedicated classes.
    download = transifex_api.new(
        type='glossaries_async_downloads',
        glossary=transifex_api.new(type='glossaries', id=GLOSSARY_ID),
        language=transifex_api.Language(id=f'l:{LANGUAGE}'),
    )
    download.save()
    deadline = time.monotonic() + max_wait
    while not download.redirect:
        status = download.attributes['status']
        if status == 'failed':
            raise ValueError('Transifex glossary export failed.')
        if status not in {'pending', 'processing'}:
            raise ValueError(f'Unexpected glossary export status: {status!r}')
        if time.monotonic() >= deadline:
            raise ValueError('Transifex glossary export timed out.')
        time.sleep(3)
        download.reload()
    # Download the CSV without sending the API token to the signed storage URL.
    export = requests.get(download.redirect, timeout=30)
    export.raise_for_status()
    return export.content.decode('utf-8-sig')


def _glossary_words(content: str) -> list[str]:
    reader = csv.DictReader(io.StringIO(content))
    translation_column = f'translation_{LANGUAGE}'
    if not reader.fieldnames or translation_column not in reader.fieldnames:
        raise ValueError('Transifex glossary CSV has no Polish translation column.')
    words = {
        word
        for row in reader
        for word in re.findall(
            r'[^\W\d_]+', unicodedata.normalize('NFC', row[translation_column] or '')
        )
    }
    if not words:
        raise ValueError('Transifex glossary has no Polish terms.')
    return sorted(words)


def fetch_glossary(output: Path):
    """Fetch Polish terminology and write a UTF-8 Hunspell personal dictionary."""
    token = _get_tx_token().strip()
    if not token:
        raise ValueError('TX_TOKEN is required to download the Transifex glossary.')
    words = _glossary_words(_download_glossary(token))
    output.write_text(f'{len(words)}\n' + '\n'.join(words) + '\n', encoding='utf-8')
    print(f'Added {len(words)} Polish glossary words to {output}.')


def _call(command: str):
    if (return_code := call(command, shell=True)) != 0:
        sys.exit(return_code)


def recreate_tx_config():
    """
    Regenerate Transifex client config for all resources.
    """
    with TemporaryDirectory() as directory:
        with chdir(directory):
            _clone_cpython_repo(VERSION)
            _build_gettext()
            with chdir(Path(directory) / 'cpython/Doc/build'):
                _create_txconfig()
                _update_txconfig_resources()
                with open('.tx/config', 'r') as file:
                    contents = file.read()
        contents = contents.replace('./<lang>/LC_MESSAGES/', '')
        with open('.tx/config', 'w') as file:
            file.write(contents)
    warn_about_files_to_delete()


def warn_about_files_to_delete():
    files = list(_get_files_to_delete())
    if not files:
        return
    warn(f'Found {len(files)} file(s) to delete: {", ".join(files)}.')


def _get_files_to_delete():
    with open('.tx/config') as config_file:
        config = config_file.read()
    for file in Path().rglob('*.po'):
        if os.fsdecode(file) not in config:
            yield os.fsdecode(file)


def _clone_cpython_repo(version: str):
    _call(
        f'git clone -b {version} --single-branch https://github.com/python/cpython.git --depth 1'
    )


def _build_gettext():
    _call('make -C cpython/Doc/ gettext')


def _create_txconfig():
    _call('sphinx-intl create-txconfig')


def _update_txconfig_resources():
    _call(
        f'sphinx-intl update-txconfig-resources --transifex-organization-name python-doc '
        f'--transifex-project-name={PROJECT_SLUG} --locale-dir . --pot-dir gettext'
    )


@dataclass
class ResourceLanguageStatistics:
    name: str
    total_words: int
    translated_words: int
    total_strings: int
    translated_strings: int

    @classmethod
    def from_api_entry(cls, data: transifex_api.ResourceLanguageStats) -> Self:
        return cls(
            name=data.id.removeprefix(f'o:python-doc:p:{PROJECT_SLUG}:r:').removesuffix(
                f':l:{LANGUAGE}'
            ),
            total_words=data.attributes['total_words'],
            translated_words=data.attributes['translated_words'],
            total_strings=data.attributes['total_strings'],
            translated_strings=data.attributes['translated_strings'],
        )


def _get_tx_token() -> str:
    if os.path.exists('.tx/api-key'):
        with open('.tx/api-key') as f:
            transifex_api_key = f.read()
    else:
        transifex_api_key = os.getenv('TX_TOKEN', '')
    return transifex_api_key


def _get_resources() -> list[transifex_api.Resource]:
    transifex_api.setup(auth=_get_tx_token())
    return transifex_api.Resource.filter(project=f'o:python-doc:p:{PROJECT_SLUG}').all()


def get_resource_language_stats() -> list[ResourceLanguageStatistics]:
    transifex_api.setup(auth=_get_tx_token())
    resources = transifex_api.ResourceLanguageStats.filter(
        project=f'o:python-doc:p:{PROJECT_SLUG}', language=f'l:{LANGUAGE}'
    ).all()
    return [ResourceLanguageStatistics.from_api_entry(entry) for entry in resources]


def progress_from_resources(
    resources: Iterable[ResourceLanguageStatistics],
) -> tuple[float, float]:
    word_pairs = ((e.translated_words, e.total_words) for e in resources)
    string_pairs = ((e.translated_strings, e.total_strings) for e in resources)
    translated_total_words, total_words = (sum(counts) for counts in zip(*word_pairs))
    translated_total_strs, total_strs = (sum(counts) for counts in zip(*string_pairs))
    return (
        translated_total_words / total_words * 100,
        translated_total_strs / total_strs * 100,
    )


def language_switcher(entry: ResourceLanguageStatistics) -> bool:
    language_switcher_resources_prefixes = ('bugs', 'tutorial', 'library--functions')
    return any(
        entry.name.startswith(prefix) for prefix in language_switcher_resources_prefixes
    )


def generate_commit_msg():
    """Generate a commit message
    Parses staged files and generates a commit message with Last-Translator's as
    co-authors.
    """
    translators: set[str] = set()

    result = run(
        ['git', 'diff', '--cached', '--name-only', '--diff-filter=ACM'],
        capture_output=True,
        text=True,
        check=True,
    )
    staged = [
        filename for filename in result.stdout.splitlines() if filename.endswith('.po')
    ]

    for file in staged:
        staged_file = run(
            ['git', 'show', f':{file}'], capture_output=True, text=True, check=True
        ).stdout
        try:
            old_file = run(
                ['git', 'show', f'HEAD:{file}'],
                capture_output=True,
                text=True,
                check=True,
            ).stdout
        except CalledProcessError:
            old_file = ''

        new_po = pofile(staged_file)
        old_po = pofile(old_file) if old_file else POFile()
        old_entries = {entry.msgid: entry.msgstr for entry in old_po}

        for entry in new_po:
            if entry.msgstr and (
                entry.msgid not in old_entries
                or old_entries[entry.msgid] != entry.msgstr
            ):
                translator = new_po.metadata.get('Last-Translator')
                translator = translator.split(',')[0].strip()
                if translator:
                    translators.add(f'Co-Authored-By: {translator}')
                break

    print('Update translation from Transifex\n\n' + '\n'.join(translators))


if __name__ == '__main__':
    RUNNABLE_SCRIPTS = (
        'fetch',
        'recreate_tx_config',
        'warn_about_files_to_delete',
        'generate_commit_msg',
        'fetch_glossary',
    )

    parser = ArgumentParser()
    parser.add_argument('cmd', choices=RUNNABLE_SCRIPTS)
    parser.add_argument(
        '--output', type=Path, help='Hunspell dictionary path for fetch_glossary'
    )
    options = parser.parse_args()

    if options.cmd == 'fetch_glossary':
        if options.output is None:
            parser.error('--output is required for fetch_glossary')
        try:
            fetch_glossary(options.output)
        except (requests.RequestException, JsonApiException) as error:
            # Exceptions may contain signed URLs; report the status without those URLs.
            status = (
                error.response.status_code
                if error.response is not None
                else 'network error'
            )
            parser.exit(1, f'Transifex glossary request failed: {status}.\n')
        except (ValueError, KeyError) as error:
            parser.exit(1, f'Invalid Transifex glossary export: {error}\n')
    else:
        eval(options.cmd)()
