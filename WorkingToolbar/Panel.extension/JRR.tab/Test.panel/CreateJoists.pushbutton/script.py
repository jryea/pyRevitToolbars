# START WITH CREATING BEAM SYSTEM FOR LOWER LEFT
# EXTEND TO INCLUDE ALL BOTTOM BEAM SYSTEMS BETWEEN FIRST TWO GRIDS
# EXTEND TO INCLUDE ALL MIDDLE BEAM SYSTEMS
# EXTEND TO INCLUDE TOP BEAM SYSTEM BETWEEN LAST TWO GRIDS

# COLLECT HORIZONTAL GRIDS
# COLLECT TEXT NOTES OF SPECIFIC TYPE
# COLLECT JOIST TYPES
# COLLECT REFERENCE PLANES
# COLLECT LINES
  # COLLECT VERTICAL BLUE LINES
  # COLLECT RED BORDER SEGMENTS
    # COLLECT TOP BORDER SEGMENTS
    # COLLECT RIGHT BORDER SEGMENTS
    # COLLECT BOTTOM BORDER SEGMENTS
    # COLLECT LEFT BORDER SEGMENTS

# 1. CREATE BEAM SYSTEMS
  # I. START WITH ROW BETWEEN GRID(0) AND GRID(1)
    # A. COLLECT SEQUENTIAL XY POINTS
      # I. grid(0) to grid(1):
        # 1. collect right edge (blue vertical segment)
        # 2. collect border segments left of right edge and below grid(1)
        # 3. Top Left point: get intersection of grid(1) and left sections
        # 4. Top Right point: get intersection of grid(1) and right blue edge
        # 5. Bottom Right point: get intersection of right blue edge and intersecting border edge
        # 6. Bottom Left segments(points):
          # a. get endpoint of segment that intersects with blue line
          # b. loop through segments and collect all endpoints that intersect with previous line
          # c. if endpoint of current segment is greater than grid(1).Y stop loop
        # 7. get text note within border (write function for this with args(top,right,bottom,left))
    # B. GET CORRECT REFERENCE PLANE
    # C. CREATE LIST OF XYZ POINTS:
      # a. loop through each XY point and add z
    # D. GET TEXTNOTE
    # D. CREATE LIST OF SEGMENTS FOR BEAM SYSTEM
    # E. COLLECT DESIRED JOIST TYPE
      # a. If this doesn't exist use default beam type
      # b. print message to let user know this
    # F. COLLECT SPACING FROM TEXTNOTE


# public static BeamSystem Create(
# 	Document document,
# 	IList<Curve> profile,
# 	Level level,
# 	XYZ direction,
# 	bool is3d
# )

from Autodesk.Revit.DB import *
from pyrevit import revit, forms, script
import JR_utilities as utils
from JR_utilities import geometry, ref_elements, elements

uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document
active_view = doc.ActiveView

def get_joist_info_from_textnote(textnote):
  text = textnote.Text
  text_split = text.split()
  joist_info = {"type": text_split[0], "spacing": float(text_split[2])}
  return joist_info

def find_textnote(bl_pt, tr_pt, textnotes):
  textnote_current = None
  for textnote in textnotes:
    textnote_pt = textnote.Coord
    if textnote_pt.X > bl_pt[0] and textnote_pt.X < tr_pt[0]\
    and textnote_pt.Y > bl_pt[1] and textnote_pt.Y < tr_pt[1]:
      textnote_current = textnote
  if textnote_current:
    return textnote_current
  else:
    print('There was no text found within the boundaries')

def create_closed_loop_from_pts(pts_list):
  line_list = []
  for i in range(0, len(pts_list)):
    if i < len(pts_list) - 1:
      line_current = Line.CreateBound(pts_list[i], pts_list[i + 1])
    else:
      line_current = Line.CreateBound(pts_list[i], pts_list[0])
    line_list.append(line_current)
  return line_list

