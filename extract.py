from skimage import io
from skimage import color
from skimage.transform import hough_line, hough_line_peaks
from skimage.transform import PiecewiseAffineTransform, warp
from skimage.filter import threshold_otsu
from skimage.feature import corner_harris, corner_subpix, corner_peaks
import numpy as np
import matplotlib.pyplot as plt
import os
import glob
import time

DEBUG = False  # Set true to display plot to the screen
HEIGHT = 400   # The height of extracted region, will be divided by 4 for each digit
WIDTH = 150    # The width of extracted region, will be divided by 3 for each digit
MAX_VALUE = 100000000000


def calc_intersection(x1, y1, x2, y2, x3, y3, x4, y4):
    """ Calculate the intersection points between two lines """
    px = ((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)) / (
        (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4))
    py = ((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)) / (
        (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4))

    return px, py


def calc_distance(p1, p2):
    """ Calculate distance between two points. The distance measure used is L2 norm
    minus the squared operation """
    dist = 0
    for i in xrange(len(p1)):
        dist += (p1[i] - p2[i]) * (p1[i] - p2[i])
    return dist


def search_closest_points(p, points):
    """ Search for queried point p the closest point in the set of points points """
    min_dist = MAX_VALUE
    cp = None
    for i in xrange(len(points)):
        dist = calc_distance(p, points[i])
        if dist < min_dist:
            min_dist = dist
            cp = points[i]
    return cp


def search_closest_line(lines, ref_line):
    """ Search closest line from a set of line (represented by two points) to a reference line
    using a simple, naive assumption of the summation of both points' distance.
    """
    closest_line = [(0, 0), (0, 0)]
    min_dist = MAX_VALUE
    for line in lines:
        dist = calc_distance(line[0], ref_line[0]) + calc_distance(line[1], ref_line[1])
        if dist < min_dist:
            min_dist = dist
            closest_line = line

    return closest_line


def extract_corner_hough(patch):
    """ Extract four corner points using Hough transform

    """
    # Find the lines that makes the boundary box using Hough Transform
    h, theta, d = hough_line(patch)

    # Divide the hough space for searching different horizontal and vertical lines
    hcroph = h[:, 0:30]
    rows, cols = patch.shape

    # Search all vertical lines in the hough parameter space
    # It is located in the middle, when theta is near zero
    vlf = []
    for _, angle, dist in zip(*hough_line_peaks(h, theta, d, min_angle=9)):
        x0 = (dist - 0 * np.sin(angle)) / np.cos(angle)
        x1 = (dist - rows * np.sin(angle)) / np.cos(angle)
        vlf += [((x0, 0), (x1, rows))]

    # Likewise previous operation, but with horizontal lines
    # Located at the left, when theta is near minus 90 degree
    hlf = []
    for _, angle, dist in zip(*hough_line_peaks(hcroph, theta, d, min_angle=9)):
        y0 = (dist - 0 * np.cos(angle)) / np.sin(angle)
        y1 = (dist - cols * np.cos(angle)) / np.sin(angle)
        hlf += [((0, y0), (cols, y1))]

    if DEBUG:
        plt.subplot(142)
        plt.title('hough line')
        plt.imshow(patch, cmap='gray')
        for i in xrange(len(vlf)):
            plt.plot((vlf[i][0][0], vlf[i][1][0]), (vlf[i][0][1], vlf[i][1][1]), 'r-')
        for i in xrange(len(hlf)):
            plt.plot((hlf[i][0][0], hlf[i][1][0]), (hlf[i][0][1], hlf[i][1][1]), 'r-')
        plt.axis([0, cols, rows, 0])

    # Search the rightmost and leftmost vertical lines
    vl = []
    vl += [search_closest_line(vlf, [(0, 0), (0, rows)])]
    vl += [search_closest_line(vlf, [(cols, 0), (cols, rows)])]

    # Search the topmost and bottommost horizontal lines
    hl = []
    hl += [search_closest_line(hlf, [(0, 0), (cols, 0)])]
    hl += [search_closest_line(hlf, [(0, rows), (cols, rows)])]

    if len(hl) < 2 or len(vl) < 2:
        print 'Not enough lines found'
        return []

    points = [vl[0], vl[-1], hl[0], hl[-1]]
    # Check for error
    for i in xrange(4):
        for j in xrange(i + 1, 4):
            if points[i] == points[j]:
                print 'Error Line'
                return []

    # Calculate the intersection between pair of vertical and horizontal lines
    # The line is defined by using two points.
    p1 = calc_intersection(vl[0][0][0], vl[0][0][1], vl[0][1][0], vl[0][1][1], hl[0][0][0], hl[0][0][1], hl[0][1][0],
                           hl[0][1][1])
    p2 = calc_intersection(vl[0][0][0], vl[0][0][1], vl[0][1][0], vl[0][1][1], hl[1][0][0], hl[1][0][1], hl[1][1][0],
                           hl[1][1][1])
    p3 = calc_intersection(vl[1][0][0], vl[1][0][1], vl[1][1][0], vl[1][1][1], hl[0][0][0], hl[0][0][1], hl[0][1][0],
                           hl[0][1][1])
    p4 = calc_intersection(vl[1][0][0], vl[1][0][1], vl[1][1][0], vl[1][1][1], hl[1][0][0], hl[1][0][1], hl[1][1][0],
                           hl[1][1][1])

    # Find the nearest point for each corner
    dim = patch.shape
    corners = [(0, 0), (0, dim[0]), (dim[1], dim[0]), (dim[1], 0)]
    points = [p1, p2, p3, p4]
    dest_points = [[] for x in range(4)]
    for i in xrange(4):
        dest_points[i] = search_closest_points(corners[i], points)

    epsilon = 1e-10
    for i in xrange(4):
        for j in xrange(i + 1, 4):
            if calc_distance(dest_points[i], dest_points[j]) < epsilon:
                print 'Error point'
                return []

    return dest_points


