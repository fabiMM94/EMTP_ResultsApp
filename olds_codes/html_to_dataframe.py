import pandas as pd
from tools import Helper

# from user_tools import UserHandler
from bs4 import BeautifulSoup
import io


class DataExtraction:
    def __init__(self, html_file, Vnom):
        self.html_file = html_file
        self.Vnom = Vnom

    def Data_Extraction(self, html_file, Vnom):
        # Verificar si es un archivo subido en Streamlit
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

        # --------------------------------------------
        # New Columns: Device, Type, V ,P Q
        new_columns = Columns.to_list()
        new_columns = new_columns[:5]
        Data = Data[new_columns[:5]]

        Generation_Table = self.GenerationData(Data)
        Load_Table = self.LoadData(Data)
        return Generation_Table, Load_Table

    def GenerationData(self, Data):
        # instantiate classs
        helper = Helper()

        # The generation elements are selected
        Types_selected = ["PVbus", "Slack", "PQbus"]
        Data_GEN = Data[Data["Type"].isin(Types_selected)]
        # Device column is expanded into 4 new columns
        Names = Data_GEN["Device"].str.split("/", expand=True)
        Names.columns = ["Name1", "Name2", "NameLF", "Name4"]

        Values = Data_GEN.iloc[:, -3:]
        Values.columns = ["V [kV]", "P [MW]", "Q [MVAr]"]

        Data_GEN = pd.concat([Names, Values], axis=1)

        Data_GEN["V [kV]"] = Data_GEN["V [kV]"].apply(helper.Get_Voltage_Magnitude)
        Data_GEN["P [MW]"] = Data_GEN["P [MW]"].apply(helper.Transformation_MW_MVAR)
        Data_GEN["Q [MVAr]"] = Data_GEN["Q [MVAr]"].apply(helper.Transformation_MW_MVAR)
        Data_GEN["Vnom [kV]"] = Data_GEN["V [kV]"].apply(helper.Get_Nominal_Voltage)

        # Nominal Voltage Correction
        N = len(Data_GEN)
        for fila in range(N):
            Name1 = Data_GEN.at[fila, "Name1"]
            Name2 = Data_GEN.at[fila, "Name2"]
            NameLF = Data_GEN.at[fila, "NameLF"]
            result = self.Vnom[
                (self.Vnom["Name1"] == Name1)|
                & (self.Vnom["Name2"] == Name2)
                & (self.Vnom["NameLF"] == NameLF)
            ]
            if len(result) == 1:
                Data_GEN.at[fila, "Vnom [kV]"] = float(
                    result["Tensión Nominal [kV]"].iloc[0]
                )

            else:
                continue
        Data_GEN["V [pu]"] = Data_GEN["V [kV]"] / Data_GEN["Vnom [kV]"]

        # Modifications ----------------------------------------
        Data_GEN_copy = Data_GEN
        c = 0
        Drop_list = []  # Eliminated row

        for name in Data_GEN_copy["Name1"]:
            if "BESS" in name:
                Data_GEN.at[c, "tipo"] = "BESS"
                Drop_list.append(c)
            if "PMGD" in name:
                Data_GEN.at[c, "tipo"] = "PMGD"
            if ("PFV" in name or "PMG" in name) and "PMGD" not in name:
                Data_GEN.at[c, "tipo"] = "PFV"
            if "PE" in name and "PFV" not in name and "Central" not in name:
                Data_GEN.at[c, "tipo"] = "PE"
            """
            if (
                "Central" in name
                or "Los_Quilos_Juncal" in name
                or "Cochrane" in name
                or "C_ANGOSTURA" in name
                or "HP_" in name
            ) and "BESS" not in name:
                Data_GEN.at[c, "tipo"] = "SG"
            """
            if (
                "HP" in name
                or "TER"
                or "HE" in name
                or "LomaALta" in name
                or "La_Mina_RColorado" in name
            ):
                Data_GEN.at[c, "tipo"] = "SG"
            if "CCSS" in name:
                Data_GEN.at[c, "tipo"] = "CS"
            if "STAT" in name:
                Data_GEN.at[c, "tipo"] = "STATCOM"
            if "BAT" in name:
                Data_GEN.at[c, "tipo"] = "BATSINC"

            c = c + 1

        return Data_GEN

    def LoadData(self, Data):
        # instantiate class
        helper = Helper()
        Types_selected = ["PQload"]
        Data_Load = Data[Data["Type"].isin(Types_selected)]
        Data_Load.columns = ["Name", "Type", "V [kV]", "P [MW]", "Q [MVAr]"]

        Data_Load["V [kV]"] = Data_Load["V [kV]"].apply(helper.Split_Voltage_Angle)
        Data_Load["P [MW]"] = 3 * Data_Load["P [MW]"].apply(
            helper.Transformation_MW_MVAR
        )
        Data_Load["Q [MVAr]"] = 3 * Data_Load["Q [MVAr]"].apply(
            helper.Transformation_MW_MVAR
        )
        Data_Load["Vnom [kV]"] = Data_Load["V [kV]"].apply(helper.Get_Nominal_Voltage)
        Data_Load["V [pu]"] = Data_Load["V [kV]"] / Data_Load["Vnom [kV]"]

        # indexes of 3 by 3
        Data_Load = Data_Load.iloc[::3]
        # The indexes are reset
        Data_Load = Data_Load.reset_index(drop=True)
        # borro el nombre "Load_a del string de su"
        Data_Load["Name"] = Data_Load["Name"].str.replace("/Load_a", "", regex=False)

        return Data_Load


