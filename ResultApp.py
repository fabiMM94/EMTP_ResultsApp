import pandas as pd
from bs4 import BeautifulSoup
import io
import unicodedata
from pathlib import Path
from tkinter import Tk, filedialog
import re


class DataExtraction:
    def __init__(self, html_file):
        self.html_file = html_file

    def get_data_from_html(self):
        if isinstance(self.html_file, io.BytesIO) or isinstance(
            self.html_file, io.StringIO
        ):
            self.html_file.seek(0)  # Reiniciar puntero
            html_content = self.html_file.read().decode("iso-8859-1")
            Data = pd.read_html(html_content)
        else:
            Data = pd.read_html(self.html_file)  # Si
        # Data= pd.read_html(html_file)
        # I take the first part of the html
        Data = pd.DataFrame(Data[0])
        # Columns are de.fined
        Columns = Data.iloc[0]
        Data.columns = Columns.to_list()
        # The zero row that had the name of the columns is deleted
        Data = Data.iloc[1:]
        # The indexes are reset
        Data = pd.DataFrame(Data.reset_index())

        # New Columns: Device, Type, V ,P Q
        new_columns = Columns.to_list()
        new_columns = new_columns[:5]
        Data = Data[new_columns[:5]]

        Generation_Table = self.GenerationData(Data)
        Load_Table = self.LoadData(Data)

        print(Data)
        return


class FileManager:
    def __init__(self):
        pass

    def select_file(self, file_path=None) -> Path | None:
        root = Tk()
        root.withdraw()
        while not file_path:
            selected_file = filedialog.askopenfilename(title="Seleccionar archivo HTML")
            if selected_file != "":
                file_path = selected_file
            else:
                break
        root.destroy()
        self.file_selected = Path(file_path) if file_path else None
        return self.file_selected


class Helper:
    def __init__(self):
        None

    def Remove_accents(self, input_str):
        # Normalizar el string a su forma combinada
        nfkd_form = unicodedata.normalize("NFKD", input_str)
        # Filtrar y mantener solo los caracteres que no son diacríticos
        return "".join([c for c in nfkd_form if not unicodedata.combining(c)])

    def Transformation_MW_MVAR(self, cadena):
        final = float(cadena) / (10**6)
        final = round(final, 2)
        return final

    def Get_Voltage_Magnitude(self, cadena):
        numeros = re.findall(r"[+-]?\d+\.\d+E[+-]?\d+", cadena)
        indices_pares = [i for i in range(len(numeros)) if i % 2 == 0]
        valores_pares = [numeros[i] for i in indices_pares]
        lista_V = [round(float(elemento), 2) for elemento in valores_pares]
        if lista_V[0] == lista_V[1] == lista_V[2]:
            return lista_V[0]
        else:
            return "desbanceado"

    # toma un el string que tiene "V+angulo y me entrega solo el "V y redondeado"
    def Split_Voltage_Angle(self, s):
        numeros = re.findall(r"[+-]?\d+\.\d+E[+-]?\d+", s)
        if numeros:
            numero_1 = float(numeros[0])  # Convertir a float
            return round(numero_1, 2)

    @staticmethod
    def kilovolts_converter(cadena):
        final = float(cadena) / (10**3)
        final = 1.732 * final
        final = round(final, 2)
        return final

    def Get_Nominal_Voltage(self, n):
        if 90 <= n + 20 <= 130 or 90 <= n - 20 <= 130:
            return 110
        elif 200 <= n + 20 <= 240 or 200 <= n - 20 <= 240:
            return 220
        elif 46 <= n + 20 <= 86 or 46 <= n - 20 <= 86:
            return 66
        elif 10 <= n + 7 <= 23.2 or 7 <= n - 7 <= 23.2:
            return 13.2
        elif 0.1 <= n + 2 <= 4 or 0.1 <= n - 2 <= 4:
            return 0.6
        else:
            return None  # Si no cae en ninguna categoría

    def Zone_data(self, excel, Hoja, type):
        # excel = "diccionario_Benja/Diccionario_EMTP_DIgSILENT_BVega_v4.xlsx"
        # excel = "diccionario_Benja/Zonas_DIgSILENT.xlsx"
        # excel = "Data/Zonas_DIgSILENT_vF.xlsx"
        data = pd.read_excel(excel, sheet_name=Hoja)
        if type == "PV":
            columnas_deseadas = [
                "Name1",
                "Name2",
                "Zona DIgSILENT",
                "Nombre DIgSILENT",
            ]  # Reemplaza con los nombres de las columnas que deseas
        elif type == "WP":
            columnas_deseadas = ["Name1", "Zona DIgSILENT", "Nombre DIgSILENT"]
        elif type == "SG":
            columnas_deseadas = [
                "Name1",
                "Name2",
                "Name3",
                "Zona DIgSILENT",
                "Nombre DIgSILENT",
            ]
        elif type == "PMGD":
            columnas_deseadas = ["Name1", "Name2", "Zona DIgSILENT", "Nombre DIgSILENT"]
        elif type == "CCSS":
            columnas_deseadas = ["Name1", "Name2", "Zona DIgSILENT", "Nombre DIgSILENT"]
        elif type == "Cargas":
            columnas_deseadas = ["Carga EMTP", "Zona DIgSILENT"]

        # Filtra el DataFrame para que contenga solo las columnas deseadas
        dataframe_filtrado = data[columnas_deseadas]
        # return dataframe_filtrado.dropna()
        return dataframe_filtrado
