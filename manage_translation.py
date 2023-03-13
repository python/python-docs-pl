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
# * recreate_readme: recreate readme to update translation progress.
# * regenerate_tx_config: recreate configuration for all resources.

from argparse import ArgumentParser
from collections import Counter
import os
from dataclasses import dataclass
from re import match
from subprocess import call, run
import sys
from typing import Self, Callable
from urllib.parse import urlparse, parse_qs

LANGUAGE = 'pl'


def fetch():
    """
    Fetch translations from Transifex, remove source lines.
    """
    if call("tx --version", shell=True) != 0:
        sys.stderr.write("The Transifex client app is required.\n")
        exit(1)
    lang = LANGUAGE
    pull_returncode = call(
        f'tx pull -l {lang} --minimum-perc=1 --force --skip', shell=True
    )
    if pull_returncode != 0:
        exit(pull_returncode)
    for root, _, po_files in os.walk('.'):
        for po_file in po_files:
            if not po_file.endswith(".po"):
                continue
            po_path = os.path.join(root, po_file)
            call(f'msgcat --no-location -o {po_path} {po_path}', shell=True)


RESOURCE_NAME_MAP = {'glossary_': 'glossary'}
PROJECT_SLUG = 'python-newest'


def recreate_tx_config():
    """
    Regenerate Transifex client config for all resources.
    """
    resources = _get_resources()
    with open('.tx/config', 'w') as config:
        config.writelines(
            (
                '[main]\n',
                'host = https://www.transifex.com\n',
            )
        )
        for resource in resources:
            slug = resource.slug
            name = RESOURCE_NAME_MAP.get(slug, slug)
            if slug == '0':
                continue
            elif '--' in slug:
                directory, file_name = name.split('--')
                if match(r'\d+_\d+', file_name):
                    file_name = file_name.replace('_', '.')
                config.writelines(
                    (
                        '\n',
                        f'[o:python-doc:p:{PROJECT_SLUG}:r:{slug}]\n',
                        f'file_filter = {directory}/{file_name}.po\n',
                        'type = PO\n',
                        'source_lang = en\n',
                    )
                )
            else:
                config.writelines(
                    (
                        '\n',
                        f'[o:python-doc:p:{PROJECT_SLUG}:r:{slug}]\n',
                        f'file_filter = {name}.po\n',
                        'type = PO\n',
                        'source_lang = en\n',
                    )
                )


@dataclass
class Resource:
    slug: str

    @classmethod
    def from_api_v3_entry(cls, data: dict) -> Self:
        return cls(slug=data['attributes']['slug'])


@dataclass
class ResourceLanguageStatistics:
    name: str
    total_words: int
    translated_words: int
    total_strings: int
    translated_strings: int

    @classmethod
    def from_api_v3_entry(cls, data: dict) -> Self:
        return cls(
            name=data['id'].removeprefix(f'o:python-doc:p:{PROJECT_SLUG}:r:').removesuffix(f':l:{LANGUAGE}'),
            total_words=data['attributes']['total_words'],
            translated_words=data['attributes']['translated_words'],
            total_strings=data['attributes']['total_strings'],
            translated_strings=data['attributes']['translated_strings'],
        )


def _get_from_api_v3_with_cursor(url: str, params: dict) -> list[dict]:
    from requests import get

    resources = []
    cursor = None
    if os.path.exists('.tx/api-key'):
        with open('.tx/api-key') as f:
            transifex_api_key = f.read()
    else:
        transifex_api_key = os.getenv('TX_TOKEN', '')
    while True:
        response = get(
            url,
            params=params | ({'page[cursor]': cursor} if cursor else {}),
            headers={'Authorization': f'Bearer {transifex_api_key}'}
        )
        response.raise_for_status()
        response_json = response.json()
        response_list = response_json['data']
        resources.extend(response_list)
        if not response_json['links'].get('next'):  # for stats no key, for list resources null
            break
        cursor, *_ = parse_qs(urlparse(response_json['links']['next']).query)['page[cursor]']
    return resources


def _get_resources() -> list[Resource]:
    resources = _get_from_api_v3_with_cursor(
        'https://rest.api.transifex.com/resources', {'filter[project]': f'o:python-doc:p:{PROJECT_SLUG}'}
    )
    return [Resource.from_api_v3_entry(entry) for entry in resources]


def _get_resource_language_stats() -> list[ResourceLanguageStatistics]:
    resources = _get_from_api_v3_with_cursor(
        'https://rest.api.transifex.com/resource_language_stats',
        {'filter[project]': f'o:python-doc:p:{PROJECT_SLUG}', 'filter[language]': f'l:{LANGUAGE}'}
    )
    return [ResourceLanguageStatistics.from_api_v3_entry(entry) for entry in resources]


LANGUAGE_SWITCHER_RESOURCES_PREFIXES = ('bugs', 'tutorial', 'library--functions')


