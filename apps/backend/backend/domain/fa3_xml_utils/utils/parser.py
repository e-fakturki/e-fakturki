from xsdata.formats.dataclass.parsers import XmlParser

import backend.domain.fa3_xml_utils.models.schemat as fa3utils


class FA3XmlParser:
    """FA3 XML parser."""

    def __init__(self):
        self.parser = XmlParser()

    def parse_string(self, xml: str) -> fa3utils.Faktura:
        """Parse FA3 XML string to fa3utils.Faktura object."""
        return self.parser.from_string(xml, fa3utils.Faktura)

    def parse_file(self, file_path: str) -> fa3utils.Faktura:
        """Parse FA3 XML file to fa3utils.Faktura object."""
        return self.parser.from_path(file_path, fa3utils.Faktura)

    def parse_bytes(self, xml: bytes) -> fa3utils.Faktura:
        """Parse FA3 XML bytes to fa3utils.Faktura object."""
        return self.parser.from_bytes(xml, fa3utils.Faktura)
