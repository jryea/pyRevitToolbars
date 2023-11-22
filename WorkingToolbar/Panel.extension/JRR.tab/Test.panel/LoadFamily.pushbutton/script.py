from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import *
from pyrevit import revit, forms, script

uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document
active_view = uidoc.ActiveView

def is_family_loaded(document, family_name):
  family_list = get_all_families(doc)
  for family in family_list:
    if Element.Name.GetValue(family) == family_name:
      return True
  return False

def get_all_families(document):
  family_col = FilteredElementCollector(document)\
               .OfClass(Family)
  return list(family_col)

def get_symbols_from_family(document, family):
  symbol_id_list = list(family.GetFamilySymbolIds())
  symbol_list = [document.GetElement(symbol_id) for symbol_id in symbol_id_list]
  return symbol_list

def get_family_by_name(document, family_name):
  family_list = get_all_families(doc)
  for family in family_list:
    if family_name == Element.Name.GetValue(family):
      return family
  return None

def get_symbol(document, family_name, symbol_name):
  symbols = get_symbols_from_family(document, family_name)
  for symbol in symbols:
    if Element.Name.GetValue(symbol) == symbol_name:
      return symbol

def does_symbol_exist(document, family, symbol_name):
  symbols = get_symbols_from_family(document, family)
  for symbol in symbols:
    if symbol_name == Element.Name.GetValue(symbol):
      return True
  return False

def set_parameter_value(new_symbol, param_name, param_value):
  for param in new_symbol.Parameters:
    if param.Definition.Name == param_name:
      param.Set(value)

def create_family_symbol(document, family, symbol_name):
  symbol_list = get_symbols_from_family(document, family)
  cur_symbol = symbol_list[0]
  new_symbol = cur_symbol.Duplicate(symbol_name)
  set_parameter_value(new_symbol, 'Width', 8)
  return new_symbol

def insert_family_symbol(document, symbol, insertion_point):
  family_instance = document.Create.NewFamilyInstance(insertion_point, symbol, Structure.StructuralType.NonStructural)
  return family_instance

family_name = 'Test Family'
symbol_name = 'Type 1'
# The r string prefix indicates a raw string literal and will ignore \ as escape characters
family_path = r"G:\My Drive\02 Work\02 Library\Families\Test Family.rfa"
insertion_point = XYZ(0,0,0)

with revit.Transaction('Create Grids'):
  # is family loaded? if not, load family
  if not is_family_loaded(doc, family_name):
    if doc.LoadFamily(family_path):
      TaskDialog.Show('Load Family', 'Loaded family: ' + family_name)
    else:
      TaskDialog.Show('Load Family', 'Could not load family')
      exit()

  # get family object
  cur_family = get_family_by_name(doc, family_name)
  symbol_name = 'Type 1'

  if cur_family:
    # does family have symbol? if not, create it
    if not does_symbol_exist(doc, cur_family, symbol_name):
      symbol = create_family_symbol(doc, cur_family, symbol_name)
      TaskDialog.Show('Created family symbol', 'Created family symbol:' + symbol_name)
    # insert family
      if symbol:
        family_instance = insert_family_symbol(doc, symbol, insertion_point)
      else:
        TaskDialog.Show('Error', 'Could not find family symbol')



















