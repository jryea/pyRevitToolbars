from Autodesk.Revit.DB import *
from Autodesk.Revit.DB.Structure import StructuralType
from pyrevit import revit, forms, script

uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document
app = __revit__.Application
active_view = uidoc.ActiveView

selection = __revit__.ActiveUIDocument.Selection
selected_element_ids = selection.GetElementIds()
selected_elements = [doc.GetElement(element_id) for element_id in selected_element_ids]

all_linked_docs_col = FilteredElementCollector(doc).OfClass(RevitLinkInstance)
all_linked_docs_list = list(all_linked_docs_col)
all_linked_docs = [link.GetLinkDocument() for link in all_linked_docs_list]

all_walls = FilteredElementCollector(doc) \
            .OfCategory(BuiltInCategory.OST_Walls) \
            .WhereElementIsNotElementType()

wall_list = list(all_walls)

level = forms.select_levels(multiple= False)

def get_walls_from_selection(selection, kind = ''):
  #For specific kind of walls use 'Basic', 'Stacked', or 'Curtain'
  walls = [element for element in selection if isinstance(element, Wall)]
  specified_walls = [wall for wall in walls if str(wall.WallType.Kind) == kind]
  if kind == 'Basic' or kind == 'Stacked' or kind == 'Curtain':
    return specified_walls
  else:
    return walls

def get_walls_of_kind(walls, kind = ''):
  #For specific kind of walls use 'Basic', 'Stacked', or 'Curtain'
  walls_list = list(walls)
  specified_walls = [wall for wall in walls_list if str(wall.WallType.Kind) == kind]
  if kind == 'Basic' or kind == 'Stacked' or kind == 'Curtain':
    return specified_walls
  else:
    return walls

def get_wall_curve(wall):
  return wall.Location.Curve

# selected_walls = get_walls_from_selection(selected_elements)

# ASK USER FOR REVIT LINK
# Pyrevit wrapper class that defines the name property for display purposes
class DocTitle(forms.TemplateListItem):
  @property
  def name(self):
    return self.Title

link_options = [DocTitle(linked_doc) for linked_doc in all_linked_docs]

linked_doc = forms.SelectFromList.show(link_options, multiselect = False, title='Select architectural link')

arch_windows_col = FilteredElementCollector(linked_doc) \
                            .OfCategory(BuiltInCategory.OST_Windows) \
                            .WhereElementIsNotElementType()

arch_doors_col = FilteredElementCollector(linked_doc)\
                            .OfCategory(BuiltInCategory.OST_Doors) \
                            .WhereElementIsNotElementType()

curtain_walls_col = FilteredElementCollector(linked_doc)\
                .OfClass(Wall)\
                .WhereElementIsNotElementType()

arch_doors_list = list(arch_doors_col)
arch_windows_list = list(arch_windows_col)
curtain_walls_list = get_walls_of_kind(curtain_walls_col, 'Curtain')

arch_doors = [door for door in arch_doors_list if door.SuperComponent == None and door.get_BoundingBox(active_view)]
arch_windows =  [window for window in arch_windows_list if window.SuperComponent == None and window.get_BoundingBox(active_view)]
curtain_walls = [wall for wall in curtain_walls_list if wall]
all_arch_openings = arch_doors + arch_windows + curtain_walls

print('Linked model contains {} door instances'.format(len(arch_doors_list)))
print('Linked model contains {} root door instances'.format(len(arch_doors)))
print('Linked model contains {} window instances'.format(len(arch_windows_list)))
print('Linked model contains {} root window instances'.format(len(arch_windows)))
print('Linked model contains {} curtain walls'.format(len(curtain_walls)))

for element in selected_elements:
  if element.GetType() == Wall:
    wall_temp = element
  else:
    family_symbol = element.Symbol

