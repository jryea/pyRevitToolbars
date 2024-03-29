
from Autodesk.Revit.DB import *
from Autodesk.Revit.DB.Structure import StructuralType
from pyrevit import revit, forms, script
import JR_utilities as utils
import JR_utilities.geometry as geo
from JR_utilities import ref_elements, views, elements, annotations

uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document
active_view = uidoc.ActiveView

def get_panel_joints(grids, direction, panels_per_bay):
  grid_pts_xy = ref_elements.get_grid_pts_xy(grids, direction)
  intermediate_pts_xy = geo.get_intermediate_pts_xy(grid_pts_xy, panels_per_bay)
  combined_pts_xy = grid_pts_xy + intermediate_pts_xy
  combined_pts_xy.sort()
  return combined_pts_xy

# Collect panel end points from a given joint_width
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
    end_point = XYZ(x_point, y_end, 0)
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

def create_plan_panel_tag(start_point, end_point, wall):
  tag_offset = 10
  tag_X = start_point.X
  tag_Y = start_point.Y
  # check to see if running horizontally or vertically
  if abs(start_point.X - end_point.X) > abs(start_point.Y - end_point.Y):
    tag_X = (start_point.X + end_point.X) / 2
    # Check to see if points running right to left
    if start_point.X > end_point.X:
      tag_Y = tag_Y - tag_offset
    else:
      tag_Y = tag_Y + tag_offset
  else:
    tag_Y = (start_point.Y + end_point.Y) / 2
    # Check to see if points running top to bottom
    if start_point.Y > end_point.Y:
      tag_X = tag_X + tag_offset
    else:
      tag_X = tag_X - tag_offset
  tag_point = XYZ(tag_X, tag_Y, 0)
  tag = IndependentTag.Create(doc, wall_tag_symbol.Id, active_view.Id, Reference(wall), False, TagOrientation.Horizontal, tag_point)
  return tag

def create_panel_with_tag(start_point, end_point, wall_mark, min_tag_threshold = 0):
    try:
      line = Line.CreateBound(start_point, end_point)
    except:
      pass
    else:
      cur_wall = Wall.Create(doc, line, wall_type.Id, selected_base_level.Id, wall_height, wall_offset, is_flipped, is_structural)
      # cur_footing = WallFoundation.Create(doc,footing_type_id, cur_wall.Id)
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
      # Adding tag to wall
      if line.Length > min_tag_threshold:
        tag_cur = create_plan_panel_tag(start_point, end_point, cur_wall)


def create_panels_from_segments(line_segments, cardinal_direction, min_wall_length):
  # Choosing which set of points to create walls from (horizontal or vertical)
  min_tagging_length = 10
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
    for index in range(0, end_of_range, 2):
      wall_suffix = str(wall_counter)
      if len(wall_suffix) == 1:
        wall_suffix = '0' + wall_suffix
      wall_mark_string = wall_prefix + wall_suffix
      panel_start = line_segment_points[index]
      panel_end = line_segment_points[index + 1]
      wall_line_length = Line.CreateBound(panel_start, panel_end).Length
      if wall_line_length > min_tagging_length:
        wall_counter += 1
      if wall_line_length > min_wall_length:
        cur_wall = create_panel_with_tag(panel_start, panel_end, wall_mark_string, min_tagging_length)

#lines Need to be in sequential order
# TEMPORARY (REPLACE WITH USER SELECTED WALL TYPE)
wall_col = FilteredElementCollector(doc)\
           .OfCategory(BuiltInCategory.OST_Walls)\
           .WhereElementIsElementType()
wall_list = list(wall_col)
wall_list.sort()

class WallType(forms.TemplateListItem):
  @property
  def name(self):
    type_id = self.Id
    return Element.Name.GetValue(doc.GetElement(self.Id))

wall_type_options = [WallType(wall_type) for wall_type in wall_list]
wall_type = forms.SelectFromList.show(wall_type_options, multiselect = False, title = 'Select wall type')
wall_curve_loop_offset = -abs(wall_type.Width / 2)

active_view_level = active_view.GenLevel

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
wall_curve_loop_list = geo.offset_curves(line_list, wall_curve_loop_offset)

# Dividing line segments into North/East/South/West
line_segments_north = [line for line in wall_curve_loop_list if int((geo.get_line_vector(line).X) == 1)]
line_segments_south = [line for line in wall_curve_loop_list if int((geo.get_line_vector(line).X) == -1)]
line_segments_west = [line for line in wall_curve_loop_list if int((geo.get_line_vector(line).Y) == 1)]
line_segments_east = [line for line in wall_curve_loop_list if int((geo.get_line_vector(line).Y) == -1)]

# Grid collection
grid_col = FilteredElementCollector(doc, active_view.Id) \
            .OfClass(Grid)
grids_list = list(grid_col)
vertical_grids = [grid for grid in grids_list if int(geo.get_line_vector(grid.Curve).X) == 0]
horizontal_grids = [grid for grid in grids_list if int(geo.get_line_vector(grid.Curve).Y) == 0]

# Collect wall tags
family_symbol_col = FilteredElementCollector(doc)\
                     .OfClass(FamilySymbol)

family_symbol_list = list(family_symbol_col)

wall_tag_symbol = elements.get_symbol_by_name('Tilt Up Panel Mark', family_symbol_list)

# Wall Variables
joint_width = (float(forms.ask_for_string(prompt = 'Enter joint width in inches', title = 'Joint width'))) / 12
joint_offset = joint_width / 2
wall_offset = -2.0
is_flipped = False
is_structural = True
panels_per_bay = int(forms.ask_for_string(prompt = 'Enter number of panels per grid gap', title = 'Panels per bay'))

panel_joints_horizontal = get_panel_joints(vertical_grids, 'X', panels_per_bay)
panel_joints_vertical = get_panel_joints(horizontal_grids, 'Y', panels_per_bay)
panel_ends_horizontal = get_panel_ends(panel_joints_horizontal, joint_width)
panel_ends_vertical = get_panel_ends(panel_joints_vertical, joint_width)

selected_base_level = forms.select_levels(title= 'Select Base Level',multiple= False)
selected_top_level = forms.select_levels(title= 'Select Top Level',multiple= False)
wall_height = selected_top_level.Elevation - selected_base_level.Elevation

with revit.Transaction('Create Walls'):
  # setting minimum length to ignore during wall creation
  minimum_wall_length = 2
  create_panels_from_segments(line_segments_north, 'north', minimum_wall_length)
  create_panels_from_segments(line_segments_south, 'south', minimum_wall_length)
  create_panels_from_segments(line_segments_east, 'east', minimum_wall_length)
  create_panels_from_segments(line_segments_west, 'west', minimum_wall_length)



