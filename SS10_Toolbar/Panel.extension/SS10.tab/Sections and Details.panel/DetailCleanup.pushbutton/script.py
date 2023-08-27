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
  if selected_sheets:
    # ITERATE THROUGH EACH SHEET
    for sheet in selected_sheets:
      #Collect all placed view ids
      placed_view_ids = sheet.GetAllPlacedViews()

      #Collect all drafting views on sheet
      placed_drafting_views = [doc.GetElement(id) for id in placed_view_ids if str(doc.GetElement(id).ViewType) == 'DraftingView']

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
          title_on_sheet_param.Set('SECTION')

        title_on_sheet = ''.join(title_on_sheet_param.AsString().splitlines())

        # set new view name
        # Add @@@ at the end of the name to prevent the same name as another on the sheet during renaming
        if __shiftclick__:
          new_view_name = '{}/{}@@@'.format(sheet_number,detail_number)
        else:
          new_view_name = '{}/{}_{}@@@'.format(sheet_number,detail_number,title_on_sheet)
        view.Name = new_view_name
        view.ChangeTypeId(new_type_id)

      # Check to see if their are any duplicate view names not on this sheet
      view_col = FilteredElementCollector(doc) \
                   .OfCategory(BuiltInCategory.OST_Views) \
                   .WhereElementIsNotElementType()
      view_list = list(view_col)
      all_drafting_views = [view for view in view_col if str(view.ViewType) == 'DraftingView']
      for view in placed_drafting_views:
        #Take temporary @@@ off of string
        new_view_name = view.Name[0:-3]
        # Add suffix 'copy' to view if there's a duplicate in the project
        for drafting_view in all_drafting_views:
          if drafting_view.Name == new_view_name and drafting_view.Id != view.Id:
            new_view_name = view.Name[0:-3] + ' copy'
        print(new_view_name)
        view.Name = new_view_name

