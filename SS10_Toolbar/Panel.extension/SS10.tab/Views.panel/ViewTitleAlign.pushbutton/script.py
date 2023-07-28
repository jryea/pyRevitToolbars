from Autodesk.Revit.DB import *
from pyrevit import revit, forms, script
from JR_utilities import views
doc = __revit__.ActiveUIDocument.Document

viewport_col = FilteredElementCollector(doc)\
                    .OfClass(Viewport)
viewport_list = list(viewport_col)

target_view = forms.select_views(title = 'Select Target View Title', multiple = False, filterfunc = views.get_all_plan_views_on_sheets, use_selection = True)

views_to_match = forms.select_views(title = 'Select View Titles to Match', multiple = True, filterfunc = views.get_all_plan_views_on_sheets, use_selection = False)

target_viewport = views.get_viewport_from_view(target_view, viewport_list)
target_viewport_label_offset = target_viewport.LabelOffset

viewports_to_match = [views.get_viewport_from_view(viewport, viewport_list) for viewport in views_to_match]


with revit.Transaction('Align View Title Position'):
  for viewport in viewports_to_match:
    viewport_x_dif = viewport.GetBoxOutline().MinimumPoint.X - target_viewport.GetBoxOutline().MinimumPoint.X
    print(viewport_x_dif)
    viewport_y_dif = viewport.GetBoxOutline().MinimumPoint.Y - target_viewport.GetBoxOutline().MinimumPoint.Y
    print(viewport_y_dif)
    adjusted_target_viewport_label_offset = XYZ(target_viewport_label_offset.X - viewport_x_dif,target_viewport_label_offset.Y - viewport_y_dif, 0)
    print(adjusted_target_viewport_label_offset)
    viewport.LabelOffset = adjusted_target_viewport_label_offset