def extract_corner_harris(patch):
    """ Extract four corner points using harris corner detection algorithm

    """
    # Find corner with harris corner detection
    coords = corner_peaks(corner_harris(patch, k=0.1), min_distance=5)
    coords_subpix = corner_subpix(patch, coords, window_size=13)

    # Find the nearest point for each corner
    dim = patch.shape
    corners = [(0, 0), (dim[0], 0), (dim[0], dim[1]), (0, dim[1])]

    dest_points = [[] for x in range(4)]
    for i in xrange(4):
        dest_points[i] = search_closest_points(corners[i], coords_subpix)

    # Check for error
    try:
        epsilon = 1e-10
        for i in xrange(4):
            for j in xrange(i + 1, 4):
                if calc_distance(dest_points[i], dest_points[j]) < epsilon:
                    print 'Error point'
                    return []
    except TypeError:
        return []

    # Reverse y,x position to x,y
    for i in xrange(4):
        dest_points[i][1], dest_points[i][0] = dest_points[i][0], dest_points[i][1]

    return dest_points


def remove_edge(patch, mode):
    """ Remove possible edge artifact at the outer edge of image.
        For the bigger patch, the possible location is at the right side.
        For digit patch, all direction must be removed, as indicated with params mode='full'
    """
    x = patch.shape[1] * 0.9
    patch[:, x:] = 0

    if mode == 'full':
        x = patch.shape[1] * 0.1
        patch[:, :x] = 0
        y = patch.shape[0] * 0.9
        patch[y:, :] = 0
        y = patch.shape[0] * 0.1
        patch[:y, :] = 0

    return patch


