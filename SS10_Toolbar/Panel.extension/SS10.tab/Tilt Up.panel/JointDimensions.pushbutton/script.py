## 7/6
## Create Revit transaction group
## Create joint dimensions in a second transaction

from Autodesk.Revit.DB import *
from pyrevit import revit, forms, script
import JR_utilities as utils
from JR_utilities import ref_elements, elements, views, annotations, geometry

uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document
active_view = uidoc.ActiveView

def get_panel_joints(grids, direction, panels_per_bay):
  grid_pts_xy = ref_elements.get_grid_pts_xy(grids, direction)
  intermediate_pts_xy = geometry.get_intermediate_pts_xy(grid_pts_xy, panels_per_bay)
  return intermediate_pts_xy

def create_joint_reference_planes(lines, panel_joints, direction = 'X', prefix = 'N'):
  ref_line_length = 1.5
  joint_index = 1
  if direction == 'X':
    for i, line in enumerate(lines):
        line_start_x = line.GetEndPoint(0).X
        line_end_x = line.GetEndPoint(1).X
        line_y = line.GetEndPoint(0).Y
        for joint in panel_joints:
          if (joint >  line_start_x and joint < line_end_x) or (joint >  line_end_x and joint < line_start_x):
            ref_line_start = XYZ(joint,line_y + (ref_line_length / 2), 100)
            ref_line_end = XYZ(joint,line_y - (ref_line_length / 2), 100)
            cur_ref_plane = doc.Create.NewReferencePlane(ref_line_start, ref_line_end, XYZ(0, 0, 1), active_view)
            cur_ref_plane.Name = '{}_jointY_{}'.format(prefix, joint_index)
            joint_index += 1
  if direction == 'Y':
    for i, line in enumerate(lines):
        line_start_y = line.GetEndPoint(0).Y
        line_end_y = line.GetEndPoint(1).Y
        line_x = line.GetEndPoint(0).X
        for joint in panel_joints:
          if (joint >  line_start_y and joint < line_end_y) or (joint >  line_end_y and joint < line_start_y):
            ref_line_start = XYZ(line_x - (ref_line_length / 2), joint, 100)
            ref_line_end = XYZ(line_x + (ref_line_length / 2), joint, 100)
            cur_ref_plane = doc.Create.NewReferencePlane(ref_line_start, ref_line_end, XYZ(0, 0, 1), active_view)
            cur_ref_plane.Name = '{}_jointX_{}'.format(prefix, joint_index)
            joint_index += 1

grid_col = FilteredElementCollector(doc, active_view.Id) \
            .OfClass(Grid)
curve_element_col = FilteredElementCollector(doc, active_view.Id)\
                    .OfClass(CurveElement)

grids_list = list(grid_col)
curve_element_list = list(curve_element_col)

curve_red_construction = [line for line in curve_element_list if str(line.LineStyle.Name) == 'IMEG_00-RED-CONSTRUCTION LINE']
floor_lines = [line.GeometryCurve for line in curve_red_construction]
wall_curves_offset = -(5 / 12)

wall_lines = geometry.offset_curves(floor_lines, wall_curves_offset)

panels_per_bay = int(forms.ask_for_string(prompt = 'Enter number of panels per grid gap', title = 'Panels per bay'))


line_segments_north = [line for line in wall_lines if int((geometry.get_line_vector(line).X) == 1)]
line_segments_south = [line for line in wall_lines if int((geometry.get_line_vector(line).X) == -1)]
line_segments_west = [line for line in wall_lines if int((geometry.get_line_vector(line).Y) == 1)]
line_segments_east = [line for line in wall_lines if int((geometry.get_line_vector(line).Y) == -1)]

horizontal_grids = [grid for grid in grids_list if int(geometry.get_line_vector(grid.Curve).X) == 0]
vertical_grids = [grid for grid in grids_list if int(geometry.get_line_vector(grid.Curve).Y) == 0]

vertical_grids = ref_elements.sort_grids_by_axis(vertical_grids,'X')
horizontal_grids = ref_elements.sort_grids_by_axis(horizontal_grids, 'Y')

horizontal_joints_x = get_panel_joints(horizontal_grids, 'X', panels_per_bay)
vertical_joints_y = get_panel_joints(vertical_grids, 'Y', panels_per_bay)

