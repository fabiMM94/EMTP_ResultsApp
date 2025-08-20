import pandas as pd
#from user_tools import UserHandler
from bs4 import BeautifulSoup
import io


class DataExtraction:
    def __init__(self,html_file):
         self.html_file = html_file
    def get_data_from_html(self):
        if isinstance(self.html_file, io.BytesIO) or isinstance(self.html_file, io.StringIO):
            self.html_file.seek(0)  # Reiniciar puntero
            html_content = self.html_file.read().decode("iso-8859-1")
            Data = pd.read_html(html_content)
        else:
            Data = pd.read_html(self.html_file)  # Si
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
        Data= Data[new_columns[:5]]

        print(Data)
        return
   