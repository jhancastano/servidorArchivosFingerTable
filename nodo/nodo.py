import zmq
import hashlib
import os
import sys
import json
import time

def printD(msg, identity):
	context = zmq.Context()
	socketD = context.socket(zmq.DEALER)
	socketD.connect('tcp://localhost:3333')
	socketD.send_multipart([identity,msg])

def hash(idnodo):
	objetohash = hashlib.sha1(idnodo.encode('utf8'))
	cadena = objetohash.hexdigest()	
	print(cadena)
	return cadena

def iniciando(nodosConectados):
	if (nodosConectados['Sucesor']['id']=='null' and 
		nodosConectados['Predecesor']['id']=='null'and 
		nodosConectados['Predecesor']['name']=='null'):
		return True
	else:
		return False

def emptyPre(mensaje_json):
	if(mensaje_json['Predecesor']['id']=='null' and 
		mensaje_json['Predecesor']['name']=='null'):
		return True
	else:
		return False
def emptySuc(mensaje_json):
	if(mensaje_json['Sucesor']['id']=='null'):
		return True
	else:
		return False

def main():# 1arg=nodoID, 2ipnodo, 3puerto nodo, 4arg=idsucesor 5arg=puerto sucesor
	if(len(sys.argv)==6):
		
		nodoID = sys.argv[1]
		iPnodo = sys.argv[2]
		Pnodo = sys.argv[3]
		nodoName = 'tcp://'+iPnodo+':' + Pnodo
		sucesorName = 'tcp://'+sys.argv[4]+':'+sys.argv[5]
		miID = {'id':nodoID,'name':nodoName}

		nodosConectados = {'Sucesor':{'id':'null','name': sucesorName} ,'Predecesor':{'id':'null','name':'null'}}
		context = zmq.Context()
		sock = context.socket(zmq.DEALER)
		sock.identity = nodoID.encode('utf8')
		sock.connect(nodosConectados['Sucesor']['name'])
		nodosConectados.update({'operacion':'iniciar'})
		msg = json.dumps(nodosConectados)
		contextR = zmq.Context()
		sockrouter = contextR.socket(zmq.ROUTER)
		sockrouter.bind("tcp://*:"+Pnodo) 
		sock.send_multipart([nodoID.encode('utf8'),msg.encode('utf8')])
		#print('Nodo  '+nodoID+' : activo')
		poller = zmq.Poller()
		poller.register(sys.stdin, zmq.POLLIN)
		poller.register(sock, zmq.POLLIN)
		poller.register(sockrouter,zmq.POLLIN)
		while(True) :
			socks = dict(poller.poll())
			if sockrouter in socks:
				sender, destino , msg = sockrouter.recv_multipart()
				mensaje_json = json.loads(msg)
				if(mensaje_json['operacion']=='iniciar'):
					print(iniciando(nodosConectados))
					if(iniciando(nodosConectados) and emptyPre(mensaje_json)):
						print('holaaaaaaaa')
						mensaje_json['Predecesor'].update({'id':nodoID,'name':nodoName})
						mensaje_json['Sucesor'].update({'id':nodoID})
						mensaje_json.update({'operacion':'registrar'})
						msg = json.dumps(mensaje_json)
						print(msg)
						sock.send_multipart([sender,msg.encode('utf8')])
					elif(emptySuc(mensaje_json)):
						print('no tengo sucesor')					
						mensaje_json.update(nodosConectados)
						mensaje_json.update()
						mensaje_json.update({'operacion':'buscando'})
						mensaje_json.update({'miID':miID})
						msg = json.dumps(mensaje_json)
						sockrouter.send_multipart([sender,sender,msg.encode('utf8')])
						print('enviado a:')
						print(sender)
				elif(mensaje_json['operacion']=='buscando'):
					print('buscando')			
				elif(mensaje_json['operacion']=='registrar'):
					del mensaje_json['operacion']
					nodosConectados.update(mensaje_json)
					print('registrar')
					print('------------')
			elif sock in socks:
				print('hay un socket')
				sender, msg = sock.recv_multipart()
				print(msg)
			elif sys.stdin.fileno() in socks:
				print("?")
				command = input()
				print(nodosConectados)


	else:
		print('se ejecuta con 6 argv')



if __name__ == '__main__':
    main()