from Autodesk.Revit.DB import *
from pyrevit import revit, forms, script
from System.Collections import IList

uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document
active_view = uidoc.ActiveView

selected_line_ids = uidoc.Selection.GetElementIds()
floor_lines = [doc.GetElement(line_id).GeometryCurve for line_id in selected_line_ids]

curve_loop = CurveLoop()
# curve_loop.Append(floor_lines)
for line in floor_lines:
  curve_loop.Append(line)

curve_loop_list = [curve_loop]

inset_curve_loop = CurveLoop.CreateViaOffset(curve_loop, 10.0, XYZ(0,0,1))

inset_curves = inset_curve_loop.GetEnumerator()
# print(list(inset_curves))

current_view_level_id = active_view.GenLevel.Id

graphics_styles = FilteredElementCollector(doc) \
                  .OfClass(GraphicsStyle)

graphics_style_centerline = None
for style in graphics_styles:
  if str(style.Name) == '<Centerline>':
    graphics_style_centerline = style
graphics_style_centerline_id = graphics_style_centerline.Id

floor_type_id = ElementId(4374)

#Have user select floor type

# public static Floor Create(
# 	Document document,
# 	IList<CurveLoop> profile,
# 	ElementId floorTypeId,
# 	ElementId levelId,
# 	bool isStructural,
# 	Line slopeArrow,
# 	double slope
# )
with revit.Transaction('Create Slab'):
  Floor.Create(doc, curve_loop_list, floor_type_id, current_view_level_id, True, floor_lines[0], 0.0)
  for curve in inset_curves:
    cur_detail_curve = doc.Create.NewDetailCurve(active_view, curve)
    # LineStyle property returns a GraphicsStyle object
    cur_detail_curve.LineStyle = doc.GetElement(graphics_style_centerline_id)
    print(cur_detail_curve.LineStyle.ToString())
    print(cur_detail_curve.LineStyle.Name)
    # print(cur_detail_curve.GetGrapihcsStyle())
