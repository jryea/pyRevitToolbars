## 7/6
## Create Revit transaction group
## Create joint dimensions in a second transaction

from Autodesk.Revit.DB import *
from pyrevit import revit, forms, script
import JR_utilities as utils
from JR_utilities import ref_elements, elements, views, annotation, geometry

uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document
active_view = uidoc.ActiveView

def get_panel_joints(grids, direction, panels_per_bay):
  grid_pts_xy = ref_elements.get_grid_pts_xy(grids, direction)
  intermediate_pts_xy = geometry.get_intermediate_pts_xy(grid_pts_xy, panels_per_bay)
  for joint in intermediate_pts_xy:
    print(joint)
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
            cur_ref_plane.Name = '{}_jointX_{}'.format(prefix, joint_index)
            joint_index += 1
  if direction == 'Y':
    for i, line in enumerate(lines):
        print('line ' + str(i) +':')
        line_start_y = line.GetEndPoint(0).Y
        print('\tline start y: '+ str(line_start_y))
        line_end_y = line.GetEndPoint(1).Y
        print('\tline end y: ' +  str(line_end_y))
        line_x = line.GetEndPoint(0).X
        for joint in panel_joints:
          if (joint >  line_start_y and joint < line_end_y) or (joint >  line_end_y and joint < line_start_y):
            print('\t\tjoint y: ' + str(joint))
            ref_line_start = XYZ(line_x - (ref_line_length / 2), joint, 100)
            ref_line_end = XYZ(line_x + (ref_line_length / 2), joint, 100)
            cur_ref_plane = doc.Create.NewReferencePlane(ref_line_start, ref_line_end, XYZ(0, 0, 1), active_view)
            cur_ref_plane.Name = '{}_jointY_{}'.format(prefix, joint_index)
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

line_segments_north = [line for line in wall_lines if int((geometry.get_line_vector(line).X) == 1)]
line_segments_south = [line for line in wall_lines if int((geometry.get_line_vector(line).X) == -1)]
line_segments_west = [line for line in wall_lines if int((geometry.get_line_vector(line).Y) == 1)]
line_segments_east = [line for line in wall_lines if int((geometry.get_line_vector(line).Y) == -1)]

vertical_grids = [grid for grid in grids_list if int(geometry.get_line_vector(grid.Curve).X) == 0]
horizontal_grids = [grid for grid in grids_list if int(geometry.get_line_vector(grid.Curve).Y) == 0]

vertical_grids = ref_elements.sort_grids_by_axis(vertical_grids,'X')
horizontal_grids = ref_elements.sort_grids_by_axis(horizontal_grids, 'Y')

horizontal_joints_x = get_panel_joints(vertical_grids, 'X', 2)
print(len(horizontal_joints_x))
vertical_joints_y = get_panel_joints(horizontal_grids, 'Y', 2)


with revit.Transaction('Create wall joint ref planes'):
  create_joint_reference_planes(line_segments_north, horizontal_joints_x, 'X', 'N')
  create_joint_reference_planes(line_segments_south, horizontal_joints_x, 'X', 'S')
  create_joint_reference_planes(line_segments_west, vertical_joints_y, 'Y', 'W')
  create_joint_reference_planes(line_segments_east, vertical_joints_y, 'Y', 'E')
  # create_joint_reference_planes(horizontal_grids, 'vertical', 2)
  