def recreate_readme():
    def _progress_from_resources(resources: list[ResourceLanguageStatistics], filter_function: Callable):
        filtered = filter(filter_function, resources)
        pairs = ((e.translated_words, e.total_words) for e in filtered)
        translated_total, total_total = (sum(counts) for counts in zip(*pairs))
        return translated_total / total_total * 100

    def _language_switcher(entry):
        return any(entry.name.startswith(prefix) for prefix in LANGUAGE_SWITCHER_RESOURCES_PREFIXES)

    def _get_number_of_translators():
        process = run(
            ['grep', '-ohP', r'(?<=^# )(.+)(?=, \d+$)', '-r', '.'],
            capture_output=True,
            text=True,
        )
        translators = [match('(.*)( <.*>)?', t).group(1) for t in process.stdout.splitlines()]
        unique_translators = Counter(translators).keys()
        return len(unique_translators)

    resources = _get_resource_language_stats()
    language_switcher_status = _progress_from_resources(resources, _language_switcher)
    total_progress_status = _progress_from_resources(resources, lambda _: True)
    number_of_translators = _get_number_of_translators()

    with open('README.md', 'w') as file:
        file.write(
            f'''\
Polskie tłumaczenie dokumentacji Pythona
========================================
![build](https://github.com/python/python-docs-pl/workflows/.github/workflows/update-and-build.yml/badge.svg)
![{language_switcher_status:.2f}% przełącznika języków](https://img.shields.io/badge/przełącznik_języków-{language_switcher_status:.2f}%25-0.svg)
![postęp tłumaczenia całości dokumentacji](https://img.shields.io/badge/całość-{total_progress_status:.2f}%25-0.svg)
![{number_of_translators} tłumaczy](https://img.shields.io/badge/tłumaczy-{number_of_translators}-0.svg)

Jeśli znalazłeś(-aś) błąd lub masz sugestię,
[dodaj zgłoszenie](https://github.com/python/python-docs-pl/issues) w tym projekcie lub
napraw go sam(a):

* Zarejestruj się na platformie [Transifex](https://www.transifex.com/) i wejdź na stronę
projektu [dokumentacji Pythona](https://www.transifex.com/python-doc/python-newest/).
* Na stronie projektu wybierz język polski.
* Naciśnij przycisk „Join this Team”, aby dołączyć do zespołu.
* Po dołączeniu do zespołu, wybierz zasób, który chcesz poprawić/zaktualizować.

Więcej informacji o używaniu Transifeksa znajdziesz w
[jego dokumentacji](https://docs.transifex.com/getting-started-1/translators).

**Postęp tłumaczenia**

![postęp tłumaczenia do przełącznika języków](language-switcher-progress.svg)

Język polski pojawi się w przełączniku języków na docs.python.org,
[kiedy w pełni przetłumaczone będą](https://www.python.org/dev/peps/pep-0545/#add-translation-to-the-language-switcher):
* `bugs`,
* wszystkie zasoby z katalogu `tutorial`,
* `library/functions`.

**Jak obejrzeć najnowszy build dokumentacji?**

Pobierz ostatnią zbudowaną dokumentację z listy artefaktów w ostatniej GitHub Action (zakładka Actions).
Tłumaczenia pobierane są z Transifeksa do tego repozytorium co około pół godziny.
Dokumentacja na python.org aktualizowana jest około raz dziennie.

**Kanały komunikacji**

* [python-docs-pl Discord](https://discord.gg/3faJmGKhta)
* [Python translations working group](https://mail.python.org/mailman3/lists/translation.python.org/)
* [Python Documentation Special Interest Group](https://www.python.org/community/sigs/current/doc-sig/)

**Licencja**

Zapraszając do współtworzenia projektu na platformie Transifex, proponujemy umowę na
przekazanie twoich tłumaczeń Python Software Foundation
[na licencji CC0](https://creativecommons.org/publicdomain/zero/1.0/deed.pl).
W zamian będzie widoczne, że jesteś tłumaczem(-ką) części, którą przetłumaczyłeś(-łaś).
Wyrażasz akceptację tej umowy przesyłając swoją pracę do włączenia do dokumentacji.

**Aktualizacja tłumaczeń**
* `./manage_translation.py recreate_tx_config`
* `./manage_translation.py fetch`
* `./manage_translation.py recreate_readme`

**Potencjalnie przydatne materiały**
* [polskie tłumaczenie dokumentacji Pythona 2.3](https://pl.python.org/docs/).
'''
        )


if __name__ == "__main__":
    RUNNABLE_SCRIPTS = ('fetch', 'recreate_tx_config', 'recreate_readme')

    parser = ArgumentParser()
    parser.add_argument('cmd', choices=RUNNABLE_SCRIPTS)
    options = parser.parse_args()

    eval(options.cmd)()
