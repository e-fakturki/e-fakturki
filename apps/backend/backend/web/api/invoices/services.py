from sqlalchemy.ext.asyncio import AsyncSession

from backend.domain.fa3_xml_utils.utils.parser import FA3XmlParser
from backend.domain.fa3_xml_utils.utils.builder import FA3XmlBuilder
from backend.db.repositories.invoice_xml_repository import get_invoice_xml


async def get_pretty_invoice_xml(db_session: AsyncSession, invoice_id: str) -> str:
    """Pull invoice XML from DB and prettify it."""
    xml = await get_invoice_xml(db_session, invoice_id)

    parser = FA3XmlParser()
    builder = FA3XmlBuilder()

    fa3 = parser.parse_string(xml)

    return builder.build_pretty_xml(fa3)
