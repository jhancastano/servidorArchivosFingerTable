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

def changeSocket(socket,nodo,conexion):
	pass


def main():# 1arg=nodoID, 2ipnodo, 3puerto nodo, 4arg=idsucesor 5arg=puerto sucesor
	if(len(sys.argv)==6):
		print(sys.argv[1])
		nodoID = hash(sys.argv[1])
		nodosConectados = {'Sucesor':{'id':'null','name': 'tcp://'+sys.argv[4]+':'+sys.argv[5]} ,'Predecesor':{'id':'null','name':'null'}}
		context = zmq.Context()
		sock = context.socket(zmq.DEALER)
		sock.identity = nodoID.encode('utf8')
		sock.connect(nodosConectados['Sucesor']['name'])
		msg = json.dumps(nodosConectados)
		printD(msg.encode('utf8'),nodoID.encode('utf8'))
		sockrouter = context.socket(zmq.ROUTER)
		sockrouter.bind("tcp://*:"+sys.argv[3])
	else:
		print('se ejecuta con 6 argv')



if __name__ == '__main__':
    main()