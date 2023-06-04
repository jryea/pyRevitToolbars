from Autodesk.Revit.DB import *
from pyrevit import revit, forms, script

uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document

all_linked_docs_col = FilteredElementCollector(doc).OfClass(RevitLinkInstance)
all_linked_docs_list = list(all_linked_docs_col)
all_linked_docs = [link.GetLinkDocument() for link in all_linked_docs_list]

# Pyrevit wrapper class that defines the name property for display purposes
class DocTitle(forms.TemplateListItem):
  @property
  def name(self):
    return self.Title

link_options = [DocTitle(doc) for doc in all_linked_docs]

linked_doc = forms.SelectFromList.show(link_options, multiselect = False, title='Select architectural link')

## GET ALL WALLS FROM SELECTED LINK
linked_walls = FilteredElementCollector(linked_doc) \
            .OfClass(Wall).WhereElementIsNotElementType() \
            .ToElements()

linked_doors = FilteredElementCollector(linked_doc) \
              .OfCategory(BuiltInCategory.OST_Doors) \
              .WhereElementIsNotElementType()

linked_windows = FilteredElementCollector(linked_doc) \
                .OfCategory(BuiltInCategory.OST_Windows) \
                .WhereElementIsNotElementType()


with revit.Transaction('testing...'):
  line = Line.CreateBound(XYZ(0,0,0), XYZ(10,10,10))
  direct_shape = DirectShape.CreateElement(doc, ElementId(BuiltInCategory.OST_GenericModel))
  direct_shape.SetShape([line])
 

# for window in list(linked_windows):
#   bounding_box_min = window.get_Geometry(Options()).GetBoundingBox().Min
#   bounding_box_max = window.get_Geometry(Options()).GetBoundingBox().Max
