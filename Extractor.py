import pandas as pd
#from user_tools import UserHandler
from bs4 import BeautifulSoup
import io

from pathlib import Path
from tkinter import Tk, filedialog

class FileManager:
    def __init__(self):
          pass
    def select_file(self, file_path=None) -> Path | None:
            root = Tk()
            root.withdraw()
            while not file_path:
                selected_file = filedialog.askopenfilename(
                    title="Seleccionar archivo HTML"
                )
                if selected_file != "":
                    file_path = selected_file
                else:
                    break
            root.destroy()
            self.file_selected = Path(file_path) if file_path else None
            return self.file_selected


class DataExtraction:
    def __init__(self):
         pass
    def get_data_from_html(self, html_file: Path) -> pd.DataFrame:
        if isinstance(html_file, io.BytesIO) or isinstance(html_file, io.StringIO):
            html_file.seek(0)  # Reiniciar puntero
            html_content = html_file.read().decode("iso-8859-1")
            Data = pd.read_html(html_content)
        else:
            Data = pd.read_html(html_file)  # Si
         #Data= pd.read_html(html_file) 
        # I take the first part of the html
        Data=pd.DataFrame(Data[0]) 
        # Columns are de.fined
        Columns=  Data.iloc[0]         
        Data.columns = Columns.to_list() 
        # The zero row that had the name of the columns is deleted
        Data = Data.iloc[1:]
        # The indexes are reset
        Data=pd.DataFrame(Data.reset_index())

        # New Columns: Device, Type, V ,P Q
        new_columns = Columns.to_list()
        new_columns= new_columns[:5] 
        Data_html= Data[new_columns[:5]]

        print(Data_html)
        return Data
    def clean_and_filter_gen_data(self,Data: pd.DataFrame)-> pd.DataFrame:
        helper = Helper()
        Types_selected = ['PVbus', 'Slack', 'PQbus']
        Data_GEN = Data[Data['Type'].isin(Types_selected)]
        Names = Data_GEN['Device'].str.split('/', expand=True)

        if Names.shape[1] == 4:
            Names.columns = ['Name1', 'Name2', 'NameLF', "Name4"]
        elif Names.shape[1] == 3:
            Names.columns = ['Name1', 'Name2', 'NameLF']
          
        pass   
    def clean_and_filter_Load_data(sel, Data: pd.DataFrame) -> pd.DataFrame:
         pass
         
class Helper():
    def __init__(self):
          pass
    def to_MW_MVar(self, valor):
        final= float(valor)/(10**6)
        return (round(final,2))
             

if __name__ == "__main__":
    manager = FileManager()
    extractor = DataExtraction()
    html_file = manager.select_file()
    LF_data = extractor.get_data_from_html(html_file)

