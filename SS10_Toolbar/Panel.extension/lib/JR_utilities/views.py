from Autodesk.Revit.DB import *

# VIEWS
# check for existing view family type
def does_vft_exist(vft_list, name):
  vft_list_names = [x.Name for x in view_family_types_drafting]
  if name in vft_list:
    return true
  else:
    return false

def get_all_plan_views_on_sheets(view):
    if view.get_Parameter(BuiltInParameter.VIEWPORT_SHEET_NUMBER).AsString() and isinstance(view, ViewPlan):
      return view

def get_viewport_from_view(view, all_viewports):
  for viewport in all_viewports:
    if viewport.ViewId == view.Id:
      return viewport
  print('viewport not found')