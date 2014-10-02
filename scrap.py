import requests as req

def prefix_pad(s, n):
	while len(s) < n:
		s = '0'+s
	return s

def image_filename(i, j):
	return prefix_pad(i, 7) + prefix_pad(j, 3) + '04'

# Loop sesuai banyak jumlah area
start_tps = 1000
end_tps = 11000
tps = 0
for i in xrange(start_tps, end_tps):
	print 'Now donwloading data from area: ', i
	r = req.get('http://kawal-pemilu.appspot.com/api/tps/' + str(i))

	if r.text == 'Error':
		continue

	json = r.json()
	for j in xrange(len(json)):
		# Cek kalau udah ada data scannya dan tidak eror rekapnya
		if json[j][6] and json[j][7] == '0':
			# Download gambar scan c1
			print 'TPS ke: ', tps
			imfname = image_filename(str(i), str(j+1))
			imreq = req.get('http://scanc1.kpu.go.id/viewp.php?f='+imfname+'.jpg')
			# Save to file
			f = open('scrap/'+str(i)+'_'+str(j)+'.txt', 'w')
			f.write('prabowo, jokowi, suara sah, tidak sah'+'\n')
			prabowo_count = str(json[j][2])
			jokowi_count = str(json[j][3])
			valid_count = str(json[j][4])
			invalid_count = str(json[j][5])
			f.write(prabowo_count+','+jokowi_count+','+valid_count+','+invalid_count)
			f.close()
			f = open('scrap/'+str(i)+'_'+str(j)+'.jpg', 'wb')
			f.write(imreq.content)
			f.close()
			tps = tps + 1