class PrettyXml:
    """Create pretty xml file.
    
    Attributes:
        name_file (str): name of new file
        file (str): path to file
        text (str): row text from xml file in one line

    """

    def __init__(self, name_file: str) -> None:
        self.name_file = name_file

    def open_from_file(self, file: str) -> None:
        """Open a file and reads it.
        
        Args:
            file: path to file

        """

        self.file = open(file)
        self.text = self.file.read()

    def open_from_string(self, string: str) -> None:
        """Assigne string to variable text.
        
        Args:
            string (str): string from xml file

        """

        self.text = string

    def make_preety(self) -> None:
        """Add newlines and tabs to only one line xml file in order to the file look better."""

        self.text = self.text.replace("<?xml version='1.0' encoding='utf8'?>\n", '')

        self.text = self.text.replace('<ns0:BAPI_GOODSMVT_CREATE xmlns:ns0="urn:sap-com:document:sap:rfc:functions">', '<ns0:BAPI_GOODSMVT_CREATE xmlns:ns0="urn:sap-com:document:sap:rfc:functions">')
        self.text = self.text.replace('</ns0:BAPI_GOODSMVT_CREATE>', '\n</ns0:BAPI_GOODSMVT_CREATE>')

        self.text = self.text.replace('<GOODSMVT_CODE>', '\n\t<GOODSMVT_CODE>')
        self.text = self.text.replace('</GOODSMVT_CODE>', '\n\t</GOODSMVT_CODE>')

        self.text = self.text.replace('<GM_CODE>', '\n\t\t<GM_CODE>')
        self.text = self.text.replace('<GOODSMVT_HEADER>', '\n\t<GOODSMVT_HEADER>')
        self.text = self.text.replace('</GOODSMVT_HEADER>', '\n\t</GOODSMVT_HEADER>')

        self.text = self.text.replace('<DOC_DATE>', '\n\t\t<DOC_DATE>')
        self.text = self.text.replace('<REF_DOC_NO>', '\n\t\t<REF_DOC_NO>')

        self.text = self.text.replace('<GOODSMVT_ITEM>', '\n\t<GOODSMVT_ITEM>')
        self.text = self.text.replace('</GOODSMVT_ITEM>', '\n\t</GOODSMVT_ITEM>')

        self.text = self.text.replace('<item>', '\n\t\t<item>')
        self.text = self.text.replace('</item>', '\n\t\t</item>')

        self.text = self.text.replace('<MATERIAL>', '\n\t\t\t<MATERIAL>')
        self.text = self.text.replace('<PLANT>', '\n\t\t\t<PLANT>')
        self.text = self.text.replace('<STGE_LOC>', '\n\t\t\t<STGE_LOC>')
        self.text = self.text.replace('<ENTRY_QNT>', '\n\t\t\t<ENTRY_QNT>')
        self.text = self.text.replace('<ENTRY_UOM_ISO>', '\n\t\t\t<ENTRY_UOM_ISO>')

        self.text = self.text.replace('<RETURN />', '\n\t<RETURN />')

    def write_to_xml_file(self) -> None:
        """Overwrites or creates good looking xml file."""

        new_file = open(self.name_file, 'w')
        new_file.write(self.text)
        new_file.close()
