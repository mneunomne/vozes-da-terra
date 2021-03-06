# 	
# 	Classe para administrar dados coletados
# 	

import json
import numpy
import os.path
from firebase import firebase
firebase = firebase.FirebaseApplication('https://vozes-da-terra.firebaseio.com/', None)

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

	def onFileUploaded(self, audio_id):
		audio_data = self._get_from_id(audio_id)
		result_post = firebase.post('/teste', audio_data)
		print('result', result_post)

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

	def _get_from_id(self, audio_id):
		for i in range(len(self.data)):
			if self.data[i]["id"] == audio_id:				
				return self.data[i]

	def set(self, audio_id, key, val):
		for i in range(len(self.data)):
			if self.data[i]["id"] == audio_id:
				self.data[i][key] = val
				self.write(self.data)

	def extract_length(data):
	    try:
	        # Also convert to int since update_time will be string.  When comparing
	        # strings, "10" is smaller than "2".
	        return int(data['length'])
	    except KeyError:
	        return 0

	def getNext(self, audio_id):					
		return self.getClosestLength(audio_id)

	def sort_by_length(self, d):
		    '''a helper function for sorting'''
		    return d['length']	

	def getClosestLength(self, audio_id):
		obj = self._get_from_id(audio_id)
		_data = self.data		
		_sorted = sorted(_data, key=self.sort_by_length)		
		for i in range(len(_sorted)):
			# print(_sorted[i]['length'])
			if _sorted[i]['length'] > obj['length']:
				if _sorted[i]['text'] != "":
					return _sorted[i]			


