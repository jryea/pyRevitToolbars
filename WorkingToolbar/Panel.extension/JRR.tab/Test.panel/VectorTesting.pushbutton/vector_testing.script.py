from Autodesk.Revit.DB import *
from pyrevit import revit, forms, script

uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document

def get_selected_element():
  selection = uidoc.Selection
  selection_ids = selection.GetElementIds()
  if len(selection_ids) < 1:
    return None
  first_element_id = selection_ids[0]
  first_element = doc.GetElement(first_element_id)
  return first_element

def get_selected_element_id():
  selection = uidoc.Selection
  selection_ids = selection.GetElementIds()
  if len(selection_ids) < 1:
    return None
  first_element = selection_ids[0]
  return first_element

selected_element = get_selected_element()

family_location = selected_element.Location.Point

#geo_objects = Autodesk.Revit.DB GeometryObject
#built_in_category = BuiltInCategory.OST_<category>)
def create_direct_shape(geo_objects,built_in_category = BuiltInCategory.OST_GenericModel):
  direct_shape = DirectShape.CreateElement(doc,ElementId(built_in_category))
  direct_shape.SetShape(geo_objects)
  return direct_shape

def visualize_as_line(vector, origin = XYZ()):
  endpoint = origin + vector
  line = Line.CreateBound(origin, endpoint)
  create_direct_shape([line])

def visualize_as_point(point):
  create_direct_shape([Point.Create(point)])

vector = XYZ(1,1.5,0)
new_vector = XYZ(0,-1,0)

with revit.Transaction('Create Geometry'):
  moved_point = family_location + new_vector
  visualize_as_line(new_vector, family_location)
  visualize_as_point(family_location)
  visualize_as_point(moved_point)
  element = get_selected_element_id()
  if element:
    ElementTransformUtils.MoveElement(doc, element, vector)
    # create_direct_shape([Point.Create(point)], BuiltInCategory.OST_Furniture)
  else:
    forms.alert('Please select element')



