import math
from Autodesk.Revit.DB import  *

# STRINGS
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


# def get_panel_joints(grids, direction, panels_per_bay):
#   if len(grids) <= 1:
#     print('There are not enough grids to create panel joints')
#     return
#   if direction == 'horizontal':
#     grid_points = [grid.Curve.GetEndPoint(0).X for grid in grids]
#   if direction == 'vertical':
#     grid_points = [grid.Curve.GetEndPoint(0).Y for grid in grids]
#   panel_joints = grid_points[:]
#   distance_between_grids = grid_points[1] - grid_points[0]
#   distance_between_panels = distance_between_grids / panels_per_bay

#   for index, grid_point in enumerate(grid_points):
#     # Skip last grid
#     if index < len(grid_points) - 1:
#       # Add intermediate points
#       for i in range(panels_per_bay - 1):
#         intermediate_joint = grid_points[index] + distance_between_panels * (i+1)
#         panel_joints.append(intermediate_joint)
#   panel_joints.sort()
#   return panel_joints
