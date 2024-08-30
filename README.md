Polskie tłumaczenie dokumentacji Pythona
========================================
![build](https://github.com/python/python-docs-pl/workflows/.github/workflows/update-and-build.yml/badge.svg)
![66.39% przełącznika języków](https://img.shields.io/badge/przełącznik_języków-66.39%25-0.svg)
![postęp tłumaczenia całości dokumentacji](https://img.shields.io/badge/dynamic/json.svg?label=całość&query=$.pl&url=http://gce.zhsj.me/python/39)
![19 tłumaczy](https://img.shields.io/badge/tłumaczy-19-0.svg)

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
