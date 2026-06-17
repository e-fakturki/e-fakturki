from babel import Locale

from backend.schemas.companies import IsoCountry

KSEF_SPECIFIC_COUNTRIES = {
    "AN": "Antyle Holenderskie",
    "XC": "Ceuta",
    "XL": "Melilla",
    "XI": "Zjednoczone Królestwo (Irlandia Północna)",
}


def get_polish_country_name(code: str) -> IsoCountry:
    """Get Polish name of the country based on country code."""
    locale = Locale("pl")
    if code in KSEF_SPECIFIC_COUNTRIES:
        return IsoCountry(label=KSEF_SPECIFIC_COUNTRIES[code], value=code)

    return IsoCountry(label=locale.territories.get(code, code), value=code)
