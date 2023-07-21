from Autodesk.Revit.DB import *
from pyrevit import revit, forms, script

uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document

## Get user selected elements
selection = uidoc.Selection
selected_element_ids = selection.GetElementIds()
selected_elements = [doc.GetElement(element_id) for element_id in selected_element_ids]

def get_drafting_views_from_views(view):
    if isinstance(view, ViewDrafting):
      return view

with revit.Transaction('transaction'):
  if selected_elements: 
    desired_view_id = forms.select_views(title='Select new reference view', multiple = False, filterfunc=get_drafting_views_from_views).Id
    if desired_view_id:
      print('SECTION VIEW REFERENCES CHANGED:')
      print('------------------------------------------------------------------------------')
      for element in selected_elements:
        reference_id = element.Id
        try:
          old_view_id = ReferenceableViewUtils.GetReferencedViewId(doc,reference_id)
          old_view = doc.GetElement(old_view_id).Title
          new_view = doc.GetElement(desired_view_id).Title
          print(old_view + " Changed to: " + new_view)
          ReferenceableViewUtils.ChangeReferencedView(doc, reference_id, desired_view_id)
        except:
          forms.alert('Please select only sections that reference drafting views')
          break
        






