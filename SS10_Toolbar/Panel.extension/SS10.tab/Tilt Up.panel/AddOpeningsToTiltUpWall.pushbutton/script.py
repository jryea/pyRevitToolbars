from Autodesk.Revit.DB import *
from Autodesk.Revit.DB.Structure import StructuralType
from pyrevit import revit, forms, script
import JR_utilities as utils
from JR_utilities import elements, geometry

uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document
app = __revit__.Application
active_view = uidoc.ActiveView

def draw_bounding_box_rect(bounding_box):
  bb_min = bounding_box.Min
  bb_max = bounding_box.Max
  tl_pt = XYZ(bb_min.X, bb_max.Y, 0)
  tr_pt = XYZ(bb_max.X, bb_max.Y, 0)
  br_pt = XYZ(bb_max.X, bb_min.Y, 0)
  bl_pt = XYZ(bb_min.X, bb_min.Y, 0)
  top_line = Line.CreateBound(tl_pt, tr_pt)
  right_line = Line.CreateBound(tr_pt, br_pt)
  bottom_line = Line.CreateBound(br_pt, bl_pt)
  left_line = Line.CreateBound(bl_pt, tl_pt)
  doc.Create.NewDetailCurve(active_view, top_line)
  doc.Create.NewDetailCurve(active_view, right_line)
  doc.Create.NewDetailCurve(active_view, bottom_line)
  doc.Create.NewDetailCurve(active_view, left_line)

def get_arch_door_bounding_box(door):
  if door.get_BoundingBox(active_view):
    # Find nested garage doors
    if door.Symbol.FamilyName == 'Dr_OH':
      subcomponent_ids = list(door.GetSubComponentIds())
      for subcomponent_id in subcomponent_ids:
        subcomponent = linked_doc.GetElement(subcomponent_id)
        if subcomponent:
          if subcomponent.Symbol.FamilyName == 'Leaf_OHS':
            return subcomponent.get_BoundingBox(active_view)
    else:
      return door.get_BoundingBox(active_view)

selection = __revit__.ActiveUIDocument.Selection
selected_element_ids = selection.GetElementIds()
selected_elements = [doc.GetElement(element_id) for element_id in selected_element_ids]

linked_docs_col = FilteredElementCollector(doc).OfClass(RevitLinkInstance)
wall_col = FilteredElementCollector(doc) \
            .OfCategory(BuiltInCategory.OST_Walls) \
            .WhereElementIsNotElementType()

all_linked_docs_list = list(linked_docs_col)
wall_list = list(wall_col)
all_linked_docs = [link.GetLinkDocument() for link in all_linked_docs_list]

level = forms.select_levels(multiple= False)

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
symbol_col = FilteredElementCollector(doc)\
              .OfClass(FamilySymbol)

arch_doors_list = list(arch_doors_col)
arch_windows_list = list(arch_windows_col)
curtain_walls_list = elements.get_walls_of_kind(curtain_walls_col, 'Curtain')
symbol_list = list(symbol_col)

arch_doors = [door for door in arch_doors_list if door.SuperComponent == None and door.get_BoundingBox(active_view)]
arch_windows =  [window for window in arch_windows_list if window.SuperComponent == None and window.get_BoundingBox(active_view)]
curtain_walls = [wall for wall in curtain_walls_list if wall]
# all_arch_openings = arch_doors + arch_windows + curtain_walls

family_symbol = elements.get_symbol_by_name('Tiltup Panel Opening', symbol_list)

# This grouping is only useful for indentifying how many bounding boxes are in the view
door_bounding_boxes = [door.get_BoundingBox(active_view) for door in arch_doors if door.get_BoundingBox(active_view)]
window_bounding_boxes = [window.get_BoundingBox(active_view) for window in arch_windows if window.get_BoundingBox(active_view)]
curtain_wall_bounding_boxes = [wall.get_BoundingBox(active_view) for wall in curtain_walls if wall.get_BoundingBox(active_view)]
all_arch_bounding_boxes = door_bounding_boxes + window_bounding_boxes + curtain_wall_bounding_boxes

door_host_curves = [door.Host.Location.Curve for door in arch_doors]
window_host_curves = [window.Host.Location.Curve for window in arch_windows]
curtain_wall_curves = [wall.Location.Curve for wall in curtain_walls]

with revit.Transaction('test'):
  # Find the linked architectural doors base points, heights, lengths and find host walls
  arch_door_transforms = []
  for door in arch_doors:
    bounding_box = get_arch_door_bounding_box(door)
    # draw_bounding_box_rect(bounding_box)
    try:
      door_host_curve = door.Host.Location.Curve
    except:
      print('Host location curve not found')
    else:
      # Setting the base_point using the linked doors bounding box
      x_location = (bounding_box.Min.X + bounding_box.Max.X)/2
      y_location = (bounding_box.Min.Y + bounding_box.Max.Y)/2
      z_location = bounding_box.Min.Z

      # Using the host curve to:
      # set the x or y base point location along the curve
      # determine the created families length
      length = 0
      perp_line = None
      perp_line_ext = 1
      # Search for vertical host walls
      if round(door_host_curve.GetEndPoint(0).X, 3) == round(door_host_curve.GetEndPoint(1).X, 3):
        x_location = door_host_curve.GetEndPoint(0).X
        length = bounding_box.Max.Y - bounding_box.Min.Y
        perp_line_start = XYZ(bounding_box.Min.X - perp_line_ext, y_location, z_location)
        perp_line_end = XYZ(bounding_box.Max.X + perp_line_ext, y_location, z_location)
        perp_line = Line.CreateBound(perp_line_start, perp_line_end)
      # Search for horizontal host walls
      if round(door_host_curve.GetEndPoint(0).Y, 5) == round(door_host_curve.GetEndPoint(1).Y, 5):
        y_location = door_host_curve.GetEndPoint(0).Y
        length = bounding_box.Max.X - bounding_box.Min.X
        perp_line_start = XYZ(x_location, bounding_box.Min.Y - perp_line_ext, z_location)
        perp_line_end = XYZ(x_location, bounding_box.Max.Y + perp_line_ext, z_location)
        perp_line = Line.CreateBound(perp_line_start, perp_line_end)
        cur_ref_plane = doc.Create.NewReferencePlane(perp_line_start, perp_line_end, XYZ(0,0,1), active_view)

      base_point = geometry.get_xy_intersection(perp_line, door_host_curve)
      height = bounding_box.Max.Z - bounding_box.Min.Z
      arch_door_transforms.append({'base_point': base_point, 'length': length, 'height': height, 'perp_line': perp_line})

  for transform in arch_door_transforms:
    wall_host = None
    for wall in wall_list:
      if wall.Location.Curve.Intersect(transform['perp_line']) == SetComparisonResult.Overlap:
        wall_host = wall
    opening = doc.Create.NewFamilyInstance(transform['base_point'], family_symbol, wall_host, level, StructuralType.NonStructural)
    height_param = opening.LookupParameter('Height')
    height_param.Set(transform['height'])
    length_param = opening.LookupParameter('Length')
    length_param.Set(transform['length'])










