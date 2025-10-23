import pandas as pd

# from user_tools import UserHandler
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
            selected_file = filedialog.askopenfilename(title="Seleccionar archivo HTML")
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
        Data_html = Data[new_columns[:5]]

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

    def clean_and_filter_gen_data(self, Data: pd.DataFrame) -> pd.DataFrame:
        helper = Helper()
        Types_selected = ["PVbus", "Slack", "PQbus"]
        Data_GEN = Data[Data["Type"].isin(Types_selected)]
        Names = Data_GEN["Device"].str.split("/", expand=True)
        Names.columns = ["Name1", "NameLF", "ExtraName"]

        Values = Data_GEN.iloc[:, -3:]
        Values.columns = ["V [kV]", "P [MW]", "Q [MVAr]"]
        Data_GEN = pd.concat([Names, Values], axis=1)

        Data_GEN["V [kV]"] = Data_GEN["V [kV]"].apply(
            lambda x: helper.get_voltage_magnitude(x, phases=3)
        )
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

        Data_load["V [kV]"] = Data_load["V [kV]"].apply(
            lambda x: helper.get_voltage_magnitude(x, phases=1)
        )
        Data_load["P [MW]"] = 3 * Data_load["P [MW]"].apply(helper.to_MW_MVar)
        Data_load["Q [MVAr]"] = 3 * Data_load["Q [MVAr]"].apply(helper.to_MW_MVar)
        Data_load["Vnom [kV]"] = Data_load["V [kV]"].apply(helper.get_nominal_voltage)
        Data_load["V [pu]"] = Data_load["V [kV]"] / Data_load["Vnom [kV]"]

        # indexes of 3 by 3
        Data_load = Data_load.iloc[::3]
        # The indexes are reset
        Data_load = Data_load.reset_index(drop=True)
        # borro el nombre "Load_a del string de su"
        Data_load["Name"] = Data_load["Name"].str.replace("/Load_a", "", regex=False)

        return Data_load


