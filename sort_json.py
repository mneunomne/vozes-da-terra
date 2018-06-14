import memoria
import json 

_memoria = memoria.Memoria()

data = _memoria.data

def sort_by_length(d):
    '''a helper function for sorting'''
    return d['length']

_sorted = sorted(data, key=sort_by_length)

for i in range(len(_sorted)):
	# print(_sorted[i]['length'])
	if _sorted[i]['length'] > 500:
		if _sorted[i]['text'] != "":
			print(_sorted[i]['text'])
	else: 
		print('-', _sorted[i]['length'])


# print(json.dumps(_sorted, indent=4, sort_keys=True))