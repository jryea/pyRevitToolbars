from Autodesk.Revit.DB import *
from pyrevit import revit, forms, script

uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document

active_view = doc.ActiveView

cont_footing_col = FilteredElementCollector(doc)\
                .OfClass(WallFoundation)
cont_footing_list = list(cont_footing_col)

## COLLECT FOOTING LOCATION CURVES
cont_footing_curves = [footing.Location for footing in cont_footing_list]

print(len(cont_footing_list))
for footing in cont_footing_curves:
  print(footing)