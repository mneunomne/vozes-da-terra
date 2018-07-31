from tkinter import *

class GUI:
	def __init__(self, root):
		self.root = root
		self.w, self.h = root.winfo_screenwidth()-100, root.winfo_screenheight()-100
		self.root.overrideredirect(0)
		
		self.root.geometry("%dx%d+0+0" % (self.w, self.h))
		self.root.configure(background="blue")
		     
	def update(self):
		self.root.update_idletasks()
		self.root.update()

	def set_state(self, state):
		if state == 'listening':
			self.change_color("green")
		elif state == 'playing':		
			self.change_color("red")
		self.update()


	def change_color(self, color):
		print('change color:', color)
		self.root.configure(background=color)