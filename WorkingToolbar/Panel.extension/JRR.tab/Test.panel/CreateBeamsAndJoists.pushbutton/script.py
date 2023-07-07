from Autodesk.Revit.DB import *
from pyrevit import revit, forms, script
import JR_utilities as utils

uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document
active_view = uidoc.ActiveView

reference_plane_col = FilteredElementCollector(doc)\
                      .OfClass(ReferencePlane)
grid_col = FilteredElementCollector(doc, active_view.Id) \
            .OfClass(Grid)
curve_element_col = FilteredElementCollector(doc, active_view.Id) \
                    .OfClass(CurveElement)
column_col = FilteredElementCollector(doc)\
            .OfCategory(BuiltInCategory.OST_StructuralColumns)\
            .WhereElementIsNotElementType()
family_symbol_col = FilteredElementCollector(doc)\
                     .OfClass(FamilySymbol)

reference_planes = list(reference_plane_col)
grid_list = list(grid_col)
curve_element_list = list(curve_element_col)
column_list = list(column_col)
family_symbol_list = list(family_symbol_col)

tos_reference_planes = [plane for plane in reference_planes if utils.does_string_contain_word(plane.Name, 'tos')]
column_selected_list = [column for column in column_list if Element.Name.GetValue(column.Symbol) == Element.Name.GetValue(column.Symbol)]
curve_blue_construction = [line for line in curve_element_list if str(line.LineStyle.Name) == 'IMEG_00-BLUE-CONSTRUCTION LINE']
lines_blue_construction = [line.GeometryCurve for line in curve_blue_construction]

seat_depth = 5.5 / 12
horizontal_grids = utils.sort_grids_by_axis(grid_list, 'X')
#Assumes all horizontal grid spacing is the same
dist_between_horizontal_grids = horizontal_grids[1].Curve.GetEndPoint(0).X - horizontal_grids[0].Curve.GetEndPoint(0).X
sorted_columns = utils.sort_columns(column_selected_list)
beam_pts = utils.get_beam_pts_from_sorted_columns(doc, sorted_columns, dist_between_horizontal_grids)
for i, group in enumerate(beam_pts):
  print('group ' + str(i+1) + ":")
  for j,pt in enumerate(group):
    print('\tpoint ' + str(j+1) + str(pt))
beam_symbol = utils.get_symbol_by_name('48G8N17K', family_symbol_list)
beam_tag_symbol = utils.get_symbol_by_name('Standard Tilt Up', family_symbol_list)

with revit.Transaction('Create Beams and Joists'):
  for group in beam_pts:
    for i, pt in enumerate(group):
      print(pt)
      if i < len(group) - 1:
        beam_start_pt = pt
        print('Beam start point: ' + str(beam_start_pt))
        beam_end_pt = group[i+1]
        print('Beam end point: ' + str(beam_end_pt))
        beam_line = Line.CreateBound(beam_start_pt, beam_end_pt)
        cur_beam = doc.Create.NewFamilyInstance(beam_line, beam_symbol, active_view.GenLevel , Structure.StructuralType.Beam)
        cur_beam.get_Parameter(BuiltInParameter.Z_OFFSET_VALUE).Set(-(seat_depth))
        cur_beam.StructuralUsage = Structure.StructuralInstanceUsage.Girder
        tag_pt_X = (beam_start_pt.X + beam_end_pt.X) / 2
        tag_pt = XYZ(tag_pt_X, beam_start_pt.Y + 1.5, 0)
        IndependentTag.Create(doc, beam_tag_symbol.Id, active_view.Id, Reference(cur_beam), False, TagOrientation.Horizontal, tag_pt)

    # cur_sketch_plane = SketchPlane.Create(doc, tos_reference_planes[2].Id)
    # cur_beam_system = BeamSystem.Create(doc, line_list, cur_sketch_plane, 1)
















