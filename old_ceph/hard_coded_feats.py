# find B point: local minimum(?) of mandibular symphysis
# find ANS: anterior nasal spine
# look at middle sector, threshold or morph-open away the white nose shadow, take maxima. upper max. is probs ANS!
# find PNS: posterior nasal spine
# find A point: lower point of maxillar symphysis
# like with ANS, but this time it's the lower maximum
# find Sella: midpoint of that U shape (sella turcica)
# find gonion: inferior-posterior point of jaw (point of inflection, or local max when compared to sella-men axis)

import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import argrelextrema
from skimage.data import data_dir
from skimage.util import img_as_ubyte,img_as_int, img_as_float
from skimage import measure, io, novice, feature
from skimage.morphology import erosion, dilation, opening, closing, white_tophat, disk
from skimage.morphology import black_tophat, skeletonize, convex_hull_image
from skimage.filters import roberts, sobel, scharr, threshold_otsu, threshold_adaptive
from skimage.segmentation import felzenszwalb, slic, quickshift
from skimage.segmentation import mark_boundaries



def min_and_max(mylist):
    x_lines_min = argrelextrema(np.asarray(mylist), np.less)
    x_lines_max = argrelextrema(np.asarray(mylist), np.greater)
    # values of rel extrema
    nulist_min = []
    nulist_max = []
    for i in x_lines_min[0]:
        nulist_min.append(i)
    for i in x_lines_max[0]:
        nulist_max.append(i)
    x_lines_min = nulist_min
    x_lines_max = nulist_max
    return [x_lines_min, x_lines_max]

def hist(t):
    hist = np.histogram(t, bins=np.arange(0, 256))
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 3))
    ax1.imshow(t, cmap=plt.cm.gray, interpolation='nearest')
    ax1.axis('off')
    ax2.plot(smooth_triangle(hist[1][:-1], 3), hist[0], lw=2)
    ax2.set_title('histogram of grey values')


def trimmed(image, fraction):
    cutoff = fraction*image.shape[0]
    trimmed_image = image[cutoff::]
    return trimmed_image

def smooth_triangle(data,degree,dropVals=False):
        """performs moving triangle smoothing with a variable degree."""
        """note that if dropVals is False, output length will be identical
        to input length, but with copies of data at the flanking regions"""
        triangle=np.array(range(degree)+[degree]+range(degree)[::-1])+1
        smoothed=[]
        for i in range(degree,len(data)-degree*2):
                point=data[i:i+len(triangle)]*triangle
                smoothed.append(sum(point)/sum(triangle))
        if dropVals: return smoothed
        smoothed=[smoothed[0]]*(degree+degree/2)+smoothed
        while len(smoothed)<len(data):smoothed.append(smoothed[-1])
        return smoothed

def white_hat(image,size_selem, plot_bool=False):
    selem = disk(size_selem) #structuring element...have to look up what the argument stands for
    w_tophat = white_tophat(image, selem)
    if plot_bool:
        plot_comparison(image, w_tophat, 'white tophat')
    else:
        return w_tophat

def adaptive_thresh(image, block_size=40, plot_bool=False):
    binary_adaptive = threshold_adaptive(image, block_size, offset=10)
    if plot_bool:
        plot_comparison(image, binary_adaptive, 'binary adaptive')
    else:
        return binary_adaptive

def trim_in_x(image, mode = False):
    x_sums = np.sum(image,0)
    x_lines = argrelextrema(np.asarray(x_sums), np.less)
    nulist2 = []
    for i in x_lines[0]:
        nulist2.append(i)
    x_lines = nulist2
    li=[]
    for d in nulist2:
        li.append([d,x_sums[d]])
    li = sorted(li,key=lambda l:l[1]) # sorted(np.asarray(x_sums)[x_lines])
    x_li_local = [li[0][0],li[1][0]] # two lowest minima tend to be good jaw demarcations so far
    # print li
    # li = li[0:2,]
    if mode:
        return image[::,x_li_local[0]:x_li_local[-1]]
    else:
        return image[::,nulist2[0]:nulist2[-1]]

def plot_line_sums(image):
    # remember: IMAGE[y-coord, x-coord] for addressing

    # calc sums and smooth the resulting intensity curve:
    sm_factor = 10
    y_sums = smooth_triangle(np.sum(image, 0), sm_factor, dropVals=False)
    x_sums = smooth_triangle(np.sum(image, 1), sm_factor, dropVals=False)
    y_coord_max = np.sum(image, 0).size
    x_coord_max = np.sum(image, 1).size
    y_axis = np.arange(0, len(y_sums))[::-1]
    x_axis = np.arange(0, len(x_sums))[::-1]

    # try out local minima search:
    x_lines_min, x_lines_max = min_and_max(x_sums)
    y_lines_min, y_lines_max = min_and_max(y_sums)

    # try out guess_jawlines():
    # x_lines_min, x_lines_max = guess_jawline(min_and_max(x_sums)[0], min_and_max(x_sums)[1], x_sums, image.shape[0])

    # plot it:
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(8, 4))
    plt.gray()
    # AXES
    ax1.imshow(image)
    # ax1.hlines(guess_jawline(x_lines_min,x_lines_max, x_coord_max), 0, y_coord_max, 'b')
    y_lines_min_inverted = [(image.shape[1] - point) for point in y_lines_min] # inverted like photo axes
    x_lines_min_inverted = [(image.shape[0] - point) for point in x_lines_min] # inverted like photo axes
    x_lines_max_inverted = [(image.shape[0] - point) for point in x_lines_max]
    for line in x_lines_min:
        ax1.axhline(line, color='b') # this plots the minima of summed intensities of x-axis pixel rows
    for line in x_lines_max:
        ax1.axhline(line, color='r') # this plots the maxima of summed I...etc.
    for line in x_lines_min_inverted:
        ax2.axhline(line, color = 'g')
    for line in x_lines_max_inverted:
        ax2.axhline(line, color = 'r')
    # ax1.hlines(x_lines_min, 0, x_coord_max, 'b')
    ax2.plot(x_sums, x_axis)

    for line in y_lines_min_inverted:
        # ax3.axvline(line, color='r') # this plots the summed intensities of the pixel rows along y_axis
        pass
    # ax2.hlines(y_lines_min, 0, 420000, 'b')
    # ax2.hlines(y_lines_max, 0, x_coord_max, 'r')
    ax3.plot(y_axis,y_sums)
    ax4.axis('off')
    # ax3.plot(y_axis,y_sums)

