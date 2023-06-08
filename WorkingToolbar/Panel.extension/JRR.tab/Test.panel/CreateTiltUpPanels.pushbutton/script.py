# Curves have a CreateOffset method. May want to try to see if it works.
# Bound curve vs Unbound curve?

# Creating wall segments that are too small where start/end of line segment lands between grids. Instead of creating intermediate panels split between points that include line ends,  panel intersections should be created half way between grid lines

from Autodesk.Revit.DB import *
from pyrevit import revit, forms, script

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



selected_base_level = forms.select_levels(multiple=False)
selected_top_level = forms.select_levels(multiple=False)
wall_height = selected_top_level.Elevation - selected_base_level.Elevation
## Offset base of wall 2 feet below level
wall_offset = -2.0
is_flipped = False
is_structural = True

wall_type_id = ElementId(1234631)

with revit.Transaction('Create Walls'):
  for line in lines_left_to_right:
    # setting minimum length to ignore during wall creating
    min_wall_length = 5
    # setting 3/4" wall joints
    joint_width = 0.0625
    joint_offset = 0.0625 / 2
    line_start = line.GetEndPoint(0).X
    line_end = line.GetEndPoint(1).X
    panel_intersections = [line_start]
    for grid in vertical_grids:
      #Check grids position along line
      grid_intersection = grid.Curve.GetEndPoint(0).X
      # Check to see if grid falls within range of line segment
      if  grid_intersection > line_start and grid_intersection < line_end:
        # add grid intersections and intermediate panels (assuming 2 panels between grids)
        intermediate_panel = (panel_intersections[-1] + grid_intersection) /2
        panel_intersections.append(intermediate_panel)
        panel_intersections.append(grid_intersection)
    intermediate_panel = (panel_intersections[-1] + line_end) /2
    panel_intersections.append(intermediate_panel)
    panel_intersections.append(line_end)
    # create wall ends with wall joints. Ignore first and last points
    panel_ends = []
    i = 0
    for intersection in panel_intersections:
      if i > 0 and i < len(panel_intersections) - 1:
        panel_ends.append(intersection - joint_offset)
        panel_ends.append(intersection + joint_offset)
      else:
        panel_ends.append(intersection)
      i+= 1
    # Create Walls
    i = 0
    while i < len(panel_ends):
      startpoint = XYZ(panel_ends[i], line.GetEndPoint(0).Y, line.GetEndPoint(0).Z)
      endpoint = XYZ(panel_ends[i + 1], line.GetEndPoint(0).Y, line.GetEndPoint(0).Z)
      if panel_ends[i+1] - panel_ends[i] > min_wall_length:
        line = Line.CreateBound(startpoint, endpoint)
        print(line)
        cur_wall = Wall.Create(doc, line, wall_type_id, selected_base_level.Id, wall_height, wall_offset, is_flipped, is_structural)
        print(cur_wall)
        WallUtils.DisallowWallJoinAtEnd(cur_wall, 0)
        WallUtils.DisallowWallJoinAtEnd(cur_wall, 1)
        # Set the Wall location to exterior face
        # 1- Core Centerline
        # 2- Finish Face: Exterior
        # 3- Finish Face: Interior
        # 4- Core Face: Exterior
        # 5- Core Face: Interior
        cur_wall.get_Parameter(BuiltInParameter.WALL_KEY_REF_PARAM).Set(4)
      i += 2