def create_joists(lines_list, textnote, joist_type_list, default_beam_type, default_spacing, joist_symbol):
  rp_sp = lines_list[-1].GetEndPoint(1)
  rp_ep = lines_list[-1].GetEndPoint(0)
  rp_third_pt = lines_list[0].GetEndPoint(1)
  rp_cur = doc.Create.NewReferencePlane2(rp_sp, rp_ep, rp_third_pt, active_view)
  print(rp_cur)
  plane = rp_cur.GetPlane()
  print(plane)
  sketch_plane = SketchPlane.Create(doc, plane)
  print(sketch_plane)
  desired_joist_type = get_joist_info_from_textnote(textnote)["type"]
  desired_joist_spacing = get_joist_info_from_textnote(textnote)["spacing"]
  joist_type = default_beam_type
  joist_spacing = default_spacing
  cp_xy = geometry.get_center_point(lines_list)
  xy_extents = geometry.get_min_max_xy_extents(lines_list)
  horizontal_width = xy_extents['max_x'] - xy_extents['min_x']
  vertical_height = xy_extents['max_y'] - xy_extents['min_y']
  cp_xyz = XYZ(cp_xy[0], cp_xy[1], 0)
  if desired_joist_type:
    for joist_t in joist_type_list:
      if desired_joist_type == Element.Name.GetValue(joist_t):
        joist_type = joist_t
  else:
    print('Joist type not found. Using default beam type')
  if desired_joist_spacing:
    joist_spacing = desired_joist_spacing
  # 2D BEAM SYSTEM:
  # beam_system_cur = BeamSystem.Create(doc, lines_list, active_view.GenLevel, 1, False)
  # 3D BEAM TEST:
  beam_system_cur = BeamSystem.Create(doc, lines_list, sketch_plane, 1)
  beam_system_cur.BeamType = joist_type
  beam_system_cur.get_Parameter(BuiltInParameter.JOIST_SYSTEM_FIXED_SPACING_PARAM).Set(joist_spacing)
  joist_dc = doc.Create.NewFamilyInstance(cp_xyz, joist_symbol, active_view)
  joist_dc.LookupParameter('L1A').Set(horizontal_width / 2)
  joist_dc.LookupParameter('L1B').Set(horizontal_width / 2)
  joist_dc.LookupParameter('L2A').Set(vertical_height / 2)
  joist_dc.LookupParameter('L2B').Set(vertical_height / 2)
  text_string_xyz = XYZ(cp_xyz.X + 10, cp_xyz.Y + 10, 0)
  text_string = desired_joist_type + ' @ ' + str(desired_joist_spacing) + "'"
  textnote_cur = TextNote.Create(doc, active_view.Id, text_string_xyz, .05, text_string, new_textnote_type_id)
  leader = textnote_cur.AddLeader(TextNoteLeaderTypes.TNLT_STRAIGHT_L)
  leader.End = cp_xyz
  leader.Elbow = XYZ(leader.Elbow.X - 3, leader.Elbow.Y, 0)

grid_col = FilteredElementCollector(doc)\
            .OfClass(Grid)
textnote_col = FilteredElementCollector(doc, active_view.Id)\
              .OfClass(TextNote)\
              .WhereElementIsNotElementType()
textnote_type_col = FilteredElementCollector(doc)\
                    .OfClass(TextNoteType)
beam_type_col = FilteredElementCollector(doc)\
                .OfCategory(BuiltInCategory.OST_StructuralFraming)\
                .WhereElementIsElementType()
ref_plane_col = FilteredElementCollector(doc)\
                .OfClass(ReferencePlane)
curve_element_col = FilteredElementCollector(doc, active_view.Id)\
                    .OfClass(CurveElement)
symbol_col = FilteredElementCollector(doc)\
             .OfClass(FamilySymbol)


grid_list = list(grid_col)
textnote_list = list(textnote_col)
textnote_type_list = list(textnote_type_col)
beam_type_list = list(beam_type_col)
ref_plane_list = list(ref_plane_col)
curve_element_list = list(curve_element_col)
symbol_list = list(symbol_col)

horiz_grids = [grid for grid in grid_list\
              if abs(ref_elements.get_grid_vector(grid).X) == 1]
horiz_grids = ref_elements.sort_grids_by_axis(horiz_grids, 'Y')
textnote_list = [textnote for textnote in textnote_list\
                if Element.Name.GetValue(textnote) == 'SS10 JOIST SCRIPT']
tos_ref_planes = [rp for rp in ref_plane_list\
                  if utils.does_string_contain_word(Element.Name.GetValue(rp), 'tos')]
border_lines = [line.GeometryCurve for line in curve_element_list\
                if line.LineStyle.Name == 'IMEG_00-RED-CONSTRUCTION LINE']
