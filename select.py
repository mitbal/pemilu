import random
import glob
import shutil

nC1 = 1000
dest = 'select'

all_pics = glob.glob('scrap/*.jpg')
for i in xrange(nC1):
	nPic = len(all_pics)
	pic = all_pics[int(random.random()*nPic)]
	txt = pic[:-3]+'txt'

	print 'copying', pic
	shutil.copy(pic, dest)
	shutil.copy(txt, dest)
