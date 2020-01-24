Polskie tłumaczenie dokumentacji Pythona
========================================
![build](https://github.com/m-aciek/python-docs-pl/workflows/.github/workflows/update-and-build.yml/badge.svg)
![10.40% language switchera](https://img.shields.io/badge/language_switcher-10.40%25-0.svg)
![postęp tłumaczenia całości dokumentacji](https://img.shields.io/badge/dynamic/json.svg?label=całość&query=$.pl&url=http://gce.zhsj.me/python/newest)

[Pomóż tłumaczyć](https://www.transifex.com/python-doc/python-newest/)
dokumentację Pythona na język polski.

Przydatne materiały:
* [polskie tłumaczenie dokumentacji Pythona 2.3](https://pl.python.org/docs/).

Znalazłeś błąd lub masz sugestię?
---------------------------------
* [Dodaj zgłoszenie](https://github.com/m-aciek/python-docs-pl/issues) w tym projekcie
* lub sam [nanieś poprawkę](https://www.transifex.com/python-doc/python-newest/)
  w projekcie *Python document translation* na platformie Transifex.

Jak pobrać najnowszy deweloperski build?
----------------------------------------
* Zaloguj się na GitHubie,
* wejdź w [zakładkę Actions](https://github.com/m-aciek/python-docs-pl/actions),
* wejdź w ostatni pomyślnie zakończony workflow (*.github/workflows/update-and-build.yml*),
* w sekcji *Artifacts* wybierz *build*, aby pobrać dokumentację,
* po rozpakowaniu otwórz `index.html` w przeglądarce.

[Raz dziennie](https://github.com/m-aciek/python-docs-pl/blob/3.8/.github/workflows/update-and-build.yml#L3)
tłumaczenie synchronizowane jest z Transifeksa do tego repozytorium.
 
Dlaczego ta dokumentacja nie jest dostępna na docs.python.org?
--------------------------------------------------------------
Pojawi się w tam i w language switcherze (przełączniku w lewym górnym rogu),
[kiedy w pełni przetłumaczone będą zasoby](https://www.python.org/dev/peps/pep-0545/#add-translation-to-the-language-switcher):
* `bugs`,
* wszystkie w katalogu `tutorial`,
* `library/functions`.
 
Aktualizacja tłumaczeń
----------------------
* `./manage_translations.py recreate_tx_config`
* `./manage_translations.py fetch`
* `./manage_translations.py recreate_readme`
