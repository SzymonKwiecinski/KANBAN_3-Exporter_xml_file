from tkinter.constants import TRUE
import pandas as pd
from datetime import datetime


class History:
    """Manage csv file which contein history of operation.
    
    Attrubutes:
        file (str): path to file
        df (DataFrame): contein data from history file

    """

    def __init__(self, file: str) -> None:
        self.file = file
        self.load_file()
        self.df_filter = self.df

    def get_df(self):
        return self.df

    def get_df_filter(self) -> pd.DataFrame:
        return self.df_filter

    def load_file(self):
        """Read csv file and load it to DataFrame."""

        self.df = pd.read_csv(self.file)
        self.sort_by_time()

    def sort_by_time(self) -> None:
        """Sort Dataframe by date."""

        self.df = self.df.sort_values('data', ascending=False)

    def filter_file(self, date_start: datetime, date_end: datetime) -> None:
        """Filter DataFrame by giving time.
        
        Args:
            date_start (datetime)
            date_end (datetime)

        """
        self.df_filter = self.df[(self.df['data'] >= date_start) &
                          (self.df['data'] <= date_end)]


    def add_record(self, record: str) -> None:
        """Adds data to end csv file with date of operation
        
        Args:
            record (str): descriptions of operation

        """
        with open(self.file, 'a', encoding='utf-8') as csvfile:
            csvfile.write(f"\n{datetime.now().date()},{record}", )
        
        self.load_file()


