import glob
import os

all_txt = glob.glob('scrap/*.txt')
all_pics = glob.glob('scrap/*.jpg')

for txt in all_txt:
	if not txt[:-3]+'jpg' in all_pics:
		print 'remove', txt
		os.remove(txt)

print 'Finish'
