# line intersections
def line_slope(p1, p2):
	dy = float(p2[1]-p1[1])
	dx = float(p2[0]-p1[0])
	try: slope = dy/dx
	except ZeroDivisionError:
		# do something more clever. gotta figure out how handle vert.lines
		slope = 100
	return slope

def y_offset(p1, p2):
	slope = line_slope(p1,p2)
	y_offset = p1[1] - slope*p1[0]
	return float(y_offset)

def is_in_range(x,y,*segment_markers):
	# check if point is actually on defined line segment
	x_series = [s[0] for s in segment_markers]
	print "x_series:", x_series
	y_series = [s[1] for s in segment_markers]
	if x < min(x_series) or x > max(x_series) or y < min(y_series) or y > max(y_series):
		return False
	else:
		return True
		
def in_range(x,y,p1,p2):
	if x < min(p1[0],p2[0]) or x > max(p1[0],p2[0]):
		return False
	elif y < min(p1[1],p2[1]) or y > max(p1[1],p2[1]):
		return False
	else: 
		return True


def segment_intersection(p1,p2,p3,p4):
	# returns intersection of line segments as int for cv2 plot function
	# solve for intersection point
	delta_slope = float(line_slope(p1,p2) - line_slope(p3,p4))
	delta_offset = float(y_offset(p3,p4) - y_offset(p1,p2))
	if delta_offset != 0 and delta_slope !=0:
		x_intersect = delta_offset / delta_slope
		y_intersect = line_slope(p1,p2)*x_intersect + y_offset(p1,p2)
		# if is_in_range(x_intersect, y_intersect, p1, p2, p3, p4):
		if in_range(x_intersect, y_intersect, p1, p2) and in_range(x_intersect, y_intersect, p3, p4):
			return (int(x_intersect),int(y_intersect))
		else: 
			return False
			# return x_intersect, y_intersect
	else: 
		return False

def numpy_intersection():
	pass
	# take list of lines 1
	# take list of lines 2
	# for line in lines_2:
	# if cross list of lines 1 -> return intersect
	# return distance intersect to points of line
	# idx = np.argwhere(np.diff(np.sign(f - g)) != 0).reshape(-1) + 0

# print is_in_range((0,2),(1,2),(3,4),(5,6))
#p1 = (0.0,-2.0)
#p2 = (3,4)
#p3 = (0.0,2.0)
#p4 = (3.0,3.5)
#print segment_intersection(p1,p2,p3,p4)

