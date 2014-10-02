from Tkinter import *
from PIL import Image, ImageTk
import PIL
from tkFileDialog import askopenfilename
from extract import extract_digits, remove_edge
from skimage import io
from subprocess import call


class App:
    def __init__(self, master):
        """
        Initialize the GUI appearance
        """
        frame = Frame(master, width=700, height=900)
        frame.pack()
        frame.pack_propagate(0)

        self.imgpath = StringVar()
        self.imgpath.set('Path to the image file')
        self.label_img_path = Label(frame, textvariable=self.imgpath)
        self.label_img_path.place(x=10, y=10)

        self.btn_load_img = Button(frame, text='Load Image', command=self.load_image)
        self.btn_load_img.place(x=550, y=10)

        image = Image.open('lenna.jpg')
        photo = ImageTk.PhotoImage(image)
        self.label_im = Label(frame, image=photo)
        self.label_im.image = photo  # Keep a reference, so it won't get GC'ed
        self.label_im.place(x=10, y=50)

        self.btn_load_model = Button(frame, text='Load Model', command=self.load_model)
        self.btn_load_model.place(x=550, y=80)

        self.modelname = StringVar()
        self.modelname.set('<<Model Name>>')
        self.label_model_name = Label(frame, textvariable=self.modelname)
        self.label_model_name.place(x=550, y=115)

        self.btn_process = Button(frame, text='Process', command=self.process)
        self.btn_process.place(x=550, y=250)

        self.label_prabowo = Label(frame, text='Suara Prabowo')
        self.label_prabowo.place(x=550, y=280)

        self.label_jokowi = Label(frame, text='Suara Jokowi')
        self.label_jokowi.place(x=550, y=310)

        self.label_sah = Label(frame, text='Total Suara Sah')
        self.label_sah.place(x=550, y=340)

        self.label_tidaksah = Label(frame, text='Total Tidak Sah')
        self.label_tidaksah.place(x=550, y=370)

        self.prabowo_vote = StringVar()
        self.prabowo_vote.set('0')
        self.jokowi_vote = StringVar()
        self.jokowi_vote.set('0')
        self.sah_vote = StringVar()
        self.sah_vote.set('0')
        self.tidaksah_vote = StringVar()
        self.tidaksah_vote.set('0')

        self.label_prabowo_vote = Label(frame, textvariable=self.prabowo_vote)
        self.label_prabowo_vote.place(x=650, y=280)

        self.label_jokowi_vote = Label(frame, textvariable=self.jokowi_vote)
        self.label_jokowi_vote.place(x=650, y=310)

        self.label_sah_vote = Label(frame, textvariable=self.sah_vote)
        self.label_sah_vote.place(x=650, y=340)

        self.label_tidaksah_vote = Label(frame, textvariable=self.tidaksah_vote)
        self.label_tidaksah_vote.place(x=650, y=370)

        # Important variable
        self.imfilename = ''
        self.modfilename = ''

    def load_image(self):
        self.imfilename = askopenfilename()
        self.imgpath.set(self.imfilename)

        # Load image & resize
        image = Image.open(self.imfilename)
        max_width = 500
        ratio = max_width / float(image.size[0])
        height = int(ratio * float(image.size[1]))
        image = image.resize((max_width, height), PIL.Image.ANTIALIAS)

        print image.size
        print max_width, height

        photo = ImageTk.PhotoImage(image)
        self.label_im.configure(image=photo)
        self.label_im.image = photo

    def load_model(self):
        self.modfilename = askopenfilename()
        self.modelname.set(self.modfilename.split('/')[-1])

    def process(self):
        # Extract the vote count region
        extract_digits(self.imfilename, mode='test')
        exfilename = self.imfilename.split('/')[-1][:-4] + '-ex' + '.png'
        image = Image.open(exfilename)
        photo = ImageTk.PhotoImage(image)
        self.label_im.configure(image=photo)
        self.label_im.image = photo

        # Write the feature into file. For now we use raw greyscale value as feature
        f = open('predict.csv', 'w')
        header = ''
        total_feature = 100*50
        for i in xrange(total_feature):
            header += 'f'+str(i)+','
        header += 'class'
        f.write(header+'\n')

        im = io.imread(exfilename)
        for i in xrange(4):
            for j in xrange(3):
                patch = im[i*100:(i+1)*100, j*50:(j+1)*50]
                patch = remove_edge(patch, 'full')
                rows, cols = patch.shape
                line = ''
                for k in xrange(rows):
                    for m in xrange(cols):
                        line += str(patch[k, m]) + ','
                line += '?'
                f.write(line+'\n')
        f.close()

        # convert CSV to ARFF
        #call(['javac', '-cp', 'weka.jar', 'CVS2Arff.java'])
        #call(['java', '-cp', 'weka.jar;.', 'CVS2Arff', 'predict.csv', 'predict.arff'])

        # Prediction with pretrained model
        call(['javac', '-cp', 'weka.jar', 'Predictor.java'])
        call(['java', '-cp', 'weka.jar;.', 'Predictor', self.modelname.get()])

        # Update vote count
        f = open('vote.txt', 'r')
        self.prabowo_vote.set(f.readline()[:-1])
        self.jokowi_vote.set(f.readline()[:-1])
        self.sah_vote.set(f.readline()[:-1])
        self.tidaksah_vote.set(f.readline()[:-1])


root = Tk()
app = App(root)
root.resizable(0, 0)
root.mainloop()
