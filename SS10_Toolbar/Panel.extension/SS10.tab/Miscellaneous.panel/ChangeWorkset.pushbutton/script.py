from Autodesk.Revit.DB import *
from pyrevit import revit, forms, script
from JR_utilities import views

uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document

## Get user selected elements
selection = uidoc.Selection
selected_element_ids = selection.GetElementIds()
selected_elements = [doc.GetElement(element_id) for element_id in selected_element_ids]

workset_col = FilteredWorksetCollector(doc)\
              .OfKind(WorksetKind.UserWorkset)
workset_list = list(workset_col)

class WorksetName(forms.TemplateListItem):
  @property
  def name(self):
    return self.Name

workset_options = [WorksetName(workset) for workset in workset_list]

target_workset = forms.SelectFromList.show(workset_options, multiselect = False, title = 'Select target workset')

target_workset_id = target_workset.Id.IntegerValue

print(target_workset)
print(target_workset.Name)
print(target_workset_id)

print(selected_elements[0].WorksetId)

with revit.Transaction('Change Workset'):
  for element in selected_elements:
    # print(element.get_Parameter(BuiltInParameter.ELEM_PARTITION_PARAM).IsReadOnly)
    if element.get_Parameter(BuiltInParameter.ELEM_PARTITION_PARAM).IsReadOnly == False:
      element.get_Parameter(BuiltInParameter.ELEM_PARTITION_PARAM).Set(target_workset_id)


