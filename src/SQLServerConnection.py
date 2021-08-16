import pyodbc
from datetime import datetime


class SQLServerConnection:
    """Connects with MS SQL Server and manage it.
    
    Attributes:
        conn (pyodbc.connect)
        cursor (pydoc.connect.coursor)

    """

    def __init__(self) -> None:
        self.connect()

    def get_cursor(self) -> pyodbc.Cursor:
        return self.cursor

    def connect(self) -> None:
        """Connects with server."""

        try:   
            self.conn =\
                pyodbc.connect(r"Driver={SQL Server Native Client 11.0};"
                               r"Server=name_of_server;"
                               r"Database=name_of_db;"
                               r"UID=name_of_user;"
                               r"PWD=password;")
            self.cursor = self.conn.cursor()
        except Exception as e:
            print(e)

    def query_filtr_zk_by_date(self, date):
        """Select ZK full numbers in descending order.

        Args:
            date (datatime): time of ZK dokument create

        """

        try:
            self.cursor.execute(f"""
            SELECT dok_Id, dok_NrPelny, dok_DataWyst, dok_PlatnikId
            FROM AREX.dbo.dok__Dokument
            WHERE dok_PlatnikId = 78 AND dok_NrPelny LIKE 'ZK%' AND dok_DataWyst >= '{date}'
            ORDER BY dok_NrPelny DESC """)
        except Exception as e:
            print(e)

    def query_date_info(self, zk_number):
        """Select from database date(time) of create of ZK dokument.
        
        Args:
            zk_number (str): full name of dokument 

        """

        try:
            self.cursor.execute(f"""SELECT dok_NrPelny, dok_DataWyst
                                FROM AREX.dbo.dok__Dokument
                                WHERE dok_NrPelny = '{zk_number}'""")
        except Exception as e:
            print(e)

    def query_zk_details(self, zk_number):
        """Select from database kanban details.
        
        Selecting 5 items.
        <MATERIAL>20-0202964-3</MATERIAL>   part number
        <PLANT>2000</PLANT>                 Kielce number
        <STGE_LOC>0050</STGE_LOC>           localization in their storage
        <ENTRY_QNT>20</ENTRY_QNT>           quantity
        <ENTRY_UOM_ISO>SZT</ENTRY_UOM_ISO>  unit of measure

        """

        try:
            self.cursor.execute(f"""
            SELECT t.tw_Pole6, t.tw_Pole6, p.ob_Opis, p.ob_Ilosc, p.ob_Jm
            FROM AREX.dbo.dok_Pozycja as p
            FULL JOIN AREX.dbo.dok__Dokument as d
            ON p.ob_DokHanId = d.dok_Id
            INNER JOIN AREX.dbo.tw__Towar as t
            ON p.ob_TowId = t.tw_Id
            WHERE d.dok_NrPelny = '{zk_number}'""")
        except Exception as e:
            print(e)
