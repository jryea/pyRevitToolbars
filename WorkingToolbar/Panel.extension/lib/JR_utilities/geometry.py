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

def sort_curves(lines_list, axis = 'x'):
  sorted_curves = lines_list
  def sort_x(line):
    return line.GetEndPoint(0).X
  def sort_y(line):
    return line.GetEndPoint(0).Y
  if axis == 'x':
    sorted_curves.sort(key=sort_x)
  if axis == 'y':
    sorted_curves.sort(key=sort_y)
  return sorted_curves

def set_all_curves_same_direction(lines_list, vector):
  sorted_lines = []
  for line in lines_list:
    sp = line.GetEndPoint(0)
    ep = line.GetEndPoint(1)
    if vector.X == 1:
      if sp.X > ep.X:
        sorted_lines.append(line.CreateReversed())
      else:
        sorted_lines.append(line)
    if vector.X == -1:
      if sp.X < ep.X:
        sorted_lines.append(line.CreateReversed())
      else:
        sorted_lines.append(line)
    if vector.Y == 1:
      if sp.Y > ep.Y:
        sorted_lines.append(line.CreateReversed())
      else:
        sorted_lines.append(line)
    if vector.Y == -1:
      if sp.Y < ep.Y:
        sorted_lines.append(line.CreateReversed())
      else:
        sorted_lines.append(line)
  return sorted_lines

# POINTS

def get_intermediate_pts_xy(pts_xy, divisions):
  intermediate_pts_xy = []
  for i in range(len(pts_xy) - 1):
    distance = abs(pts_xy[i+1] - pts_xy[i]) / divisions
    for j in range(1, divisions):
      intermediate_pt = pts_xy[i] + distance * j
      intermediate_pts_xy.append(intermediate_pt)
  return intermediate_pts_xy

def get_intersection(line1, line2):
  results = clr.Reference[IntersectionResultArray]()
  result = line1.Intersect(line2, results)
  if result != SetComparisonResult.Overlap:
    print('No Intersection Found')
  intersection = results.Item[0]
  return intersection.XYZPoint

def get_xy_intersection(line1, line2):
  if abs(get_line_vector(line1).X) == 1:
    horiz_line = line1
  else:
    vert_line = line1
  if abs(get_line_vector(line2).X) == 1:
    horiz_line = line2
  else:
    vert_line = line2
  if horiz_line and vert_line:
    return XYZ(vert_line.GetEndPoint(0).X, horiz_line.GetEndPoint(0).Y, horiz_line.GetEndPoint(0).Z)
  else:
    print('One line needs to be horizontal and the other vertical')

def get_y_from_slope(x1, y1, x2, y2, x):
  # y = mx + c, m = slope, c = y-intercept
  m = (y2 - y1) / (x2 - x1)
  c = y1 - m * x1
  y = m * x + c
  return y

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

def get_min_max_xy_extents(lines_list):
  endpoints = []
  for line in lines_list:
    sp = line.GetEndPoint(0)
    ep = line.GetEndPoint(1)
    endpoints.extend([sp, ep])
  min_x = endpoints[0].X
  max_x = endpoints[0].X
  min_y = endpoints[0].Y
  max_y = endpoints[0].Y
  for pt in endpoints:
    if pt.X < min_x:
      min_x = pt.X
    if pt.X > max_x:
      max_x = pt.X
    if pt.Y < min_y:
      min_y = pt.Y
    if pt.Y > max_y:
      max_y = pt.Y
  return {"min_x": min_x, "max_x": max_x, "min_y": min_y, "max_y": max_y}

def get_center_point(lines_list):
  min_x = get_min_max_xy_extents(lines_list)["min_x"]
  max_x = get_min_max_xy_extents(lines_list)["max_x"]
  min_y = get_min_max_xy_extents(lines_list)["min_y"]
  max_y = get_min_max_xy_extents(lines_list)["max_y"]
  centerpoint = ((max_x + min_x) / 2, (max_y + min_y) / 2)
  return centerpoint

