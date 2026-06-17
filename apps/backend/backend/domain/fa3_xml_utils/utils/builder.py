from xsdata.formats.dataclass.serializers import XmlSerializer
from xsdata.formats.dataclass.serializers.config import SerializerConfig

import backend.domain.fa3_xml_utils.models.schemat as fa3utils


class FA3XmlBuilder:
    """FA3 XML builder."""

    def __init__(self):
        self.namespace = fa3utils.__NAMESPACE__
        self.serializer = XmlSerializer(config=SerializerConfig())
        self.pretty_serializer = XmlSerializer(
            config=SerializerConfig(
                pretty_print=True,
                xml_declaration=True,
                indent="\t",
                globalns=vars(fa3utils),
            )
        )

    def build_plain_xml(self, faktura: fa3utils.Faktura) -> str:
        """Build plain FA3 XML string from fa3utils.Faktura object."""
        return self.serializer.render(faktura)

    def build_pretty_xml(self, faktura: fa3utils.Faktura) -> str:
        """Build pretty FA3 XML string from fa3utils.Faktura object."""
        return self.pretty_serializer.render(faktura)

    def build_bytes_xml(self, faktura: fa3utils.Faktura) -> bytes:
        """Build FA3 XML bytes from fa3utils.Faktura object."""
        xml_string = self.serializer.render(faktura)

        if isinstance(xml_string, bytes):
            return xml_string

        return xml_string.encode("utf-8")
