import xml.etree.ElementTree as et
from PrettyXml import PrettyXml


class Kanban:
    """Create xml kanban file.
    
    Attributes:
        zk_data (list of lists) :
            [['20-900248-1', 2000, '0050', 100, 'SZT'],
            ['20-0265689-1', 2000, '0010', 50, 'SZT']]
        zk_number (str): ZK 991/2016 -> 9912016
        zk_date (str): 2016-09-09 -> 20160909
        file_name (str): -> 9912016-20160909.xml
    """

    def __init__(self, zk_data: str, zk_number: str, zk_date: str) -> None:
        self.zk_data = zk_data
        self.zk_number_in_file = zk_number.replace('ZK ', '') # 974/2011
        self.zk_number = zk_number.replace('ZK ', '').replace('/', '')
        self.zk_date = zk_date.replace('-', '')
        self.file_name = self.zk_number + '-' + self.zk_date + '.xml'
        self.create()

    def get_file_name(self) -> str:
        return self.file_name

    def create(self) -> None:
        """Create xml kanban file."""

        self.top = et.Element('ns0:BAPI_GOODSMVT_CREATE')
        self.top.attrib = {'xmlns:ns0': 'urn:sap-com:document:sap:rfc:functions'}

        child_1 = et.SubElement(self.top, 'GOODSMVT_CODE')
        child_2 = et.SubElement(child_1, 'GM_CODE')
        child_2.text = '01'

        child_1_GOODSMVT_HEADER = et.SubElement(self.top, 'GOODSMVT_HEADER')
        child_2_DOC_DATE = et.SubElement(child_1_GOODSMVT_HEADER, 'DOC_DATE')
        child_2_DOC_DATE.text = self.zk_date
        child_2_REF_DOC_NO = et.SubElement(child_1_GOODSMVT_HEADER, 'REF_DOC_NO')
        child_2_REF_DOC_NO.text = self.zk_number_in_file

        child_1_GOODSMVT_ITEM = et.SubElement(self.top, 'GOODSMVT_ITEM')

        for items in self.zk_data:
            child_2_ITEM = et.SubElement(child_1_GOODSMVT_ITEM, 'item')

            child_2_MATERIAL = et.SubElement(child_2_ITEM, 'MATERIAL')
            child_2_MATERIAL.text = str(items[0].replace('|',''))

            child_2_PLANT = et.SubElement(child_2_ITEM, 'PLANT')
            child_2_PLANT.text = str(items[1].replace('|',''))

            child_2_STGE_LOC = et.SubElement(child_2_ITEM, 'STGE_LOC')
            child_2_STGE_LOC.text = str(items[2].replace('|',''))

            child_2_ENTRY_QNT = et.SubElement(child_2_ITEM, 'ENTRY_QNT')
            child_2_ENTRY_QNT.text = str(items[3].replace('|',''))

            child_2_ENTRY_UOM_ISO = et.SubElement(child_2_ITEM, 'ENTRY_UOM_ISO')
            child_2_ENTRY_UOM_ISO.text = str(items[4].replace('|',''))

        et.SubElement(self.top, 'RETURN')

        preety_kanban = PrettyXml(self.file_name)
        preety_kanban.open_from_string(et.tostring(self.top, encoding='utf8').decode('utf8'))
        preety_kanban.make_preety()
        preety_kanban.write_to_xml_file()


