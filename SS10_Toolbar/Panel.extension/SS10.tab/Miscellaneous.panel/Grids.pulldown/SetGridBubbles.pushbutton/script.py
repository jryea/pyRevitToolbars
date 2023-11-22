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


datum_end_options = ['Start Bubble', 'End Bubble']

datum_ends = forms.SelectFromList.show(datum_end_options, title='Select bubble ends to turn on', button_name = 'Select Ends', multiselect=True )

# Make sure all grids are running in the same absolute direction
if (len(selected_grids) < 1):
  print('Please select the grids you want to modify')
  script.exit()

with revit.Transaction('Modify grid bubbles'):
  for grid in selected_grids:
    if 'Start Bubble' in datum_ends:
      grid.ShowBubbleInView(DatumEnds.End0, active_view)
    else:
      grid.HideBubbleInView(DatumEnds.End0, active_view)
    if 'End Bubble' in datum_ends:
      grid.ShowBubbleInView(DatumEnds.End1, active_view)
    else:
      grid.HideBubbleInView(DatumEnds.End1, active_view)

