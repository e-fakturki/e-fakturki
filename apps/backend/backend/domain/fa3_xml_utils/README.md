## fa3_xml_utils

##### Moduł zawierający pomocniczne klasy i funkcje obsługujące parsowanie, tworzenie oraz walidację dokumentów XML w strukturze FA (3).

Link do dokumentacji struktury FA (3): [Czym jest faktura ustrukturyzowana?](https://ksef.podatki.gov.pl/informacje-ogolne-ksef-20/faktura-ustrukturyzowana-i-struktura-logiczna-fa/)

---

Do czego służy moduł fa3_xml_utils:

- dostarcza funkcje do tworzenia i parsowania dokumentów XML FA (3),
- obsługuje mapowanie między strukturami danych aplikacji, modelami w bazie danych a reprezentacją XML,
- waliduje dokumenty XML FA (3), na podstawie oficjalnego schematu XSD (`schemat.xsd`).

---

Zawartość folderu:

- `__init__.py` : inicjalizuje moduł.
- `models/` : Typy danych reprezentujące strukturę XML FA (3).
    - `__init__.py`: inicjalizuje moduł, agreguje importy.
    - `elementarne_typy_danych_v10_0_e.py` : Typy danych dla pojedynczego i podwójnego pola wyboru.
    - `kody_krajow_v10_0_e.py` : Kody krajów.
    - `schemat.py` : Typy danych reprezentujące strukturę XML FA (3).
    - `struktury_danych_v10_0_e.py` : Typy danych reprezentujące pola w dokumentach XML FA (3).
- `utils/` : narzędzia pomocnicze do obsługi XML.
    - `validator.py` : Walidator XML FA (3).
    - `parser.py` : Parser XML FA (3).
    - `builder.py` : Tworzenie XML FA (3).
- `schemat.xsd` : Schemat XML FA (3) (Oficjalny schemat udostępniony w [CRWDE](https://ksef.podatki.gov.pl/informacje-ogolne-ksef-20/struktura-logiczna-fa-3/)).
- `styl.xsl` : XSLT do formatowania XML FA (3). (Oficjalny styl udostępniony w [CRWDE](https://ksef.podatki.gov.pl/informacje-ogolne-ksef-20/struktura-logiczna-fa-3/)).
- `wyroznik.xml` : Dokument wyroznikowy FA (3). (Oficjalny wyróżnik udostępniony w [CRWDE](https://ksef.podatki.gov.pl/informacje-ogolne-ksef-20/struktura-logiczna-fa-3/)).
- `README.md` : Opisy, linki, instrukcje.

---

Zawartość folderu `models/` została wygenerowana na podstawie schematu `schemat.xsd` za pomoca narzędzia _xsdata_.
Dokumentacja _xsdata_: [https://xsdata.readthedocs.io/en/latest/](https://xsdata.readthedocs.io/en/latest/).

```bash
~ e-fakturki/apps/backend/backend/domain/fa3_xml_utils
$ xsdata generate schemat.xsd --package models --structure-style filenames --docstring-style Google --compound-fields
```
