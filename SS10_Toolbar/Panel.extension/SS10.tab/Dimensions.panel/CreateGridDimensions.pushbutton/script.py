from Autodesk.Revit.DB import *
from pyrevit import revit, forms, script

uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document
active_view = uidoc.ActiveView

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

def get_grid_vector(grid):
  grid_line = grid.Curve
  startpoint = grid_line.GetEndPoint(0)
  endpoint = grid_line.GetEndPoint(1)
  vector = endpoint - startpoint
  normalized_vector = vector.Normalize()
  return normalized_vector

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

#function for the pyrevit 'select_views' form
def get_plan_views_from_views(view):
    if isinstance(view, ViewPlan):
      return view

selected_plan_views = forms.select_views(title='Select plan views to dimension', multiple= True, filterfunc= get_plan_views_from_views)

with revit.Transaction('Create Grids'):
  # Loop through selected plans
  if selected_plan_views:
    for view in selected_plan_views:
      # COLLECT GRIDS ON CURRENT VIEW
      current_view = view
      grids_col = FilteredElementCollector(doc, current_view.Id) \
              .OfClass(Grid)
      grids_list = list(grids_col)
      grids_sorted_by_vectors = sort_grids_by_vector(grids_list)
      # Create dimension strings
      for key in grids_sorted_by_vectors.keys():
        grids = grids_sorted_by_vectors.get(key)
        if len(grids) <= 1:
          continue
        vector = get_grid_vector(grids[0])
        ## Convert 3/8" dimension snap distance to model scale
        offset_vector = vector * (view.Scale * ((0.375) / 12))
        min_grid = get_min_or_max_grid(vector, grids, 'min')
        max_grid = get_min_or_max_grid(vector, grids, 'max')
        grid_line_startpoint = min_grid.Curve.GetEndPoint(0)
        grid_line_endpoint = max_grid.Curve.GetEndPoint(0)

        #Adding conditional to make sure X and Y grids dimensions are aligned
        if vector.X == 1:
          grid_line_endpoint = XYZ(grid_line_startpoint.X, grid_line_endpoint.Y, grid_line_endpoint.Z)
        if vector.Y == 1:
          grid_line_endpoint = XYZ(grid_line_endpoint.X, grid_line_startpoint.Y, grid_line_endpoint.Z)

        #move line points by adding offset_vector
        overall_dim_line_startpoint = grid_line_startpoint + offset_vector * 0.5
        overall_dim_line_endpoint = grid_line_endpoint + offset_vector * 0.5
        grid_dim_line_startpoint = grid_line_startpoint + offset_vector * 1.5
        grid_dim_line_endpoint = grid_line_endpoint + offset_vector * 1.5
        overall_dim_line = Line.CreateBound(overall_dim_line_startpoint, overall_dim_line_endpoint)
        grid_dim_line = Line.CreateBound(grid_dim_line_startpoint, grid_dim_line_endpoint)

        overall_reference_array = ReferenceArray()
        grid_reference_array = ReferenceArray()

        for grid in grids:
          grid_start = grid.Curve.GetEndPoint(0)
          grid_end = grid.Curve.GetEndPoint(1)
          grid_reference_array.Append(Reference(grid))
        overall_reference_array.Append(Reference(min_grid))
        overall_reference_array.Append(Reference(max_grid))
        doc.Create.NewDimension(current_view, overall_dim_line, overall_reference_array)
        doc.Create.NewDimension(current_view, grid_dim_line, grid_reference_array)