def extract_digits(fname):
    """ Extract the sub images of digits from the scanned image.
        fname is the filename of the image
    """
    c1 = io.imread(fname)

    # Calculate the region of interest, this value is based on experimental observation
    # Basically it divides the scanned image into 3 different size, small, medium, and big
    # However this does not constitute the full variation of size of scanned images
    dim = c1.shape
    y0 = 350
    y1 = y0 + 450
    if dim[0] < 1100:
        y0 = dim[0] * 300 / 1700
        y1 = y0 + dim[0] * 400 / 1700
    elif 1700 < dim[0] < 2400:
        y0 = 350
        y1 = y0 + 450
    else:
        y0 = dim[0] * 350 / 1700
        y1 = y0 + dim[0] * 450 / 1700
    x0 = dim[1] * 19 / 24

    # Cropped and convert to grayscale
    cropped = c1[y0:y1, x0:]
    gcrop = color.rgb2gray(cropped)

    # Threshold to create binary image
    thresh = threshold_otsu(gcrop)
    gcrope = gcrop < thresh

    # Remove unwanted edge
    gcrope = remove_edge(gcrope, mode='r')

    if DEBUG:
        plt.subplot(141);
        plt.title('Cropped')
        plt.imshow(gcrop, cmap='gray')

    # Extract four corner points, either using hough or harris method
    dest_points = extract_corner_hough(gcrope)
    # dest_points = extract_corner_harris(gcrope)
    src_points = [(0, 0), (0, HEIGHT), (WIDTH, HEIGHT), (WIDTH, 0)]

    if not dest_points:
        return False

    if DEBUG:
        plt.subplot(143)
        plt.title('Thresholded & corner points')
        plt.imshow(gcrope, cmap='gray')
        for p in dest_points:
            plt.plot(p[0], p[1], 'bo', markersize=10)

    #Transform to rescale and reorient the image
    dst = np.array(dest_points)
    src = np.array(src_points)
    tform = PiecewiseAffineTransform()
    tform.estimate(src, dst)
    warped = warp(gcrope, tform, output_shape=(HEIGHT, WIDTH))

    if DEBUG:
        plt.subplot(144)
        plt.title('Warped')
        plt.imshow(warped, cmap='gray')
        plt.show()

    # Prepare the directory
    if not os.path.exists('extracted'):
        os.makedirs('extracted')
        for i in xrange(10):
            os.makedirs('extracted/' + str(i))

    # Load the annotation for each digit
    fname_txt = fname[:-3] + 'txt'
    f = open(fname_txt, 'r')
    f.readline()  # Remove the header
    lines = f.readline().split(',')
    f.close()

    width = WIDTH / 3
    # Extract each digit
    for i in xrange(4):
        if len(lines[i]) < 3:
            hundred = '0'
        else:
            hundred = lines[i][0]
        counter[int(hundred)] += 1
        patch = remove_edge(warped[i * 100:i * 100 + 100, :width], mode='full')
        io.imsave('extracted/' + hundred + '/' + str(counter[int(hundred)]) + '.png', patch)

    for i in xrange(4):
        if len(lines[i]) == 3:
            hundred = lines[i][1]
        elif len(lines[i]) == 2:
            hundred = lines[i][0]
        else:
            hundred = '0'
        counter[int(hundred)] += 1
        patch = remove_edge(warped[i * 100:i * 100 + 100, width:2 * width], mode='full')
        io.imsave('extracted/' + hundred + '/' + str(counter[int(hundred)]) + '.png', patch)

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
        patch = remove_edge(warped[i * 100:i * 100 + 100, 2 * width:3 * width], mode='full')
        io.imsave('extracted/' + hundred + '/' + str(counter[int(hundred)]) + '.png', patch)

    return True


if __name__ == "__main__":
    counter = [0] * 10
    success = 0
    fail = 0

    start_time = time.time()

    all_pics = glob.glob('G:/Kerjaan/Scan C1/*.jpg')
    start_index = 0
    end_index = 100000
    # end_index = len(all_pics)
    for i in xrange(start_index, end_index):
        pic = all_pics[i]
        print 'Extracting', pic, '...'
        if extract_digits(pic):
            success += 1
            print 'Success!!!'
        else:
            fail += 1
            print 'Fail.. :('

    end_time = time.time()

    print 'total success:', success
    print 'total fail:', fail
    print 'statistic:', counter
    print 'elapsed time:', end_time - start_time
