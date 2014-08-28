from skimage import io
from skimage import color
from skimage.transform import hough_line, hough_line_peaks
from skimage.feature import corner_harris
from skimage.filter import canny
from skimage.filter import threshold_otsu
import numpy as np
import matplotlib.pyplot as plt

def calcIntersection(x1, y1, x2, y2, x3, y3, x4, y4):
    px = ((x1*y2 - y1*x2)*(x3-x4) - (x1-x2)*(x3*y4 - y3*x4)) / ((x1-x2)*(y3-y4) - (y1-y2)*(x3-x4))
    py = ((x1*y2 - y1*x2)*(y3-y4) - (y1-y2)*(x3*y4 - y3*x4)) / ((x1-x2)*(y3-y4) - (y1-y2)*(x3-x4))
    
    return (px, py)

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

plt.subplot(131)
plt.imshow(gcrop, cmap=plt.cm.gray)
plt.title('Input image')

plt.subplot(132)
hcrop = h[:, 0:50]
plt.imshow(np.log(1 + h),
           extent=[np.rad2deg(theta[-1]), np.rad2deg(theta[0]),
                   d[-1], d[0]],
           cmap=plt.cm.gray, aspect=1/1.5)
plt.title('Hough transform')
plt.xlabel('Angles (degrees)')
plt.ylabel('Distance (pixels)')

plt.subplot(133)
plt.imshow(gcrope, cmap='gray')
rows, cols = gcrope.shape

# Vertical lines
VL = []
for _, angle, dist in zip(*hough_line_peaks(h, theta, d, min_distance=100, min_angle=9)):
    y0 = (dist - 0 * np.cos(angle)) / np.sin(angle)
    y1 = (dist - cols * np.cos(angle)) / np.sin(angle)
    plt.plot((0, cols), (y0, y1), '-r')
    VL += [((0, y0), (cols, y1))]
# Horizontal lines
HL = []
for _, angle, dist in zip(*hough_line_peaks(hcrop, theta, d, min_distance=250, min_angle=9)):
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
plt.plot(p2[0], p2[1], 'ro')
plt.plot(p3[0], p3[1], 'ro')
plt.plot(p4[0], p4[1], 'ro')
plt.show()

# Affine transform
