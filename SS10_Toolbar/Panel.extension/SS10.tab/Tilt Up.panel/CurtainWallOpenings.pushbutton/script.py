## NEED TO CREATE IN FLOOR PLAN VIEW

from Autodesk.Revit.DB import *
from Autodesk.Revit.DB.Structure import StructuralType
from pyrevit import revit, forms, script
import JR_utilities as utils
from JR_utilities import elements, geometry

uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document
app = __revit__.Application
active_view = uidoc.ActiveView

def get_cw_perp_line(curtain_wall):
  length = 0
  try:
    cw_curve = curtain_wall.Location.Curve
  except:
    print('Curtain Wall curve not found')
  else:
    perp_line = None
    perp_line_ext = 2
    cwc_start = cw_curve.GetEndPoint(0)
    cwc_end = cw_curve.GetEndPoint(1)
    # Search for vertical host walls
    if round(cwc_start.X, 3) == round(cwc_end.X, 3):
      x_pt = cwc_start.X
      y_pt = (cwc_start.Y + cwc_end.Y) / 2
      z_pt = cwc_start.Z
      perp_line_start = XYZ(x_pt - perp_line_ext, y_pt, z_pt)
      perp_line_end = XYZ(x_pt + perp_line_ext, y_pt, z_pt)
    # Search for horizontal host walls
    if round(cwc_start.Y, 3) == round(cwc_end.Y, 3):
      x_pt = (cwc_start.X + cwc_end.X) / 2
      y_pt = cwc_start.Y
      z_pt = cwc_start.Z
      perp_line_start = XYZ(x_pt, y_pt - perp_line_ext, z_pt)
      perp_line_end = XYZ(x_pt, y_pt + perp_line_ext, z_pt)
    perp_line = Line.CreateBound(perp_line_start, perp_line_end)
    return perp_line


def find_local_wall_panel(perp_line, panel_list):
  if perp_line and panel_list:
    for panel in panel_list:
      panel_line = panel.Location.Curve
      if perp_line.Intersect(panel_line) == SetComparisonResult.Overlap:
        return panel
    print('Panel that intersects elements perpendicular line not found')
  else:
    if not perp_line:
      print('Perpendicular line not found!')
    if not panel_list:
      print('wall_list not found')

def get_curtain_wall_transform_info(doc, active_view, curtain_wall):
  level = doc.GetElement(curtain_wall.LevelId)
  level_elev = level.Elevation
  wall_base_offset_param = curtain_wall.get_Parameter(BuiltInParameter.WALL_BASE_OFFSET)
  wall_base_offset = wall_base_offset_param.AsDouble()
  # bounding_box = curtain_wall.get_BoundingBox(active_view)
  location_curve = curtain_wall.Location.Curve
  location_sp = location_curve.GetEndPoint(0)
  location_ep = location_curve.GetEndPoint(1)
  min_x = bounding_box.Min.X
  max_x = bounding_box.Max.X
  min_y = bounding_box.Min.Y
  max_y = bounding_box.Max.Y
  min_z = bounding_box.Min.Z
  max_z = bounding_box.Max.Z
  if abs(geometry.get_line_vector(location_curve).X) == 1:
    base_pt = XYZ((location_sp.X + location_ep.X)/2, location_sp.Y, location_sp.Z + wall_base_offset)
  elif abs(geometry.get_line_vector(location_curve).Y) == 1:
    base_pt = XYZ(location_sp.X, (location_sp.Y + location_ep.Y)/2, location_sp.Z + wall_base_offset)
  else:
    print("Can't find the basepoint for an angled wall")
  length = location_curve.ApproximateLength
  height = max_z - min_z
  return {"base_pt": base_pt, "length": length, "height": height}

linked_docs_col = FilteredElementCollector(doc).OfClass(RevitLinkInstance)
wall_col = FilteredElementCollector(doc) \
            .OfCategory(BuiltInCategory.OST_Walls) \
            .WhereElementIsNotElementType()

all_linked_docs_list = list(linked_docs_col)
wall_list = list(wall_col)
all_linked_docs = [link.GetLinkDocument() for link in all_linked_docs_list]

# level = forms.select_levels(multiple= False)
level = active_view.GenLevel

# ASK USER FOR REVIT LINK
# Pyrevit wrapper class that defines the name property for display purposes
class DocTitle(forms.TemplateListItem):
  @property
  def name(self):
    return self.Title

link_options = [DocTitle(linked_doc) for linked_doc in all_linked_docs]

# linked_doc = forms.SelectFromList.show(link_options, multiselect = False, title='Select architectural link')

curtain_walls_col = FilteredElementCollector(linked_doc)\
                .OfClass(Wall)\
                .WhereElementIsNotElementType()
symbol_col = FilteredElementCollector(doc)\
              .OfClass(FamilySymbol)

curtain_walls_list = elements.get_walls_of_kind(curtain_walls_col, 'Curtain')
symbol_list = list(symbol_col)

test_perp_line =  get_cw_perp_line(curtain_walls_list[0])
wall_panel = find_local_wall_panel(test_perp_line, wall_list)

box_symbol = elements.get_symbol_by_name('Box', symbol_list)
opening_symbol = elements.get_symbol_by_name('Tiltup Panel Opening', symbol_list)

# This grouping is only useful for indentifying how many bounding boxes are in the view
curtain_wall_bounding_boxes = [wall.get_BoundingBox(active_view) for wall in curtain_walls_list if wall.get_BoundingBox(active_view)]
curtain_wall_curves = [wall.Location.Curve for wall in curtain_walls_list]

with revit.Transaction('Curtain Wall Openings'):
  for wall in curtain_walls_list:
    perp_line = get_cw_perp_line(wall)
    wall_panel = find_local_wall_panel(perp_line, wall_list)
    base_pt = get_curtain_wall_transform_info(linked_doc, active_view, wall)['base_pt']
    length = get_curtain_wall_transform_info(linked_doc, active_view, wall)['length']
    height = get_curtain_wall_transform_info(linked_doc, active_view, wall)['height']
    # opening = doc.Create.NewFamilyInstance(base_pt, box_symbol, StructuralType.NonStructural)
    opening = doc.Create.NewFamilyInstance(base_pt, opening_symbol, wall_panel, level, StructuralType.NonStructural)
    height_param = opening.LookupParameter('Height')
    height_param.Set(height)
    length_param = opening.LookupParameter('Length')
    length_param.Set(length)
    # width_param = opening.LookupParameter('Width')
    # width_param.Set(depth)











