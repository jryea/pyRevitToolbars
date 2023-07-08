from Autodesk.Revit.DB import *

# GRIDs

def get_grid_pts_xy(grids, direction = 'X'):
  if direction == 'X':
    grid_points = [grid.Curve.GetEndPoint(0).X for grid in grids]
  if direction == 'Y':
    grid_points = [grid.Curve.GetEndPoint(0).Y for grid in grids]
  return grid_points

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

def sort_grids_by_vector(grids_list):
  # Returns dictionary with keys set to vector values
  grids_sorted = {}
  for grid in grids_list:
    key = str(get_grid_vector(grid))
    values = grids_sorted.get(key)
    if values:
      values.append(grid)
    else:
      values = [grid]
    updated_grids = {key: values}
    grids_sorted.update(updated_grids)
  return grids_sorted

def find_xy_grid_intersections(grids):
  horizontal_grids = sort_grids_by_axis(grids, 'X')
  horizontal_grid_curves = [grid.Curve for grid in horizontal_grids]
  vertical_grids = sort_grids_by_axis(grids, 'Y')
  vertical_grid_curves = [grid.Curve for grid in vertical_grids]
  grid_intersections = []
  for h_grid_curve in horizontal_grid_curves:
    for v_grid_curve in vertical_grid_curves:
      if h_grid_curve.Intersect(v_grid_curve) == SetComparisonResult.Overlap:
        int_point = XYZ(h_grid_curve.GetEndPoint(0).X, v_grid_curve.GetEndPoint(0).Y,0)
        if str(int_point) not in str(grid_intersections):
          grid_intersections.append(int_point)
  return grid_intersections

def get_min_or_max_grid(vector, grids, min_or_max = 'min'):
  if abs(vector.X) > abs(vector.Y):
    grids_sorted = sort_grids_by_axis(grids, 'Y')
  else:
    grids_sorted = sort_grids_by_axis(grids, 'X')
  if min_or_max == 'min':
    return grids_sorted[0]
  else:
    return grids_sorted[-1]

def get_grid_vector(grid):
  grid_line = grid.Curve
  startpoint = grid_line.GetEndPoint(0)
  endpoint = grid_line.GetEndPoint(1)
  vector = endpoint - startpoint
  normalized_vector = vector.Normalize()
  return normalized_vector