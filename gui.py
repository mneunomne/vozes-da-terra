from tkinter import *

fullscreen = False

class GUI:
	def __init__(self, root):
		self.root = root
		self.w, self.h = root.winfo_screenwidth(), root.winfo_screenheight()
		self.root.overrideredirect(fullscreen)
		
		self.root.geometry("%dx%d+0+0" % (self.w, self.h))
		self.root.configure(background="blue")
		     
	def update(self):
		self.root.update_idletasks()
		self.root.update()

	def set_state(self, state):
                if state == 'echo':
                    self.change_color("white")
                if state == 'random':
                    self.change_color("purple")
                if state == 'oraculo':
                    self.change_color("green")
                elif state == 'playing':
                    self.change_color("blue")
                self.update()

	def change_color(self, color):
		print('change color:', color)
		self.root.configure(background=color)