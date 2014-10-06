import requests as req


def prefix_pad(s, n):
    """ Prepend string s with 0 until it has length of n
    :param s: The string to be prepended
    :param n: The final length of prepended string
    :return: The prepended string
    """
    while len(s) < n:
        s = '0' + s
    return s


def image_filename(i, j):
    """ Prepare the KPU formatted image filename
    :param i: the area code
    :param j: the station code
    :return: The formatted filename
    """
    return prefix_pad(i, 7) + prefix_pad(j, 3) + '04'

# Loop for every area in Indonesia
start_area = 1
end_area = 80000
tps = 0
for i in xrange(start_area, end_area):
    print 'Now donwloading data from area: ', i
    r = req.get('http://kawal-pemilu.appspot.com/api/tps/' + str(i))

    if r.text == 'Error':
        continue

    json = r.json()
    for j in xrange(len(json)):
        # Check to see whether there is no error in json and also there is vote count data inside
        if json[j][6] and json[j][7] == '0':
            # Download C1 scanned image
            print 'TPS ke: ', tps
            imfname = image_filename(str(i), str(j + 1))
            imreq = req.get('http://scanc1.kpu.go.id/viewp.php?f=' + imfname + '.jpg')

            # Save to file
            f = open('scrap/' + str(i) + '_' + str(j) + '.txt', 'w')
            f.write('prabowo, jokowi, suara sah, tidak sah' + '\n')
            prabowo_count = str(json[j][2])
            jokowi_count = str(json[j][3])
            valid_count = str(json[j][4])
            invalid_count = str(json[j][5])
            f.write(prabowo_count + ',' + jokowi_count + ',' + valid_count + ',' + invalid_count)
            f.close()
            f = open('scrap/' + str(i) + '_' + str(j) + '.jpg', 'wb')
            f.write(imreq.content)
            f.close()
            tps += 1