# This grouping is only useful for indentifying how many bounding boxes are in the view
door_bounding_boxes = [door.get_BoundingBox(active_view) for door in arch_doors if door.get_BoundingBox(active_view)]
print('Linked model contains {} door bounding boxes'.format(len(door_bounding_boxes)))
window_bounding_boxes = [window.get_BoundingBox(active_view) for window in arch_windows if window.get_BoundingBox(active_view)]
print('Linked model contains {} window bounding boxes'.format(len(door_bounding_boxes)))
curtain_wall_bounding_boxes = [wall.get_BoundingBox(active_view) for wall in curtain_walls if wall.get_BoundingBox(active_view)]
print('Linked model contains {} curtain wall bounding boxes'.format(len(curtain_wall_bounding_boxes)))
all_arch_bounding_boxes = door_bounding_boxes + window_bounding_boxes + curtain_wall_bounding_boxes


door_host_curves = [door.Host.Location.Curve for door in arch_doors]
window_host_curves = [window.Host.Location.Curve for window in arch_windows]
curtain_wall_curves = [wall.Location.Curve for wall in curtain_walls]


# with revit.Transaction('test'):
#   # Find the linked architectural doors base points, heights, lengths and find host walls
#   arch_opening_transforms = []
#   for index, bounding_box in enumerate(all_arch_bounding_boxes):
#     door_host_curve = door.Host.Location.Curve
#     # Setting the base_point using the linked doors bounding box
#     x_location = (bounding_box.Min.X + bounding_box.Max.X)/2
#     y_location = (bounding_box.Min.Y + bounding_box.Max.Y)/2
#     z_location = bounding_box.Min.Z

#     # Using the host curve to:
#     # set the x or y base point location along the curve
#     # determine the created families length
#     length = 0
#     perp_line = None
#     # Search for vertical host walls
#     if round(door_host_curve.GetEndPoint(0).X, 5) == round(door_host_curve.GetEndPoint(1).X, 5):
#       x_location = door_host_curve.GetEndPoint(0).X
#       length = bounding_box.Max.Y - bounding_box.Min.Y
#       perp_line_start = XYZ(bounding_box.Min.X, y_location, z_location)
#       perp_line_end = XYZ(bounding_box.Max.X, y_location, z_location)
#       perp_line = Line.CreateBound(perp_line_start, perp_line_end)
#       ## Draw perp_line as a model line
#     # Search for horizontal host walls
#     if round(door_host_curve.GetEndPoint(0).Y, 5) == round(door_host_curve.GetEndPoint(1).Y, 5):
#       y_location = door_host_curve.GetEndPoint(0).Y
#       length = bounding_box.Max.X - bounding_box.Min.X
#       perp_line_start = XYZ(x_location, bounding_box.Min.Y, z_location)
#       perp_line_end = XYZ(x_location, bounding_box.Max.Y, z_location)
#       perp_line = Line.CreateBound(perp_line_start, perp_line_end)
#       cur_ref_plane = doc.Create.NewReferencePlane(perp_line_start, perp_line_end, XYZ(0,0,1), active_view)
#       ## Draw perp_line as a model line
#     base_point = XYZ(x_location, y_location, z_location)
#     height = bounding_box.Max.Z - bounding_box.Min.Z
#     arch_opening_transforms.append({'base_point': base_point, 'length': length, 'height': height, 'perp_line': perp_line})

#   for arch_opening in arch_opening_transforms:
#     wall_host = None
#     for wall in wall_list:
#       print(wall.Location.Curve.Intersect(arch_opening['perp_line']))
#       if wall.Location.Curve.Intersect(arch_opening['perp_line']) == SetComparisonResult.Overlap:
#         wall_host = wall

#     opening = doc.Create.NewFamilyInstance(door['base_point'], family_symbol, wall_host, level, StructuralType.NonStructural)
#     # opening = doc.Create.NewFamilyInstance(door['base_point'], family_symbol, StructuralType.NonStructural)
#     height_param = opening.LookupParameter('Height')
#     height_param.Set(door['height'])
#     length_param = opening.LookupParameter('Length')
#     length_param.Set(door['length'])










