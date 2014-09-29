from skimage import io
import glob


def read_dir(f, path, cl, num_data):
    """
    Read file images in one directory
    :param f: The output file stream
    :param cl: The class label
    :param path: The directory path
    :return:
    """
    path = path + cl + '/'
    print 'preparing data from: ', path
    all_pics = glob.glob(path + '*.png')
    for i in xrange(num_data):
        print i
        im = io.imread(all_pics[i])
        dim = im.shape
        line = ''
        for j in xrange(dim[0]):
            for k in xrange(dim[1]):
                line += str(im[j, k]) + ','
        line += 'c' + cl
        f.write(line + '\n')


def prepare_input(fname, num_data, include_x=False):
    """
    Prepare CSV-formatted input from the extracted digit images
    :param fname: The name of output file
    :param num_data: Number of instances per class
    :param include_x: Included special character 'X' that appears only on the most significant bit
    :return: True is successful
    """

    # Open the file stream and prepare header
    f = open(fname, 'w')
    header = ''
    for i in xrange(100 * 50):
        header += 'f' + str(i + 1) + ','
    header += 'class'
    f.write(header + '\n')

    path = 'cleaned/'
    for i in xrange(10):
        read_dir(f, path, str(i), num_data)

    if include_x:
        read_dir(f, path, 'X', num_data)

    f.close()

if __name__ == '__main__':
    fname = 'input500.csv'
    num_data = 500
    include_x = True
    prepare_input(fname, num_data, include_x)
