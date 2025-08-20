
from tkinter import filedialog, messagebox
import file_manager 
import pathlib
import streamlit as st

class FileManager:
    def __init__(self, ecf_path=None, html_path=None):
        self.ecf_path = ecf_path
        self.html_path = html_path

    def promt_select_ecf_file(self):
        ecf_path = filedialog.askopenfilename(title="Select EMTP ECF file", filetypes=[("ECF Files", "*.ecf")])
        self.ecf_path = pathlib.Path(ecf_path) # It also changes the forward slashes to backslahes
        self.ecf_name = self.ecf_path.name
        self.ecf_stem = self.ecf_path.stem
        self.ecf_parent = self.ecf_path.parent
        return(self.find_html_results())

    def find_html_results(self):
        html_path = self.ecf_parent / (self.ecf_stem + "_pj") / (self.ecf_stem + "_lf.html")
        self.html_path = pathlib.Path(html_path)

        if not self.html_path.exists():
            messagebox.showinfo("HTML results file", "HTML file was not found.")
            
        else:
            print(self.html_path)
            return str(self.html_path)
      
    def find_html_results(self, ecf_file):
        """Busca el archivo HTML relacionado con el archivo ECF."""
        ecf_name = pathlib.Path(ecf_file.name).stem  # Obtener el nombre sin extensión
        html_path = pathlib.Path(ecf_name + "_pj") / (ecf_name + "_lf.html")  # Ruta esperada del HTML
        
        if html_path.exists():
            self.html_path = html_path
            return str(html_path)
        else:
            st.warning(f"No se encontró el archivo HTML esperado: {html_path}")
            return None
if __name__ == "__main__":

    file_manager = FileManager()
    if file_manager.ecf_path==None:
        file_manager.promt_select_ecf_file()
    
    file_manager.find_html_results()