class BusExtraction:
    def __init__(self, html_file):
        self.html_file = html_file

    def BusData(self):
        helper = Helper()

        # Verifica si `self.html_file` es un archivo subido en Streamlit
        if isinstance(self.html_file, io.BytesIO) or isinstance(
            self.html_file, io.StringIO
        ):
            self.html_file.seek(0)  # Reiniciar puntero
            Read_html = self.html_file.read().decode("iso-8859-1")  # Leer y decodificar
        else:
            with open(self.html_file, "r", encoding="iso-8859-1") as file:
                Read_html = file.read()

        """
        # Read HTML
        with open(self.html_file, "r", encoding="iso-8859-1") as file:
            Read_html = file.read()
        """
        # Parsear el HTML y filtrar tablas relevantes
        soup = BeautifulSoup(Read_html, "html.parser")
        tablas_filtradas = [
            tabla
            for tabla in soup.find_all("table")
            if any(
                "Node Voltages (RMS)" in celda.text for celda in tabla.find_all("td")
            )
        ]

        # Procesar las tablas filtradas
        all_data = []
        for tabla in tablas_filtradas:
            filas = tabla.find_all("tr")
            tabla_data = [
                [celda.text.strip() for celda in fila.find_all("td")] for fila in filas
            ]
            all_data.extend(tabla_data)

        # Crear un DataFrame con las columnas esperadas
        df = pd.DataFrame(
            all_data, columns=["BusName", "index", "Voltage [kV]", "Angle [°]"]
        )

        # Clean y filter data
        exclude_patterns = "PFV|PMGD|STAT|BESS|PE_|SVC_|Central_|TR_"
        df = df[~df["BusName"].str.contains(exclude_patterns, na=False)]
        df = df[df["BusName"].str.contains("220|500|110", na=False)]
        df = df[~df["BusName"].str.endswith(("b", "c"), na=False)]

        # Convertir valores y calcular nuevas columnas
        df["Voltage [kV]"] = df["Voltage [kV]"].apply(helper.kilovolts_converter)
        df["Voltage [kV]"] = pd.to_numeric(df["Voltage [kV]"], errors="coerce")

        df["Nominal Voltage [kV]"] = df["BusName"].apply(
            lambda name: (
                110
                if "110" in name
                else 220 if "220" in name else 500 if "500" in name else None
            )
        )
        df["V [pu]"] = df["Voltage [kV]"] / df["Nominal Voltage [kV]"]
        df["V [pu]"] = df["V [pu]"].astype(float).round(3)
        # Convertir los valores a flotantes y mostrar sin notación científica
        df["Angle [°]"] = df["Angle [°]"].apply(lambda x: float(x)).round(1)
        # borro columna indice
        df.drop("index", axis=1, inplace=True)
        # Reiniciar el índice y retornar el DataFrame
        return df.reset_index(drop=True)


