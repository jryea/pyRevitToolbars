from Autodesk.Revit.DB import *
from pyrevit import revit, forms, script
import JR_utilities as utils
from JR_utilities import ref_elements, geometry, elements, annotations

uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document
active_view = uidoc.ActiveView

reference_plane_col = FilteredElementCollector(doc)\
                      .OfClass(ReferencePlane)
curve_element_col = FilteredElementCollector(doc, active_view.Id) \
                    .OfClass(CurveElement)
curve_element_list = list(curve_element_col)
rp_list = list(reference_plane_col)
floor_lines = [line.GeometryCurve for line in curve_element_list if str(line.LineStyle.Name) == 'IMEG_00-RED-CONSTRUCTION LINE']

rp_slope = rp_list[-1]

print(ref_elements.get_z_elev_from_y_and_rp_slope(rp_slope, 601.5))

# line_segments_west = [line for line in floor_lines if int((geometry.get_line_vector(line).Y) == 1)]
# line_segments_east = [line for line in floor_lines if int((geometry.get_line_vector(line).Y) == -1)]

# def create_clockwise_curve_loop(lines_list):
#   cw_curve_loop = []
#   horiz_lines = [line for line in lines_list if abs(geometry.get_line_vector(line).X) == 1]
#   vert_lines = [line for line in lines_list if abs(geometry.get_line_vector(line).Y) == 1]
#   ## Find highest horizontal line
#   top_horiz_line = horiz_lines[0]
#   print('------------------------------')
#   print('Starting horizontal line')
#   print('------------------------------')
#   print('top horizontal line start point: ' + str(top_horiz_line.GetEndPoint(0)))
#   print('top horizontal line end point: ' + str(top_horiz_line.GetEndPoint(1)))
#   print('top horizontal line vector: ' + str(geometry.get_line_vector(top_horiz_line)))
#   for line in horiz_lines:
#     top_horiz_line_sp = top_horiz_line.GetEndPoint(0)
#     line_sp = line.GetEndPoint(0)
#     if line_sp.Y > top_horiz_line_sp.Y:
#       top_horiz_line = line
#   # set vector to [1,0,0] if not already
#   if geometry.get_line_vector(top_horiz_line).X == -1:
#     top_horiz_line = top_horiz_line.CreateReversed()
#   # set this line to be the first line in the curve loop
#   cw_curve_loop.append(top_horiz_line)
#   print('last item in cw_curve_loop: ' + str(cw_curve_loop[-1]))

#   print('------------------------------')
#   print('End horizontal line')
#   print('------------------------------')
#   print('top horizontal line start point: ' + str(top_horiz_line.GetEndPoint(0)))
#   print('top horizontal line end point: ' + str(top_horiz_line.GetEndPoint(1)))
#   print('top horizontal line vector: ' + str(geometry.get_line_vector(top_horiz_line)))
#   #Keep looping until new curve loop list is as long as input line list
#   while len(cw_curve_loop) < len(lines_list):
#     next_line = None
#     cur_cw_line = cw_curve_loop[-1]
#     for line in lines_list:
#       print('last item in cw_curve_loop: ' + str(cw_curve_loop[-1]))
#       print('last item in cw_curve_loop: ' + str(cur_cw_line))
#       cur_cw_line_ep = cur_cw_line.GetEndPoint(1)
#       # ASSUME ALTERNATING HORIZONTAL AND VERTICAL LINES
#       if line.Intersect(cur_cw_line) == SetComparisonResult.Overlap:
#         print('Overlap!!!')
#         if next_line == None:
#           next_line = line
#         else:
#           line_sp = line.GetEndPoint(0)
#           next_line_sp = next_line.GetEndPoint(0)
#           if abs(geometry.get_line_vector(cur_cw_line).X) == 1:
#             if abs(cur_cw_line_ep.X - line_sp.X) < abs(cur_cw_line_ep.X - next_line_sp.X):
#               next_line = line
#           if abs(geometry.get_line_vector(cur_cw_line).Y) == 1:
#             if abs(cur_cw_line_ep.Y - line_sp.Y) < abs(cur_cw_line_ep.Y - next_line_sp.Y):
#               next_line = line
#       next_line_sp = next_line.GetEndPoint(0)
#       next_line_ep = next_line.GetEndPoint(1)
#       if abs(geometry.get_line_vector(cur_cw_line).X) == 1:
#         if abs(cur_cw_line_ep.Y - next_line_sp.Y) < abs(cur_cw_line_ep.Y - next_line_ep.Y):
#           cw_curve_loop.append(next_line)
#         else:
#           cw_curve_loop.append(next_line.CreateReversed())
#       if abs(geometry.get_line_vector(cur_cw_line).Y) == 1:
#         if abs(cur_cw_line_ep.X - next_line_sp.X) < abs(cur_cw_line_ep.X - next_line_ep.X):
#           cw_curve_loop.append(next_line)
#         else:
#           cw_curve_loop.append(next_line.CreateReversed())
#   print(len(cw_curve_loop))
#   return cw_curve_loop

# print(len(floor_lines))
# cw_curves_list = create_clockwise_curve_loop(floor_lines)
# print(len(cw_curves_list))
# for i, curve in enumerate(cw_curves_list):
#   print('curve {}:'.format(i))
#   print('sorted curve start point :' + str(curve.GetEndPoint(0)))
#   print('sorted curve end point :' + str(curve.GetEndPoint(1)))

# curve_loop_testing = CurveLoop.Create(cw_curves_list)

















