import zmq
import hashlib
import os
import sys
import json

def printD(msg, identity):
	context = zmq.Context()
	sock = context.socket(zmq.DEALER)
	sock.connect('tcp://localhost:4444')
	sock.send_multipart([identity,msg])

def hash(idnodo):
	objetohash = hashlib.sha1(idnodo.encode('utf8'))
	cadena = objetohash.hexdigest()	
	print(cadena)
	return cadena

def main():# 1arg=nodoID, 2arg=idsucesor 2arg=puerto sucesor
	if(len(sys.argv)==4):
		print(sys.argv[1])
		nodoID = hash(sys.argv[1])
		conexion = {'Sucesor':'tcp://'+sys.argv[2]+':'+sys.argv[3] ,'Predecesor':'null'}
		print('hola')						
		print(conexion['Sucesor'])
		context = zmq.Context()
		sock = context.socket(zmq.DEALER)
		sock.identity = nodoID.encode('utf8')
		sock.connect(conexion['Sucesor'])

		msg = json.dumps(conexion)

		printD(msg.encode('utf8'),nodoID.encode('utf8'))

	else:
		print('se ejecuta con 3 argv')



if __name__ == '__main__':
    main()