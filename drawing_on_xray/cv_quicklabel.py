""" # Example usage:
python cv_quicklabel.py -f pano/ -o NORMAL_LABELS.txt -m bbox
"""
import cv2
import argparse
import os

# construct argument parser
ap = argparse.ArgumentParser()
ap.add_argument("-f", "--folder", required=True, help="Path to the image folder")
ap.add_argument("-o", "--output", required=True, help="Path to output file")
ap.add_argument("-m", "--mode", required=True, help="mode: point or bbox")
args = vars(ap.parse_args())

def square_corners(x,y,w):
	"""return 2 opposing vertices of square of width w centered at (x,y)"""
	w_half = int(0.5*w)
	x1 = x-w_half
	y1 = y-w_half
	x2 = x+w_half
	y2 = y+w_half
	return x1, y1, x2, y2

def mark_point(event,x,y,flags,param):
	"""mark point and draw square around it"""
	if event == cv2.EVENT_LBUTTONDOWN:
		x1,y1,x2,y2 = square_corners(x,y,ROI_WIDTH)
		cv2.rectangle(img, (x1,y1), (x2,y2), (0,255,0), 1)
		cv2.circle(img, (x,y), 1, (0,255,0), 1)
		# rescale again before appending:
		append_to_roi((x1,y1),(x2,y2))
		
# set mouse call back: 2-click-line
def mark_bbox(event,x,y,flags,param):
	"""mark 2 points and draw bounding rect"""
	global draw_mode, refPt
	if event == cv2.EVENT_LBUTTONDOWN and not draw_mode:
		print "IM HERE"
		cv2.circle(img, (x,y), 1, (0,255,0), 1)
		refPt[0] = (x,y)
		draw_mode = True
	elif event == cv2.EVENT_LBUTTONDOWN and draw_mode:
		cv2.circle(img, (x,y), 1, (0,255,0), 1)
		refPt[1] = (x,y)
		p1, p2 = refPt[0], refPt[1]
		cv2.rectangle(img, p1, p2, (0,255,0), 1)
		append_to_roi(p1,p2)
		draw_mode = False

def append_to_roi(p1, p2):
	filename = images[counter]
	(x1,y1), (x2,y2) = format_bbox(p1, p2)
	x1,y1,x2,y2 = [n*CONV_RATIO for n in (x1, y1, x2, y2)]
	img_roi.append("{},{},{},{},{}\n".format(filename, x1, y1, x2, y2))

def format_bbox(p1, p2):
	"""return bboxes in same format"""
	x1, y1 = p1
	x2, y2 = p2
	p1_new = (max(x1, x2), max(y1,y2))
	p2_new = (min(x1, x2), min(y1, y2))
	return p1_new, p2_new


def setup_img(filename, c_ratio):
	"""load img, create clone, resize by conversion ratio for easy display"""
	img = cv2.imread(filename)
	print "working on", filename
	img = cv2.resize(img, (0,0), fx=1/float(c_ratio), fy=1/float(c_ratio)) 
	clone = img.copy()
	return img, clone

####
images = [(args["folder"] + f) for f in os.listdir(args["folder"]) if (f[-4:] in (".TIF", ".JPG", ".PNG"))]
# region_list for *all* imgs
roi_output = []
ROI_WIDTH = 40
# points for rectangle:
global draw_mode, refPt
draw_mode = False
refPt = [(0,0), (0,0)]
# loop list img_roi for appending to global region list after img labeling end
img_roi = []
# conversion ratio for way-too-large images like my beloved TIFs
CONV_RATIO = 2
# bit inelegant but whatever, here's a loop counter: 
counter = 0
# initialise img /clone before loop:
img, clone = setup_img(images[counter], CONV_RATIO)
cv2.namedWindow("img", flags=cv2.WINDOW_NORMAL)

# mouse callback function
# keep looping until breaking with 'k'
if args["mode"] == "point":
	cv2.setMouseCallback("img", mark_point)
elif args["mode"] == "bbox":
	cv2.setMouseCallback("img", mark_bbox)

while True:
	cv2.imshow("img", img)
	key = cv2.waitKey(1) & 0xFF
	# if 'r' key is pressed, reset image
	if key == ord("r"):
		img_roi = []
		img = clone.copy()
	if key == ord("n"):
		# -- save and go to next image
		print "saving coords:", img_roi
		# add rois to global list
		roi_output.extend(img_roi)
		# reset loop roi list
		img_roi = []
		# load new image from file list
		counter += 1
		filename = images[counter]
		print "next image:", filename
		img, clone = setup_img(filename, CONV_RATIO)
	# if 'k' key pressed, cancel labeling for all images
	if key == ord("k"):
		break

# close all open windows
cv2.destroyAllWindows()
with open(args["output"], "ab") as out:
	# then write one roi on each line
	out.write("\n".join(roi_output))

"""
print "region list: \n", region_list
# TESTING:
img = cv2.imread(args["img"])
for r in region_list:
	_, x1, y1, x2, y2 = r
	cv2.rectangle(img, (x1,y1), (x2,y2), (0,255,0), -1)
CONV_RATIO = 4
img = cv2.resize(img, (0,0), fx=1/float(CONV_RATIO), fy=1/float(CONV_RATIO)) 
cv2.imshow("img", img)
key = cv2.waitKey(0)
cv2.destroyAllWindows()
"""









