from Autodesk.Revit.DB import *
from pyrevit import revit, forms, script

uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document

all_linked_docs_col = FilteredElementCollector(doc).OfClass(RevitLinkInstance)
all_linked_docs_list = list(all_linked_docs_col)
all_linked_docs = [link.GetLinkDocument() for link in all_linked_docs_list]

def get_walls_from_selection(selection, kind = ''):
  #For specific kind of walls use 'Basic', 'Stacked', or 'Curtain'
  walls = [element for element in selection if isinstance(element, Wall)]
  specified_walls = [wall for wall in walls if str(wall.WallType.Kind) == kind]
  if kind == 'Basic' or kind == 'Stacked' or kind == 'Curtain':
    return specified_walls
  else:
    return walls

## ASK USER FOR REVIT LINK
# Pyrevit wrapper class that defines the name property for display purposes
class DocTitle(forms.TemplateListItem):
  @property
  def name(self):
    return self.Title

link_options = [DocTitle(doc) for doc in all_linked_docs]

linked_doc = forms.SelectFromList.show(link_options, multiselect = False, title='Select architectural link')

print(linked_doc.Title)

## ASK USER FOR PLAN VIEW IN LINK
linked_views_col = FilteredElementCollector(linked_doc) \
                  .OfCategory(BuiltInCategory.OST_Views) \
                  .WhereElementIsNotElementType() \

linked_plan_views = [view for view in linked_views_col if view.ViewType == ViewType.FloorPlan]

# Pyrevit wrapper class that defines the name property for display purposes
class PlanViewTitle(forms.TemplateListItem):
  @property
  def name(self):
    return self.Name
  
plan_view_options = [PlanViewTitle(view) for view in linked_plan_views]

linked_plan_view = forms.SelectFromList.show(plan_view_options, multiselect = False, title='Select linked view')

all_walls_linked = FilteredElementCollector(linked_doc, linked_plan_view.Id) \
                        .OfClass(Wall)

all_basic_walls_linked = get_walls_from_selection(all_walls_linked, 'Basic')

all_wall_types_linked = [doc.GetElement(wall.GetTypeId()) for wall in list(all_basic_walls_linked)]

all_wall_types_linked_unique = [all_wall_types_linked[0]]
for wall in all_wall_types_linked:
  is_wall_unique = True
  for unique_wall in all_wall_types_linked_unique:
    if Element.Name.__get__(wall) == Element.Name.__get__(unique_wall):
      is_wall_unique = False
  if is_wall_unique == True:
    all_wall_types_linked_unique.append(wall)

for wall_type in all_wall_types_linked_unique:
  print(Element.Name.__get__(wall_type))


## ASK USER FOR Exterior Wall Types
# Pyrevit wrapper class that defines the name property for display purposes
# pyRevit is really not liking this return on the class
class WallTypeNames(forms.TemplateListItem):
  @property
  def name(self):
    return Element.Name.__get__(self)

wall_type_options = [WallTypeNames(wall_type) for wall_type in all_wall_types_linked_unique]

wall_types_to_copy = forms.SelectFromList.show(wall_type_options, multiselect = True, title='Linked wall types to copy')