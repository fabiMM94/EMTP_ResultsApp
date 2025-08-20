
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
