# ProjectManager.py
import ttkbootstrap as tb
import Persistance
from GUI_components.UnitTab import UnitTab
from GUI_components.ObjectiveTab import ObjectiveTab

#from GUI_components.tabs.ConsumableTab import ConsumableTab
#from GUI_components.tabs.LocationTab import LocationTab

class ProjectManager:
    def __init__(self):
        Persistance.Base.metadata.create_all(Persistance.engine)
        self.root = tb.Window(themename="superhero")
        self.setup_window()
        self.create_notebook()
        self.create_tabs()

    def setup_window(self):
        self.root.title("Foundations of Manufacturing 2025-2026")
        self.root.geometry('1280x1024')

    def create_notebook(self):
        self.notebook = tb.Notebook(self.root, bootstyle="dark")
        self.notebook.grid(pady=20)

    def create_tabs(self):
        tabs = {
            "Units": UnitTab,
            "Objectives": ObjectiveTab,
            #"Consumables": ConsumableTab,
            #"Classroom Locations": LocationTab
        }

        for label, tab_class in tabs.items():
            tab = tab_class(self.notebook)
            self.notebook.add(tab, text=label)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":

    app = ProjectManager()
    app.run()
