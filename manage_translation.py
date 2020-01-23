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

import os
import sys
from argparse import ArgumentParser
from subprocess import call

LANGUAGE = 'pl'


def fetch():
    """
    Fetch translations from Transifex, remove source lines.
    """
    if call("tx --version", shell=True) != 0:
        sys.stderr.write("The Transifex client app is required (pip install transifex-client).\n")
        exit(1)
    lang = LANGUAGE
    if os.getenv('GITHUB_ACTIONS'):
        call(f'tx pull -l {lang} --minimum-perc=25 --force', shell=True)
    else:
        call(f'tx pull -l {lang} --minimum-perc=25', shell=True)
    for root, _, po_files in os.walk('.'):
        for po_file in po_files:
            if not po_file.endswith(".po"):
                continue
            po_path = os.path.join(root, po_file)
            call(f'msgcat --no-location -o {po_path} {po_path}', shell=True)


RESOURCE_NAME_MAP = {
    'glossary_': 'glossary'
}
PROJECT_SLUG = 'python-newest'


def recreate_tx_config():
    """
    Regenerate Transifex client config for all resources.
    """
    resources = _get_resources()
    with open('.tx/config', 'w') as config:
        config.writelines((
            '[main]\n',
            'host = https://www.transifex.com\n',
        ))
        for resource in resources:
            slug = resource['slug']
            name = RESOURCE_NAME_MAP.get(slug, slug)
            if '--' in slug:
                directory, file_name = name.split('--')
                config.writelines((
                    '\n',
                    f'[{PROJECT_SLUG}.{slug}]\n',
                    f'trans.{LANGUAGE} = {directory}/{file_name}.po\n',
                    'type = PO\n',
                    'source_lang = en\n',
                ))
            else:
                config.writelines((
                    '\n',
                    f'[{PROJECT_SLUG}.{slug}]\n',
                    f'trans.{LANGUAGE} = {name}.po\n',
                    'type = PO\n',
                    'source_lang = en\n',
                ))


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
            auth=('api', transifex_api_key))
        response_list = response.json()
        resources.extend(response_list)
        if len(response_list) < 100:
            break
        offset += len(response_list)
    return resources


def recreate_readme():
    from numpy import average
    
    def language_switcher(entry):
        return (entry['name'].startswith('bugs') or
                entry['name'].startswith('tutorial') or
                entry['name'].startswith('library--functions'))

    resources = _get_resources()
    filtered = list(filter(language_switcher, resources))
    average_list = [e['stats']['translated']['percentage'] for e in filtered]
    weights_list = [e['wordcount'] for e in filtered]

    language_switcher_status = average(average_list, weights=weights_list) * 100

    with open('README.md', 'w') as file:
        file.write(
            f'''\
Polskie tłumaczenie dokumentacji Pythona
========================================
![{language_switcher_status:.2f}% language switchera](https://img.shields.io/badge/language_switcher-{language_switcher_status:.2f}%25-0.svg)
![postęp tłumaczenia całości dokumentacji](https://img.shields.io/badge/dynamic/json.svg?label=całość&query=$.{LANGUAGE}&url=http://gce.zhsj.me/python/newest)

[Pomóż tłumaczyć](https://www.transifex.com/python-doc/python-newest/)
dokumentację Pythona na język polski.

Przydatne materiały:
* [polskie tłumaczenie dokumentacji Pythona 2.3](https://pl.python.org/docs/).

Znalazłeś błąd lub masz sugestię?
---------------------------------
* [Dodaj zgłoszenie](https://github.com/m-aciek/python-docs-pl/issues) w tym projekcie
* lub sam [nanieś poprawkę](https://www.transifex.com/python-doc/python-newest/)
  w projekcie *Python document translation* na platformie Transifex.
 
Aktualizacja tłumaczeń
----------------------
* `./manage_translations.py recreate_tx_config`
* `./manage_translations.py fetch`
* `./manage_translations.py recreate_readme`
'''
        )


if __name__ == "__main__":
    RUNNABLE_SCRIPTS = ('fetch', 'recreate_tx_config', 'recreate_readme')

    parser = ArgumentParser()
    parser.add_argument('cmd', nargs=1, choices=RUNNABLE_SCRIPTS)
    options = parser.parse_args()

    eval(options.cmd[0])()
