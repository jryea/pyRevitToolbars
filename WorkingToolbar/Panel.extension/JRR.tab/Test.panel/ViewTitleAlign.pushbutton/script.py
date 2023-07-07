from Autodesk.Revit.DB import *
from pyrevit import revit, forms, script

doc = __revit__.ActiveUIDocument.Document

#filter func for view collection
def get_all_plan_views_on_sheets(view):
    if view.get_Parameter(BuiltInParameter.VIEWPORT_SHEET_NUMBER).AsString() and isinstance(view, ViewPlan):
      return view

def get_viewport_from_view(view, all_viewports):
  for viewport in all_viewports:
    if viewport.ViewId == view.Id:
      return viewport
  print('viewport not found')

viewport_col = FilteredElementCollector(doc)\
                    .OfClass(Viewport)
viewport_list = list(viewport_col)

target_view = forms.select_views(title = 'Select Target View Title', multiple = False, filterfunc = get_all_plan_views_on_sheets, use_selection = True)

views_to_match = forms.select_views(title = 'Select View Titles to Match', multiple = True, filterfunc = get_all_plan_views_on_sheets, use_selection = False)

target_viewport = get_viewport_from_view(target_view, viewport_list)
target_viewport_label_offset = target_viewport.LabelOffset

viewports_to_match = [get_viewport_from_view(viewport, viewport_list) for viewport in views_to_match]


with revit.Transaction('Align View title position'):
  for viewport in viewports_to_match:
    viewport.LabelOffset = target_viewport_label_offset


