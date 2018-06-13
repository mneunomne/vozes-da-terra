from firebase import firebase
firebase = firebase.FirebaseApplication('https://vozes-da-terra.firebaseio.com/', None)
result_get = firebase.get('/teste', None)
print('get', result_get)
stemms = {'stemms':['asd','asd','fawf']}
result_post = firebase.post('/stemms', stemms)
print('post', result_post)