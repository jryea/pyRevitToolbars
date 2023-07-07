from Autodesk.Revit.DB import *
from pyrevit import revit, forms, script
import clr
clr.AddReference("RevitAPI")
clr.AddReference("RevitAPIUI")

uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document
active_view = uidoc.ActiveView

def does_string_contain_word(full_string, word):
  full_split_string_list = []
  string_split_by_spaces = full_string.split()
  for string_a in string_split_by_spaces:
    string_dash_sublist = string_a.split('-')
    for string_b in string_dash_sublist:
      string_underscore_sublist = string_b.split('_')
      for string_c in string_underscore_sublist:
        full_split_string_list.append(string_c.upper())
  if word.upper() in full_split_string_list:
    return True
  else:
    return False

def get_line_vector(line):
  startpoint = line.GetEndPoint(0)
  endpoint = line.GetEndPoint(1)
  vector = endpoint - startpoint
  normalized_vector = vector.Normalize()
  return normalized_vector

def sort_grids_by_axis(grids, axis = 'X'):
  # Returns list
  sorted_grids = grids
  def sort_x(grid):
    return grid.Curve.GetEndPoint(0).X
  def sort_y(grid):
    return grid.Curve.GetEndPoint(0).Y
  if axis == 'X':
    sorted_grids.sort(key=sort_x)
  if axis == 'Y':
    sorted_grids.sort(key=sort_y)
  return sorted_grids

def find_ortho_grid_intersections(grids):
  horizontal_grids = sort_grids_by_axis(grids, 'X')
  horizontal_grid_curves = [grid.Curve for grid in horizontal_grids]
  vertical_grids = sort_grids_by_axis(grids, 'Y')
  vertical_grid_curves = [grid.Curve for grid in vertical_grids]
  grid_intersections = []
  for h_grid_curve in horizontal_grid_curves:
    for v_grid_curve in vertical_grid_curves:
      # print(h_grid_)
      if h_grid_curve.Intersect(v_grid_curve) == SetComparisonResult.Overlap:
        int_point = XYZ(h_grid_curve.GetEndPoint(0).X, v_grid_curve.GetEndPoint(0).Y,0)
        if str(int_point) not in str(grid_intersections):
          grid_intersections.append(int_point)
  return grid_intersections


def find_pts_inside_ortho_border(points, curve_loop):
  curves_list = list(curve_loop.GetEnumerator())
  curves_top = [curve for curve in curves_list if round(curve.GetEndPoint(0).Y, 5) == round(curve.GetEndPoint(1).Y, 5) and curve.GetEndPoint(0).X < curve.GetEndPoint(1).X ]
  curves_bottom = [curve for curve in curves_list if round(curve.GetEndPoint(0).Y, 5) == round(curve.GetEndPoint(1).Y, 5) and curve.GetEndPoint(0).X > curve.GetEndPoint(1).X ]
  curves_left = [curve for curve in curves_list if round(curve.GetEndPoint(0).X, 5) == round(curve.GetEndPoint(1).X, 5) and curve.GetEndPoint(0).Y < curve.GetEndPoint(1).Y ]
  curves_right = [curve for curve in curves_list if round(curve.GetEndPoint(0).X, 5) == round(curve.GetEndPoint(1).X, 5) and curve.GetEndPoint(0).Y > curve.GetEndPoint(1).Y ]
  points_inside_border = []
  for point in points:
    is_point_inside_top = False
    is_point_inside_bottom = False
    is_point_inside_left= False
    is_point_inside_right = False
    for curve_t in curves_top:
      curve_t_sp = curve_t.GetEndPoint(0)
      curve_t_ep = curve_t.GetEndPoint(1)
      if point.X > curve_t_sp.X and point.X < curve_t_ep.X and point.Y < curve_t_sp.Y:
        is_point_inside_top = True
    for curve_b in curves_bottom:
      curve_b_sp = curve_b.GetEndPoint(0)
      curve_b_ep = curve_b.GetEndPoint(1)
      if point.X < curve_b_sp.X and point.X > curve_b_ep.X and point.Y > curve_b_sp.Y:
        is_point_inside_bottom = True
    for curve_l in curves_left:
      curve_l_sp = curve_l.GetEndPoint(0)
      curve_l_ep = curve_l.GetEndPoint(1)
      if point.Y > curve_l_sp.Y and point.Y < curve_l_ep.Y and point.X > curve_l_sp.X:
        is_point_inside_left = True
    for curve_r in curves_right:
      curve_r_sp = curve_r.GetEndPoint(0)
      curve_r_ep = curve_r.GetEndPoint(1)
      if point.Y < curve_r_sp.Y and point.Y > curve_r_ep.Y and point.X < curve_r_sp.X:
        is_point_inside_right = True
    if is_point_inside_top == True and is_point_inside_bottom == True and is_point_inside_left == True and is_point_inside_right == True:
      points_inside_border.append(point)
  return points_inside_border