class ReportHandler:
    def __init__(self, Data_gen: pd.DataFrame, Data_load: pd.DataFrame):
        self.Data_gen = Data_gen
        self.Data_load = Data_load
        # Suma de potencias
        self.P_gen_PFV = self.get_MW_sum_by_type("PFV")
        self.P_gen_PE = self.get_MW_sum_by_type("PE")
        self.P_gen_PMGD = self.get_MW_sum_by_type("PMGD")
        self.P_gen_SG = self.get_MW_sum_by_type("SG")
        self.P_BESS = self.get_MW_sum_by_type("BESS")
        self.P_Batsinc = self.get_MW_sum_by_type("BATSINC")
        self.P_CCSS = self.get_MW_sum_by_type("CCSS")
        self.P_HVDC = self.get_MW_sum_by_type("HVDC")
        self.P_load = round(self.Data_load["P [MW]"].sum(), 1)
        # Numero de plantas de cada tecnologia
        self.N_PV = self.count_plants_by_type("PFV")
        self.N_PE = self.count_plants_by_type("PE")
        self.N_PMGD = self.count_plants_by_type("PMGD")
        self.N_SG = self.count_plants_by_type("SG")
        self.N_BESS = self.count_plants_by_type("BESS")
        self.N_Batsinc = self.count_plants_by_type("BATSINC")
        self.N_CCSS = self.count_plants_by_type("CCSS")
        # Porcentajes de generacion
        self.pP_PFV = self.gen_percent(self.P_gen_PFV)
        self.pP_PE = self.gen_percent(self.P_gen_PE)
        self.pP_BATg = self.gen_percent(self.get_Batsinc_gen())
        self.pP_PMGD = self.gen_percent(self.P_gen_PMGD)
        self.pP_IBR = self.gen_percent(self.get_MW_IBR_gen())
        self.pP_SG = self.gen_percent(self.P_gen_SG)

    def get_MW_sum_by_type(self, plant_type: str) -> float:
        P_sum = round(
            self.Data_gen[self.Data_gen["type"] == plant_type]["P [MW]"].sum(), 1
        )
        return P_sum

    def count_plants_by_type(self, plant_type: str) -> int:
        N = int(self.Data_gen["type"].str.count(plant_type).sum())
        return N

    def get_MW_IBR_gen(self) -> float:
        P_IBR_GEN = sum(
            [self.P_gen_PFV, self.P_gen_PE, self.P_gen_PMGD, self.get_BESS_gen()]
        )
        return P_IBR_GEN

    def get_BESS_gen(self) -> float:
        if self.P_BESS > 0:
            P_BESS_gen = self.P_BESS
        elif self.P_BESS <= 0:
            P_BESS_gen = 0
        return P_BESS_gen

    def get_BESS_no_gen(self) -> float:
        if self.P_BESS < 0:
            P_BESS_gen = self.P_BESS
        elif self.P_BESS > 0:
            P_BESS_gen = 0
        return P_BESS_gen

    def get_Batsinc_gen(self) -> float:
        if self.P_Batsinc > 0:
            P_bat = self.P_Batsinc
        elif self.P_Batsinc <= 0:
            P_bat = 0
        return P_bat

    def get_Batsinc_no_gen(self) -> float:
        if self.P_Batsinc < 0:
            P_bat = self.P_Batsinc
        elif self.P_Batsinc >= 0:
            P_bat = 0
        return P_bat

    def get_total_consumption(self) -> float:
        consumption = (
            abs(self.get_Batsinc_no_gen()) + abs(self.get_BESS_no_gen()) + self.P_load
        )
        return consumption

    def get_losses_ac(self) -> float:
        losses = (
            self.get_total_gen()
            - self.get_total_consumption()
            - abs(self.P_CCSS)
            - abs(self.P_HVDC)
        )
        return losses

    def get_losses_dc(self) -> float:
        losses_dc = abs(self.P_HVDC)
        return losses_dc

    def get_losses_total(self) -> float:
        losses_total = self.get_losses_ac() + self.get_losses_dc()
        return losses_total

    def get_total_gen(self) -> float:
        P_total = (
            self.get_MW_IBR_gen()
            + self.P_gen_SG
            + self.get_Batsinc_gen()
            + self.get_BESS_gen()
        )
        return P_total

    def gen_percent(self, active_power: float) -> float:
        percent = round(100 * active_power / self.get_total_gen(), 1)
        return percent

    def buil_report(self) -> pd.DataFrame:
        data = [
            ("Total IBR PV Generation", self.P_gen_PFV, "MW"),
            ("Total IBR WF Generation", self.P_gen_PE, "MW"),
            ("Total IBR Batteries Generation", self.get_BESS_gen(), "MW"),
            ("Total Distributed Generation (PMGD)", self.P_gen_PMGD, "MW"),
            ("Total IBR Generation", self.get_MW_IBR_gen(), "MW"),
            ("Total Synchronous Generation", self.P_gen_SG, "MW"),
            ("Total Generation", self.get_total_gen(), "MW"),
            ("Total Load (Passive)", self.P_load, "MW"),
            ("Total IBR Batteries Consumption", self.get_BESS_no_gen(), "MW"),
            ("Total Synchronous Batteries", self.get_Batsinc_no_gen(), "MW"),
            ("Total CCSS Consumption", self.P_CCSS, "MW"),
            ("Total Consumption (Load+Batteries)", self.get_total_consumption(), "MW"),
            ("Total HVDC", self.P_HVDC, "MW"),
            ("AC Losses", self.get_losses_ac(), "MW"),
            ("DC Losses", self.get_losses_dc(), "MW"),
            ("Total Losses", self.get_losses_total(), "MW"),
            (None, None, None),
            (None, None, None),
            ("IBR PV Generation Participation", self.pP_PFV, "%"),
            ("IBR WF Generation Participation", self.pP_PE, "%"),
            ("IBR Batteries Generation Part.", self.pP_BATg, "%"),
            ("Distributed Generation (PMGD) Part.", self.pP_PMGD, "%"),
            ("IBR Generation Participation", self.pP_IBR, "%"),
            ("Synchronous Generation Participation", self.pP_SG, "%"),
            (None, None, None),
            (None, None, None),
            ("Number of photovoltaic generators", self.N_PV, "-"),
            ("Number of wind generators", self.N_PE, "-"),
            ("Number of synchronous generators", self.N_SG, "-"),
            ("Number of PMGDs", self.N_PMGD, "-"),
            ("Numner of BESS", self.N_BESS, "-"),
            ("Number of synchronous batteries", self.N_Batsinc, "-"),
            ("Number of synchronous Condenser", self.N_CCSS, "-"),
        ]

        return pd.DataFrame(data, columns=["Item", "Value", "Unit"])


class Helper:
    def __init__(self):
        pass

    def to_MW_MVar(self, valor):
        final = float(valor) / (10**6)
        return round(final, 2)

    def get_voltage_magnitude(self, raw_string: str, phases: int = 3) -> float | str:
        # Extract all numbers in scientific notation (magnitudes and angles interleaved)
        voltage_angle_values = re.findall(r"[+-]?\d+\.\d+E[+-]?\d+", raw_string)

        # Keep only the voltage magnitudes (even indices)
        voltage_magnitudes = [round(float(v), 2) for v in voltage_angle_values[::2]]

        if phases == 1:
            return voltage_magnitudes[0] if voltage_magnitudes else None
        elif phases == 3:
            if (
                len(voltage_magnitudes) >= 3
                and voltage_magnitudes[0]
                == voltage_magnitudes[1]
                == voltage_magnitudes[2]
            ):
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
        elif 0.1 <= n + 2 <= 4 or 0.1 <= n - 2 <= 4:
            return 0.6
        else:
            return None  # Si no cae en ninguna categorí


if __name__ == "__main__":
    manager = FileManager()
    extractor = DataExtractor()

    html_file = manager.select_file()
    gen_data = extractor.get_generation_data(html_file)
    load_data = extractor.get_load_data(html_file)

    report = ReportHandler(gen_data, load_data)
    df_report = report.buil_report()
    print(df_report)
