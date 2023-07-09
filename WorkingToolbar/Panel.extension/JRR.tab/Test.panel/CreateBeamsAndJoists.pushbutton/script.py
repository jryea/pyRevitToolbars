from Autodesk.Revit.DB import *
from pyrevit import revit, forms, script
import JR_utilities as utils
from JR_utilities import ref_elements, geometry, elements, annotations

uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document
active_view = uidoc.ActiveView

# def geometry.get_line_vector(line):
#   print(line)
#   startpoint = line.GetEndPoint(0)
#   endpoint = line.GetEndPoint(1)
#   vector = endpoint - startpoint
#   normalized_vector = vector.Normalize()
#   return normalized_vector

def get_border_from_overlapping_segments(line_list):
  cleaned_lines = line_list
  lines_horizontal = [line for line in cleaned_lines
                      if abs(geometry.get_line_vector(line).X) == 1]
  lines_vertical = [line for line in cleaned_lines
                      if abs(geometry.get_line_vector(line).Y) == 1]
  for line_h in lines_horizontal:
    line_h_sp = line_h.GetEndPoint(0)
    line_h_ep = line_h.GetEndPoint(1)
    for line_v in lines_vertical:
      line_v_sp = line_v.GetEndPoint(0)
      line_v_ep = line_v.GetEndPoint(1)
      print('horizontal line start: ' + str(line_h_sp))
      print('horizontal line end: ' + str(line_h_ep))
      print('vertical line start: ' + str(line_v_sp))
      print('vertical line end: ' + str(line_v_ep))
      if line_h.Intersect(line_v) == SetComparisonResult.Overlap:
        print("Overlap!!!")
        # LOWER LEFT OVERLAP AND UPPER RIGHT OVERLAP
        # Is vertical line closer to left end point?
        # Is horizontal line closer to bottom start point?
        if abs(line_v_sp.X - line_h_ep.X) < abs(line_v_sp.X - line_h_sp.X)\
        and abs(line_h_sp.Y - line_v_sp.Y) < abs(line_h_sp.Y - line_v_ep.Y):
          # LOWER LEFT OVERLAP (works if lines are running clockwise)
          if geometry.get_line_vector(line_h).X == -1\
          and geometry.get_line_vector(line_v).Y == 1:
            line_h = Line.CreateBound(line_h_sp,
                                          XYZ(line_v_ep.X, line_h_ep.Y, line_h_sp.Z))
            line_v = Line.CreateBound(XYZ(line_v_sp.X, line_h_sp.Y, line_v_sp.Z),
                                          line_v_ep)
            print('\tnew horizontal line start: ' + str(line_h.GetEndPoint(0)))
            print('\tnew horizontal line end: ' + str(line_h.GetEndPoint(1)))
            print('\tnew vertical line start: ' + str(line_v.GetEndPoint(0)))
            print('\tnew vertical line end: ' + str(line_v.GetEndPoint(1)))
          # UPPER RIGHT OVERLAP (works if lines are running clockwise)
          elif geometry.get_line_vector(line_h).X == 1\
          and geometry.get_line_vector(line_v).Y == -1:
            line_h = Line.CreateBound(line_h_sp,
                                          XYZ(line_v_ep.X, line_h_ep.Y, line_h_sp.Z))
            line_v = Line.CreateBound(XYZ(line_v_sp.X, line_h_sp.Y, line_v_sp.Z),
                                          line_v_ep)
            print('\tnew horizontal line start: ' + str(line_h.GetEndPoint(0)))
            print('\tnew horizontal line end: ' + str(line_h.GetEndPoint(1)))
            print('\tnew vertical line start: ' + str(line_v.GetEndPoint(0)))
            print('\tnew vertical line end: ' + str(line_v.GetEndPoint(1)))
          else:
            print('\nLINES ARE NOT RUNNING CLOCKWISE\n')
        # UPPER LEFT OVERLAP AND LOWER RIGHT OVERLAP
        # Is vertical line closer to left start point?
        # Is horizontal line closer to top end point?
        if abs(line_v_sp.X - line_h_sp.X) < abs(line_v_sp.X - line_h_ep.X)\
        and abs(line_h_sp.Y - line_v_ep.Y) < abs(line_h_sp.Y - line_v_sp.Y):
          line_h = Line.CreateBound(line_h_sp,
                                         XYZ(line_v_ep.X, line_h_ep.Y, line_h_sp.Z))
          line_v = Line.CreateBound(XYZ(line_v_sp.X, line_h_sp.Y, line_v_sp.Z),
                                        line_v_ep)
          print('\tnew horizontal line start: ' + str(line_h.GetEndPoint(0)))
          print('\tnew horizontal line end: ' + str(line_h.GetEndPoint(1)))
          print('\tnew vertical line start: ' + str(line_v.GetEndPoint(0)))
          print('\tnew vertical line end: ' + str(line_v.GetEndPoint(1)))
    

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
curve_element_col = FilteredElementCollector(doc, active_view.Id)\
                    .OfClass(CurveElement)

curve_element_list = list(curve_element_col)
reference_planes = list(reference_plane_col)
grid_list = list(grid_col)
curve_element_list = list(curve_element_col)
column_list = list(column_col)
family_symbol_list = list(family_symbol_col)

horizontal_grids = [grid for grid in grid_list if int(geometry.get_line_vector(grid.Curve).X) == 0]
horizontal_grids = ref_elements.sort_grids_by_axis(horizontal_grids, 'Y')
vertical_grids = [grid for grid in grid_list if int(geometry.get_line_vector(grid.Curve).Y) == 0]
vertical_grids = ref_elements.sort_grids_by_axis(vertical_grids,'X')

