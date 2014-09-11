from skimage import io
from skimage import color
from skimage.transform import hough_line, hough_line_peaks
from skimage.transform import rotate
from skimage.transform import PiecewiseAffineTransform, warp
from skimage.feature import corner_harris
from skimage.filter import canny
from skimage.filter import threshold_otsu
import numpy as np
import matplotlib.pyplot as plt
import math
import os

def calcIntersection(x1, y1, x2, y2, x3, y3, x4, y4):
    px = ((x1*y2 - y1*x2)*(x3-x4) - (x1-x2)*(x3*y4 - y3*x4)) / ((x1-x2)*(y3-y4) - (y1-y2)*(x3-x4))
    py = ((x1*y2 - y1*x2)*(y3-y4) - (y1-y2)*(x3*y4 - y3*x4)) / ((x1-x2)*(y3-y4) - (y1-y2)*(x3-x4))
    
    return (px, py)

def calc_distance(p1, p2):
    dist = 0
    for i in xrange(len(p1)):
        dist += (p1[i] - p2[i])*(p1[i] - p2[i])
    return dist

def search_closest_points(p, points):
    min_dist = 1000000000
    cp = None
    for i in xrange(len(points)):
        dist = calc_distance(p, points[i])
        if dist < min_dist:
            min_dist = dist
            cp = points[i]
    return cp

fname = 'select/40658_3.jpg'
c1 = io.imread(fname)

# Cropped the region of interest
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

#gcrope = canny(gcrop)
#corner_response = corner_harris(gcrop)
thresh = threshold_otsu(gcrop)
gcrope = gcrop < thresh
#plt.imshow(gcrope, cmap='gray')
#plt.show()
h, theta, d = hough_line(gcrope)

plt.figure(figsize=(8, 4))

plt.subplot(141)
plt.imshow(gcrop, cmap=plt.cm.gray)
plt.title('Input image')

plt.subplot(142)
hcropv = h[:, 60:120]
hcroph = h[:, 0:30]
plt.imshow(np.log(1 + hcropv),
           extent=[np.rad2deg(theta[-1]), np.rad2deg(theta[0]),
                   d[-1], d[0]],
           cmap=plt.cm.gray, aspect=1/1.5)
plt.title('Hough transform')
plt.xlabel('Angles (degrees)')
plt.ylabel('Distance (pixels)')

plt.subplot(143)
plt.imshow(np.log(1 + hcroph),
           extent=[np.rad2deg(theta[-1]), np.rad2deg(theta[0]),
                   d[-1], d[0]],
           cmap=plt.cm.gray, aspect=1/1.5)
plt.title('Hough transform')
plt.xlabel('Angles (degrees)')
plt.ylabel('Distance (pixels)')

#plt.subplot(144)
#plt.imshow(gcrope, cmap='gray')
#rows, cols = gcrope.shape

# Vertical lines
VL = []
for _, angle, dist in zip(*hough_line_peaks(h, theta, d, min_distance=100, min_angle=9, num_peaks=2)):
    y0 = (dist - 0 * np.cos(angle)) / np.sin(angle)
    y1 = (dist - cols * np.cos(angle)) / np.sin(angle)
    plt.plot((0, cols), (y0, y1), '-r')
    VL += [((0, y0), (cols, y1))]
# Horizontal lines
HL = []
for _, angle, dist in zip(*hough_line_peaks(hcroph, theta, d, min_distance=250, min_angle=9)):
    y0 = (dist - 0 * np.cos(angle)) / np.sin(angle)
    y1 = (dist - cols * np.cos(angle)) / np.sin(angle)
    plt.plot((0, cols), (y0, y1), '-r')
    HL += [((0, y0), (cols, y1))]

plt.axis((0, cols, rows, 0))

# Calculate the intersection between points using determinants
p1 = calcIntersection(VL[0][0][0], VL[0][0][1], VL[0][1][0], VL[0][1][1], HL[0][0][0], HL[0][0][1], HL[0][1][0], HL[0][1][1])
p2 = calcIntersection(VL[0][0][0], VL[0][0][1], VL[0][1][0], VL[0][1][1], HL[1][0][0], HL[1][0][1], HL[1][1][0], HL[1][1][1])
p3 = calcIntersection(VL[1][0][0], VL[1][0][1], VL[1][1][0], VL[1][1][1], HL[0][0][0], HL[0][0][1], HL[0][1][0], HL[0][1][1])
p4 = calcIntersection(VL[1][0][0], VL[1][0][1], VL[1][1][0], VL[1][1][1], HL[1][0][0], HL[1][0][1], HL[1][1][0], HL[1][1][1])

plt.plot(p1[0], p1[1], 'ro')
#plt.plot(p2[0], p2[1], 'ro')
#plt.plot(p3[0], p3[1], 'ro')
#plt.plot(p4[0], p4[1], 'ro')
#plt.show()

src_points = [(0,0), (210, 0), (0, 400), (210, 400)]
dim = cropped.shape
corners = [(0,0), (dim[0], 0), (0, dim[1]), (dim[0], dim[1])]

src = np.array(src_points)

dest_points = [[] for x in range(4)]
points = [p1, p2, p3, p4]

for i in xrange(4):
    dest_points[i] = search_closest_points(src_points[i], points)

dst = np.array(dest_points)

tform = PiecewiseAffineTransform()
tform.estimate(src, dst)
warped = warp(gcrope, tform, output_shape=(400, 210))

plt.subplot(144)
plt.imshow(warped)
plt.show()

# Prepare the directory
if not os.path.exists('extracted'):
    os.makedirs('extracted')
for i in xrange(10):
    os.makedirs('extracted/'+str(i))

fname_txt = fname[:-3]+'txt'

f = open(fname_txt, 'r')
f.readline() # the header
lines = f.readline().split(',')
f.close()

counter = [0]*10

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

#rgcrope = rotate(gcrope, 2)
#plt.subplot(144)
#plt.imshow(rgcrope, cmap='gray')
