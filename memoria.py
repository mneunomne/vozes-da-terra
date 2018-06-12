# 	
# 	Classe para administrar dados coletados
# 	

import json
import os.path

class Memoria:		
	def __init__(self, datafile= "data.json"):
		self.data = []
		self.datafile = datafile
		print('init')
		if os.path.exists(datafile):
			self.update()
		else:
			self.create_file()

	def update(self):
		with open(self.datafile,"rb") as f:
			try:
				self.data = json.load(f)
				print('file opened')
			except:            
				print('unable to open file')

	def create_file(self):
		with open(self.datafile, "w") as f:
			json.dump([], f)

	def read_file(self):
		print('read')

	def append(self, new_data):
		with open(self.datafile,"rb") as f:
			try:
				self.data = json.load(f)
				print('file opened')				
			except:            
				print('unable to open file')
		self.data.append(new_data)
		self.write(self.data)

	def write(self, data):
		with open(self.datafile,"w") as f:        	
			json.dump(data, f, indent=4, sort_keys=True)
			print("data.json updated")

	def get(self):
		return self.data

	def set(self, audio_id, key, val):
		for i in range(len(self.data)):
			if self.data[i]["id"] == audio_id:
				self.data[i][key] = val
				self.write(self.data)	

