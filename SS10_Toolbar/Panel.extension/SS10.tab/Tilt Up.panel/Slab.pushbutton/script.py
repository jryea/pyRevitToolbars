from Autodesk.Revit.DB import *
from pyrevit import revit, forms
from JR_utilities import geometry

uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document
active_view = uidoc.ActiveView

curve_element_col = FilteredElementCollector(doc, active_view.Id)\
                    .OfClass(CurveElement)

curve_element_list = list(curve_element_col)

floor_type_id = doc.GetDefaultElementTypeId(ElementTypeGroup.FloorType)

curve_red_construction = [line for line in curve_element_list if str(line.LineStyle.Name) == 'IMEG_00-RED-CONSTRUCTION LINE']
floor_lines = [line.GeometryCurve for line in curve_red_construction]

curve_loop = CurveLoop()
for line in floor_lines:
  curve_loop.Append(line)
curve_loop_list = [curve_loop]
inset_curve_loop = CurveLoop.CreateViaOffset(curve_loop, 10.0, XYZ(0,0,1))

inset_curves = inset_curve_loop.GetEnumerator()
# for curve in inset_curves:
#   print(int(geometry.get_line_vector(curve).X))

# inset_curves_left = [line for line in inset_curves\
#                     if int(geometry.get_line_vector(line).Y) == 1]
# inset_curves_right = [line for line in inset_curves\
#                      if int(geometry.get_line_vector(line).Y) == -1]
# inset_curves_top = [line for line in inset_curves\
#                      if int(geometry.get_line_vector(line).X) == 1]
# inset_curves_bottom = [line for line in inset_curves\
#                      if int(geometry.get_line_vector(line).X) == -1]

# print(len(inset_curves_left))
# print(len(inset_curves_right))
# print(len(inset_curves_top))
# print(len(inset_curves_bottom))

# tl_pt = XYZ(min_x, max_y, 0)
# tr_pt = XYZ(max_x, max_y, 0)
# br_pt = XYZ(max_x, min_y, 0)
# bl_pt = XYZ(min_x, min_y, 0)
# simplified_inset_pts = [tl_pt, tr_pt, br_pt, bl_pt]
# simplified_inset_lines = geometry.create_lines_from_points(simplified_inset_pts)
# print(len(simplified_inset_lines))
# print(simplified_inset_lines)

current_view_level_id = active_view.GenLevel.Id
graphics_styles = FilteredElementCollector(doc) \
                  .OfClass(GraphicsStyle)
graphics_style_centerline = None
for style in graphics_styles:
  if str(style.Name) == '<Centerline>':
    graphics_style_centerline = style
graphics_style_centerline_id = graphics_style_centerline.Id

with revit.Transaction('Create Slab'):
  Floor.Create(doc, curve_loop_list, floor_type_id, current_view_level_id, True, floor_lines[0], 0.0)
  for curve in inset_curves:
    cur_detail_curve = doc.Create.NewDetailCurve(active_view, curve)
    # LineStyle property returns a GraphicsStyle object
    cur_detail_curve.LineStyle = doc.GetElement(graphics_style_centerline_id)