def returnblackspace(im):
    rowlengths = []
    for rw in range(im.shape[0]):
        length = 0
        pixel = 0
        while pixel == 0:
            pixel = im[rw][im[rw].shape[0]-1-length]
            length += 1
        rowlengths.append(length)
    rowlengths = np.asarray(rowlengths)
    return rowlengths

dent = img_as_ubyte(io.imread('/Users/franzr/PycharmProjects/untitled/d1.png', as_grey=True))
skull = img_as_ubyte(io.imread('/Users/franzr/PycharmProjects/untitled/p1.png', as_grey=True))

trimmed_skull = np.asarray([row[1000:2100] for row in skull])[0:3200]

t = trimmed_skull.copy()

def threshotsu(img):
    thresh = 0.5*threshold_otsu(img)
    img[img < thresh] = 0
    img[img > thresh] = 250

def threshlayers(img):
    img[img > 180] = 255
    img[img < 180] = 0
    #img[img < 100] = 50
    #img[img < 50] = 0


rt = returnblackspace(t)
skull_grad = np.gradient(rt)  # gradient tells us where there are sudden blips, like at the naseon
z = np.arange(rt.shape[0])[::-1]  # flipped axis for gradient and rt to work with

# find naseon
naseon = [0, 0]
naseon[0] = np.where(np.absolute(skull_grad) > 20)[0][0] - 1  # this will return y coordinate of naseon blip
naseon[1] = t.shape[1] - rt[naseon[0]]  # this should return x coordinate of naseon blip


# find menton: the lowest, downward facing forward spot on the chin
menton = [0, 0]
#menton[0] = np.where(np.absolute(skull_grad) > 20)[0][-1] - 1  # minus offset to make sure we end up just before blip
menton[1] = t.shape[1] - rt[menton[0]] # x coordinate


# find pogonion: local maximum of anterior chin curvature
skullminima, skullmaxima = min_and_max(smooth_triangle(rt, 2))
pogonion = [0,0]
pogonion[0] = skullmaxima[-1] # y value of first local maximum (on chin!)
pogonion[1] = t.shape[1] - rt[pogonion[0]] # x coordinate of pogonion


def showsegments():
    # fig, ax = plt.subplot2grid(3,3)
    fig, ((ax1,ax2),(ax3,ax4)) = plt.subplots(2,2)
    ax1.imshow(np.asarray([row[0:1500] for row in skull ][0:1500]))
    ax2.imshow(np.asarray([row[0:1500] for row in skull ][1500::]))
    ax3.imshow(np.asarray([row[1500::] for row in skull ][0:1500]))
    ax4.imshow(np.asarray([row[1500::] for row in skull ][1500::]))
# showsegments()

def plotwithpoints():
    fig, ax = plt.subplots(1,1)
    ax.imshow(t, cmap=plt.cm.gray) #cmap=plt.cm.gray)
    # ax.imshow(trimmed_skull, cmap=plt.cm.gray) #cmap=plt.cm.gray)
    # ax.plot(smooth_triangle(skull_grad, 3), z, smooth_triangle(rt, 3), z)
    nas = plt.Circle((naseon[1], naseon[0]), 40, color='r', linewidth=2, fill=False) # its x,y, hence the weirdness!
    ax.add_patch(nas)
    pog = plt.Circle((pogonion[1], pogonion[0]), 40, color='r', linewidth=2, fill=False)
    ax.add_patch(pog)
    men = plt.Circle((menton[1], menton[0]), 40, color='r', linewidth=2, fill=False)
    ax.add_patch(men)
    # ax.axis('off')

plotwithpoints()

def plotcanny():
    img = img_as_ubyte(io.imread('/Users/franzr/PycharmProjects/untitled/p1.png'))
    #segments_fz = felzenszwalb(img, scale=100, sigma=0.5, min_size=50)
    # segments_slic = slic(img, n_segments=250, compactness=10, sigma=1)
    # segments_quick = quickshift(img, kernel_size=3, max_dist=6, ratio=0.5)
    fig, ax = plt.subplots(1, 3)
    fig.set_size_inches(8, 3, forward=True)
    fig.subplots_adjust(0.05, 0.05, 0.95, 0.95, 0.05, 0.05)
    #ax[0].imshow(mark_boundaries(img, segments_fz))
    ax[0].set_title("Felzenszwalbs's method")
    #ax[1].imshow(mark_boundaries(img, segments_slic))
    #ax[1].set_title("SLIC")
    #ax[2].imshow(mark_boundaries(img, segments_quick))
    #ax[2].set_title("Quickshift")
    # fig, (ax1, ax2) = plt.subplots(1, 2)
    # ax1.imshow(sobel(trimmed_skull), cmap=plt.cm.gray)
    # ax2.imshow(roberts(trimmed_skull), cmap=plt.cm.gray)

# plotcanny()

plt.show()



