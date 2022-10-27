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
from re import match
from subprocess import call, run
import sys

LANGUAGE = 'pl'


def fetch(args):
    """
    Fetch translations from Transifex, remove source lines.
    """
    if call("tx --version", shell=True) != 0:
        sys.stderr.write("The Transifex client app is required.\n")
        exit(1)
    lang = LANGUAGE
    pull_returncode = call(
        f'tx --token {args.tx_token} pull -l {lang} --minimum-perc=1 --force --skip', shell=True
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


def recreate_tx_config(args):
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
            slug = resource['slug']
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


def _get_resources():
    from requests import get

    resources = []
    offset = 0
    if os.path.exists('.tx/api-key'):
        with open('.tx/api-key') as f:
            transifex_api_key = f.read()
    else:
        transifex_api_key = os.getenv('TX_TOKEN')
    while True:
        response = get(
            f'https://api.transifex.com/organizations/python-doc/projects/{PROJECT_SLUG}/resources/',
            params={'language_code': LANGUAGE, 'offset': offset},
            auth=('api', transifex_api_key),
        )
        response.raise_for_status()
        response_list = response.json()
        resources.extend(response_list)
        if len(response_list) < 100:
            break
        offset += len(response_list)
    return resources


def _get_number_of_translators():
    process = run(
        ['grep', '-ohP', r'(?<=^# )(.+)(?=, \d+$)', '-r', '.'],
        capture_output=True,
        text=True,
    )
    translators = [match('(.*)( <.*>)?', t).group(1) for t in process.stdout.splitlines()]
    unique_translators = Counter(translators).keys()
    return len(unique_translators)


def recreate_readme(args):
    def language_switcher(entry):
        return (
            entry['name'].startswith('bugs')
            or entry['name'].startswith('tutorial')
            or entry['name'].startswith('library--functions')
        )

    def average(averages, weights):
        return sum([a * w for a, w in zip(averages, weights)]) / sum(weights)

    resources = _get_resources()
    filtered = list(filter(language_switcher, resources))
    average_list = [e['stats']['translated']['percentage'] for e in filtered]
    weights_list = [e['wordcount'] for e in filtered]

    language_switcher_status = average(average_list, weights=weights_list) * 100
    number_of_translators = _get_number_of_translators()

    with open('README.md', 'w') as file:
        file.write(
            f'''\
Polskie tłumaczenie dokumentacji Pythona
========================================
![build](https://github.com/python/python-docs-pl/workflows/.github/workflows/update-and-build.yml/badge.svg)
![{language_switcher_status:.2f}% przełącznika języków](https://img.shields.io/badge/przełącznik_języków-{language_switcher_status:.2f}%25-0.svg)
![postęp tłumaczenia całości dokumentacji](https://img.shields.io/badge/dynamic/json.svg?label=całość&query=$.{LANGUAGE}&url=http://gce.zhsj.me/python/newest)
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
    subparsers = parser.add_subparsers()
    fetch_parser = subparsers.add_parser('fetch')
    fetch_parser.add_argument('tx_token', nargs=1)
    fetch_parser.set_defaults(func=fetch)
    config_parser = subparsers.add_parser('recreate_tx_config')
    config_parser.set_defaults(func=recreate_tx_config)
    readme_parser = subparsers.add_parser('recreate_readme')
    readme_parser.set_defaults(func=recreate_readme)
    options = parser.parse_args()
    options.func(options)
