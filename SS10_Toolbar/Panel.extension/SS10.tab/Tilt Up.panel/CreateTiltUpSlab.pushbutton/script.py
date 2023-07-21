from Autodesk.Revit.DB import *
from pyrevit import revit, forms, script
from System.Collections import IList

uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document
active_view = uidoc.ActiveView

# Line segment collection
# Get IMEG-RED-CONSTRUCTION LINE GraphicsStyle
# All lines in view
curve_element_col = FilteredElementCollector(doc, active_view.Id)\
                    .OfClass(CurveElement)

curve_element_list = list(curve_element_col)

floor_type_id = doc.GetDefaultElementTypeId(ElementTypeGroup.FloorType)

# Get all lines set to IMEG_RED-CONSTRUCTION LINE GraphicsStyle
curve_red_construction = [line for line in curve_element_list if str(line.LineStyle.Name) == 'IMEG_00-RED-CONSTRUCTION LINE']
floor_lines = [line.GeometryCurve for line in curve_red_construction]

curve_loop = CurveLoop()
for line in floor_lines:
  curve_loop.Append(line)
curve_loop_list = [curve_loop]
inset_curve_loop = CurveLoop.CreateViaOffset(curve_loop, 10.0, XYZ(0,0,1))
inset_curves = inset_curve_loop.GetEnumerator()
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
