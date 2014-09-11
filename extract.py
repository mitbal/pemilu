from skimage import io
from skimage import color
from skimage.transform import hough_line, hough_line_peaks
from skimage.transform import PiecewiseAffineTransform, warp
from skimage.filter import threshold_otsu
import numpy as np
import matplotlib.pyplot as plt
import os

def calcIntersection(x1, y1, x2, y2, x3, y3, x4, y4):
    """ Calculate the intersection points between two lines """
    px = ((x1*y2 - y1*x2)*(x3-x4) - (x1-x2)*(x3*y4 - y3*x4)) / ((x1-x2)*(y3-y4) - (y1-y2)*(x3-x4))
    py = ((x1*y2 - y1*x2)*(y3-y4) - (y1-y2)*(x3*y4 - y3*x4)) / ((x1-x2)*(y3-y4) - (y1-y2)*(x3-x4))
    
    return (px, py)

def calc_distance(p1, p2):
    """ Calculate distance between two points """
    dist = 0
    for i in xrange(len(p1)):
        dist += (p1[i] - p2[i])*(p1[i] - p2[i])
    return dist

def search_closest_points(p, points):
    """ Search for queried point p the closest point in the set of points points """ 
    min_dist = 1000000000
    cp = None
    for i in xrange(len(points)):
        dist = calc_distance(p, points[i])
        if dist < min_dist:
            min_dist = dist
            cp = points[i]
    return cp

def extract_digits(fname):
    """ Extract the sub images of digits from the scanned image

    fname is the filename of the image
    """
    c1 = io.imread(fname)

    # Cropped the region of interest and convert to grayscale
    dim = c1.shape
    y0 = 350; y1 = y0+450;
    if dim[0] < 1100:
        y0 = dim[0]*300/1700; y1 = y0 + dim[0]*400/1700
    elif dim[0] > 1700 and dim[0] < 2400:
        y0 = 350; y1 = y0+450;
    else:
        y0 = dim[0]*350/1700; y1 = y0 + dim[0]*450/1700
    x0 = dim[1]*19/24

    cropped = c1[y0:y1, x0:]
    gcrop = color.rgb2gray(cropped)

    # Threshold to create binary image
    thresh = threshold_otsu(gcrop)
    gcrope = gcrop < thresh

    # Find the lines that makes the boundary box using Hough Transform
    h, theta, d = hough_line(gcrope)

    # Divide the hough space for searching the different horizontal and vertical lines
    hcropv = h[:, 60:120]
    hcroph = h[:, 0:30]

    rows, cols = gcrope.shape
    # Vertical lines
    VL = []
    for _, angle, dist in zip(*hough_line_peaks(h, theta, d, min_distance=100, min_angle=9, num_peaks=2)):
        y0 = (dist - 0 * np.cos(angle)) / np.sin(angle)
        y1 = (dist - cols * np.cos(angle)) / np.sin(angle)
        VL += [((0, y0), (cols, y1))]
        #plt.plot((0, cols), (y0, y1), '-r')
    # Horizontal lines
    HL = []
    for _, angle, dist in zip(*hough_line_peaks(hcroph, theta, d, min_distance=250, min_angle=9, num_peaks=2)):
        y0 = (dist - 0 * np.cos(angle)) / np.sin(angle)
        y1 = (dist - cols * np.cos(angle)) / np.sin(angle)
        HL += [((0, y0), (cols, y1))]
        #plt.plot((0, cols), (y0, y1), '-r')

    if len(HL) != 2 or len(VL) != 2:
        return

    # Calculate the intersection between points using determinants
    p1 = calcIntersection(VL[0][0][0], VL[0][0][1], VL[0][1][0], VL[0][1][1], HL[0][0][0], HL[0][0][1], HL[0][1][0], HL[0][1][1])
    p2 = calcIntersection(VL[0][0][0], VL[0][0][1], VL[0][1][0], VL[0][1][1], HL[1][0][0], HL[1][0][1], HL[1][1][0], HL[1][1][1])
    p3 = calcIntersection(VL[1][0][0], VL[1][0][1], VL[1][1][0], VL[1][1][1], HL[0][0][0], HL[0][0][1], HL[0][1][0], HL[0][1][1])
    p4 = calcIntersection(VL[1][0][0], VL[1][0][1], VL[1][1][0], VL[1][1][1], HL[1][0][0], HL[1][0][1], HL[1][1][0], HL[1][1][1])

    # Transform the region of interest into correct orientation and scale
    src_points = [(0,0), (210, 0), (0, 400), (210, 400)]
    dim = cropped.shape
    corners = [(0,0), (dim[0], 0), (0, dim[1]), (dim[0], dim[1])]

    src = np.array(src_points)

    dest_points = [[] for x in range(4)]
    points = [p1, p2, p3, p4]

    for i in xrange(4):
        dest_points[i] = search_closest_points(corners[i], points)

    dst = np.array(dest_points)

    tform = PiecewiseAffineTransform()
    tform.estimate(src, dst)
    warped = warp(gcrope, tform, output_shape=(400, 210))

    # Prepare the directory
    if not os.path.exists('extracted'):
        os.makedirs('extracted')
    for i in xrange(10):
        os.makedirs('extracted/'+str(i))

    # Load the annotation for each digit
    fname_txt = fname[:-3]+'txt'
    f = open(fname_txt, 'r')
    f.readline()                        # Remove the header
    lines = f.readline().split(',')
    f.close()

    # Extract each digit
    counter = [0]*10    # The counter for filename
    for i in xrange(4):
        if len(lines[i]) < 3:
            hundred = '0'
        else:
            hundred = lines[i][0]
        counter[int(hundred)] += 1
        io.imsave('extracted/'+hundred+'/'+str(counter[int(hundred)])+'.png', warped[i*100:i*100+100, :70])
        
    for i in xrange(4):
        if len(lines[i]) == 3:
            hundred = lines[i][1]
        elif len(lines[i]) == 2:
            hundred = lines[i][0]
        else:
            hundred = '0'
        counter[int(hundred)] += 1
        io.imsave('extracted/'+hundred+'/'+str(counter[int(hundred)])+'.png', warped[i*100:i*100+100, 70:140])

    for i in xrange(4):
        if len(lines[i]) == 1:
            hundred = lines[i][0]
        elif len(lines[i]) == 2:
            hundred = lines[i][1]
        elif len(lines[i]) == 3:
            hundred = lines[i][2]
        else:
            hundred = '0'
        counter[int(hundred)] += 1
        io.imsave('extracted/'+hundred+'/'+str(counter[int(hundred)])+'.png', warped[i*100:i*100+100, 140:210])

fname = 'select/40658_3.jpg'
extract_digits(fname)
