from pathlib import Path

from lxml import etree


class Fa3XmlValidationError(Exception):
    """XML validation error."""

    def __init__(self, error_log: str):
        super().__init__(str(error_log))
        self.error_log = error_log


class Fa3XmlValidator:
    """XML validator class."""

    def __init__(self):
        self.schema_path: str = "backend/domain/fa3_xml_utils/schemat.xsd"
        self.schema_root: etree.XML = None
        self.schema: etree.XMLSchema = None

        with Path.open(self.schema_path, "rb") as schema_file:
            self.schema_root = etree.XML(schema_file.read())
            schema_file.close()
        self.schema = etree.XMLSchema(self.schema_root)

    def validate(self, xml: str) -> bool:
        """Validate XML."""
        xml_doc = etree.fromstring(xml.encode("utf-8"))

        if not self.schema.validate(xml_doc):
            error_log = self.schema.error_log
            raise Fa3XmlValidationError(error_log)
        return True
