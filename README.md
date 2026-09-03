Polskie tłumaczenie dokumentacji Pythona
========================================
<!-- [[[cog
from manage_translation import get_resource_language_stats, progress_from_resources, language_switcher

stats = get_resource_language_stats()
core_words, _ = progress_from_resources(list(filter(language_switcher, stats)))
total_words, total_strings = progress_from_resources(stats)

print(
f'''[![build](https://github.com/python/python-docs-pl/actions/workflows/update-and-build.yml/badge.svg)](https://github.com/python/python-docs-pl/actions/workflows/update-and-build.yml)
[![podstawowe artykuły {core_words:.2f}%](https://img.shields.io/badge/podstawowe_artykuły-{core_words:.2f}%25-0.svg)](https://translations.python.org/#pl)
[![postęp tłumaczenia całości dokumentacji](https://img.shields.io/badge/całość_słów-{total_words:.2f}%25-0.svg)](https://translations.python.org/#pl)
[![postęp tłumaczenia całości dokumentacji](https://img.shields.io/badge/całość_napisów-{total_strings:.2f}%25-0.svg)](https://translations.python.org/#pl)
[![liczba błędów lintowania](https://shields.io/badge/dynamic/xml?url=https%3A%2F%2Ftranslations.python.org%2Fbuild-details.html&query=%2F%2Ftr%5Btd%5B%40data-label%3D%27language%27%20and%20contains%28.%2C%20%27%28pl%29%27%29%5D%5D%20%20%20%2F%2Ftd%5B%40data-label%3D%27lint%27%5D%2Fa%2Ftext()&label=b%C5%82%C4%99dy%20lintowania)](https://github.com/python/python-docs-pl/actions/workflows/lint.yml)
''')
]]] -->
[![build](https://github.com/python/python-docs-pl/actions/workflows/update-and-build.yml/badge.svg)](https://github.com/python/python-docs-pl/actions/workflows/update-and-build.yml)
[![podstawowe artykuły 100.00%](https://img.shields.io/badge/podstawowe_artykuły-100.00%25-0.svg)](https://translations.python.org/#pl)
[![postęp tłumaczenia całości dokumentacji](https://img.shields.io/badge/całość_słów-5.76%25-0.svg)](https://translations.python.org/#pl)
[![postęp tłumaczenia całości dokumentacji](https://img.shields.io/badge/całość_napisów-12.48%25-0.svg)](https://translations.python.org/#pl)
[![liczba błędów lintowania](https://shields.io/badge/dynamic/xml?url=https%3A%2F%2Ftranslations.python.org%2Fbuild-details.html&query=%2F%2Ftr%5Btd%5B%40data-label%3D%27language%27%20and%20contains%28.%2C%20%27%28pl%29%27%29%5D%5D%20%20%20%2F%2Ftd%5B%40data-label%3D%27lint%27%5D%2Fa%2Ftext()&label=b%C5%82%C4%99dy%20lintowania)](https://github.com/python/python-docs-pl/actions/workflows/lint.yml)

<!-- [[[end]]] -->

*Read this in another language: [English](README.en.md)*

### Jak sprawdzić, co jest do przetłumaczenia?

Służy do tego paczka [`potodo`](https://pypi.org/project/potodo/). Wywołaj ją w głównym katalogu projektu,
na przykład `uvx potodo`.

Jeżeli interesują cię podstawowe artykuły, użyj filtrowania. Przykład:

```
$ uvx potodo --exclude '**/*' '!tutorial/*' '!bugs.po' '!library/functions.po'
1 directory  99.68% done
└── python-docs-pl/  99.68% done
    ├── library/  98.61% done
    │   └── functions.po                  99.0% translated 535/536
    └── tutorial/  100.00% done
```

Propozycje priorytetowych zasobów do tłumaczenia można znaleźć w [issue #50](https://github.com/python/python-docs-pl/issues/50).

### Jak tłumaczyć?

* Wejdź na stronę
projektu [dokumentacji Pythona](https://explore.transifex.com/python-doc/python-newest/) na Transifeksie.
* Naciśnij przycisk „Join this project”, aby dołączyć do projektu.
* Utwórz konto Transifex.
* Na stronie projektu wybierz język polski.
* Po wysłaniu zgłoszenia do zespołu przedstaw się na kanale [Discord Python Polska `#dokumentacja`](https://discord.gg/VCyBDGH38e).
  Pozwoli to szybciej potwierdzić Twoje zgłoszenie.
* Po dołączeniu do zespołu wybierz zasób, który chcesz poprawić lub zaktualizować.
* Zapoznaj się ze [składnią reStructuredText](https://www.sphinx-doc.org/pl/master/usage/restructuredtext/basics.html),
  formatem dokumentacji.
* Więcej informacji o używaniu Transifeksa znajdziesz w [jego artykułach pomocy](https://help.transifex.com/en/articles/6318216-translating-with-the-web-editor)
  lub [w naszym przewodniku](https://python-docs-transifex-automation.readthedocs.io/new-translators.html).

### Jak lokalnie sprawdzić poprawność moich zmian?

[Zainstaluj Transifex CLI](https://github.com/transifex/cli#installation) i zapisz
[klucz API Transifex](https://help.transifex.com/en/articles/6248858-generating-an-api-token) do `~/.transifexrc`, aby
pobrać zmiany z Transifeksa. Pobierz zmieniony rozdział, np.:

```
$ tx pull --languages pl python-newest.library--turtle
# Getting info about resources

python-newest.library--turtle - Done
[##############################] (1 / 1)

# Pulling files

python-newest.library--turtle [pl] - Done
[##############################] (1 / 1)
```

Uruchom [`sphinx-lint`](https://pypi.org/project/sphinx-lint/), aby sprawdzić poprawność zmian, na przykład:

```
$ uvx sphinx-lint library/turtle.po
No problems found.
```

### Jak obejrzeć najnowszy build dokumentacji?

Pobierz ostatnią zbudowaną dokumentację z listy artefaktów w ostatniej GitHub Action (zakładka Actions).
Tłumaczenia pobierane są z Transifeksa do tego repozytorium co około godzinę.
Dokumentacja na https://docs.python.org/pl/ aktualizowana jest około raz dziennie.

### Jak zbudować dokumentację?

Aby zbudować dokumentację potrzebujesz mieć kopię repozytorium CPythona.

Zrób link symboliczny (Unix) lub kopię (Windows) zawartości projektu `python-docs-pl` w katalogu
`Doc/locales/pl/LC_MESSAGES` w repozytorium CPython.

Następnie uruchom `make -C Doc SPHINXOPTS="-D language=pl" html` w projekcie CPython, aby zbudować dokumentację.

### Kanały komunikacji

* [Discord Python Polska #dokumentacja](https://discord.gg/VCyBDGH38e)
* [Python Documentation Community](https://docs-community.readthedocs.io/en/latest/)
* [Python Documentation Special Interest Group](https://www.python.org/community/sigs/current/doc-sig/)

### Postęp tłumaczenia

<img src="translation_progress_pl.svg" alt="Postęp tłumaczenia">

<!---
Excludes the changelog from calculations.
Made using: https://gist.github.com/StanFromIreland/ce400e0d497018fc8e8eb6b739e0b8eb
--->

### Licencja

Zapraszając do współtworzenia projektu na platformie Transifex, proponujemy umowę na
przekazanie twoich tłumaczeń Python Software Foundation
[na licencji CC0](https://creativecommons.org/publicdomain/zero/1.0/deed.pl).
W zamian będzie widoczne, że jesteś tłumaczem(-ką) części, którą przetłumaczyłeś(-łaś).
Wyrażasz akceptację tej umowy, przesyłając swoją pracę do włączenia do dokumentacji.

### Aktualizacje w repozytorium

* `./manage_translation.py recreate_tx_config`
* `./manage_translation.py fetch`
* `cog -rP README.md`

### Przydatne materiały

* [Python Developer's Guide: Translating](https://devguide.python.org/documentation/translations/translating/)
* [Python docs Transifex: Documentation](https://python-docs-transifex-automation.readthedocs.io/)
* [statystyki oglądalności](https://analytics.python.org/docs.python.org?f=contains,page,/pl/)

### Podobne projekty

* [projekty Python Packaging Authority](https://hosted.weblate.org/projects/pypa/-/pl/)
* [Scientific Python Translations](https://scientific-python-translations.github.io/)
* [micro:bit translation programme](https://microbit.org/translate/)
* [tłumaczenie Sphinksa](https://www.sphinx-doc.org/en/master/usage/advanced/intl.html#contributing-to-sphinx-reference-translation)
* [Localizing Django](https://docs.djangoproject.com/en/dev/internals/contributing/localizing/)
