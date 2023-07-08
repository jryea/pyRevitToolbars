from Autodesk.Revit.DB import *

# SYMBOLS

def get_symbol_by_name(symbol_name, all_symbols):
  symbol = None
  for e in all_symbols:
    if Element.Name.GetValue(e) == symbol_name:
      symbol = e
  if not symbol:
    print(symbol_name + ' not found')
  else:
    return symbol

# WALLS

def get_walls_from_selection(selection, kind = ''):
  #For specific kind of walls use 'Basic', 'Stacked', or 'Curtain'
  walls = [element for element in selection if isinstance(element, Wall)]
  specified_walls = [wall for wall in walls if str(wall.WallType.Kind) == kind]
  if kind == 'Basic' or kind == 'Stacked' or kind == 'Curtain':
    return specified_walls
  else:
    return walls

def get_walls_of_kind(walls, kind = ''):
  #For specific kind of walls use 'Basic', 'Stacked', or 'Curtain'
  walls_list = list(walls)
  specified_walls = [wall for wall in walls_list if str(wall.WallType.Kind) == kind]
  if kind == 'Basic' or kind == 'Stacked' or kind == 'Curtain':
    return specified_walls
  else:
    return walls
  
# BEAMS
# Returns list of connected beam points
def get_beam_pts_from_sorted_columns(document, columns, max_length):
  all_beam_list = []
  beam_group_list = []
  for column in columns:
    top_level = document.GetElement(column.get_Parameter(BuiltInParameter.FAMILY_TOP_LEVEL_PARAM).AsElementId())
    level_elevation = top_level.Elevation
    level_offset = column.get_Parameter(BuiltInParameter.FAMILY_TOP_LEVEL_OFFSET_PARAM).AsDouble()
    pt_z = level_elevation + level_offset
    beam_location = column.Location.Point
    beam_pt = XYZ(beam_location.X, beam_location.Y, pt_z)
    if len(beam_group_list) == 0:
      beam_group_list.append(beam_pt)
    elif len(beam_group_list) > 0 and int(beam_pt.X - beam_group_list[-1].X) <= max_length and int(beam_pt.Y) == int(beam_group_list[-1].Y):
      beam_group_list.append(beam_pt)
    else:
      if len(beam_group_list) > 1:
        all_beam_list.append(beam_group_list)
        beam_group_list = [beam_pt]
      else:
        beam_group_list = [beam_pt]
  if beam_group_list > 1:
    all_beam_list.append(beam_group_list)
  return all_beam_list


# COLUMNS

def sort_columns(columns):
  sorted_columns = columns
  def sort_x(column):
    return column.Location.Point.X
  def sort_y(column):
    return column.Location.Point.Y
  sorted_columns.sort(key=sort_x)
  sorted_columns.sort(key=sort_y)
  return sorted_columns