from sys import argv
#script, user_name = argv
# define list of teeth

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

def main():
	norm_dentition = ["11", "12", "13", "14", "15", "16"]
	recorded_dentition = []
	for toothname in norm_dentition:
		prompt = "how long is %s? if doesn't exist, hit 'k'    " %toothname
		response = raw_input(prompt)
		if response == 'k':
			break
		else:
			recorded_dentition.append(tooth(toothname, response))

	print recorded_dentition[0].name, recorded_dentition[0].axis_length

if __name__ == "__main__":
    # execute only if run as a script
    main()


# show text in image
#cv2.putText(image, "Axis_Len_1", (100,100), cv2.FONT_HERSHEY_SIMPLEX, 3,(255,255,255),True)