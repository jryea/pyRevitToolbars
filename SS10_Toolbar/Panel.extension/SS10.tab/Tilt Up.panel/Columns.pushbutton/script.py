from Autodesk.Revit.DB import *
from pyrevit import revit, forms, script
import JR_utilities as utils
from JR_utilities import elements, ref_elements, annotations, geometry

uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document
active_view = uidoc.ActiveView

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
columns_col = FilteredElementCollector(doc)\
              .OfCategory(BuiltInCategory.OST_StructuralColumns)\
              .WhereElementIsElementType()
footings_col = FilteredElementCollector(doc)\
               .OfCategory(BuiltInCategory.OST_StructuralFoundation)\
              .WhereElementIsElementType()

curve_element_list = list(curve_element_col)
grids_list = list(grid_col)
family_list = list(family_symbol_col)
symbol_list = list(family_symbol_col)
reference_plane_list = list(reference_plane_col)
columns_list = list(columns_col)
footings_list = list(footings_col)

floor_lines = [line.GeometryCurve for line in curve_element_list if str(line.LineStyle.Name) == 'IMEG_00-RED-CONSTRUCTION LINE']
roof_tos_ref_planes = [rp for rp in reference_plane_list if utils.does_string_contain_word(rp.Name, 'TOS')]

class FamilySymbol(forms.TemplateListItem):
  @property
  def name(self):
    id = self.Id
    return Element.Name.GetValue(doc.GetElement(self.Id))

column_type_options = [FamilySymbol(column_type) for column_type in columns_list]
column_symbol = forms.SelectFromList.show(column_type_options, multiselect = False, title = 'Select column type')
footing_type_options = [FamilySymbol(footing_type) for footing_type in footings_list]
footing_symbol = forms.SelectFromList.show(footing_type_options, multiselect = False, title = 'Select footing type')

floor_curve_loop = CurveLoop()
for line in floor_lines:
  floor_curve_loop.Append(line)
floor_curve_loop_list = [floor_curve_loop]

min_column_offset_from_wall = float(forms.ask_for_string(prompt = 'Enter minimum offset from wall in feet', title = 'Minimum Column Wall Offset'))
inset_curve_loop = CurveLoop.CreateViaOffset(floor_curve_loop, min_column_offset_from_wall, XYZ(0,0,1))
grid_intersections = ref_elements.find_xy_grid_intersections(grids_list)
points_inside_border = geometry.find_pts_inside_xy_border(grid_intersections, inset_curve_loop)

column_tag_symbol = elements.get_symbol_by_family_and_name('45', 'IMEG_Structural Column Tag', symbol_list)
footing_tag_symbol = elements.get_symbol_by_family_and_name('Mark Only', 'IMEG_Foundation - Ref Level Tag', symbol_list)
footing_width = footing_symbol.get_Parameter(BuiltInParameter.STRUCTURAL_FOUNDATION_WIDTH).AsDouble()
footing_tag_offset = footing_width / 2 + 1
current_view_level_id = active_view.GenLevel.Id
horizontal_grids = ref_elements.sort_grids_by_axis(grids_list, 'X')

with revit.Transaction('Create Columns'):
  # If not being currently used, symbols are not activated to conserve memory
  # This will activate the selected symbol and regenerate the doc
  if column_symbol.IsActive == False:
    column_symbol.Activate()
    doc.Regenerate()
  if footing_symbol.IsActive == False:
    footing_symbol.Activate()
    doc.Regenerate()
  footing_counter = 0
  for grid_int in points_inside_border:
    cur_column = doc.Create.NewFamilyInstance(grid_int, column_symbol, active_view.GenLevel, Structure.StructuralType.Column)
    cur_column.get_Parameter(BuiltInParameter.SCHEDULE_BASE_LEVEL_OFFSET_PARAM).Set(-1.0)
    attachment_rp = None
    for rp in roof_tos_ref_planes:
      if grid_int.Y > rp.BubbleEnd.Y and grid_int.Y < rp.FreeEnd.Y:
        attachment_rp = rp
    ColumnAttachment.AddColumnAttachment(doc, cur_column, attachment_rp, 1, ColumnAttachmentCutStyle.None, ColumnAttachmentJustification.Midpoint, 0.0 )
    cur_footing = doc.Create.NewFamilyInstance(grid_int, footing_symbol, active_view.GenLevel, Structure.StructuralType.Footing)
    footing_counter += 1
    IndependentTag.Create(doc, column_tag_symbol.Id, active_view.Id, Reference(cur_column), False, TagOrientation.Horizontal, grid_int)
    footing_tag_pt = XYZ(grid_int.X, grid_int.Y - footing_tag_offset, grid_int.Z)
    IndependentTag.Create(doc, footing_tag_symbol.Id, active_view.Id, Reference(cur_footing), False, TagOrientation.Horizontal, footing_tag_pt)
  print('{} COLUMNS({}) CREATED WITH {} FOOTINGS'.format(footing_counter, Element.Name.GetValue(column_symbol), Element.Name.GetValue(footing_symbol)))
  print('------------------------------------------------------------------------------')

