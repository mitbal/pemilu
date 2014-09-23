from Tkinter import *
from PIL import Image, ImageTk

class App:

	def __init__(self, master):

		frame = Frame(master)
		frame.pack()

		self.label_img_path = Label(frame, text='Path to the image file')
		self.label_img_path.pack(side=LEFT)

		self.btn_load_img = Button(
			frame, text='Load Image', command=self.load_image)
		self.btn_load_img.pack(side=LEFT)

		image = Image.open('lenna.jpg')
		photo = ImageTk.PhotoImage(image)
		self.label_im = Label(frame, image=photo)
		self.label_im.image = photo # Keep a reference, so it won't get GC'ed
		self.label_im.pack(side=BOTTOM)

		self.btn_load_model = Button(frame, text='Load Model', command=self.load_model)
		self.btn_load_model.pack()

		self.btn_process = Button(frame, text='Process', command=self.process)
		self.btn_process.pack()

		self.label_prabowo = Label(frame, text='Suara Prabowo')
		self.label_prabowo.pack()
		
		self.label_jokowi = Label(frame, text='Suara Jokowi')
		self.label_jokowi.pack()

		self.label_sah = Label(frame, text='Total Suara Sah')
		self.label_sah.pack()

		self.label_tidaksah = Label(frame, text='Total Tidak Sah')
		self.label_tidaksah.pack()

	def load_image(self):
		return 0

	def load_model(self):
		return 0

	def process(self):
		return 0

root = Tk()
app = App(root)
root.mainloop()
