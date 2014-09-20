from skimage import io
import glob

# Number of instance per class
NUMDATA = 500

f = open('input.csv', 'w')
header = ''
for i in xrange(100*50):
	header += 'feat'+str(i+1)+','
header += 'class'
f.write(header+'\n')

for i in xrange(10):
	print 'preparing data from class:', i
	all_pics = glob.glob('cleaned/'+str(i)+'/*.png')
	for j in xrange(NUMDATA):
		im = io.imread(all_pics[j])
		dim = im.shape
		line = ''
		for k in xrange(dim[0]):
			for m in xrange(dim[1]):
				line += str(im[k, m])+','
		line += 'c'+str(i)
		f.write(line+'\n')

f.close()
