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
from pathlib import Path
from re import match, search
from subprocess import call, run
import sys
from urllib.parse import unquote
from warnings import warn

LANGUAGE = 'pl'


def fetch():
    """
    Fetch translations from Transifex, remove source lines.
    """
    if call("tx --version", shell=True) != 0:
        sys.stderr.write(
            "The Transifex client app is required (pip install transifex-client).\n"
        )
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
PROJECT_SLUG = 'python-39'


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
                        f'[{PROJECT_SLUG}.{slug}]\n',
                        f'trans.{LANGUAGE} = {directory}/{file_name}.po\n',
                        'type = PO\n',
                        'source_lang = en\n',
                    )
                )
            else:
                config.writelines(
                    (
                        '\n',
                        f'[{PROJECT_SLUG}.{slug}]\n',
                        f'trans.{LANGUAGE} = {name}.po\n',
                        'type = PO\n',
                        'source_lang = en\n',
                    )
                )
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


@dataclass
class Resource:
    slug: str

    @classmethod
    def from_api_v3_entry(cls, data: dict):
        return cls(slug=data['attributes']['slug'])


@dataclass
class ResourceLanguageStatistics:
    name: str
    total_words: int
    translated_words: int
    total_strings: int
    translated_strings: int

    @classmethod
    def from_api_v3_entry(cls, data: dict):
        return cls(
            name=search('r:([^:]*)', data['id']).group(1),
            total_words=data['attributes']['total_words'],
            translated_words=data['attributes']['translated_words'],
            total_strings=data['attributes']['total_strings'],
            translated_strings=data['attributes']['translated_strings'],
        )


def _get_from_api_v3_with_cursor(url: str, params: dict):
    from requests import get

    resources = []
    cursor = None
    if os.path.exists('.tx/api-key'):
        with open('.tx/api-key') as f:
            transifex_api_key = f.read()
    else:
        transifex_api_key = os.getenv('TX_TOKEN')
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
        cursor = unquote(search('page\[cursor]=([^&]*)', response_json['links']['next']).group(1))
    return resources


def _get_resources():
    resources = _get_from_api_v3_with_cursor(
        'https://rest.api.transifex.com/resources', {'filter[project]': f'o:python-doc:p:{PROJECT_SLUG}'}
    )
    return [Resource.from_api_v3_entry(entry) for entry in resources]


def _get_resource_language_stats():
    resources = _get_from_api_v3_with_cursor(
        'https://rest.api.transifex.com/resource_language_stats',
        {'filter[project]': f'o:python-doc:p:{PROJECT_SLUG}', 'filter[language]': f'l:{LANGUAGE}'}
    )
    return [ResourceLanguageStatistics.from_api_v3_entry(entry) for entry in resources]


def _get_number_of_translators():
    process = run(
        ['grep', '-ohP', r'(?<=^# )(.+)(?=, \d+$)', '-r', '.'],
        capture_output=True,
        text=True,
    )
    translators = [match('(.*)( <.*>)?', t).group(1) for t in process.stdout.splitlines()]
    unique_translators = Counter(translators).keys()
    return len(unique_translators)


def recreate_readme():
    def language_switcher(entry):
        return (
            entry.name.startswith('bugs')
            or entry.name.startswith('tutorial')
            or entry.name.startswith('library--functions')
        )

    def average(averages, weights):
        return sum([a * w for a, w in zip(averages, weights)]) / sum(weights)

    resources = _get_resource_language_stats()
    filtered = list(filter(language_switcher, resources))
    average_list = [e.translated_strings / e.total_strings for e in filtered]
    weights_list = [e.total_words for e in filtered]

    language_switcher_status = average(average_list, weights=weights_list) * 100
    number_of_translators = _get_number_of_translators()

    with open('README.md', 'w') as file:
        file.write(
            f'''\
Polskie tłumaczenie dokumentacji Pythona
========================================
![build](https://github.com/python/python-docs-pl/workflows/.github/workflows/update-and-build.yml/badge.svg)
![{language_switcher_status:.2f}% przełącznika języków](https://img.shields.io/badge/przełącznik_języków-{language_switcher_status:.2f}%25-0.svg)
![postęp tłumaczenia całości dokumentacji](https://img.shields.io/badge/dynamic/json.svg?label=całość&query=$.{LANGUAGE}&url=http://gce.zhsj.me/python/39)
![{number_of_translators} tłumaczy](https://img.shields.io/badge/tłumaczy-{number_of_translators}-0.svg)

Praca nad tłumaczeniem dokumentacji odbywa się na platformie [Transifex](https://www.transifex.com/).

Jeśli znalazłeś(-aś) błąd lub masz sugestię,
[dodaj zgłoszenie](https://github.com/python/python-docs-pl/issues) w tym projekcie lub
przejdź do projektu
[*Python document translation*](https://www.transifex.com/python-doc/python-39/)
na platformie Transifex.

Jeśli chcesz pomóc w tłumaczeniu, oto co powinnaś(-nieneś) zrobić:

* Zarejestruj się na plaformie [Transifex](https://www.transifex.com/) i odwiedź stronę
projektu [Python document](https://www.transifex.com/python-doc/python-39/).
* Na stronie projektu wybierz język nad którym chcesz pracować.
* Następnie naciśnij przycisk „Join this Team”, aby dołączyć do zespołu.
* Gdy już będziesz członkiem zespołu na stronie zespołu wybierz zasób, który chcesz zaktualizować.

Więcej informacji o używaniu Transifexa znajdziesz w
[dokumentacji Transifexa](https://docs.transifex.com/getting-started-1/translators).

**Jak obejrzeć build dokumentacji?**

Wejdź na [https://docs.python.org/pl/](https://docs.python.org/pl/)
lub pobierz zbudowaną dokumentację z listy artefaktów w ostatniej GitHub Action. 

**Dlaczego ta dokumentacja nie jest dostępna w przełączniku języków?**

Pojawi się w tam
[kiedy w pełni przetłumaczone będą zasoby](https://www.python.org/dev/peps/pep-0545/#add-translation-to-the-language-switcher):
* `bugs`,
* wszystkie z katalogu `tutorial`,
* `library/functions`.

**Kanały komunikacji**

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
    RUNNABLE_SCRIPTS = ('fetch', 'recreate_tx_config', 'recreate_readme', 'warn_about_files_to_delete')

    parser = ArgumentParser()
    parser.add_argument('cmd', nargs=1, choices=RUNNABLE_SCRIPTS)
    options = parser.parse_args()

    eval(options.cmd[0])()
