# VIEWS
# check for existing view family type
def does_vft_exist(vft_list, name):
  vft_list_names = [x.Name for x in view_family_types_drafting]
  if name in vft_list:
    return true
  else:
    return false