joist_divider_lines = [line.GeometryCurve for line in curve_element_list\
                if line.LineStyle.Name == 'IMEG_00-BLUE-CONSTRUCTION LINE']
joist_divider_lines = geometry.sort_curves(joist_divider_lines, 'x')
joist_divider_lines = geometry.set_all_curves_same_direction(joist_divider_lines, XYZ(0, -1, 0))

# for textnote in texnote_type_list:
#   print(Element.Name.GetValue(textnote))

default_spacing = float(6)
default_beam_type_id = doc.GetDefaultFamilyTypeId(ElementId(BuiltInCategory.OST_StructuralFraming))
default_beam_type = doc.GetElement(default_beam_type_id)
joist_extents_dc = elements.get_symbol_by_family_and_name('Standard', 'SS10 - Joist Span Direction - Annotation', symbol_list)
new_textnote_type_id = doc.GetDefaultElementTypeId(ElementTypeGroup.TextNoteType)
for tn_type in textnote_type_list:
  print(Element.Name.GetValue(tn_type))
  if Element.Name.GetValue(tn_type) == 'IMEG_3/32" Arial (circle)':
    new_textnote_type_id = tn_type.Id

joist_borders_list = []
joist_pts_xy = []
joist_pts_xyz = []

# COLLECT SEQUENTIAL XY POINTS (LOWER LEFT)
right_border = None
for line in joist_divider_lines:
  sp = line.GetEndPoint(0)
  ep = line.GetEndPoint(1)
  if sp.Y > horiz_grids[1].Curve.GetEndPoint(0).Y\
  and ep.Y < horiz_grids[0].Curve.GetEndPoint(1).Y:
    right_border = line
    break
right_border_x = right_border.GetEndPoint(0).X
bottom_left_segments = [line for line in border_lines if\
                        (line.GetEndPoint(0).X < right_border_x\
                        or line.GetEndPoint(1).X < right_border_x)\
                        and (line.GetEndPoint(0).Y < horiz_grids[1].Curve.GetEndPoint(0).Y\
                        or line.GetEndPoint(1).Y < horiz_grids[1].Curve.GetEndPoint(0).Y)]
print(str(len(bottom_left_segments)) + ' segments in bottom right segments')
start_segment = None
end_segment = None
for line in bottom_left_segments:
  if line.Intersect(right_border) == SetComparisonResult.Overlap:
    start_segment = line
  if line.GetEndPoint(1).Y >= round(horiz_grids[1].Curve.GetEndPoint(0).Y, 2):
    end_segment = line
tl_pt = (end_segment.GetEndPoint(0).X, horiz_grids[1].Curve.GetEndPoint(0).Y)
tr_pt = (right_border_x, horiz_grids[1].Curve.GetEndPoint(0).Y)
br_pt = (right_border_x, start_segment.GetEndPoint(0).Y)
bl_pt = (end_segment.GetEndPoint(0).X, start_segment.GetEndPoint(0).Y)
joist_pts_xy.extend([tl_pt, tr_pt, br_pt, bl_pt])

ref_plane_current = None
for rp in tos_ref_planes:
  rp_sp = rp.BubbleEnd
  rp_ep = rp.FreeEnd
  if rp_sp.Y < horiz_grids[0].Curve.GetEndPoint(0).Y\
  and rp_ep.Y > horiz_grids[1].Curve.GetEndPoint(0).Y:
    ref_plane_current = rp
rp_sp = ref_plane_current.BubbleEnd
rp_ep = ref_plane_current.FreeEnd
rp_plane = ref_plane_current.GetPlane()

# For slope, reference plane Y = X, and Z = Y
for point in joist_pts_xy:
  point_z = geometry.get_y_from_slope(rp_sp.Y, rp_sp.Z, rp_ep.Y, rp_ep.Z, point[1])
  # point_z = float(0)
  joist_pts_xyz.append(XYZ(point[0], point[1], point_z))
joist_border = create_closed_loop_from_pts(joist_pts_xyz)
joist_textnote = find_textnote(bl_pt, tr_pt, textnote_list)

with revit.Transaction('Create Joist Beam Systems'):
  # sketch_plane = SketchPlane.Create(doc, rp_plane)
  create_joists(joist_border, joist_textnote, beam_type_list, default_beam_type, default_spacing, joist_extents_dc)
