
from Autodesk.Revit.DB import FilteredElementCollector, BuiltInCategory, Document, Transaction, ViewFamily, ViewFamilyType, Element, ViewDrafting
from pyrevit import revit, forms, script

doc = __revit__.ActiveUIDocument.Document

vft_col = FilteredElementCollector(doc).OfClass(ViewFamilyType)
drafting_vft = None
for vft in vft_col:
  if str(vft.ViewFamily) == 'Drafting':
    drafting_vft = vft
    break

# COLLECT SHEETS FROM USER
selected_sheets = forms.select_sheets(title='Select Sheets', button_name='Select', width=500, multiple=True, filterfunc=None, doc=None, include_placeholder=True, use_selection=False)

with revit.Transaction('Update detail view names'):

  # ITERATE THROUGH EACH SHEET
  for sheet in selected_sheets:
    #Collect all placed view ids
    placed_view_ids = sheet.GetAllPlacedViews()

    #Collect all drafting views on sheet
    placed_drafting_views = []
    for view_id in placed_view_ids:
      if str(doc.GetElement(view_id).ViewType) == 'DraftingView':
        placed_drafting_views.append(doc.GetElement(view_id))

    sheet_number = sheet.SheetNumber

    # Get the correct ViewFamilyType
    new_vft = None

    for vft in vft_col:
      # GET VIEW FAMILY TYPE WITH SHEET NAME
      if Element.Name.__get__(vft) == sheet_number:
        new_vft = vft

    if new_vft == None:
      new_vft = drafting_vft.Duplicate(sheet_number)

    new_type_id = new_vft.Id

    print(new_type_id)
    # ITERATE THROUGH EACH DRAFTING VIEW

    for view in placed_drafting_views:

      # collecting relevant view parameters
      detail_number_param = view.LookupParameter('Detail Number')
      title_on_sheet_param = view.LookupParameter('Title on Sheet')
      view_name_param = view.LookupParameter('View Name')

      # collecting name strings from view parameters
      detail_number = detail_number_param.AsString()

      #set title on sheet to section if empty
      if title_on_sheet_param.AsString():
        pass
      else:
        title_on_sheet_param.Set('Section')

      title_on_sheet = ''.join(title_on_sheet_param.AsString().splitlines())
      print(title_on_sheet)

      # #set new view name
      new_view_name = '{}/{}_{}'.format(sheet_number,detail_number,title_on_sheet)
      view.Name = new_view_name

      view.ChangeTypeId(new_type_id)