class DataExtractionOnlyHTML:
    def __init__(self, html_file):
        self.html_file = html_file
        

    def Data_Extraction(self, html_file):
        if isinstance(self.html_file, io.BytesIO) or isinstance(
            self.html_file, io.StringIO
        ):
            self.html_file.seek(0)  # Reiniciar puntero
            html_content = self.html_file.read().decode(
                "iso-8859-1"
            )  # Decodificar el contenido
            Data = pd.read_html(html_content)
        else:
            Data = pd.read_html(self.html_file)  # Si
        # Data = pd.read_html(html_file, flavor="lxml")
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

        # --------------------------------------------
        # New Columns: Device, Type, V ,P Q
        new_columns = Columns.to_list()
        new_columns = new_columns[:5]
        Data = Data[new_columns[:5]]

        Generation_Table = self.GenerationData(Data)
        Load_Table = self.LoadData(Data)
        return Generation_Table, Load_Table

    def GenerationData(self, Data):
        # instantiate classs
        helper = Helper()

        # The generation elements are selected
        Types_selected = ["PVbus", "Slack", "PQbus"]
        Data_GEN = Data[Data["Type"].isin(Types_selected)]
        # Device column is expanded into 4 new columns
        Names = Data_GEN["Device"].str.split("/", expand=True)
        Names.columns = ["Name1", "NameLF","NameX"]

        Values = Data_GEN.iloc[:, -3:]
        Values.columns = ["V [kV]", "P [MW]", "Q [MVAr]"]

        Data_GEN = pd.concat([Names, Values], axis=1)

        Data_GEN["V [kV]"] = Data_GEN["V [kV]"].apply(helper.Get_Voltage_Magnitude)
        Data_GEN["P [MW]"] = Data_GEN["P [MW]"].apply(helper.Transformation_MW_MVAR)
        Data_GEN["Q [MVAr]"] = Data_GEN["Q [MVAr]"].apply(helper.Transformation_MW_MVAR)
        Data_GEN["Vnom [kV]"] = Data_GEN["V [kV]"].apply(helper.Get_Nominal_Voltage)
        

        # Nominal Voltage Correction
        """
        N = len(Data_GEN)
        for fila in range(N):
            Name1 = Data_GEN.at[fila, "Name1"]
            # Name2 = Data_GEN.at[fila, "Name2"]
            NameLF = Data_GEN.at[fila, "NameLF"]
            result = self.Vnom[
                (self.Vnom["Name1"] == Name1)
                # & (self.Vnom["Name2"] == Name2)
                & (self.Vnom["NameLF"] == NameLF)
            ]
            if len(result) == 1:
                Data_GEN.at[fila, "Vnom [kV]"] = float(
                    result["Tensión Nominal [kV]"].iloc[0]
                )

            else:
                continue
        Data_GEN["V [pu]"] = Data_GEN["V [kV]"] / Data_GEN["Vnom [kV]"]
        """
        # Modifications ----------------------------------------
        Data_GEN_copy = Data_GEN
        c = 0
        Drop_list = []  # Eliminated row

        for name in Data_GEN_copy["Name1"]:
            if "BESS" in name:
                Data_GEN.at[c, "tipo"] = "BESS"
                Drop_list.append(c)
            if "PMGD" in name:
                Data_GEN.at[c, "tipo"] = "PMGD"
            if ("PFV" in name or "PMG" in name) and "PMGD" not in name:
                Data_GEN.at[c, "tipo"] = "PFV"
            if "PE" in name and "PFV" not in name and "Central" not in name:
                Data_GEN.at[c, "tipo"] = "PE"
            """
            if (
                "Central" in name
                or "Los_Quilos_Juncal" in name
                or "Cochrane" in name
                or "C_ANGOSTURA" in name
                or "HP_" in name
            ) and "BESS" not in name:
                Data_GEN.at[c, "tipo"] = "SG"
            """
            if (
                "HP" in name
                or "TER"
                or "HE" in name
                or "LomaALta" in name
                or "La_Mina_RColorado" in name
            ):
                Data_GEN.at[c, "tipo"] = "SG"
            if "CCSS" in name:
                Data_GEN.at[c, "tipo"] = "CS"
            if "STAT" in name:
                Data_GEN.at[c, "tipo"] = "STATCOM"
            if "BAT" in name:
                Data_GEN.at[c, "tipo"] = "BATSINC"

            c = c + 1

        return Data_GEN

    def LoadData(self, Data):
        # instantiate class
        helper = Helper()
        Types_selected = ["PQload"]
        Data_Load = Data[Data["Type"].isin(Types_selected)]
        Data_Load.columns = ["Name", "Type", "V [kV]", "P [MW]", "Q [MVAr]"]

        Data_Load["V [kV]"] = Data_Load["V [kV]"].apply(helper.Split_Voltage_Angle)
        Data_Load["P [MW]"] = 3 * Data_Load["P [MW]"].apply(
            helper.Transformation_MW_MVAR
        )
        Data_Load["Q [MVAr]"] = 3 * Data_Load["Q [MVAr]"].apply(
            helper.Transformation_MW_MVAR
        )
        Data_Load["Vnom [kV]"] = Data_Load["V [kV]"].apply(helper.Get_Nominal_Voltage)
        Data_Load["V [pu]"] = Data_Load["V [kV]"] / Data_Load["Vnom [kV]"]

        # indexes of 3 by 3
        Data_Load = Data_Load.iloc[::3]
        # The indexes are reset
        Data_Load = Data_Load.reset_index(drop=True)
        # borro el nombre "Load_a del string de su"
        Data_Load["Name"] = Data_Load["Name"].str.replace("/Load_a", "", regex=False)

        return Data_Load
