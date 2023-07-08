from Autodesk.Revit.DB import *
from pyrevit import revit, forms, script
import JR_utilities as utils
from JR_utilities import elements, ref_elements, annotations, geometry
# import clr
# clr.AddReference("RevitAPI")
# clr.AddReference("RevitAPIUI")

uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document
active_view = uidoc.ActiveView

# def get_symbol_by_family_and_symbol_names(family_name, symbol_name, all_families, all_symbols):
#   symbol = None
#   family = None
#   for f in all_families:
#     if Element.Name.GetValue(f) == family_name:
#       family = f
#   for s in all_symbols:
#     if Element.Name.GetValue(s) == symbol_name and Element.Name.GetValue(s.Family) == Element.Name.GetValue(family):
#       symbol = s
#   if not family:
#     print(family_name + ' not found')
#   if not symbol:
#     print("type " + symbol_name + " not found in the " + family_name + " family")
#   if family and symbol:
#     return symbol

curve_element_col = FilteredElementCollector(doc, active_view.Id)\
                    .OfClass(CurveElement)
grid_col = FilteredElementCollector(doc, active_view.Id) \
            .OfClass(Grid)
family_col = FilteredElementCollector(doc)\
                     .OfClass(Family)
family_symbol_col = FilteredElementCollector(doc)\
                     .OfClass(FamilySymbol)
reference_plane_col = FilteredElementCollector(doc)\
                      .OfClass(ReferencePlane)

curve_element_list = list(curve_element_col)
grids_list = list(grid_col)
family_list = list(family_symbol_col)
family_symbol_list = list(family_symbol_col)
reference_plane_list = list(reference_plane_col)

floor_lines = [line.GeometryCurve for line in curve_element_list if str(line.LineStyle.Name) == 'IMEG_00-RED-CONSTRUCTION LINE']
# column_selected_list = [column for column in column_list if Element.Name.GetValue(column.Symbol) == Element.Name.GetValue(column.Symbol)]
curve_blue_construction = [line for line in curve_element_list if str(line.LineStyle.Name) == 'IMEG_00-BLUE-CONSTRUCTION LINE']
lines_blue_construction = [line.GeometryCurve for line in curve_blue_construction]
roof_tos_ref_planes = [rp for rp in reference_plane_list if utils.does_string_contain_word(rp.Name, 'TOS')]

floor_curve_loop = CurveLoop()
for line in floor_lines:
  floor_curve_loop.Append(line)
floor_curve_loop_list = [floor_curve_loop]

min_column_offset_from_wall = 10
inset_curve_loop = CurveLoop.CreateViaOffset(floor_curve_loop, min_column_offset_from_wall, XYZ(0,0,1))
# inset_curves = inset_curve_loop.GetEnumerator()
# print(inset_curves)
grid_intersections = ref_elements.find_xy_grid_intersections(grids_list)
points_inside_border = geometry.find_pts_inside_xy_border(grid_intersections, inset_curve_loop)

column_symbol = elements.get_symbol_by_name('HSS10X10X1/2', family_symbol_list)
footing_symbol = elements.get_symbol_by_name('8\'-0" x 8\'-0" x 1\'-0"', family_symbol_list)

column_tag_symbol = elements.get_symbol_by_name('45', family_symbol_list)
footing_tag_symbol = elements.get_symbol_by_name('Mark Only', family_symbol_list)

footing_tag_offset = 5
current_view_level_id = active_view.GenLevel.Id
horizontal_grids = ref_elements.sort_grids_by_axis(grids_list, 'X')

with revit.Transaction('Create Columns'):

  for grid_int in points_inside_border:
    cur_column = doc.Create.NewFamilyInstance(grid_int, column_symbol, active_view.GenLevel, Structure.StructuralType.Column)
    cur_column.get_Parameter(BuiltInParameter.SCHEDULE_BASE_LEVEL_OFFSET_PARAM).Set(-1.0)
    attachment_rp = None
    for rp in roof_tos_ref_planes:
      if grid_int.Y > rp.BubbleEnd.Y and grid_int.Y < rp.FreeEnd.Y:
        attachment_rp = rp
    ColumnAttachment.AddColumnAttachment(doc, cur_column, attachment_rp, 1, ColumnAttachmentCutStyle.None, ColumnAttachmentJustification.Midpoint, 0.0 )
    cur_footing = doc.Create.NewFamilyInstance(grid_int, footing_symbol, active_view.GenLevel, Structure.StructuralType.Footing)
    IndependentTag.Create(doc, column_tag_symbol.Id, active_view.Id, Reference(cur_column), False, TagOrientation.Horizontal, grid_int)
    footing_tag_pt = XYZ(grid_int.X, grid_int.Y - footing_tag_offset, grid_int.Z)
    IndependentTag.Create(doc, footing_tag_symbol.Id, active_view.Id, Reference(cur_footing), False, TagOrientation.Horizontal, footing_tag_pt)
