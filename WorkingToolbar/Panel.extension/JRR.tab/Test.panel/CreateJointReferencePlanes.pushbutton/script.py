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

# returns a list of XYZ x or y values depending on the input direction
# includes all of the x(or y) points along the grid and intermediate points (depending on panels)
def create_joint_reference_planes(grids, direction, num_joints_between_grids):
  if len(grids) <= 1:
    print('There are not enough grids to create reference planes')
    return
  if direction == 'horizontal':
    joint_x_list = []
    joint_y_start = grids[0].Curve.GetEndPoint(0).Y
    joint_y_end = grids[0].Curve.GetEndPoint(1).Y
    # Loop through all grids, but last one
    for index in range(0, len(grids) - 1):
      first_grid_x = grids[index].Curve.GetEndPoint(0).X
      next_grid_x = grids[index + 1].Curve.GetEndPoint(0).X
      distance_between_joints = (next_grid_x - first_grid_x) / num_joints_between_grids
      # create joint X values between grids:
      for i in range(0 , num_joints_between_grids - 1):
        joint_x_list.append(first_grid_x + distance_between_joints * (i+1))
    for index, joint_x in enumerate(joint_x_list):
      cur_ref_plane = doc.Create.NewReferencePlane(XYZ(joint_x, joint_y_start, 100), XYZ(joint_x, joint_y_end, 100), XYZ(0,0,1), active_view)
      cur_ref_plane.Name = 'jointX_{}'.format(index+1)
  if direction == 'vertical':
    joint_y_list = []
    joint_x_start = grids[0].Curve.GetEndPoint(0).X
    joint_x_end = grids[0].Curve.GetEndPoint(1).X
    # Loop through all grids, but last one
    for index in range(0, len(grids) - 1):
      first_grid_y = grids[index].Curve.GetEndPoint(0).Y
      next_grid_y = grids[index + 1].Curve.GetEndPoint(0).Y
      distance_between_joints = (next_grid_y - first_grid_y) / num_joints_between_grids
      # create joint X values between grids:
      for i in range(0 , num_joints_between_grids - 1):
        joint_y_list.append(first_grid_y + distance_between_joints * (i+1))
    for index, joint_y in enumerate(joint_y_list):
      cur_ref_plane = doc.Create.NewReferencePlane(XYZ(joint_x_start, joint_y, 100), XYZ(joint_x_end, joint_y, 100), XYZ(0,0,1), active_view)
      cur_ref_plane.Name = 'jointY_{}'.format(index+1)

grid_col = FilteredElementCollector(doc, active_view.Id) \
            .OfClass(Grid)
grids_list = list(grid_col)
vertical_grids = [grid for grid in grids_list if int(get_line_vector(grid.Curve).X) == 0]
vertical_grids = sort_grids_by_axis(vertical_grids,'X')
horizontal_grids = [grid for grid in grids_list if int(get_line_vector(grid.Curve).Y) == 0]
horizontal_grids = sort_grids_by_axis(horizontal_grids, 'Y')

with revit.Transaction('Create Walls'):
  create_joint_reference_planes(vertical_grids, 'horizontal', 2)
  create_joint_reference_planes(horizontal_grids, 'vertical', 2)
  














