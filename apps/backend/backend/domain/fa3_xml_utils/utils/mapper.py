from fastapi import HTTPException
from xsdata.models.datatype import XmlDateTime

from backend.schemas.invoices import InvoiceEntryRequest, InvoiceObjectRequest
import backend.domain.fa3_xml_utils.models.schemat as fa3utils

from datetime import datetime
import re

def to_tdate(value: str | datetime) -> str:
    """
    Converts various date/datetime formats into FA3 TData format:
    YYYY-MM-DD
    """

    if isinstance(value, datetime):
        return value.date().isoformat()

    value = value.strip()

    # 1) "13.06.2026, 22:19:21"
    if "," in value:
        date_part = value.split(",")[0].strip()
        day, month, year = date_part.split(".")
        return f"{year}-{month}-{day}"

    # 2) ISO datetime: 2026-06-13T20:21:15.786Z
    value = value.replace("Z", "")
    value = re.sub(r"\.\d+", "", value)

    # If full datetime → cut to date
    if "T" in value:
        value = value.split("T")[0]

    # Already YYYY-MM-DD
    return value


class FA3ObjectMapper:
    """FA3 Object mapper/builder."""

    def __init__(self):
        self.namespace = fa3utils.__NAMESPACE__

        self.default_invoice_header = fa3utils.Tnaglowek(
            kod_formularza=fa3utils.Tnaglowek.KodFormularza(
                value=fa3utils.TkodFormularza.FA,
            ),
            wariant_formularza=fa3utils.TnaglowekWariantFormularza.VALUE_3,
            data_wytworzenia_fa=XmlDateTime.now(),
            system_info="efakturki v0.1.0",
        )

    def build_fa3_invoice_from_invoice_object(
        self, invoice_data: InvoiceObjectRequest
    ) -> fa3utils.Faktura:
        """Convert invoice object to FA3 compatible object."""

        return fa3utils.Faktura(
            naglowek=self.default_invoice_header,
            podmiot1=fa3utils.Faktura.Podmiot1(
                dane_identyfikacyjne=fa3utils.Tpodmiot1(
                    nip=invoice_data.seller_info.nip,
                    nazwa=invoice_data.seller_info.name,
                ),
                adres=fa3utils.Tadres(
                    kod_kraju=invoice_data.seller_info.country_code,
                    adres_l1=invoice_data.seller_info.address_l1 or None,
                    adres_l2=invoice_data.seller_info.address_l2 or None,
                ),
                adres_koresp=self.generate_company_coresp_address_from_invoice_object(True, invoice_data),
                dane_kontaktowe=[self.generate_company_contact_from_invoice_object(True, invoice_data)],
            ),
            podmiot2=fa3utils.Faktura.Podmiot2(
                dane_identyfikacyjne=fa3utils.Tpodmiot2(
                    choice=[fa3utils.Tpodmiot2.Nip(value=invoice_data.buyer_info.nip)],
                    nazwa=invoice_data.buyer_info.name,
                ),
                adres=fa3utils.Tadres(
                    kod_kraju=invoice_data.buyer_info.country_code,
                    adres_l1=invoice_data.buyer_info.address_l1 or None,
                    adres_l2=invoice_data.buyer_info.address_l2 or None,
                ),
                adres_koresp=self.generate_company_coresp_address_from_invoice_object(False, invoice_data),
                dane_kontaktowe=[self.generate_company_contact_from_invoice_object(False, invoice_data)],
                # TODO:
                # Po wdrożeniu Podmiot3 umożliwić oznaczanie kontrahenta jako:
                # - jednostka podrzędna JST
                # - członek grupy VAT
                jst=fa3utils.Podmiot2Jst.VALUE_2,
                gv=fa3utils.Podmiot2Gv.VALUE_2
            ),
            fa=fa3utils.Faktura.Fa(
                kod_waluty=invoice_data.currency,
                p_1=to_tdate(invoice_data.issue_date),
                p_1_m=invoice_data.issue_place,
                p_2=invoice_data.invoice_number,
                rodzaj_faktury=invoice_data.invoice_type,
                fa_wiersz=self.collect_fa3_entries_to_list(invoice_data),
                platnosc=self.generate_fa3_payment_form_invoice_object(invoice_data),
                #### dodac sumy faktury
                p_15=invoice_data.gross_total,
                adnotacje=fa3utils.Faktura.Fa.Adnotacje(
                    p_16=fa3utils.Twybor12.VALUE_2,
                    p_17=fa3utils.Twybor12.VALUE_2,
                    p_18=fa3utils.Twybor12.VALUE_2,
                    p_18_a=fa3utils.Twybor12.VALUE_2,
                    zwolnienie=fa3utils.Faktura.Fa.Adnotacje.Zwolnienie(
                        choice=[fa3utils.Faktura.Fa.Adnotacje.Zwolnienie.P19N(
                            value=fa3utils.Twybor1.VALUE_1)
                        ]
                        ),
                    nowe_srodki_transportu=fa3utils.Faktura.Fa.Adnotacje.NoweSrodkiTransportu(
                        choice=[fa3utils.Faktura.Fa.Adnotacje.NoweSrodkiTransportu.P22N(
                            value=fa3utils.Twybor1.VALUE_1)
                        ],
                        ),
                    p_23=fa3utils.Twybor12.VALUE_2,
                    pmarzy=fa3utils.Faktura.Fa.Adnotacje.Pmarzy(
                        choice=[fa3utils.Faktura.Fa.Adnotacje.Pmarzy.PPmarzyN(
                            value=fa3utils.Twybor1.VALUE_1)
                        ],
                    )
                )
            ),
        )

    def generate_company_coresp_address_from_invoice_object(
        self,
        seller: bool,
        invoice_data: InvoiceObjectRequest
    ) -> fa3utils.Tadres | None:
        """Extract company address from invoice object and build a company address object from fa3 structure."""

        info = invoice_data.seller_info if seller else invoice_data.buyer_info

        if not info.address_correspondance_l1:
            return None

        return fa3utils.Tadres(
            kod_kraju=info.country_code,
            adres_l1=info.address_correspondance_l1,
            adres_l2=info.address_correspondance_l2,
        )

    def generate_company_contact_from_invoice_object(
        self,
        seller: bool,
        invoice_data: InvoiceObjectRequest
    ) -> fa3utils.Faktura.Podmiot2.DaneKontaktowe | fa3utils.Faktura.Podmiot1.DaneKontaktowe | None:
        """Extract company address from invoice object and build a company address object from fa3 structure."""

        info = invoice_data.seller_info if seller else invoice_data.buyer_info

        if not info.email and not info.phone_number:
            return None

        cls = (
            fa3utils.Faktura.Podmiot1.DaneKontaktowe
            if seller
            else fa3utils.Faktura.Podmiot2.DaneKontaktowe
        )

        return cls(
            email=info.email or None,
            telefon=info.phone_number or None,
        )

    def generate_fa3_payment_form_invoice_object(
        self, invoice_data: InvoiceObjectRequest
    ) -> fa3utils.Faktura.Fa.Platnosc:
        """Extract payment info from invoice object and build a payment object from fa3 structure."""
        if invoice_data.payment.payment_status == "paid":
            if invoice_data.payment.payment_type == 1:
                return fa3utils.Faktura.Fa.Platnosc(
                    choice=[
                        fa3utils.Twybor1.VALUE_1,
                        to_tdate(invoice_data.payment.payment_date),
                    ],
                    forma_platnosci_or_platnosc_inna_or_opis_platnosci=[
                        fa3utils.TformaPlatnosci.VALUE_1
                    ],
                )
            return fa3utils.Faktura.Fa.Platnosc(
                choice=[fa3utils.Twybor1.VALUE_1, to_tdate(invoice_data.payment.payment_date)],
                forma_platnosci_or_platnosc_inna_or_opis_platnosci=[
                    fa3utils.TformaPlatnosci(invoice_data.payment.payment_type)
                ],
                rachunek_bankowy=fa3utils.TrachunekBankowy(
                    nr_rb=invoice_data.payment.seller_bank_account_number,
                    nazwa_banku=invoice_data.payment.seller_bank_name,
                ),
            )
        elif invoice_data.payment.payment_status == "unpaid":  # noqa: RET505
            if invoice_data.payment.payment_type == 1:
                return fa3utils.Faktura.Fa.Platnosc(
                    termin_platnosci=fa3utils.Faktura.Fa.Platnosc.TerminPlatnosci(
                        termin=to_tdate(invoice_data.payment.payment_due_date)
                    ),
                    forma_platnosci_or_platnosc_inna_or_opis_platnosci=[
                        fa3utils.TformaPlatnosci.VALUE_1
                    ],
                )
            return fa3utils.Faktura.Fa.Platnosc(
                termin_platnosci=fa3utils.Faktura.Fa.Platnosc.TerminPlatnosci(
                    termin=to_tdate(invoice_data.payment.payment_due_date)
                ),
                forma_platnosci_or_platnosc_inna_or_opis_platnosci=[
                    fa3utils.TformaPlatnosci(invoice_data.payment.payment_type)
                ],
                rachunek_bankowy=fa3utils.TrachunekBankowy(
                    nr_rb=invoice_data.payment.seller_bank_account_number,
                    nazwa_banku=invoice_data.payment.seller_bank_name,
                ),
            )
        elif invoice_data.payment.payment_status == "partial":
            raise HTTPException(
                status_code=422, detail="Partial payments not handled yet."
            )
        else:
            raise HTTPException(status_code=422, detail="Wrong payment type.")

    def generate_fa3_invoice_entry_from_invoice_object(self, entry: InvoiceEntryRequest) -> fa3utils.Faktura.Fa.FaWiersz:
        """Extract entry info from invoice object and build an entry object from fa3 structure."""
        return fa3utils.Faktura.Fa.FaWiersz(
            nr_wiersza_fa=entry.row_number,
            p_6_a=(entry.delivery_date.split("T"))[0],
            p_7=entry.name,
            p_8_a=entry.unit,
            p_8_b=entry.amount,
            p_9_a=entry.net_price,
            p_11=entry.net_total,
            p_12=entry.tax_rate,
        )

    def collect_fa3_entries_to_list(self, invoice_data: InvoiceObjectRequest) -> fa3utils.Faktura.Fa.FaWiersz:
        """Extract entries info from invoice object and create a fa3 entries object"""
        return [self.generate_fa3_invoice_entry_from_invoice_object(entry) for entry in invoice_data.entries]
