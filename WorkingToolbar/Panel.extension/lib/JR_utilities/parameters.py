## Based on Michael Kilkelly's How-To lesson
## First checks for an instance parameter, then defaults to type if instance isn't found
def get_instance_or_type_parameter_by_name(element, param_name):
  cur_param = element.LookupParameter(param_name)
  if cur_param == None:
    # element.Document returns the document where the element resides
    cur_type = element.Document.GetElement(element.GetTypeId())
    if cur_type != None:
      cur_param = cur_type.LookupParameter(param_name)
  if cur_param != None:
    return cur_param
  else:
    return None
