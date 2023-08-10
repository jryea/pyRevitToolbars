import math
from Autodesk.Revit.DB import  *

# STRINGS
def does_string_contain_word(full_string, word):
  full_split_string_list = []
  string_split_by_spaces = full_string.split()
  for string_a in string_split_by_spaces:
    string_dash_sublist = string_a.split('-')
    for string_b in string_dash_sublist:
      string_underscore_sublist = string_b.split('_')
      for string_c in string_underscore_sublist:
        full_split_string_list.append(string_c.upper())
  if word.upper() in full_split_string_list:
    return True
  else:
    return False

def draw_bounding_box_rect(doc, active_view, bounding_box):
  bb_min = bounding_box.Min
  bb_max = bounding_box.Max
  tl_pt = XYZ(bb_min.X, bb_max.Y, 0)
  tr_pt = XYZ(bb_max.X, bb_max.Y, 0)
  br_pt = XYZ(bb_max.X, bb_min.Y, 0)
  bl_pt = XYZ(bb_min.X, bb_min.Y, 0)
  top_line = Line.CreateBound(tl_pt, tr_pt)
  right_line = Line.CreateBound(tr_pt, br_pt)
  bottom_line = Line.CreateBound(br_pt, bl_pt)
  left_line = Line.CreateBound(bl_pt, tl_pt)
  doc.Create.NewDetailCurve(active_view, top_line)
  doc.Create.NewDetailCurve(active_view, right_line)
  doc.Create.NewDetailCurve(active_view, bottom_line)
  doc.Create.NewDetailCurve(active_view, left_line)