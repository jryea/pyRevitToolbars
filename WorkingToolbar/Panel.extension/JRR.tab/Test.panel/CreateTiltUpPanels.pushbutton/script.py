## Looking through the forum conversations, it looks like the split tool hasn't been exposed in the Revit API yet
## Will need to create a process that creates walls from either an already created wall (or lines)

# Curves have a CreateOffset method. May want to try to see if it works.
# Bound curve vs Unbound curve?

from Autodesk.Revit.DB import *
from pyrevit import revit, forms, script
import math

uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document
active_view = uidoc.ActiveView

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

def get_min_or_max_grid(vector, grids, min_or_max = 'min'):
  if abs(vector.X) > abs(vector.Y):
    grids_sorted = sort_grids_by_axis(grids, 'Y')
  else:
    grids_sorted = sort_grids_by_axis(grids, 'X')
  if min_or_max == 'min':
    return grids_sorted[0]
  else:
    return grids_sorted[-1]

curve_element_col = FilteredElementCollector(doc, active_view.Id) \
            .OfClass(CurveElement)
curve_element_list = list(curve_element_col)
line_list = [line.GeometryCurve for line in curve_element_list]
grid_col = FilteredElementCollector(doc, active_view.Id) \
            .OfClass(Grid)

grids_list = list(grid_col)

vertical_grids = [grid for grid in grids_list if round(get_line_vector(grid.Curve).X) == 0]
horizontal_grids = [grid for grid in grids_list if round(get_line_vector(grid.Curve).Y) == 0]

lines_left_to_right = [line for line in line_list if round((get_line_vector(line).X) == 1)]
lines_right_to_left = [line for line in line_list if round((get_line_vector(line).X) == -1)]
lines_bottom_to_top = [line for line in line_list if round((get_line_vector(line).Y) == 1)]
lines_top_to_bottom = [line for line in line_list if round((get_line_vector(line).Y) == -1)]

for line in lines_left_to_right:
  # setting minimum length to ignore during wall creating
  min_length = 1
  # setting 3/4" wall joints
  joint_width = 0.0625
  line_start_x = line.GetEndPoint(0).X
  line_end_x = line.GetEndPoint(1).X
  print('line start: ')
  print(line_start_x)
  print('line end: ')
  print(line_end_x)
  print('all grid x:')
  panel_ends = [line.GetEndPoint(0).X]
  for grid in vertical_grids:
    grid_x = grid.Curve.GetEndPoint(0).X
    if  grid_x > line_start_x and grid_x < line_end_x:
      panel_ends.append(grid_x)
  print(panel_ends)

# selected_base_level = forms.select_levels(multiple=False)
# selected_top_level = forms.select_levels(multiple=False)
# wall_height = selected_top_level.Elevation - selected_base_level.Elevation
# ## Offset base of wall 2 feet below level
# wall_offset = -2.0
# is_flipped = False
# is_structural = True

# wall_type_id = ElementId(1234631)

# with revit.Transaction('Create Walls'):
#   for line in line_list:
#     # cur_wall = Wall.Create(doc, line, selected_level.Id, True)
#     cur_wall = Wall.Create(doc, line, wall_type_id, selected_base_level.Id, wall_height, wall_offset, is_flipped, is_structural)

#     # Set the Wall location to interior face
#     # 1- Core Centerline
#     # 2- Finish Face: Exterior
#     # 3- Finish Face: Interior
#     # 4- Core Face: Exterior
#     # 5- Core Face: Interior
#     print(cur_wall.get_Parameter(BuiltInParameter.WALL_KEY_REF_PARAM))
#     cur_wall.get_Parameter(BuiltInParameter.WALL_KEY_REF_PARAM).Set(4)

#     # Collect Grids X
#     # Collect Grids Y
#     # Exclude min and max Grids
#     # Pair (1,0,0) line vectors with (0,1,0) grid vectors
















