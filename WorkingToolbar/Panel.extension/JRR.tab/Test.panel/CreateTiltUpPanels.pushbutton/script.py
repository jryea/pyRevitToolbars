from Autodesk.Revit.DB import *
from pyrevit import revit, forms, script

uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document
active_view = uidoc.ActiveView

def get_line_vector(line):
  startpoint = line.GetEndPoint(0)
  endpoint = line.GetEndPoint(1)
  vector = endpoint - startpoint
  normalized_vector = vector.Normalize()
  return normalized_vector

def sort_grids_by_axis(grids, axis = 'X'):
  # Returns list
  sorted_grids = grids
  def sort_x(grid):
    return grid.Curve.GetEndPoint(0).X
  def sort_y(grid):
    return grid.Curve.GetEndPoint(0).Y
  if axis == 'X':
    sorted_grids.sort(key=sort_x)
  if axis == 'Y':
    sorted_grids.sort(key=sort_y)
  return sorted_grids

def get_min_or_max_grid(vector, grids, min_or_max = 'min'):
  if abs(vector.X) > abs(vector.Y):
    grids_sorted = sort_grids_by_axis(grids, 'Y')
  else:
    grids_sorted = sort_grids_by_axis(grids, 'X')
  if min_or_max == 'min':
    return grids_sorted[0]
  else:
    return grids_sorted[-1]



# returns a list of XYZ x or y values depending on the input direction
# includes all of the x(or y) points along the grid and intermediate points (depending on panels)
def get_panel_joints(grids, direction, panels_per_bay):
  if len(grids) <= 1:
    print('There are not enough grids to create panel joints')
    return
  if direction == 'horizontal':
    grid_points = [grid.Curve.GetEndPoint(0).X for grid in grids]
  if direction == 'vertical':
    grid_points = [grid.Curve.GetEndPoint(0).Y for grid in grids]
  panel_joints = grid_points[:]
  distance_between_grids = grid_points[1] - grid_points[0]
  distance_between_panels = distance_between_grids / panels_per_bay

  for index, grid_point in enumerate(grid_points):
    # Skip last grid
    if index < len(grid_points) - 1:
      # Add intermediate points
      for i in range(panels_per_bay - 1):
        intermediate_joint = grid_points[index] + distance_between_panels * (i+1)
        panel_joints.append(intermediate_joint)
  panel_joints.sort()
  return panel_joints

def create_joint_reference_planes(grids, direction, num_joints_between_grids):
  if len(grids) <= 1:
    print('There are not enough grids to create reference planes')
    return
  if direction == 'horizontal':
    joint_x_list = []
    joint_y_start = grids[0].Curve.GetEndPoint(0).Y
    joint_y_end = grids[0].Curve.GetEndPoint(1).Y
    # Loop through all grids, but last one
    for index in range(0, len(grids) - 1):
      first_grid_x = grids[index].Curve.GetEndPoint(0).X
      next_grid_x = grids[index + 1].Curve.GetEndPoint(0).X
      distance_between_joints = (next_grid_x - first_grid_x) / num_joints_between_grids
      # create joint X values between grids:
      for i in range(0 , num_joints_between_grids - 1):
        joint_x_list.append(first_grid_x + distance_between_joints * (i+1))
    for index, joint_x in enumerate(joint_x_list):
      cur_ref_plane = doc.Create.NewReferencePlane(XYZ(joint_x, joint_y_start, 100), XYZ(joint_x, joint_y_end, 100), XYZ(0,0,1), active_view)
      cur_ref_plane.Name = 'jointX_{}'.format(index+1)
  if direction == 'vertical':
    joint_y_list = []
    joint_x_start = grids[0].Curve.GetEndPoint(0).X
    joint_x_end = grids[0].Curve.GetEndPoint(1).X
    # Loop through all grids, but last one
    for index in range(0, len(grids) - 1):
      first_grid_y = grids[index].Curve.GetEndPoint(0).Y
      next_grid_y = grids[index + 1].Curve.GetEndPoint(0).Y
      distance_between_joints = (next_grid_y - first_grid_y) / num_joints_between_grids
      # create joint X values between grids:
      for i in range(0 , num_joints_between_grids - 1):
        joint_y_list.append(first_grid_y + distance_between_joints * (i+1))
    for index, joint_y in enumerate(joint_y_list):
      cur_ref_plane = doc.Create.NewReferencePlane(XYZ(joint_x_start, joint_y, 100), XYZ(joint_x_end, joint_y, 100), XYZ(0,0,1), active_view)
      cur_ref_plane.Name = 'jointY_{}'.format(index+1)


