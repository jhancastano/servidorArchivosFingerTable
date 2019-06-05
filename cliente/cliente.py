import zmq
import hashlib
import os
import sys
import json
import time

def joinFiles(msg,nombre):

	with open(nombre+'.','wb') as file:
		for x in msg['name']:
			name = msg['name'][x]['namePart']
			with open(name, 'rb') as f:
				data = f.read()
			os.remove(name)	
			file.write(data)

def subir(msg,identity,socket):
	pass

def upload(msg,identity,nodoConectado):
	context = zmq.Context()
	socket = context.socket(zmq.DEALER)
	socket.identity = identity
	socket.connect(nodoConectado)

	poller = zmq.Poller()	
	poller.register(socket, zmq.POLLIN)
	name = msg.keys()
	for keys in name:
		name= keys
	for x in msg[name]:
		print(msg[name][x])		
		op = {'operacion':'upload','parte':msg[name][x]['namePart']}
		while(msg[name][x]['nodo'] == 'null') :
			socks = dict(poller.poll())
			if socket in socks:
				sender, msg, data = socket.recv_multipart()
				mensaje_json = json.loads(msg)
				operacion = mensaje_json['operacion']
			
			print(msg[name][x]['namePart'])
	
	print(identity)
	pass



	

def download(msg,identity):
	pass	

def hashearArchivo(FILE):
	if(os.path.isfile(FILE)): 
		SizeFile = os.stat(FILE).st_size
		SizePart = 10*1024
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
		return diccionario
	else:
		print('archivo no existe en carpeta')
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
				print(msg)
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
						upload(hashearArchivo(msg),identity)



						msg1 = {}
						msg1.update({'operacion':'upload'})
						msg1 = json.dumps(msg1)
						socket.send_multipart([identity,msg1.encode('utf8'),b'0'])
					else:
						print('no existe el archivo')

				elif(op=='d'):
					os.system('clear')
					print('download')
					msg = {}
					msg.update({'operacion':'download'})
					msg = json.dumps(msg)
					socket.send_multipart([identity,msg.encode('utf8'),b'0'])
				elif(op=='l'):
					print(listaArchivos)
				else:
					pass
		#end main-----------------------------------------
	else:
		print('se ejecuta con 3 argv')


if __name__ == '__main__':
    main()