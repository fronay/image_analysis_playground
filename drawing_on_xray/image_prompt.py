### Playing around with OPG xray metrics...
### First press "D" to draw in borders of maxillary/mandibular bone
### Second press "A" to mark axis of teeth
### Press "K" to exit when done -> script should print out pixel lengths as
### well as above-bone/within-bone length ratio of marked teeth
### Based on CV2 image editing tutorial

# manual path append, cv2 won't work with messed-up python setup otherwise...
import sys
sys.path.append('/usr/local/lib/python2.7/site-packages')
# the rest are actually needed libs:
import cv2
import argparse
from prompt_teeth import tooth, euclidian_dist
from helper_functions import *
#from test_drawing import interactive_drawing

first_point_marked = False
refPt = []
dentition_record = []
tooth_number = 1

###remove these (for drawing function):
drawing=False # true if mouse is pressed
mode=True # if True, draw rectangle. Press 'm' to toggle to curve


###
# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True, help="Path to the image")
args = vars(ap.parse_args())

def draw_circle_mark(image,x,y):
	cv2.circle(image,(x,y),1,(0,255,0),-1)

def display_text(image, text):
	cv2.putText(image, text, (100,100), cv2.FONT_HERSHEY_SIMPLEX, 2,(10,100,255),True)

# set mouse call back: 2-click-line
def mark_axis_points(event,x,y,flags,param):
	global refPt, first_point_marked, tooth_number

	if event == cv2.EVENT_LBUTTONDOWN and not first_point_marked:
		draw_circle_mark(image,x,y)
		first_point_marked = True
		refPt = [(x, y)]

	elif event == cv2.EVENT_LBUTTONDOWN and first_point_marked:
		draw_circle_mark(image,x,y)
		refPt.append((x, y))
		cv2.line(image, refPt[0], refPt[1], (100,200,0), thickness=1, shift=0)
		# now that both axis tips have been defined, add a tooth to record
		dentition_record.append(tooth("tooth_no." + str(tooth_number),refPt[0], refPt[1]))
		tooth_number += 1
		refPt = []
		first_point_marked = False

def euclidian_dist(p1,p2):
	# return line length between 2 (tuple) coordinates 
	dy = p1[0]-p2[0]
	dx = p1[1]-p2[1]
	dist = (dy*dy + dx*dx) ** 0.5
	return dist

class tooth:
    def __init__(self, name, crowntip, roottip):
        self.name = name 
        self.crowntip = crowntip
        self.roottip = roottip
        self.axis_length = euclidian_dist(crowntip, roottip)
        self.crownlength = "n/a"
        self.rootlength = "n/a"

    def add_bone_intersect(self, bone_intersect):
    	self.crownlength = euclidian_dist(self.crowntip, bone_intersect)
    	self.rootlength = euclidian_dist(self.roottip, bone_intersect)

# load the image, clone it, and setup the mouse callback function
image = cv2.imread(args["image"])
clone = image.copy()
cv2.namedWindow("image")

####
# mouse callback function
def interactive_drawing(event,x,y,flags,param):
	global ix,iy,drawing, mode, image
	# print "in interactive_drawing"
	if event==cv2.EVENT_LBUTTONDOWN:
		drawing=True
		ix,iy=x,y
		print "noticed button press"
	elif event==cv2.EVENT_MOUSEMOVE:
		if drawing==True:
			if mode==True:
				pass
				# draw line between former and present pixel
				cv2.line(image,(ix,iy),(x,y),(0,0,255),thickness = 1) 
				### check for collisions with tooth axis:
				for d in dentition_record:
					intersect = segment_intersection((ix,iy),(x,y),d.roottip,d.crowntip)
					if intersect:
						cv2.circle(image,intersect,2,(0,255,0),-1)
						d.add_bone_intersect(intersect)
				ix=x # save former x coordinate
				iy=y # save former y coordinate
		# print "noticed  event mousemove"""
	elif event==cv2.EVENT_LBUTTONUP:
		drawing=False
		if mode==True:
			pass
	return x,y

#####

# keep looping until the 'k' key is pressed
while True:
	cv2.imshow("image", image)
	key = cv2.waitKey(1) & 0xFF
	if key == ord("a"):
		cv2.setMouseCallback("image", mark_axis_points)
	if key == ord("d"):
		cv2.setMouseCallback("image", interactive_drawing)
	# if the 'r' key is pressed, reset the cropping region
	if key == ord("r"):
		image = clone.copy()

	# if the 'k' key is pressed, break from the loop
	if key == ord("k"):
		break


# if there are two reference points, then crop the region of interest
# from the image and display it

 
# close all open windows
cv2.destroyAllWindows()
for d in dentition_record:
	print "tooth: ", d.name, " ax_len: ", d.axis_length, " rt_len: ", d.rootlength, " cr_len: ", d.crownlength

# show xray with prompt (e.g. please mark roottip/crowntip of incisor 11)
# (check if previous lines from toothlist present -> show them on xray)
# notice button down -> mark first point
# notice button down -> mark second point
# (cancel using 'r' -> delete line)
# update tooth list
# show xray with new tooth-axis marked (+ rounded axial length) & new prompt
# ...

# extra function for drawing bone curve