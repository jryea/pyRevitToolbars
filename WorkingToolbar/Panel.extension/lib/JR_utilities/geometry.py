import math
from Autodesk.Revit.DB import  *

# VECTORS

def convert_deg_to_XYZ(angle_deg):
  angle_rad = (180 - angle_deg) * math.pi / 180.0
  return XYZ(math.cos(angle_rad), math.sin(angle_rad), 0)

def get_line_vector(line):
  startpoint = line.GetEndPoint(0)
  endpoint = line.GetEndPoint(1)
  vector = endpoint - startpoint
  normalized_vector = vector.Normalize()
  return normalized_vector

# CURVES

def offset_curves(lines_list, offset):
  # returns an offset list of curves
  curve_loop = CurveLoop()
  for line in lines_list:
    curve_loop.Append(line)
  offset_curve_loop = CurveLoop.CreateViaOffset(curve_loop, offset, XYZ(0,0,1))
  return list(offset_curve_loop)

# POINTS

def get_intermediate_pts_xy(pts_xy, divisions):
  intermediate_pts_xy = []
  for i in range(len(pts_xy) - 1):
    distance = abs(pts_xy[i+1] - pts_xy[i]) / divisions
    for j in range(1, divisions):
      intermediate_pt = pts_xy[i] + distance * j
      intermediate_pts_xy.append(intermediate_pt)
  return intermediate_pts_xy

def find_intersection(line1, line2):
  results = clr.Reference[IntersectionResultArray]()
  result = line1.Intersect(line2, results)
  if result != SetComparisonResult.Overlap:
    print('No Intersection Found')
  intersection = results.Item[0]
  return intersection.XYZPoint

def find_pts_inside_xy_border(points, curve_loop):
  curves_list = list(curve_loop.GetEnumerator())
  curves_top = [curve for curve in curves_list if round(curve.GetEndPoint(0).Y, 5) == round(curve.GetEndPoint(1).Y, 5) and curve.GetEndPoint(0).X < curve.GetEndPoint(1).X ]
  curves_bottom = [curve for curve in curves_list if round(curve.GetEndPoint(0).Y, 5) == round(curve.GetEndPoint(1).Y, 5) and curve.GetEndPoint(0).X > curve.GetEndPoint(1).X ]
  curves_left = [curve for curve in curves_list if round(curve.GetEndPoint(0).X, 5) == round(curve.GetEndPoint(1).X, 5) and curve.GetEndPoint(0).Y < curve.GetEndPoint(1).Y ]
  curves_right = [curve for curve in curves_list if round(curve.GetEndPoint(0).X, 5) == round(curve.GetEndPoint(1).X, 5) and curve.GetEndPoint(0).Y > curve.GetEndPoint(1).Y ]
  points_inside_border = []
  for point in points:
    is_point_inside_top = False
    is_point_inside_bottom = False
    is_point_inside_left= False
    is_point_inside_right = False
    for curve_t in curves_top:
      curve_t_sp = curve_t.GetEndPoint(0)
      curve_t_ep = curve_t.GetEndPoint(1)
      if point.X > curve_t_sp.X and point.X < curve_t_ep.X and point.Y < curve_t_sp.Y:
        is_point_inside_top = True
    for curve_b in curves_bottom:
      curve_b_sp = curve_b.GetEndPoint(0)
      curve_b_ep = curve_b.GetEndPoint(1)
      if point.X < curve_b_sp.X and point.X > curve_b_ep.X and point.Y > curve_b_sp.Y:
        is_point_inside_bottom = True
    for curve_l in curves_left:
      curve_l_sp = curve_l.GetEndPoint(0)
      curve_l_ep = curve_l.GetEndPoint(1)
      if point.Y > curve_l_sp.Y and point.Y < curve_l_ep.Y and point.X > curve_l_sp.X:
        is_point_inside_left = True
    for curve_r in curves_right:
      curve_r_sp = curve_r.GetEndPoint(0)
      curve_r_ep = curve_r.GetEndPoint(1)
      if point.Y < curve_r_sp.Y and point.Y > curve_r_ep.Y and point.X < curve_r_sp.X:
        is_point_inside_right = True
    if is_point_inside_top == True and is_point_inside_bottom == True and is_point_inside_left == True and is_point_inside_right == True:
      points_inside_border.append(point)
  return points_inside_border