#Collect panel end points from a given joint_width
def get_panel_ends(panel_joints, joint_width):
  joint_offset = joint_width / 2
  panel_ends = []
  for joint in panel_joints:
    panel_ends.append(joint - joint_offset)
    panel_ends.append(joint + joint_offset)
  return panel_ends

# Return XYZ points for a line segment
def get_panel_points_for_line_segment(line_segment, panel_ends, cardinal_direction):
  panel_ends_list = panel_ends[:]
  #Check to see if segments are running in reverse
  if cardinal_direction == 'south' or cardinal_direction == 'east':
    panel_ends_list.reverse()
  #Check to see if line segments are running horizontal
  if cardinal_direction == 'north' or cardinal_direction == 'south':
    x_start = line_segment.GetEndPoint(0).X
    x_end = line_segment.GetEndPoint(1).X
    y_point = line_segment.GetEndPoint(0).Y
    start_point = XYZ(x_start, y_point, 0)
    end_point = XYZ(x_end, y_point, 0)
    segment_panel_points = [start_point]
    for end in panel_ends_list:
      # Are segments running left to right?
      if cardinal_direction == 'north':
        # Do panel ends land within the lines extents?
        if end > x_start and end < x_end:
          segment_panel_points.append(XYZ(end, y_point, 0))
      # Are segments running right to left?
      if cardinal_direction == 'south':
        # Do panel ends land within the lines extents?
        if end > x_end and end < x_start:
          segment_panel_points.append(XYZ(end, y_point, 0))
    segment_panel_points.append(end_point)
  #Check to see if line segments are running vertical
  if cardinal_direction == 'west' or cardinal_direction == 'east':
    y_start = line_segment.GetEndPoint(0).Y
    y_end = line_segment.GetEndPoint(1).Y
    x_point = line_segment.GetEndPoint(0).X
    start_point = XYZ(x_point, y_start, 0)
    print(start_point)  
    end_point = XYZ(x_point, y_end, 0)
    print(end_point)
    segment_panel_points = [start_point]
    for end in panel_ends_list:
      # Are segments running bottom to top?
      if cardinal_direction == 'west':
        if end > y_start and end < y_end:
          segment_panel_points.append(XYZ(x_point, end, 0))
      # Are segments running top to bottom?
      if cardinal_direction == 'east':
        if end > y_end and end < y_start:
          segment_panel_points.append(XYZ(x_point, end, 0))
    segment_panel_points.append(end_point)
  return segment_panel_points

def create_wall_from_points(start_point, end_point, min_wall_length, wall_mark):
    try:
      line = Line.CreateBound(start_point, end_point)
    except:
      pass
      # print('Line is too short')
    else:
      if line.Length > min_wall_length:
        cur_wall = Wall.Create(doc, line, wall_type_id, selected_base_level.Id, wall_height, wall_offset, is_flipped, is_structural)
        WallUtils.DisallowWallJoinAtEnd(cur_wall, 0)
        WallUtils.DisallowWallJoinAtEnd(cur_wall, 1)
        # Set the Wall location to exterior face
        # 1- Core Centerline
        # 2- Finish Face: Exterior
        # 3- Finish Face: Interior
        # 4- Core Face: Exterior
        # 5- Core Face: Interior
        cur_wall.get_Parameter(BuiltInParameter.ALL_MODEL_MARK).Set(wall_mark)
        cur_wall.get_Parameter(BuiltInParameter.WALL_KEY_REF_PARAM).Set(5)


