Polskie tłumaczenie dokumentacji Pythona
========================================
![build](https://github.com/m-aciek/python-docs-pl/workflows/.github/workflows/update-and-build.yml/badge.svg)
![20.26% language switchera](https://img.shields.io/badge/language_switcher-20.26%25-0.svg)
![postęp tłumaczenia całości dokumentacji](https://img.shields.io/badge/dynamic/json.svg?label=całość&query=$.pl&url=http://gce.zhsj.me/python/newest)
![4 tłumaczy](https://img.shields.io/badge/tłumaczy-4-0.svg)

[Pomóż tłumaczyć](https://www.transifex.com/python-doc/python-newest/)
dokumentację Pythona na język polski.

Przydatne materiały:
* [polskie tłumaczenie dokumentacji Pythona 2.3](https://pl.python.org/docs/).

Znalazłeś błąd lub masz sugestię?
---------------------------------
* [Dodaj zgłoszenie](https://github.com/m-aciek/python-docs-pl/issues) w tym projekcie
* lub sam(a) [nanieś poprawkę](https://www.transifex.com/python-doc/python-newest/)
  w projekcie *Python document translation* na platformie Transifex.

Jak obejrzeć najnowszy deweloperski build?
----------------------------------------
Wejdź na [https://m-aciek.github.io/python-docs-pl/](https://m-aciek.github.io/python-docs-pl/). Tłumaczenie
synchronizowane jest z Transifeksa
[raz dziennie](/.github/workflows/update-and-build.yml#L3).
 
Dlaczego ta dokumentacja nie jest dostępna na [docs.python.org](https://docs.python.org)?
-----------------------------------------------------------------------------------------
Pojawi się w tam i w language switcherze (przełączniku w lewym górnym rogu),
[kiedy w pełni przetłumaczone będą zasoby](https://www.python.org/dev/peps/pep-0545/#add-translation-to-the-language-switcher):
* `bugs`,
* wszystkie z katalogu `tutorial`,
* `library/functions`.
 
Aktualizacja tłumaczeń
----------------------
* `./manage_translations.py recreate_tx_config`
* `./manage_translations.py fetch`
* `./manage_translations.py recreate_readme`
