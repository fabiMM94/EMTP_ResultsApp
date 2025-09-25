import pandas as pd
#from user_tools import UserHandler
from bs4 import BeautifulSoup
import io
import re

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

class DataExtractor:
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
        return Data_html
    def get_generation_data(self, html_file: Path) -> pd.DataFrame:
        data_html = self.get_data_from_html(html_file)
        data_gen = self.clean_and_filter_gen_data(data_html)
        return data_gen
    def get_load_data(self, html_file: Path) -> pd.DataFrame:
        data_html = self.get_data_from_html(html_file)
        data_load = self.clean_and_filter_load_data(data_html)
        return data_load

    def clean_and_filter_gen_data(self,Data: pd.DataFrame)-> pd.DataFrame:
        helper = Helper()
        Types_selected = ['PVbus', 'Slack', 'PQbus']
        Data_GEN = Data[Data['Type'].isin(Types_selected)]
        Names = Data_GEN['Device'].str.split('/', expand=True)
        Names.columns = ["Name1", "NameLF", "ExtraName"]

        Values = Data_GEN.iloc[:, -3:]
        Values.columns = ["V [kV]", "P [MW]", "Q [MVAr]"]
        Data_GEN = pd.concat([Names, Values], axis=1)    

        Data_GEN["V [kV]"] = Data_GEN["V [kV]"].apply(lambda x: helper.get_voltage_magnitude(x, phases=3))
        Data_GEN["P [MW]"] = Data_GEN["P [MW]"].apply(helper.to_MW_MVar)
        Data_GEN["Q [MVAr]"] = Data_GEN["Q [MVAr]"].apply(helper.to_MW_MVar)
        Data_GEN["Vnom [kV]"] = Data_GEN["V [kV]"].apply(helper.get_nominal_voltage)

        Data_GEN_copy = Data_GEN
        c = 0
        for name in Data_GEN_copy["Name1"]:
            if "BESS" in name:
                Data_GEN.at[c, "type"] = "BESS"
            if "PMGD" in name:
                Data_GEN.at[c, "type"] = "PMGD"
            if ("PFV" in name or "PMG" in name) and "PMGD" not in name:
                Data_GEN.at[c, "type"] = "PFV"
            if "PE" in name and "PFV" not in name and "Central" not in name:
                Data_GEN.at[c, "type"] = "PE"
     
            if (
                "HP_" in name
                or "TER_" in name
                or "HE_" in name
                or "LomaALta" in name
                or "La_Mina_RColorado" in name
            ):
                Data_GEN.at[c, "type"] = "SG"
            if "CCSS" in name:
                Data_GEN.at[c, "type"] = "CCSS"
            if "STAT" in name:
                Data_GEN.at[c, "type"] = "STATCOM"
            if "BAT" in name:
                Data_GEN.at[c, "type"] = "BATSINC"
            if "HVDC" in name:
                Data_GEN.at[c, "type"] = "HVDC"

            c = c + 1

        return Data_GEN
 
    def clean_and_filter_load_data(sel, Data: pd.DataFrame) -> pd.DataFrame:
        helper = Helper()
        Types_selected = ["PQload"]
        Data_load = Data[Data["Type"].isin(Types_selected)]
        Data_load.columns = ["Name", "Type", "V [kV]", "P [MW]", "Q [MVAr]"]
        
        Data_load["V [kV]"] = Data_load["V [kV]"].apply(lambda x: helper.get_voltage_magnitude(x, phases=1))
        Data_load["P [MW]"] = Data_load["P [MW]"].apply(helper.to_MW_MVar)
        Data_load["Q [MVAr]"] = Data_load["Q [MVAr]"].apply(helper.to_MW_MVar)
        Data_load["Vnom [kV]"] = Data_load["V [kV]"].apply(helper.get_nominal_voltage)
        Data_load["V [pu]"] = Data_load["V [kV]"] / Data_load["Vnom [kV]"]

         # indexes of 3 by 3
        Data_load = Data_load.iloc[::3]
         # The indexes are reset
        Data_load = Data_load.reset_index(drop=True)
        # borro el nombre "Load_a del string de su"
        Data_load["Name"] = Data_load["Name"].str.replace("/Load_a", "", regex=False)

        return Data_load
         
class Helper():
    def __init__(self):
          pass
    def to_MW_MVar(self, valor):
        final= float(valor)/(10**6)
        return (round(final,2))
    def get_voltage_magnitude_3(self, raw_string) -> float | str:
        scientific_numbers = re.findall(r'[+-]?\d+\.\d+E[+-]?\d+', raw_string)
        even_indices = [i for i in range(len(scientific_numbers)) if i % 2 == 0]
        even_values = [scientific_numbers[i] for i in even_indices]
        voltage_values = [round(float(value), 2) for value in even_values]
        
        if voltage_values[0] == voltage_values[1] == voltage_values[2]:
            return voltage_values[0]
        else:
            return "unbalanced"
    def get_voltage_magnitude_1(self, raw_string):
        numeros = re.findall(r'[+-]?\d+\.\d+E[+-]?\d+', raw_string)
        if numeros:
            numero_1 = float(numeros[0])  # Convertir a float
            return round(numero_1, 2)    
    def get_voltage_magnitude(self, raw_string: str, phases: int = 3) -> float | str:
        # Extract all numbers in scientific notation (magnitudes and angles interleaved)
        voltage_angle_values = re.findall(r'[+-]?\d+\.\d+E[+-]?\d+', raw_string)
        
        # Keep only the voltage magnitudes (even indices)
        voltage_magnitudes = [round(float(v), 2) for v in voltage_angle_values[::2]]
        
        if phases == 1:
            return voltage_magnitudes[0] if voltage_magnitudes else None
        elif phases == 3:
            if len(voltage_magnitudes) >= 3 and voltage_magnitudes[0] == voltage_magnitudes[1] == voltage_magnitudes[2]:
                return voltage_magnitudes[0]
            else:
                return "unbalanced"
        else:
            raise ValueError("Only 1-phase or 3-phase supported")
    
        
    def get_nominal_voltage(self, n):
        if 90 <= n + 20 <= 130 or 90 <= n - 20 <= 130:
            return 110
        elif 200 <= n + 20 <= 240 or 200 <= n - 20 <= 240:
            return 220
        elif 46 <= n + 20 <= 86 or 46 <= n - 20 <= 86:
            return 66
        elif 10 <= n + 7 <= 23.2 or 7 <= n - 7 <= 23.2:
            return 13.2    
        elif 0.1 <= n + 2 <= 4 or 0.1 <= n -2 <= 4:
            return 0.6     
        else:
            return None  # Si no cae en ninguna categorí 

class ReportHandler:
    def __init__(self):
        pass

if __name__ == "__main__":
    manager = FileManager()
    extractor = DataExtractor()
    html_file = manager.select_file()
    gen_data = extractor.get_generation_data(html_file)
    load_data = extractor.get_load_data(html_file)
    print(load_data)