def create_walls_from_segments(line_segments, cardinal_direction, min_wall_length):
  # Choosing which set of points to create walls from (horizontal or vertical)
  if cardinal_direction == 'north' or cardinal_direction == 'south':
    panel_ends = panel_ends_horizontal
  if cardinal_direction == 'west' or cardinal_direction == 'east':
    panel_ends = panel_ends_vertical
  # Creating the wall mark prefix:
  wall_prefix = cardinal_direction[0].upper()
  wall_counter = 1
  for i, line in enumerate(line_segments):
    line_segment_points = get_panel_points_for_line_segment(line, panel_ends, cardinal_direction)
    end_of_range = len(line_segment_points) - 1
    # print('line {}: '.format(i+1))
    for index in range(0, end_of_range, 2):
      wall_suffix = str(wall_counter)
      if len(wall_suffix) == 1:
        wall_suffix = '0' + wall_suffix
      wall_mark_string = wall_prefix + wall_suffix
      wall_counter += 1
      cur_wall = create_wall_from_points(line_segment_points[index], line_segment_points[index + 1], min_wall_length, wall_mark_string)

def offset_curves(lines_list, offset):
  # returns an offset list of curves
  curve_loop = CurveLoop()
  for line in lines_list:
    curve_loop.Append(line)
  offset_curve_loop = CurveLoop.CreateViaOffset(curve_loop, offset, XYZ(0,0,1))
  return list(offset_curve_loop)

#lines Need to be in sequential order
# TEMPORARY (REPLACE WITH USER SELECTED WALL TYPE)
wall_type_id = ElementId(1234631)
wall_type = doc.GetElement(wall_type_id)
wall_curve_loop_offset = -abs(wall_type.Width / 2)

# Line segment collection
# Get IMEG-RED-CONSTRUCTION LINE GraphicsStyle
# All lines in view
curve_element_col = FilteredElementCollector(doc, active_view.Id) \
            .OfClass(CurveElement)
curve_element_list = list(curve_element_col)
# Get all lines set to IMEG_RED-CONSTRUCTION LINE GraphicsStyle
curve_red_construction = [line for line in curve_element_list if str(line.LineStyle.Name) == 'IMEG_00-RED-CONSTRUCTION LINE']
line_list = [line.GeometryCurve for line in curve_red_construction]

# Create curve loop and offset slab edge to create wall centerline
wall_curve_loop_list = offset_curves(line_list, wall_curve_loop_offset)

# Dividing line segments into North/East/South/West
line_segments_north = [line for line in wall_curve_loop_list if int((get_line_vector(line).X) == 1)]
line_segments_south = [line for line in wall_curve_loop_list if int((get_line_vector(line).X) == -1)]
line_segments_west = [line for line in wall_curve_loop_list if int((get_line_vector(line).Y) == 1)]
line_segments_east = [line for line in wall_curve_loop_list if int((get_line_vector(line).Y) == -1)]

# Grid collection
grid_col = FilteredElementCollector(doc, active_view.Id) \
            .OfClass(Grid)
grids_list = list(grid_col)
vertical_grids = [grid for grid in grids_list if int(get_line_vector(grid.Curve).X) == 0]
horizontal_grids = [grid for grid in grids_list if int(get_line_vector(grid.Curve).Y) == 0]

# Wall Variables
joint_width = .0625
wall_offset = -2.0
is_flipped = False
is_structural = True

panel_joints_horizontal = get_panel_joints(vertical_grids, 'horizontal', 2)
panel_joints_vertical = get_panel_joints(horizontal_grids, 'vertical', 2)
panel_ends_horizontal = get_panel_ends(panel_joints_horizontal, joint_width)
panel_ends_vertical = get_panel_ends(panel_joints_vertical, joint_width)

selected_base_level = forms.select_levels(title= 'Select Base Level',multiple= False)
selected_top_level = forms.select_levels(title= 'Select Top Level',multiple= False)
wall_height = selected_top_level.Elevation - selected_base_level.Elevation



with revit.Transaction('Create Walls'):
  # setting minimum length to ignore during wall creation
  minimum_wall_length = 2
  create_walls_from_segments(line_segments_north, 'north', minimum_wall_length)
  create_walls_from_segments(line_segments_south, 'south', minimum_wall_length)
  create_walls_from_segments(line_segments_east, 'east', minimum_wall_length)
  create_walls_from_segments(line_segments_west, 'west', minimum_wall_length)