def get_symbol_by_name(symbol_name, all_symbols):
  symbol = None
  for e in all_symbols:
    if Element.Name.GetValue(e) == symbol_name:
      symbol = e
  if not symbol:
    print(symbol_name + ' not found')
  else:
    return symbol

def get_symbol_by_family_and_symbol_names(family_name, symbol_name, all_families, all_symbols):
  symbol = None
  family = None
  for f in all_families:
    if Element.Name.GetValue(f) == family_name:
      family = f
  for s in all_symbols:
    if Element.Name.GetValue(s) == symbol_name and Element.Name.GetValue(s.Family) == Element.Name.GetValue(family):
      symbol = s
  if not family:
    print(family_name + ' not found')
  if not symbol:
    print("type " + symbol_name + " not found in the " + family_name + " family")
  if family and symbol:
    return symbol

curve_element_col = FilteredElementCollector(doc, active_view.Id)\
                    .OfClass(CurveElement)
grid_col = FilteredElementCollector(doc, active_view.Id) \
            .OfClass(Grid)
family_col = FilteredElementCollector(doc)\
                     .OfClass(Family)
family_symbol_col = FilteredElementCollector(doc)\
                     .OfClass(FamilySymbol)
reference_plane_col = FilteredElementCollector(doc)\
                      .OfClass(ReferencePlane)

curve_element_list = list(curve_element_col)
grids_list = list(grid_col)
family_list = list(family_symbol_col)
family_symbol_list = list(family_symbol_col)
reference_plane_list = list(reference_plane_col)

roof_tos_ref_planes = [rp for rp in reference_plane_list if does_string_contain_word(rp.Name, 'TOS')]
curve_red_construction = [line for line in curve_element_list if str(line.LineStyle.Name) == 'IMEG_00-RED-CONSTRUCTION LINE']
floor_lines = [line.GeometryCurve for line in curve_red_construction]
grid_intersections = find_ortho_grid_intersections(grids_list)
# NEED TO CREATE CURVE LOOP FUNCTION THAT ORGANIZES A LIST OF CLOSED SEGMENTS INTO THE CORRECT SEQUENCE AND DIRECTION
curve_loop = CurveLoop()
# curve_loop.Append(floor_lines)
for line in floor_lines:
  curve_loop.Append(line)
points_inside_border = find_pts_inside_ortho_border(grid_intersections, curve_loop)

column_symbol = get_symbol_by_name('HSS10X10X1/2', family_symbol_list)
footing_symbol = get_symbol_by_name('8\'-0" x 8\'-0" x 1\'-0"', family_symbol_list)

column_tag_symbol = get_symbol_by_name('45', family_symbol_list)
footing_tag_symbol = get_symbol_by_name('Mark Only', family_symbol_list)



footing_tag_offset = 5

current_view_level_id = active_view.GenLevel.Id
horizontal_grids = sort_grids_by_axis(grids_list, 'X')


with revit.Transaction('Create Columns'):

  for grid_int in points_inside_border:
    cur_column = doc.Create.NewFamilyInstance(grid_int, column_symbol, active_view.GenLevel, Structure.StructuralType.Column)
    cur_column.get_Parameter(BuiltInParameter.SCHEDULE_BASE_LEVEL_OFFSET_PARAM).Set(-1.0)
    attachment_rp = None
    for rp in roof_tos_ref_planes:
      if grid_int.Y > rp.BubbleEnd.Y and grid_int.Y < rp.FreeEnd.Y:
        attachment_rp = rp
    ColumnAttachment.AddColumnAttachment(doc, cur_column, attachment_rp, 1, ColumnAttachmentCutStyle.None, ColumnAttachmentJustification.Midpoint, 0.0 )
    cur_footing = doc.Create.NewFamilyInstance(grid_int, footing_symbol, active_view.GenLevel, Structure.StructuralType.Footing)
    IndependentTag.Create(doc, column_tag_symbol.Id, active_view.Id, Reference(cur_column), False, TagOrientation.Horizontal, grid_int)
    footing_tag_pt = XYZ(grid_int.X, grid_int.Y - footing_tag_offset, grid_int.Z)
    IndependentTag.Create(doc, footing_tag_symbol.Id, active_view.Id, Reference(cur_footing), False, TagOrientation.Horizontal, footing_tag_pt)

  