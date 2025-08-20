#from tracemalloc import _TraceTupleT
import pandas as pd
import numpy as np
import math as m

class Report:
    def __init__(self,DataGen,DataLoad):
        self.DataGen = DataGen
        self.DataLoad = DataLoad

    def ResultsReport(self):
        Report = pd.DataFrame(columns=['Item', 'Value',"Unit"])
        P_IBR_PV = round(self.DataGen[self.DataGen["tipo"] == "PFV"]["P [MW]"].sum(),1)
        P_IBR_WF = round(self.DataGen[self.DataGen["tipo"] == "PE"]["P [MW]"].sum(),1)
        P_IBR_BESS_GEN = 0
        P_PMGD = round(self.DataGen[self.DataGen["tipo"] == "PMGD"]["P [MW]"].sum(),1)
        Total_IBR_GEN = P_IBR_PV+P_IBR_WF+P_IBR_BESS_GEN+P_PMGD

        P_Gen_SG = round(self.DataGen[self.DataGen["tipo"] == "SG"]["P [MW]"].sum(),1)
        Total_GEN = Total_IBR_GEN + P_Gen_SG

        P_Load = round(self.DataLoad["P [MW]"].sum(),1) # Source reference, i.e., positive when generating
        P_BESS = abs(round(self.DataGen[self.DataGen["tipo"] == "BESS"]["P [MW]"].sum(),1))
        P_BATSINC = abs(round(self.DataGen[self.DataGen["tipo"] == "BATSINC"]["P [MW]"].sum(),1))

        Total_consumption = P_Load + P_BESS+ P_BATSINC
        
        P_HVDC = round(self.DataGen[self.DataGen["tipo"] == "HVDC"]["P [MW]"].sum(),1)
        P_CS   = round(self.DataGen[self.DataGen["tipo"] == "CS"]["P [MW]"].sum(),1)
        Loss = Total_GEN - Total_consumption+ P_HVDC+ P_CS

        #---------------------------------------------------------------------------------
        #-- Porcentajes
        p_IBR_PV = round(100*P_IBR_PV/Total_GEN,1)
        p_IBR_WF = round(100*P_IBR_WF/Total_GEN,1)
        p_IBR_BESS_GEN = round(100*P_IBR_BESS_GEN/Total_GEN,1)
        p_PMGD = round( 100*P_PMGD/Total_GEN,1)

        p_IBR_GEN = round( 100*Total_IBR_GEN/Total_GEN ,1)
        p_Gen_SG = round( 100*P_Gen_SG/Total_GEN ,1 )
        


        #----------------------------------------------------------------------------
        # Numero de generadores 
        N_PV = int(self.DataGen["tipo"].str.count("PFV").sum() )
        N_WP=   self.DataGen["tipo"].str.count("PE").sum() 
        N_SG =  self.DataGen["tipo"].str.count("SG").sum() 
        N_PMGD =  self.DataGen["tipo"].str.count("PMGD").sum() 
        N_BESS =  self.DataGen["tipo"].str.count("BESS").sum() 
        N_BATSINC= self.DataGen["tipo"].str.count("BATSINC").sum()
        N_CS =  self.DataGen["tipo"].str.count("CS").sum()
        #-----------------------------------------------------------------------------
        #-- Agrego a dataframe


        Report = {
                "Item": ['Total IBR PV Generation', 'Total IBR WF Generation', 'Total IBR Batteries Generation',
                        'Total Distributed Generation (PMGD)','Total IBR Generation', 'Total Synchronous Generation',
                         'Total Generation','Total Load (Passive)', 'Total IBR Batteries Consumption', "Total Synchronous Batteries"," Total CS Consumption",
                          'Total Consumption (Load+Batteries)','Total Losses',
                              None, None,
                              'IBR PV Generation Participation','IBR WF Generation Participation',
                              'IBR Batteries Generation Part.','Distributed Generation (PMGD) Part.',
                              'IBR Generation Participation','Synchronous Generation Participation',
                              None, None,
                              'Number of photovoltaic generators', 'Number of wind generators', 'Number of synchronous generators',
                                'Number of PMGDs', 'Numner of BESS',"Number of synchronous batteries", "Number of synchronous Condenser"
                              ],

                "Value": [P_IBR_PV, P_IBR_WF, P_IBR_BESS_GEN, P_PMGD, Total_IBR_GEN, 
                         P_Gen_SG,  Total_GEN,P_Load, P_BESS, P_BATSINC,P_CS, Total_consumption, Loss,
                          None, None,
                         p_IBR_PV,p_IBR_WF,p_IBR_BESS_GEN,p_PMGD,p_IBR_GEN,p_Gen_SG,
                          None, None,
                          N_PV, N_WP, N_SG, N_PMGD, N_BESS, N_BATSINC, N_CS ],

                "Unit": ['MW','MW','MW','MW','MW','MW','MW','MW','MW','MW','MW','MW','MW',
                         None,None,
                         '%','%','%','%','%','%',
                         None, None,
                         '-', '-', '-', '-', '-', '-', '-']
                }
        Report = pd.DataFrame(Report)        
 
        return Report


        """
        P_Gen =  round(self.DataGen["P [MW]"].sum(),1)
        P_Load = round(self.DataLoad["P [MW]"].sum(),1)

        P_Gen_PFV = round(self.DataGen[self.DataGen["tipo"] == "PFV"]["P [MW]"].sum(),1)
        P_Gen_PE = round(self.DataGen[self.DataGen["tipo"] == "PE"]["P [MW]"].sum(),1)
        P_PMGD = round(self.DataGen[self.DataGen["tipo"] == "PMGD"]["P [MW]"].sum(),1)
        P_IBR = round(P_Gen_PFV+P_Gen_PE+P_PMGD,2)
        P_Gen_SG =round(self.DataGen[self.DataGen["tipo"] == "SG"]["P [MW]"].sum(),1)
        P_BESS = round(self.DataGen[self.DataGen["tipo"] == "BESS"]["P [MW]"].sum(),1)
       
        Total_GEN = P_IBR+P_Gen_SG

        porcent_PFV = 100*P_Gen_PFV/Total_GEN
        porcent_PE = 100*P_Gen_PE/Total_GEN
        porcent_PMGD =100*P_PMGD/Total_GEN
        porcent_BESS = round(100*P_BESS/Total_GEN,1)
        porcent_Load= 100*P_Load/Total_GEN
    

        porcent_GFL = round(porcent_PFV+ porcent_PE+porcent_PMGD,1)
        porcent_SG = round(100*P_Gen_SG/Total_GEN,1)

        #porcent_error= 100- porcent_GFL-porcent_SG- porcent_BESS -P_Load/Total_GEN
        porcent_error = round(100-porcent_Load+porcent_BESS,1)
        
        
        
        #Report.append({'Name': 'Total P Gen', 'P [MW]':P_Gen}, ignore_index=True)
        #Report.append({'Name': 'Total P Load', 'P [MW]':P_Load}, ignore_index=True)
        
        # Crear filas para agregar al DataFrame
        total_gen = pd.DataFrame([{'Name': 'Total Generation', 'P [MW]': P_Gen}])
        total_load = pd.DataFrame([{'Name': 'Total Load', 'P [MW]': P_Load}])
        total_gen_PFV = pd.DataFrame([{'Name': 'Total PFV Generation', 'P [MW]': P_Gen_PFV}])
        total_gen_PE = pd.DataFrame([{'Name': 'Total PE Generation', 'P [MW]': P_Gen_PE}])
        total_gen_SG = pd.DataFrame([{'Name': 'Total SG Generation', 'P [MW]': P_Gen_SG}])
        total_BESS = pd.DataFrame([{'Name': 'Total BESS', 'P [MW]': P_BESS}])
        total_PMGD = pd.DataFrame([{'Name': 'Total PMGD', 'P [MW]': P_PMGD}])
        total_IBR = pd.DataFrame([{'Name': 'Total IBR GEN', 'P [MW]': P_IBR}])

     

        Report2 = pd.DataFrame(columns=['Variable', 'Porcent %'])
        pIBR = pd.DataFrame([{'Variable': 'IBR Generation %', 'Porcent %': porcent_GFL}])
        pIBR_BESS = pd.DataFrame([{'Variable': 'IBR Bateries %', 'Porcent %': porcent_BESS}])
        pSG = pd.DataFrame([{'Variable': 'SG %', 'Porcent %': porcent_SG}])
        pError =  pd.DataFrame([{'Variable': 'Error %', 'Porcent %': porcent_error}])
      


        # Usar pd.concat para agregar las filas al DataFrame
        Report = pd.concat([Report, total_gen, total_load,total_gen_PFV,total_gen_PE,total_gen_SG,total_PMGD,total_BESS,total_IBR], ignore_index=True)
        Report2 = pd.concat([Report2,pIBR,pIBR_BESS,pSG,pError], ignore_index=True)
        
        ReportFinal=pd.concat([Report,Report2], axis=1) 
        """


      