# offset_vector = vector * (view.Scale * ((0.375) / 12))
min_grid_horizontal = ref_elements.get_min_or_max_grid(XYZ(0,1,0), horizontal_grids, 'min')
max_grid_horizontal = ref_elements.get_min_or_max_grid(XYZ(0,1,0), horizontal_grids, 'max')
min_grid_vertical = ref_elements.get_min_or_max_grid(XYZ(1,0,0), vertical_grids, 'min')
max_grid_vertical = ref_elements.get_min_or_max_grid(XYZ(1,0,0), vertical_grids, 'max')

horizontal_offset_vector = ref_elements.get_grid_vector(min_grid_horizontal) * (active_view.Scale * ((0.375) / 12)) * 2.5
vertical_offset_vector = ref_elements.get_grid_vector(min_grid_vertical) * (active_view.Scale * ((0.375) / 12)) * 2.5

north_dim_line = Line.CreateBound(min_grid_horizontal.Curve.GetEndPoint(0) + horizontal_offset_vector, max_grid_horizontal.Curve.GetEndPoint(0) + horizontal_offset_vector) 
south_dim_line = Line.CreateBound(min_grid_horizontal.Curve.GetEndPoint(1) - horizontal_offset_vector, max_grid_horizontal.Curve.GetEndPoint(1) - horizontal_offset_vector)
east_dim_line = Line.CreateBound(min_grid_vertical.Curve.GetEndPoint(0) + vertical_offset_vector, max_grid_vertical.Curve.GetEndPoint(0) + vertical_offset_vector)
west_dim_line = Line.CreateBound(min_grid_vertical.Curve.GetEndPoint(1) - vertical_offset_vector, max_grid_vertical.Curve.GetEndPoint(1) - vertical_offset_vector)

north_grid_ref_array = ReferenceArray()
south_grid_ref_array = ReferenceArray()
east_grid_ref_array = ReferenceArray()
west_grid_ref_array = ReferenceArray()
for grid in horizontal_grids:
  north_grid_ref_array.Append(Reference(grid))
for grid in horizontal_grids:
  south_grid_ref_array.Append(Reference(grid))
for grid in vertical_grids:
  east_grid_ref_array.Append(Reference(grid))
for grid in vertical_grids:
  west_grid_ref_array.Append(Reference(grid))


with TransactionGroup(doc, 'Create Joint Dimensions') as tg:
  tg.Start()
  with Transaction(doc, 'Add Joint Reference Planes') as t1:
    t1.Start()
    create_joint_reference_planes(line_segments_north, horizontal_joints_x, 'X', 'N')
    create_joint_reference_planes(line_segments_south, horizontal_joints_x, 'X', 'S')
    create_joint_reference_planes(line_segments_west, vertical_joints_y, 'Y', 'W')
    create_joint_reference_planes(line_segments_east, vertical_joints_y, 'Y', 'E')
    t1.Commit()
  with Transaction(doc, 'Add Dimensions') as t2:
    t2.Start()
    ref_plane_col = FilteredElementCollector(doc, active_view.Id)\
                    .OfClass(ReferencePlane)
    ref_plane_list = list(ref_plane_col)
    ref_plane_north = [rp for rp in ref_plane_list if utils.does_string_contain_word(rp.Name, 'N')]
    ref_plane_south = [rp for rp in ref_plane_list if utils.does_string_contain_word(rp.Name, 'S')]
    ref_plane_east = [rp for rp in ref_plane_list if utils.does_string_contain_word(rp.Name, 'E')]
    ref_plane_west = [rp for rp in ref_plane_list if utils.does_string_contain_word(rp.Name, 'W')]
    for rp in ref_plane_north:
      north_grid_ref_array.Append(Reference(rp))
    for rp in ref_plane_south:
      south_grid_ref_array.Append(Reference(rp))
    for rp in ref_plane_east:
      east_grid_ref_array.Append(Reference(rp))
    for rp in ref_plane_west:
      west_grid_ref_array.Append(Reference(rp))
    doc.Create.NewDimension(active_view, north_dim_line, north_grid_ref_array)
    doc.Create.NewDimension(active_view, south_dim_line, south_grid_ref_array)
    doc.Create.NewDimension(active_view, east_dim_line, east_grid_ref_array)
    doc.Create.NewDimension(active_view, west_dim_line, west_grid_ref_array)
    t2.Commit()
  tg.Commit()















