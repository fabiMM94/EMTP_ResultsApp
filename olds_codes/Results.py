import html_to_dataframe
import results_analysis
#from tkinter import filedialog, messagebox
import pandas as pd
#import tkinter as tk
#from pandastable import Table,config, TableModel
import streamlit as st
class ResultsTable:
    def __init__(self,html_full_file_name,root):
          self.html_full_file_name  = html_full_file_name 
          self.root =root
          self.Bus_Table=None
    
    def get_report(self):
        data_extractor = html_to_dataframe.DataExtractionOnlyHTML(self.html_full_file_name)
        Generation_Table, Load_Table = data_extractor.Data_Extraction(self.html_full_file_name)
        

        Bus_extractor = html_to_dataframe.BusExtraction(self.html_full_file_name)
        Bus_Table = Bus_extractor.BusData()
       

        # Crear reporte
        Create_Report = results_analysis.Report(Generation_Table, Load_Table)
        Report_Table = Create_Report.ResultsReport()
        # Guardar los DataFrames en la lista
        self.dfs =[Generation_Table,Load_Table,Bus_Table,Report_Table]



        #--------- save results
        self.Bus_Table= Bus_Table


        Report_Table['Value'] = Report_Table.apply(
            lambda row: int(row['Value']) if pd.notna(row['Value']) and row['Unit'] == '-' 
            else (f"{row['Value']:.0f}" if pd.notna(row['Value']) else row['Value']),
            axis=1
            )
        return Report_Table
        #self.show_dataframe(Report_Table,600,650)
    def get_BusData(self):
         Bus_extractor = html_to_dataframe.BusExtraction(self.html_full_file_name)
         Bus_Table = Bus_extractor.BusData()
         print(Bus_Table)
         #self.show_dataframe(Bus_Table,800,1000)  
         return Bus_Table
    def get_GenData(self):
          data_extractor = html_to_dataframe.DataExtractionOnlyHTML(self.html_full_file_name)
          Generation_Table, Load_Table = data_extractor.Data_Extraction(self.html_full_file_name) 
          #self.show_dataframe(Generation_Table,1350,1000)   
          return Generation_Table 
    def get_LoadData(self):
          data_extractor = html_to_dataframe.DataExtractionOnlyHTML(self.html_full_file_name)
          Generation_Table, Load_Table = data_extractor.Data_Extraction(self.html_full_file_name) 
          #self.show_dataframe(Load_Table,900,1000)  
          return Load_Table  
    """
    def get_LoadDataZone(self):
        zone_data_Loads = helper.Zone_data(excel_file_zone,"Cargas","Cargas")
        N = len(zone_data_Loads)         
        for i in range(0,N):
            c=-1
            for name1 in Load_Table["Name"]:   
                c=c+1
                if name1 == zone_data_Loads.iloc[i,0]:
                    Load_Table.at[c,"Página PowerFactory"] = zone_data_Loads.iloc[i,1]      
    """                          

    def get_excel(self):
         if self.dfs:
            ruta_guardado = ""
            try:
                with pd.ExcelWriter(ruta_guardado, engine='openpyxl') as writer:
                    def highlight_cells(val):
                            return "background-color: #FFCCCC" if val > 1.05 or val < 0.95 else "background-color: #CCFFCC"
                    self.dfs[0].to_excel(writer, sheet_name="DataGEN", index=False)
                    self.dfs[1].to_excel(writer, sheet_name="DataLoad", index=False)
                    self.dfs[2].style.applymap(highlight_cells, subset=["V [pu]"]).to_excel(writer, sheet_name="DataBus", index=False)
                    self.dfs[3].to_excel(writer, sheet_name="Report", index=False)
            except Exception as e:
                    print("holas")   
         
              
                 

#if __name__:
     #Results= ResultsTable()
