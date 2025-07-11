import Model.ProjectCategory

class AddDefaultObjects:

    def __init__(self, add_project_categories):
        """select which objects to create - no often used, mostly a new testing approach"""
        self.add_project_categories()


    def add_project_categories(self):
        category1 = Model.project_category.ProjectCategory("Career", "Career related projects")
        category2 = Model.project_category.ProjectCategory("Guided", "projects that have a clear set of instructions designed to teach a specific skill")
        category3 = Model.project_category.ProjectCategory("Knowledge", "Projects that are predominantly book work")
        category4 = Model.project_category.ProjectCategory("Extension","projects that use skills gained in guided and knowledge projects, they typically do not have a set follow-me list of instructions, but rather have a list of end goals")
        category5 = Model.project_category.ProjectCategory("Capstone", "Projects that are predominantly book work")
        category6 = Model.project_category.ProjectCategory("Add-On", "Projects that are predominantly book work")
    
        category1.save()
        category2.save()
        category3.save()
        category4.save()
        category5.save()
        category6.save()    