floor_lines = [line.GeometryCurve for line in curve_element_list if str(line.LineStyle.Name) == 'IMEG_00-RED-CONSTRUCTION LINE']
# tos_reference_planes = [plane for plane in reference_planes if utils.does_string_contain_word(plane.Name, 'tos')]
column_selected_list = [column for column in column_list if Element.Name.GetValue(column.Symbol) == Element.Name.GetValue(column.Symbol)]
curve_blue_construction = [line for line in curve_element_list if str(line.LineStyle.Name) == 'IMEG_00-BLUE-CONSTRUCTION LINE']
lines_blue_construction = [line.GeometryCurve for line in curve_blue_construction]

line_segments_north = [line for line in floor_lines if int((geometry.get_line_vector(line).X) == 1)]
line_segments_south = [line for line in floor_lines if int((geometry.get_line_vector(line).X) == -1)]
line_segments_west = [line for line in floor_lines if int((geometry.get_line_vector(line).Y) == 1)]
line_segments_east = [line for line in floor_lines if int((geometry.get_line_vector(line).Y) == -1)]

seat_depth = 5.5 / 12
horizontal_grids = ref_elements.sort_grids_by_axis(grid_list, 'X')
# Assumes all horizontal grid spacing is the same
dist_between_horizontal_grids = horizontal_grids[1].Curve.GetEndPoint(0).X - horizontal_grids[0].Curve.GetEndPoint(0).X

sorted_columns = elements.sort_columns(column_selected_list)
beam_pts = elements.get_beam_pts_from_sorted_columns(doc, sorted_columns, dist_between_horizontal_grids)
# Adding points from the west walls
for line in line_segments_west:
  line_start = line.GetEndPoint(0)
  line_end = line.GetEndPoint(1)
  for i, group in enumerate(beam_pts):
    if group[0].Y > line_start.Y and group[0].Y < line_end.Y and abs(group[0].X - line_start.X) < dist_between_horizontal_grids + 1:
      new_point = XYZ(line_start.X, group[0].Y, group[0].Z)
      group.insert(0,new_point)
# Adding points from the east walls
for line in line_segments_east:
  line_start = line.GetEndPoint(0)
  line_end = line.GetEndPoint(1)
  for i, group in enumerate(beam_pts):
    if group[0].Y < line_start.Y and group[0].Y > line_end.Y and abs(line_start.X - group[-1].X) < dist_between_horizontal_grids + 1:
      new_point = XYZ(line_start.X, group[0].Y, group[0].Z)
      group.append(new_point)

beam_symbol = elements.get_symbol_by_name('48G8N17K', family_symbol_list)
beam_tag_symbol = elements.get_symbol_by_name('Standard Tilt Up', family_symbol_list)

## BEAM SYSTEMS

max_x = geometry.get_min_max_xy_extents(floor_lines)['max_x']
min_x = geometry.get_min_max_xy_extents(floor_lines)['min_x']
max_y = geometry.get_min_max_xy_extents(floor_lines)['max_y']
min_y = geometry.get_min_max_xy_extents(floor_lines)['min_y']
grid_divider_tolerance = 5
grid_divider_lines = [grid.Curve
                      for grid
                      in vertical_grids
                      if grid.Curve.GetEndPoint(0).Y > min_y + grid_divider_tolerance
                      and grid.Curve.GetEndPoint(0).Y < max_y - grid_divider_tolerance]

def find_border_lines(line_list, divider_lines_list):
  start_border_lines = [line for line
                        in line_list
                        if line.GetEndPoint(0).Y < divider_lines_list[0].GetEndPoint(0).Y
                        or line.GetEndPoint(1).Y < divider_lines_list[0].GetEndPoint(0).Y
                        ]
  end_border_lines = [line for line
                      in line_list
                      if line.GetEndPoint(0).Y > divider_lines_list[-1].GetEndPoint(0).Y
                      or line.GetEndPoint(1).Y > divider_lines_list[-1].GetEndPoint(0).Y]
  return start_border_lines




first_beam_system_lines = find_border_lines(floor_lines, grid_divider_lines)
print(len(first_beam_system_lines))
first_beam_system_lines.append(grid_divider_lines[0].CreateReversed())
print(len(first_beam_system_lines))

get_border_from_overlapping_segments(first_beam_system_lines)


# with revit.Transaction('Create Beams and Joists'):
#   for group in beam_pts:
#     for i, pt in enumerate(group):
#       # print(pt)
#       if i < len(group) - 1:
#         beam_start_pt = pt
#         # print('Beam start point: ' + str(beam_start_pt))
#         beam_end_pt = group[i+1]
#         # print('Beam end point: ' + str(beam_end_pt))
#         beam_line = Line.CreateBound(beam_start_pt, beam_end_pt)
#         cur_beam = doc.Create.NewFamilyInstance(beam_line, beam_symbol, active_view.GenLevel , Structure.StructuralType.Beam)
#         cur_beam.get_Parameter(BuiltInParameter.Z_OFFSET_VALUE).Set(-(seat_depth))
#         cur_beam.StructuralUsage = Structure.StructuralInstanceUsage.Girder
#         tag_pt_X = (beam_start_pt.X + beam_end_pt.X) / 2
#         tag_pt = XYZ(tag_pt_X, beam_start_pt.Y + 1.5, 0)
#         IndependentTag.Create(doc, beam_tag_symbol.Id, active_view.Id, Reference(cur_beam), False, TagOrientation.Horizontal, tag_pt)

    # cur_sketch_plane = SketchPlane.Create(doc, tos_reference_planes[2].Id)
    # cur_beam_system = BeamSystem.Create(doc, line_list, cur_sketch_plane, 1)
















