## RETRIEVING A WALLS LAYERS USING THE REVIT API ##
# WallType --> CompoundStructure --> ComputerStructureLayer


## CREATING A WALL
# Wall.Create(document, curve, wallTypeID, levelID, height, offset, flip(bool), structural(bool))

## ASK USER FOR:
  # 1. Linked wall types to create exterior walls
  # 2. Base Level to create walls
  #   a. Top Level is extracted from current framing view

from Autodesk.Revit.DB import *
from pyrevit import revit, forms, script

uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document

active_view = doc.ActiveView

## Get user selected elements
selection = __revit__.ActiveUIDocument.Selection
selected_element_ids = selection.GetElementIds()
selected_elements = [doc.GetElement(element_id) for element_id in selected_element_ids]

wall_types_col = FilteredElementCollector(doc) \
                .OfClass(WallType)

levels_col = FilteredElementCollector(doc) \
              .OfCategory(BuiltInCategory.OST_Levels) \
              .WhereElementIsNotElementType()

## ASK USER FOR BASE LEVEL

# Pyrevit wrapper class that defines the name property for display purposes
class LevelName(forms.TemplateListItem):
  @property
  def name(self):
    return self.Name

level_options = [LevelName(level) for level in levels_col]

base_level = forms.SelectFromList.show(level_options, multiselect=False, title = 'Select base level')
current_level = active_view.GenLevel

base_level_elevation = base_level.Elevation
current_level_elevation = current_level.Elevation
base_level_id = base_level.Id
current_level_id = current_level.Id

wall_height = current_level_elevation - base_level_elevation

def get_wall_type_id_from_name(name):
  for wall_type in wall_types_col:
    if Element.Name.__get__(wall_type) == name:
      return wall_type.Id

wall_type_id = get_wall_type_id_from_name('Ext_Wall-12"')
print(wall_type_id)

def get_walls_from_selection(selection, kind = ''):
  #For specific kind of walls use 'Basic', 'Stacked', or 'Curtain'
  walls = [element for element in selection if isinstance(element, Wall)]
  specified_walls = [wall for wall in walls if str(wall.WallType.Kind) == kind]
  if kind == 'Basic' or kind == 'Stacked' or kind == 'Curtain':
    return specified_walls
  else:
    return walls

basic_walls = get_walls_from_selection(selected_elements, 'Basic')

test_wall = basic_walls[0]

def get_struct_wall_layer(wall):
  wall_layers = wall.WallType.GetCompoundStructure().GetLayers()
  struct_wall_layers = [layer for layer in wall_layers if str(layer.Function) == 'Structure']
  largest_struct_layer = struct_wall_layers[0]
  for layer in struct_wall_layers:
    if layer.Width > largest_struct_layer.Width:
      largest_struct_layer = layer
  return largest_struct_layer

def get_wall_curve(wall):
  return wall.Location.Curve

wall_layer = get_struct_wall_layer(test_wall)

wall_curve = get_wall_curve(test_wall)

with revit.Transaction('Create Wall'):
  Wall.Create(doc, wall_curve, wall_type_id, base_level_id, wall_height, 0, False, True)

# wall_types_col = FilteredElementCollector(doc) \
#                 .OfClass(WallType)

# wall_basic_list = [wall for wall in list(wall_types_col) if str(wall.Kind) == 'Basic']

# print len(list(wall_basic_list))
# for wall in wall_basic_list:
#   print(wall.GetCompoundStructure())
#   for layer in wall.GetCompoundStructure().GetLayers():
#     print(layer.Function)