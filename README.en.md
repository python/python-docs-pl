Polish Translation of Python Documentation
==========================================
<!-- [[[cog
from manage_translation import get_resource_language_stats, progress_from_resources, language_switcher

stats = get_resource_language_stats()
core_words, _ = progress_from_resources(list(filter(language_switcher, stats)))
total_words, total_strings = progress_from_resources(stats)

print(
f'''[![build](https://github.com/python/python-docs-pl/actions/workflows/update-and-build.yml/badge.svg)](https://github.com/python/python-docs-pl/actions/workflows/update-and-build.yml)
[![core {core_words:.2f}%](https://img.shields.io/badge/core-{core_words:.2f}%25-0.svg)](https://translations.python.org/#pl)
[![Total Translation of Documentation](https://img.shields.io/badge/total_words-{total_words:.2f}%25-0.svg)](https://translations.python.org/#pl)
[![Total Translation of Documentation](https://img.shields.io/badge/total_strings-{total_strings:.2f}%25-0.svg)](https://translations.python.org/#pl)
[![lint errors count](https://shields.io/badge/dynamic/xml?url=https%3A%2F%2Ftranslations.python.org%2Fbuild-details.html&query=%2F%2Ftr%5Btd%5B%40data-label%3D%27language%27%20and%20contains%28.%2C%20%27%28pl%29%27%29%5D%5D%20%20%20%2F%2Ftd%5B%40data-label%3D%27lint%27%5D%2Fa%2Ftext()&label=lint%20errors)](https://github.com/python/python-docs-pl/actions/workflows/lint.yml)
''')
]]] -->
[![build](https://github.com/python/python-docs-pl/actions/workflows/update-and-build.yml/badge.svg)](https://github.com/python/python-docs-pl/actions/workflows/update-and-build.yml)
[![core 100.00%](https://img.shields.io/badge/core-100.00%25-0.svg)](https://translations.python.org/#pl)
[![Total Translation of Documentation](https://img.shields.io/badge/total_words-5.69%25-0.svg)](https://translations.python.org/#pl)
[![Total Translation of Documentation](https://img.shields.io/badge/total_strings-12.46%25-0.svg)](https://translations.python.org/#pl)
[![lint errors count](https://shields.io/badge/dynamic/xml?url=https%3A%2F%2Ftranslations.python.org%2Fbuild-details.html&query=%2F%2Ftr%5Btd%5B%40data-label%3D%27language%27%20and%20contains%28.%2C%20%27%28pl%29%27%29%5D%5D%20%20%20%2F%2Ftd%5B%40data-label%3D%27lint%27%5D%2Fa%2Ftext()&label=lint%20errors)](https://github.com/python/python-docs-pl/actions/workflows/lint.yml)

<!-- [[[end]]] -->

*Przeczytaj to w innym języku: [polski](README.md)*

### How do I check what needs translating?

Use the [`potodo`](https://pypi.org/project/potodo/) package. Run it in the project's root directory,
for example: `uvx potodo`.

If you are interested in the core articles, use filtering. For example:

```
$ uvx potodo --exclude '**/*' '!tutorial/*' '!bugs.po' '!library/functions.po'
1 directory  99.68% done
└── python-docs-pl/  99.68% done
    ├── library/  98.61% done
    │   └── functions.po                  99.0% translated 535/536
    └── tutorial/  100.00% done
```

Suggested priority resources for translation can be found in [issue #50](https://github.com/python/python-docs-pl/issues/50).

### How do I translate?

* Go to the [Python Documentation project](https://explore.transifex.com/python-doc/python-newest/) on Transifex.
* Click the "Join this project" button.
* Create an account on Transifex.
* Select Polish on the project page.
* After submitting your request to join the team, introduce yourself on the [Python Polska #dokumentacja Discord channel](https://discord.gg/QB3h2Sxc).
  This will help us approve your request sooner.
* After joining the team, select the resource you want to improve or update.
* Get familiar with [reStructuredText syntax](https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html),
  the documentation format.
* You can find more information about using Transifex in [their help articles](https://help.transifex.com/en/articles/6318216-translating-with-the-web-editor)
  or [our guide](https://python-docs-transifex-automation.readthedocs.io/new-translators.html).

### How do I check my changes locally?

[Install the Transifex CLI](https://github.com/transifex/cli#installation) and save your
[Transifex API token](https://help.transifex.com/en/articles/6248858-generating-an-api-token) to `~/.transifexrc` so that you
can download changes from Transifex. Download the changed chapter, for example:

```
$ tx pull --languages pl python-newest.library--turtle
# Getting info about resources

python-newest.library--turtle - Done
[##############################] (1 / 1)

# Pulling files

python-newest.library--turtle [pl] - Done
[##############################] (1 / 1)
```

Run [`sphinx-lint`](https://pypi.org/project/sphinx-lint/) to check your changes, for example:

```
$ uvx sphinx-lint library/turtle.po
No problems found.
```

### How do I see the latest build of the documentation?

Download the latest build from the list of artefacts in the latest GitHub Action (Actions Tab).
Translations are pulled from Transifex around once an hour.
The documentation at https://docs.python.org/pl/ is updated around once daily.

### How do I build the documentation?

[See devguide's instructions.](https://devguide.python.org/documentation/translations/translating/#how-do-i-build-a-docs-translation)

### Communication channels

* [Discord Python Polska #dokumentacja](https://discord.gg/QB3h2Sxc)
* [Python Documentation Community](https://docs-community.readthedocs.io/)
* [Python Documentation Special Interest Group](https://www.python.org/community/sigs/current/doc-sig/)

### Translation progress

<img src="translation_progress_en.svg" alt="Translation progress">

<!---
Excludes the changelog from calculations.
Made using: https://gist.github.com/StanFromIreland/ce400e0d497018fc8e8eb6b739e0b8eb
--->

### License

By inviting you to work on a project on the Transifex platform, we offer a contract for
donating your translations to the Python Software Foundation
[under the CC0 license](https://creativecommons.org/publicdomain/zero/1.0/deed.pl).
In return, it will be visible that you are the translator of the part you translated.
You signify your acceptance of this agreement by submitting your work for inclusion in the documentation.

### Repository updates

* `./manage_translation.py recreate_tx_config`
* `./manage_translation.py fetch`
* `cog -rP README.en.md`

### Useful materials

* [Python Developer's Guide: Translating](https://devguide.python.org/documentation/translations/translating/)
* [Python docs Transifex: Documentation](https://python-docs-transifex-automation.readthedocs.io/)
* [Site Statistics](https://analytics.python.org/docs.python.org?f=contains,page,/pl/)

### Similar projects

* [Projects of the Python Packaging Authority](https://hosted.weblate.org/projects/pypa/-/pl/)
* [Scientific Python Translations](https://scientific-python-translations.github.io/)
* [micro:bit translation programme](https://microbit.org/translate/)
* [Sphinx translation](https://www.sphinx-doc.org/en/master/usage/advanced/intl.html#contributing-to-sphinx-reference-translation)
* [Localizing Django](https://docs.djangoproject.com/en/dev/internals/contributing/localizing/)
