
from CheckUnit import CheckUnit
from History import History
from Kanban import Kanban
from SaveError import SaveError
import tkinter as tk
from tkinter import messagebox
import tkinter.ttk as ttk
from datetime import datetime
from datetime import timedelta
import pandas as pd
import time
import math
import re
import traceback 
import os
import shutil


class MainWindow:

    def __init__(self, ms_sql: str, web_server: str, history_file: str, error_file: str, pr_error_file: str, old_files: str):
        self.ms_sql = ms_sql
        self.server = web_server
        self.history_file = History(history_file)
        self.error_file = History(error_file)
        self.old_files = os.path.abspath(old_files)
        self.programing_error_file = SaveError(pr_error_file)
        self.front_end()
        self.top.mainloop()

    def error_mg(self, text: str):
        """Handling all errors and write them to diffrent files.
        
        Popup window with error, write this error to scv file and
        write details error to terminal and txt file

        Args:
            text (str): error message in polish

        """
        messagebox.showerror(title='Błąd',
                             message=text,
                             icon="question")
        self.error_file.add_record(text)
        self.programing_error_file.save(traceback.format_exc())
    
    def good_mg(self, text: str) -> None:
        """Write valid operation to csv file.

        Args:
            text (str): operation message in polish
            
        """
        self.history_file.add_record(text)

    def upadete_progressbar(self):
        """Makes imagination of loading file to serwer."""
        for x in range(0, 101, 10):
            time.sleep(0.005)
            self.progressbar.config(value=x)
            self.top.update_idletasks()

    def send_file_to_archive(self, file_name: str) -> None:
        """Move file from scr dir to old file dir.
        
        Args:
            file_name (str): path to file

        """
        try:
            shutil.copy(file_name, self.old_files)
            os.remove(file_name)

        except Exception:
            self.error_mg('Błąd przesyłania pliku do lokalnego archiwum')

    def send_xml_to_server(self, file_name):
        """Sends file to web server.
        
        Args:
            file_name (str): path to file which we send to serwer

        """
        try:
            if self.server.sent_file(file_name):
                self.send_file_to_archive(file_name)
                self.good_mg(f'{self.zk_number} -> plik został wysłany na serwer')
                self.delete_itmes_from_tree()
                self.button_serwer.config(state=tk.DISABLED)
                self.upadete_progressbar()
        except Exception:
            self.error_mg('Błąd wysłania na serwer')


    def create_kanban(self):
        """Creates xml kanban file base on data and send it to server"""
        try:
            self.kanban = Kanban(zk_data=[self.tree.item(y)['values'] for y in 
                                 [id_child for id_child in self.tree.get_children()]],
                                 zk_number=self.zk_number,
                                 zk_date=self.zk_date)
            self.send_xml_to_server(file_name=self.kanban.get_file_name())
            self.list_files_in_server()
        except Exception:
            self.error_mg('Błąd tworzenia pliku xml')

    def import_ZK(self):
        """Fulfill kanban tree takeing date from sql server."""

        try:
            self.insert_tree_data()
            self.zk_number_date_set()
            self.button_serwer.config(state='normal')
        except Exception:
            self.error_mg(f'Bład wczytywania numerów ZK')

    def zk_number_date_set(self):
        """Catch time and ZK number."""

        try:
            self.ms_sql.query_date_info(self.combobox_number.get())
            for x in self.ms_sql.get_cursor():
                self.zk_number = x[0]
                self.zk_date = x[1].strftime("%Y-%m-%d")
                break
        except Exception:
            self.error_mg('Błąd pobierania czasu i numeru ZK')

    def delete_itmes_from_tree(self):
        """Delete items form kanban tree."""

        try:
            for item in self.tree.get_children():
                self.tree.delete(item)
        except Exception:
            self.error_mg(f'Bład usuwania rekordów z drzewa kanban')

    def delete_itmes_from_tree_history(self):
        """Delete items form history tree."""
        try:
            for item in self.tree_history.get_children():
                self.tree_history.delete(item)
        except Exception:
            self.error_mg(f'Bład usuwania rekordów z drzewa history')

    def to_schmidt_units(self, value: float, unit: str) -> tuple:
        try:
            unify_unit = CheckUnit(unit).unify()

            if unify_unit == 'SZT':
                new_value = math.ceil(value)
                new_unit = 'SZT'
            elif unify_unit == '10SZT':
                new_value = math.ceil(value * 10)
                new_unit = 'SZT'
            elif unify_unit == '100SZT':
                new_value = math.ceil(value * 100)
                new_unit = 'SZT'
            elif unify_unit == 'MB':
                new_value = math.ceil(value)
                new_unit = 'MB'
            else:
                self.error_mg(f'Błąd unifikacji jednostek, [brak ich]')
            return (new_value, new_unit)
        except Exception:
            self.error_mg(f'Błąd konwersji jednostek ns schmitowskie')

    def insert_tree_data(self) -> None:
        """Select data from SQL DB and insert them to kanban tree.

        SELECT <MATERIAL>,<PLANT>,<STGE_LOC>,<ENTRY_QNT>,<ENTRY_UOM_ISO>

        """
        self.delete_itmes_from_tree()
        try:
            self.ms_sql.query_zk_details(self.combobox_number.get())
            for i, row in enumerate(self.ms_sql.get_cursor()):
                (value, unit) = self.to_schmidt_units(row[3], row[4])
                self.tree.insert(parent='',
                                index=tk.END,
                                iid=i,
                                text=i+1,
                                # values=(row[0], '2000', str(row[2]), value, unit))
                                values=(f"|{row[0]}|", '|2000|', f"|{row[2]}|", f"|{value}|", f"|{unit}|"))
        except Exception:
            self.error_mg(f'Błąd wpisywania do drzewa kanban')

    def insert_tree_history_data(self, df: pd.DataFrame) -> None:
        """Loads date from Dataframe and insert to history tree."""

        self.delete_itmes_from_tree_history()
        try:
            for i, row in df.iterrows():
                self.tree_history.insert(parent='',
                                        index=tk.END,
                                        iid=i,
                                        text=i+1,
                                        values=(row[0], row[1]))
        except Exception:
            self.error_mg(f'Błąd wpisywania do drzewa history')

    def combobox_year_selected(self, event) -> None:
        """Choosen time which be use to filter ZK number."""

        year = self.combobox_year.get()
        # year_now = (datetime.now() - timedelta(days=4)).strftime("%Y-%m-%d")
        if year == self.combobox_year_values[0]:
            # self.combobox_number_filtr(datetime(2016, 9, 9).strftime("%Y-%m-%d"))
            self.combobox_number_filtr(datetime.now().strftime("%Y-%m-%d"))
        elif year == self.combobox_year_values[1]:
            # self.combobox_number_filtr(datetime(2016, 9, 6))
            self.combobox_number_filtr((datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"))
        elif year == self.combobox_year_values[2]:
            # self.combobox_number_filtr(datetime(2016, 9, 5))
            self.combobox_number_filtr((datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"))
        elif year == self.combobox_year_values[3]:
            # self.combobox_number_filtr(datetime(2016, 9, 2))
            self.combobox_number_filtr(datetime(2021, 7, 10))
            

    def combobox_number_filtr(self, date: datetime) -> None:
        """Puts into combobox ZK number filtering by date
        
        Args:
            data (datetime): day of creating ZK nymber

        """
        try:
            self.ms_sql.query_filtr_zk_by_date(date)
            self.zk_numbers = [numbers[1] for numbers in self.ms_sql.get_cursor()]
            self.combobox_number.configure(value=self.zk_numbers)
        except Exception:
            self.error_mg(f'Błąd filtrowania ZK używając czasu')

    def active_button(self, event):
        self.button.config(state='normal')

    def find_zk_in_str(self, word: str) -> str:
        """Extract only zk number from full file name.
        
        word = 991202016-20160909.xml
        new_word = 991202016-
        return = 991

        Args:
            word (str): full xml file name

        Returns:
            str: extracted zk number from full name
        """
        try:
            new_word = re.match(r'\d+-', word).group()
            return new_word[:-5]
        except Exception:
            self.error_mg(f'Błąd ')

    def list_files_in_server(self):
        """Update listbox showing files in serwer."""

        try:
            self.listbox_server.delete(0, tk.END)
            for i, file in enumerate(self.server.list_of_files()):
                self.listbox_server.insert(i+1, f'{i+1} :ZK {self.find_zk_in_str(file)} ->  {file}')
        except Exception:
            self.error_mg(f'Błąd usuwania/dodawania plików do Listbox z serwera')

    def delete_file_from_server(self, file_name):
        """Delete file from web server.
        
        Args:
            file_name (str): name of file which we want to delete
        """

        yes_no_message = messagebox.askyesno(message='Czy usunąć plik\nz serwera?')
        if yes_no_message:
            try:
                new_file_name = re.search(r'\S+.xml', file_name).group()
                self.server.delete_file(f'/{new_file_name}')
                self.good_mg(f'{self.find_zk_in_str(new_file_name)} - usunięte z serwera')
                self.list_files_in_server()
            except Exception:
                self.error_mg(f'Błąd usuwania plików z serwera')

    def history_tree_select(self) -> None:
        """Loads data to history tree based on filtering"""

        # All history
        if self.rb34_var.get() == 1:
            if self.rb12_var.get() == 1:
                self.delete_itmes_from_tree_history()
                self.insert_tree_history_data(self.history_file.get_df())
            elif self.rb12_var.get() == 2:
                self.delete_itmes_from_tree_history()
                self.insert_tree_history_data(self.error_file.get_df())

        # Filtering history by date
        elif self.rb34_var.get() == 2:
            if self.rb12_var.get() == 1:
                self.history_file.filter_file(date_start=self.entry_time_1.get(),
                                              date_end=self.entry_time_2.get())
                self.delete_itmes_from_tree_history()
                self.insert_tree_history_data(self.history_file.get_df_filter())
            elif self.rb12_var.get() == 2:
                self.error_file.filter_file(date_start=self.entry_time_1.get(),
                                              date_end=self.entry_time_2.get())
                self.delete_itmes_from_tree_history()
                self.insert_tree_history_data(self.error_file.get_df_filter())


    def time_select(self):
        """Selected time to filtering history/error file."""
        
        if self.rb34_var.get() == 1:
            self.entry_time_1.config(state=tk.DISABLED)
            self.time1_var.set('2021-07-14')
            self.entry_time_2.config(state=tk.DISABLED)
            self.time2_var.set(str(datetime.now().date()))
        elif self.rb34_var.get() == 2:
            self.entry_time_1.config(state=tk.ACTIVE)
            self.entry_time_2.config(state=tk.ACTIVE)

    def front_end(self):
        """Builds GUI.
        
        Attributes:
            top (Tk): main object for GUI
            notabook (Notebook): notebook
            frame_page_1 (Frame): 'Wyślij na serwer' page
            frame_page_2 (Frame): 'Serwer' page
            frame_page_3 (Frame): 'Historia' page

        """
        self.top = tk.Tk()
        self.top.title('Program - Wysyłanie plików kanban na serwer')
        ttk.Style().theme_use('clam')

        self.notebook = ttk.Notebook(self.top)
        self.notebook.pack()

# frame_page_1 START
        self.frame_page_1 = ttk.Frame(self.notebook)
        self.frame_page_1.pack()
        self.notebook.add(self.frame_page_1, text='wyślij na serwer')

# Frame_entry START
        self.frame_entry = ttk.LabelFrame(self.frame_page_1, text='Wybierz numer ZK')
        self.frame_entry.pack(fill=tk.X)#grid(row=0, column=0, sticky='we')

        self.combobox_number = ttk.Combobox(self.frame_entry)
        self.combobox_number.pack(side='left', fill='x')
        self.combobox_number.bind('<<ComboboxSelected>>',
                                  self.active_button)
        self.combobox_year_values = ['z dzisiaj',
                                     'z 7 dni',
                                     'z 30 dni',
                                     'wszystkie od 2020']
        self.combobox_year = ttk.Combobox(self.frame_entry,
                                          value=self.combobox_year_values)
        self.combobox_year.current(0)
        self.combobox_year.bind('<<ComboboxSelected>>',
                                self.combobox_year_selected)
        self.combobox_year.pack(side='left', fill='x')

        self.combobox_year_selected('<<ComboboxSelected>>')

        self.button = ttk.Button(self.frame_entry,
                                 state='disabled',
                                 text="importuj z Subiekta",
                                 command=self.import_ZK)
        self.button.pack(side='top', fill='x')
# Frame_entry END

# Frame_tree START
        self.frame_tree = ttk.LabelFrame(self.frame_page_1, text='Podgląd przekonwertowanego pliku Zk na kanban')
        self.frame_tree.pack()#grid(row=1, column=0)

        self.scrollbar_tree = ttk.Scrollbar(self.frame_tree)
        self.scrollbar_tree.grid(row=1, column=1, sticky='ns')

        self.tree = ttk.Treeview(self.frame_tree,
                                 height=10,
                                 yscrollcommand=self.scrollbar_tree.set)
        self.tree.grid(row=1, column=0)
        self.column = ("Numer_schmitd",
                       "Zakład_kielce",
                       "Lok_mag_sch",
                       "Ilość",
                       "Jm")
        self.tree['columns'] = self.column
        self.tree.column('#0', anchor=tk.W, width=35, minwidth=35)
        self.tree.heading('#0', text='Lp', anchor=tk.W)
        self.tree.column(self.column[0], anchor=tk.CENTER, width=145)
        self.tree.heading(self.column[0], text='Numer Schmitd')
        self.tree.column(self.column[1], anchor=tk.CENTER, width=60)
        self.tree.heading(self.column[1], text='2000')
        self.tree.column(self.column[2], anchor=tk.CENTER, width=80)
        self.tree.heading(self.column[2], text='Mag_schmitd')
        self.tree.column(self.column[3], anchor=tk.CENTER, width=60)
        self.tree.heading(self.column[3], text='Ilość')
        self.tree.column(self.column[4], anchor=tk.CENTER, width=50)
        self.tree.heading(self.column[4], text='Jm')

        self.scrollbar_tree.configure(command=self.tree.yview)
# Frame_tree END

# Frame_server START
        self.frame_server = ttk.LabelFrame(self.frame_page_1, text='Wyślij plik na serwer')
        self.frame_server.pack(fill=tk.X)#grid(row=2, column=0, sticky='we')

        self.button_serwer = ttk.Button(self.frame_server,
                                        text="Stwórz plik kanban.xml oraz wyślij na serwer",
                                        state='disabled',
                                        command=self.create_kanban)
        self.button_serwer.pack(fill=tk.X)

        self.progressbar = ttk.Progressbar(self.frame_server,
                                           orient='horizontal',
                                           mode='determinate')
        self.progressbar.pack(side=tk.TOP, fill=tk.X, ipady=3)
# Frame_server END
# frame_page_1 END

# frame_page_2 START
        self.frame_page_2 = ttk.Frame(self.notebook)
        self.frame_page_2.pack()
        self.notebook.add(self.frame_page_2, text='serwer')

# frame_server_check START
        self.frame_server_check = ttk.LabelFrame(self.frame_page_2,
                                                 text='Pliki aktualnie na serwerze')
        self.frame_server_check.pack(side=tk.TOP)

        self.listbox_server = tk.Listbox(self.frame_server_check,
                                         height=10,
                                         width=40,
                                         font=15)
        self.listbox_server.pack(side=tk.LEFT)

        self.scrollbar_server_check = ttk.Scrollbar(self.frame_server_check)
        self.scrollbar_server_check.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox_server.config(yscrollcommand=self.scrollbar_server_check.set)
        self.scrollbar_server_check.config(command=self.listbox_server.yview)
# frame_server_check END

# frame_button_check_server START
        self.frame_button_check_server = ttk.LabelFrame(self.frame_page_2,
                                                        text='Przyciski')
        self.frame_button_check_server.pack(fill=tk.X, side=tk.BOTTOM)

        self.button_check_server = ttk.Button(self.frame_button_check_server,
                                              text='Odśwież',
                                              command=self.list_files_in_server)
        self.button_check_server.pack(side=tk.TOP, fill=tk.X, pady=3, ipady=5)
        self.button_delete = ttk.Button(self.frame_button_check_server,
                                        text='Usuń plik z serwera',
                                        command=lambda: self.delete_file_from_server(self.listbox_server.get(self.listbox_server.curselection()[0])))
        self.button_delete.pack(side=tk.TOP, fill=tk.X, pady=3, ipady=5)
# frame_button_check_server END
# frame_page_2 END

# frame_page_3 START
        self.frame_page_3 = ttk.Frame(self.notebook)
        self.frame_page_3.pack()
        self.notebook.add(self.frame_page_3, text='historia')

# frame_tree_history START
        self.frame_tree_history = ttk.LabelFrame(self.frame_page_3,
                                                 text='Historia opracji/błędów')
        self.frame_tree_history.pack(side=tk.TOP)

        self.scrollbar_tree_history = ttk.Scrollbar(self.frame_tree_history)
        self.scrollbar_tree_history.grid(row=1, column=1, sticky='ns')

        self.tree_history = ttk.Treeview(self.frame_tree_history,
                                         height=10,
                                         yscrollcommand=self.scrollbar_tree_history.set)
        self.tree_history.grid(row=1, column=0)
        self.column = ("Data", "historia")
        self.tree_history['columns'] = self.column
        self.tree_history.column('#0',
                                 anchor=tk.W,
                                 width=45,
                                 minwidth=45)
        self.tree_history.heading('#0',
                                  text='Lp',
                                  anchor=tk.CENTER)
        self.tree_history.column(self.column[0],
                                 anchor=tk.CENTER,
                                 width=80,
                                 minwidth=80)
        self.tree_history.heading(self.column[0],
                                  anchor=tk.CENTER,
                                  text='Data')
        self.tree_history.column(self.column[1],
                                 anchor=tk.W,
                                 width=305,
                                 minwidth=305)
        self.tree_history.heading(self.column[1],
                                  anchor=tk.CENTER,
                                  text='historia')

        self.scrollbar_tree_history.config(command=self.tree_history.yview)
# frame_tree_history END

# frame_tree_history_butons START
        self.frame_tree_history_butons = ttk.Frame(self.frame_page_3)
        self.frame_tree_history_butons.pack(side=tk.TOP, fill=tk.X, ipady=2)

        self.tree_history_b1 = ttk.Button(self.frame_tree_history_butons,
                                          text='Odśwież',
                                          command=self.history_tree_select,
                                          width=40)
        self.tree_history_b1.pack(side=tk.LEFT, fill=tk.X)

        self.rb12_var = tk.IntVar()
        self.rb12_var.set(1)
        self.tree_history_rb1 = ttk.Radiobutton(self.frame_tree_history_butons,
                                                text='Tylko operacje',
                                                variable=self.rb12_var,
                                                value=1)
        self.tree_history_rb1.pack(side=tk.RIGHT)
        self.tree_history_rb2 = ttk.Radiobutton(self.frame_tree_history_butons,
                                                text='Tylko błędy',
                                                variable=self.rb12_var,
                                                value=2)
        self.tree_history_rb2.pack(side=tk.RIGHT)

# frame_tree_history_butons END

# frame_tree_history_time START
        self.frame_tree_history_time = ttk.Frame(self.frame_page_3)
        self.frame_tree_history_time.pack(fill=tk.X, ipady=2)

        self.label_history_1 = ttk.Label(self.frame_tree_history_time,
                                       text='Czy uwzględnić czas? ')
        self.label_history_1.pack(side=tk.LEFT, fill=tk.X)

        self.rb34_var = tk.IntVar()
        self.rb34_var.set(1)
        self.time1_var = tk.StringVar()
        self.time1_var.set('2021-07-14')
        self.time2_var = tk.StringVar()
        self.time2_var.set(str(datetime.now().date()))
        self.tree_history_rb3 = ttk.Radiobutton(self.frame_tree_history_time,
                                                text='NIE',
                                                variable=self.rb34_var,
                                                value=1,
                                                command=self.time_select)
        self.tree_history_rb3.pack(side=tk.LEFT, anchor=tk.W, fill=tk.X)
        self.tree_history_rb4 = ttk.Radiobutton(self.frame_tree_history_time,
                                                text='TAK',
                                                variable=self.rb34_var,
                                                value=2,
                                                command=self.time_select)
        self.tree_history_rb4.pack(side=tk.LEFT, anchor=tk.W, fill=tk.X)

        self.entry_time_1 = ttk.Entry(self.frame_tree_history_time,
                                      width=10,
                                      textvariable=self.time1_var)
        self.entry_time_1.pack(side=tk.LEFT)

        self.label_history_2 = ttk.Label(self.frame_tree_history_time,
                                       text=' do ')
        self.label_history_2.pack(side=tk.LEFT, fill=tk.X)

        self.entry_time_2 = ttk.Entry(self.frame_tree_history_time,
                                      width=10,
                                      textvariable=self.time2_var)
        self.entry_time_2.pack(side=tk.LEFT)
        self.time_select()
# frame_tree_history_time END

        self.button_p3_open_history = ttk.Button(self.frame_page_3,
                                                text='Otwórz szczegółową historię błędów',
                                                command=lambda: os.startfile\
                                                    (os.path.abspath\
                                                        (self.programing_error_file.get_file_name())))
        self.button_p3_open_history.pack(side=tk.TOP, fill=tk.X, ipady=3)

        self.button_p3_open_old_file_folder = ttk.Button(self.frame_page_3,
                                                text='Otwórz folder ze starymi plikami',
                                                command=lambda: os.startfile\
                                                    (os.path.abspath\
                                                        ('..\\old_file\\')))
        self.button_p3_open_old_file_folder.pack(side=tk.TOP, fill=tk.X, ipady=3)




# frame_page_3 END

# >>> datetime.now()
# datetime.datetime(2021, 7, 15, 22, 58, 21, 302083)
# >>> datetime.now().date()
# datetime.date(2021, 7, 15)
# >>> print(datetime.now().date())
# 2021-07-15
# >>> print(str(datetime.now().date()))
# 2021-07-15