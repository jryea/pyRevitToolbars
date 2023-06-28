from Autodesk.Revit.DB import *
from pyrevit import revit, forms, script

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
  return word.upper() in full_split_string_list

reference_plane_col = FilteredElementCollector(doc)\
                      .OfClass(ReferencePlane)
reference_planes = list(reference_plane_col)
tos_reference_planes = [plane for plane in reference_planes if does_string_contain_word(plane.Name, 'tos')]

print(tos_reference_planes[2].Name)

curve_element_col = FilteredElementCollector(doc, active_view.Id) \
            .OfClass(CurveElement)
curve_element_list = list(curve_element_col)
# Get all lines set to IMEG_RED-CONSTRUCTION LINE GraphicsStyle
curve_blue_construction = [line for line in curve_element_list if str(line.LineStyle.Name) == 'IMEG_00-BLUE-CONSTRUCTION LINE']
line_list = [line.GeometryCurve for line in curve_blue_construction]

selected_joist_level = forms.select_levels(title= 'Select Beam System Level',multiple= False)

with revit.Transaction('Create Beam System'):
  #   public static BeamSystem Create(
  # 	Document document,
  # 	IList<Curve> profile,
  # 	SketchPlane sketchPlane,
  # 	int curveIndexForDirection
  # )

  cur_sketch_plane = SketchPlane.Create(doc, tos_reference_planes[2].Id)
  print(cur_sketch_plane)
  cur_beam_system = BeamSystem.Create(doc, line_list, cur_sketch_plane, 1)


  # BeamSystem.Create(doc,curve_blue_construction)















