from Autodesk.Revit.DB import *
from pyrevit import revit, forms, script

uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document
active_view = uidoc.ActiveView

selection = __revit__.ActiveUIDocument.Selection
selected_element_ids = selection.GetElementIds()
selected_elements = [doc.GetElement(element_id) for element_id in selected_element_ids]

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

def get_wall_curve(wall):
  return wall.Location.Curve

selected_walls = get_walls_from_selection(selected_elements)

## ASK USER FOR REVIT LINK
# Pyrevit wrapper class that defines the name property for display purposes
class DocTitle(forms.TemplateListItem):
  @property
  def name(self):
    return self.Title

link_options = [DocTitle(doc) for doc in all_linked_docs]

linked_doc = forms.SelectFromList.show(link_options, multiselect = False, title='Select architectural link')

arch_windows_col = FilteredElementCollector(linked_doc) \
                            .OfCategory(BuiltInCategory.OST_Windows) \
                            .WhereElementIsNotElementType()

arch_doors_col = FilteredElementCollector(linked_doc)\
                            .OfCategory(BuiltInCategory.OST_Doors) \
                            .WhereElementIsNotElementType()

arch_doors = list(arch_doors_col)

family_symbol = selected_elements[0].Symbol
  
# family_symbol = doc.GetElement(ElementId(1969540))

# print(family_symbol)

bounding_boxes = [door.get_BoundingBox(active_view) for door in arch_doors if door.get_BoundingBox(active_view)]

with revit.Transaction('test'):
  for bb in bounding_boxes:
    base_point = XYZ((bb.Min.X + bb.Max.X)/2, (bb.Min.Y + bb.Max.Z)/2, bb.Min.Z )
    height = bb.Max.Z - bb.Min.Z
    length = bb.Max.X - bb.Min.X
    width = bb.Max.Y - bb.Min.Y
    height = bb.Max.Z - bb.Min.Z
    test_box = doc.Create.NewFamilyInstance(base_point, family_symbol, active_view)
    # print(bb)
    # print('Min of bounding box:')
    # print(bb.Min)
    # print('Max of bounding box:')
    # print(bb.Max)










