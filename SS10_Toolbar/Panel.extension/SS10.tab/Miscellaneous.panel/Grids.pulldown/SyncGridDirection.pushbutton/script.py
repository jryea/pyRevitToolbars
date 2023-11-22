from Autodesk.Revit.DB import *
from pyrevit import revit, forms, script
from JR_utilities import geometry

## Create a shift select version that works on all grids in the viw
## Or just recognizes when nothing is selected and acts on all grids

uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document
active_view = doc.ActiveView
selection = uidoc.Selection
selected_element_ids = selection.GetElementIds()
selected_elements = [doc.GetElement(element_id) for element_id in selected_element_ids]
selected_grids = [element for element in selected_elements \
                  if element.GetType() == Grid ]

# Make sure all grids are running in the same absolute direction
if (len(selected_grids) < 1):
  print('Please select the grids you want to sync')
  script.exit()

first_selected_grid = selected_grids[0]

for grid in selected_grids:
  if str(geometry.get_line_vector(grid.Curve, True)) \
  != str(geometry.get_line_vector(first_selected_grid.Curve, True)):
    print('Please select parallel grids!')
    script.exit()

with revit.Transaction('Sync selected grids'):
  for grid in selected_grids:
    first_grid_vector = geometry.get_line_vector(first_selected_grid.Curve)
    cur_grid_vector = geometry.get_line_vector(grid.Curve)
    if str(first_grid_vector) != str(cur_grid_vector):
      grid_curve = grid.GetCurvesInView(DatumExtentType.Model, active_view)[0]
      new_grid_line = grid_curve.CreateReversed()
      grid.SetCurveInView(DatumExtentType.Model, active_view, new_grid_line)
















