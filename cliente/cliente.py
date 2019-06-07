import zmq
import hashlib
import os
import sys
import json
import time

def joinFiles(msg,nombre):

	with open(nombre+'.dwn','wb') as file:
		for x in msg:
			name = msg[x]['namePart']
			with open(name, 'rb') as f:
				data = f.read()
			os.remove(name)	
			file.write(data)


def upload(msg,idcliente,nodoConectado):
	print(idcliente)
	context = zmq.Context()
	socket = context.socket(zmq.DEALER)
	socket.identity = b'upload'
	socket.connect(nodoConectado)
	poller = zmq.Poller()	
	poller.register(socket, zmq.POLLIN)
	name = msg.keys()
	for keys in name:
		name= keys
	for x in msg[name]:		
		op = {'operacion':'upload','parte':msg[name][x]['namePart']}
		mensaje = json.dumps(op)
		socket.send_multipart([idcliente,mensaje.encode('utf8'),b'0'])
		while(msg[name][x]['nodo'] == 'null') :
			socks = dict(poller.poll())
			if socket in socks:
				sender, mensajeServidor, data = socket.recv_multipart()
				mensaje_json = json.loads(mensajeServidor)
				print(mensajeServidor)
				operacion = mensaje_json['operacion']
				if(operacion=='falso'):
					socket.disconnect(mensaje_json['name'])
					socket.connect(mensaje_json['Sucesor']['name'])
					socket.send_multipart([idcliente,mensaje.encode('utf8'),b'0'])
				elif(operacion=='verdadero'):
					with open(msg[name][x]['namePart'],'rb') as f:
						data = f.read()
					op = {'operacion':'subir','parte':msg[name][x]['namePart']}
					mensaje = json.dumps(op)
					socket.send_multipart([idcliente,mensaje.encode('utf8'),data])
					os.remove(msg[name][x]['namePart'])
					msg[name][x]['nodo'] = mensaje_json['name']
	print('succesfull upload')


	

def download(msg,idcliente,nodoConectado):
	print(idcliente)
	context = zmq.Context()
	socket = context.socket(zmq.DEALER)
	socket.identity = b'download'
	socket.connect(nodoConectado)
	poller = zmq.Poller()	
	poller.register(socket, zmq.POLLIN)
	name = msg.keys()
	for keys in name:
		name= keys
	for x in msg[name]:		
		op = {'operacion':'download','parte':msg[name][x]['namePart']}
		mensaje = json.dumps(op)
		socket.send_multipart([idcliente,mensaje.encode('utf8'),b'0'])
		while(msg[name][x]['nodo'] == 'null') :
			socks = dict(poller.poll())
			if socket in socks:
				sender, mensajeServidor, data = socket.recv_multipart()
				mensaje_json = json.loads(mensajeServidor)
				operacion = mensaje_json['operacion']
				if(operacion=='falso'):
					socket.disconnect(mensaje_json['name'])
					socket.connect(mensaje_json['Sucesor']['name'])
					socket.send_multipart([idcliente,mensaje.encode('utf8'),b'0'])
				elif(operacion=='verdadero'):
					with open(msg[name][x]['namePart'],'wb') as f:
						f.write(data)
					msg[name][x]['nodo'] = mensaje_json['name']

	os.system('clear')
	joinFiles(msg[name],name)
	print('succesfull download')




def hashearArchivo(FILE):
	if(os.path.isfile(FILE)): 
		SizeFile = os.stat(FILE).st_size
		SizePart = 20*1024*1024
		diccionario = {}
		DicPart = {}
		FileComplete = hashlib.sha1()
		with open(FILE, 'rb') as f:
			i= 1
			for x in range(int(SizeFile/SizePart)+1):			
				data = f.read(SizePart)
				objetohash = hashlib.sha1(data)
				cadena = objetohash.hexdigest()
				DicPart.update({i:{'namePart':cadena,'nodo':'null'}})
				FileComplete.update(data)
				with open(cadena, 'wb') as part:
					part.write(data)
				i=i+1
		shaprincipal =	FileComplete.hexdigest()	
		diccionario.update({shaprincipal:DicPart})

		with open(shaprincipal+'.p2p','wb') as file:
			file.write(json.dumps(diccionario).encode('utf8'))
		return diccionario

	else:
		print('archivo no existe en carpeta')
		return -1

def leerp2p(FILE):
	if(os.path.isfile(FILE)):
		with open(FILE, 'rb') as f:
			data = f.read()
		diccionario =json.loads(data)	
		return diccionario
	else:
		print('no existe p2p')
		return -1

	

def main():
	if(len(sys.argv)==4):# 1arg=id, 2arg=ipnodo, 3arg=puertonodo
		clienteID = sys.argv[1]
		iPnodo = sys.argv[2]
		Pnodo = sys.argv[3]
		nodoName = 'tcp://'+iPnodo+':' + Pnodo
		identity = clienteID.encode('utf8')
		context = zmq.Context()
		socket = context.socket(zmq.DEALER)
		socket.identity = identity
		socket.connect(nodoName)
		print("Start cliente {}".format(identity))
		
		poller = zmq.Poller()
		poller.register(sys.stdin, zmq.POLLIN)
		poller.register(socket, zmq.POLLIN)
		listaArchivos = {}
		while True:
			print("opciones[u:upload,d:download +archivo]")
			socks = dict(poller.poll())
			mensaje = {'operacion':'sin operacion'}
			mensaje_json = json.dumps(mensaje)
			if socket in socks:
				sender, msg, data = socket.recv_multipart()
				mensaje_json = json.loads(msg)
				operacion = mensaje_json['operacion']
				if(operacion=='upload'):
					print('upload')
				elif(operacion=='download'):
					print('download')
			elif sys.stdin.fileno() in socks:
				print("?")
				command = input()
				op, msg = command.split(' ', 1)
				if(op=='u'):
					os.system('clear')
					if(hashearArchivo(msg)!=-1):
						print('upload')
						listaArchivos.update(hashearArchivo(msg))
						#socket.disconnect(nodoName)
						upload(hashearArchivo(msg),identity,nodoName)
					else:
						print('no existe el archivo')

				elif(op=='d'):
					os.system('clear')
					print('download')
					if(leerp2p(msg)!=-1):
						print(leerp2p(msg))
						download(leerp2p(msg),identity,nodoName)
					else:
						print('no existe p2p')
				elif(op=='l'):
					print(listaArchivos)
				else:
					pass
		#end main-----------------------------------------
	else:
		print('se ejecuta con 3 argv')


if __name__ == '__main__':
    main()