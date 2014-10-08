__author__ = 'mit'

# Visualize subset of digit image dataset
num_x = 10
num_y = 10

import glob
from skimage import io
import numpy as np
import random


def visualize(cl):
    all_pics = glob.glob('cleaned/'+cl+'/*.png')
    image = np.zeros((1000, 500), dtype=np.uint8)

    for i in xrange(num_y):
        for j in xrange(num_x):
            num_pic = len(all_pics)
            pic = all_pics[int(random.random()*num_pic)]
            im = io.imread(pic)
            image[i*100:(i+1)*100, j*50:(j+1)*50] = im[:, :]
    io.imsave('vis-'+cl+'.png', image)

for i in xrange(10):
    print 'Visualize ', i
    visualize(str(i))

visualize('X')
