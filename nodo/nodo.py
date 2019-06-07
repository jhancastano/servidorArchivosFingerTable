import zmq
import hashlib
import os
import sys
import json
import time


def cargarArchivo(namepart,data):
	with open(namepart,'wb') as file:
		file.write(data)

def descargarArchivo(namepart):
	with open(namepart,'rb') as file:
		data = file.read()	
	return data


def hash(idnodo):
	objetohash = hashlib.sha1(idnodo.encode('utf8'))
	cadena = objetohash.hexdigest()	
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

def positionNodo(nodosConectados,miID):
	idsuc = nodosConectados['Sucesor']['id']
	idpre = nodosConectados['Predecesor']['id']
	if(miID['id']<idpre and idpre>idsuc):
		return 1#primero nodo
	if(miID['id']>idpre and idpre>idsuc):
		return 2#nodo en medio
	if(miID['id']>idpre and idsuc>idpre):
		return 3# ultimo nodo

def canUpload(nodosConectados,miID,idparte):
	if(positionNodo(nodosConectados,miID)==1):
		if(nodosConectados['Predecesor']['id']<idparte):
			return True
		elif(idparte<miID['id']):
			return True
		else:
			return False
	elif(positionNodo(nodosConectados,miID)!=1):
		if(nodosConectados['Predecesor']['id']<idparte and miID['id']>idparte):
			return True
		else:
			return False


def canDownload(nodosConectados,miID,idparte):
	if(positionNodo(nodosConectados,miID)==1):
		if(nodosConectados['Predecesor']['id']<idparte):
			return True
		elif(idparte<miID['id']):
			return True
		else:
			return False
	elif(positionNodo(nodosConectados,miID)!=1):
		if(nodosConectados['Predecesor']['id']<idparte and miID['id']>idparte):
			return True
		else:
			return False


def crearfingertable(fingertable,miID,sucesor):
	nodoid = int(miID,16)
	finger = {'nodo':hex(nodoid)[2:]}
	nodoSucesor =int(sucesor['id'],16)
	for x in range(0,159):
		nodo2 = nodoid + 2**x
		if(nodo2<=nodoSucesor):
			finger.update({'nodo'+str(x):sucesor})
	return finger
	pass

def main():# 1arg=nodoID, 2ipnodo, 3puerto nodo, 4arg=idsucesor 5arg=puerto sucesor
	if(len(sys.argv)==6):
		nodoID = hash(sys.argv[1])
		iPnodo = sys.argv[2]
		Pnodo = sys.argv[3]
		nodoName = 'tcp://'+iPnodo+':' + Pnodo
		sucesorName = 'tcp://'+sys.argv[4]+':'+sys.argv[5]
		miID = {'id':nodoID,'name':nodoName}
		fingertable = {}# finger table..............
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
		sock.send_multipart([nodoID.encode('utf8'),msg.encode('utf8'),b'0'])
		poller = zmq.Poller()
		poller.register(sys.stdin, zmq.POLLIN)
		poller.register(sock, zmq.POLLIN)
		poller.register(sockrouter,zmq.POLLIN)
		
		while(True) :
			socks = dict(poller.poll())
			#router--------------------------------
			if sockrouter in socks: # responde peticiones
				sender, destino , msg , data = sockrouter.recv_multipart()
				mensaje_json = json.loads(msg)
				if(mensaje_json['operacion']=='iniciar'):
					print(iniciando(nodosConectados))
					if(iniciando(nodosConectados) and emptyPre(mensaje_json)):
						print('primer anillo')
						mensaje_json['Predecesor'].update({'id':nodoID,'name':nodoName})
						mensaje_json['Sucesor'].update({'id':nodoID})
						mensaje_json.update({'operacion':'registrar'})
						msg = json.dumps(mensaje_json)
						print(msg)
						sock.send_multipart([sender,msg.encode('utf8'),b'0'])
						
					elif(emptySuc(mensaje_json)):
						print('no tengo sucesor')					
						mensaje_json.update(nodosConectados)
						mensaje_json.update({'operacion':'buscando'})
						mensaje_json.update({'miID':miID})
						msg = json.dumps(mensaje_json)
						sockrouter.send_multipart([sender,sender,msg.encode('utf8'),b'0'])
				elif(mensaje_json['operacion']=='buscando'):
					mensaje_json.update(nodosConectados)
					mensaje_json.update({'operacion':'buscando'})
					mensaje_json.update({'miID':miID})
					msg = json.dumps(mensaje_json)
					sockrouter.send_multipart([sender,sender,msg.encode('utf8'),b'0'])
					print('buscando posicion en anillo')			
				elif(mensaje_json['operacion']=='registrar'):
					del mensaje_json['operacion']
					nodosConectados.update(mensaje_json)
					fingertable = crearfingertable(fingertable,miID['id'],nodosConectados['Sucesor'])
					print('registrando primer anillo')
					print('------------')
				elif(mensaje_json['operacion']=='actSucesor'):
					del mensaje_json['operacion']
					nodosConectados['Sucesor'].update(mensaje_json)
					fingertable.update(crearfingertable(fingertable,miID['id'],nodosConectados['Sucesor']))
					print('actualize Sucesor')
				elif(mensaje_json['operacion']=='actPredecesor'):
					del mensaje_json['operacion']
					nodosConectados['Predecesor'].update(mensaje_json)
					print('actualize Predecesor')
			#responder cliente:
				elif(mensaje_json['operacion']=='upload'):
					if(canUpload(nodosConectados,miID,mensaje_json['parte'])):
						msg = {}
						msg.update(nodosConectados)
						msg.update({'operacion':'verdadero'})
						msg = json.dumps(msg)
						sockrouter.send_multipart([sender,sender,msg.encode('utf8'),b'0'])
					else:
						msg = {}
						msg.update(nodosConectados)
						msg.update({'operacion':'falso'})
						msg.update(miID)
						msg = json.dumps(msg)
						sockrouter.send_multipart([sender,sender,msg.encode('utf8'),b'0'])
				elif(mensaje_json['operacion']=='subir'):
					print('subiendo archivos')
					cargarArchivo(mensaje_json['parte'],data)

				elif(mensaje_json['operacion']=='download'):
					if(canDownload(nodosConectados,miID,mensaje_json['parte'])):
						msg = {}
						msg.update(nodosConectados)
						msg.update({'operacion':'verdadero'})
						msg.update(miID)
						msg = json.dumps(msg)
						data = descargarArchivo(mensaje_json['parte'])
						sockrouter.send_multipart([sender,sender,msg.encode('utf8'),data])
					else:
						msg = {}
						msg.update(nodosConectados)
						msg.update({'operacion':'falso'})
						msg.update(miID)
						msg = json.dumps(msg)
						sockrouter.send_multipart([sender,sender,msg.encode('utf8'),b'0'])
					
			#fin router-------------------------------------------
			elif sock in socks: #envia peticiones
			#----------enganchar server------------------------------------
				print('hay un socket')

				sender, msg , data = sock.recv_multipart()
				mensaje_json = json.loads(msg)
				print(msg)
				if(mensaje_json['operacion']=='buscando'):
					print('entro al if buscar')
					Sucesor = mensaje_json['Sucesor']['id']
					Predecesor = mensaje_json['Predecesor']['id']
					NodoConect = mensaje_json['miID']['id']
					if(nodoID>Sucesor and nodoID>Predecesor and nodoID>NodoConect and NodoConect > Sucesor): #para comparacion de hash quitar enteros
						print('soy el ultimo')
						nodosConectados['Sucesor'].update(mensaje_json['Sucesor'])
						nodosConectados['Predecesor'].update(mensaje_json['miID'])
						print(nodosConectados)
						msg = {}
						msg2 = {}
						msg.update(miID)
						msg2.update(miID)
						msg.update({'operacion':'actPredecesor'})
						msg = json.dumps(msg)
						msg2.update({'operacion':'actSucesor'})
						msg2 = json.dumps(msg2)
						#-----------------------------------------
						sock.disconnect(mensaje_json['miID']['name'])
						sock.connect(nodosConectados['Sucesor']['name'])
						sock.send_multipart([nodoID.encode('utf8'),msg.encode('utf8'),b'0'])
						print(nodosConectados['Sucesor']['name'])
						print(msg)
						#------------------------------------------------------
						
						sock.disconnect(mensaje_json['Sucesor']['name'])
						sock.connect(nodosConectados['Predecesor']['name'])
						sock.send_multipart([nodoID.encode('utf8'),msg2.encode('utf8'),b'0'])
						print('--------------------')
						print(nodosConectados['Predecesor']['name'])
						print(msg2)
						
						fingertable.update(crearfingertable(fingertable,miID['id'],nodosConectados['Sucesor']))
						#------------------------------------------------------

					elif(nodoID > Predecesor and nodoID < NodoConect):
						nodosConectados['Sucesor'].update(mensaje_json['miID'])
						nodosConectados['Predecesor'].update(mensaje_json['Predecesor'])
						msg = miID
						msg2 = miID
						msg.update({'operacion':'actPredecesor'})
						msg = json.dumps(msg)
						msg2.update({'operacion':'actSucesor'})
						msg2 = json.dumps(msg2)
						sock.disconnect(mensaje_json['miID']['name'])#desconectando
						sock.connect(nodosConectados['Sucesor']['name'])
						sock.send_multipart([nodoID.encode('utf8'),msg.encode('utf8'),b'0'])
						#---------------------------------------------------
						sock.disconnect(nodosConectados['Sucesor']['name'])#desconectando
						sock.connect(nodosConectados['Predecesor']['name'])
						sock.send_multipart([nodoID.encode('utf8'),msg2.encode('utf8'),b'0'])
						fingertable.update(crearfingertable(fingertable,miID['id'],nodosConectados['Sucesor']))
						print('estoy en medio')
					else:
						sock.disconnect(mensaje_json['miID']['name'])
						sock.connect(mensaje_json['Sucesor']['name'])
						nodosConectados.update({'operacion':'buscando'})
						msg = json.dumps(nodosConectados)
						print('seguir buscando mi posicion en anillo')
						sock.send_multipart([nodoID.encode('utf8'),msg.encode('utf8'),b'0'])
			#fin------- enganchar server  ---------------------------------
			elif sys.stdin.fileno() in socks:

				print("?")
				command = input()

				if(command=='n'):
					os.system('clear')
					print('-----------------------------')
					print('nodo id')
					print(miID)
					print('-----------------------------')
					print('-----------------------------')
					print('nodo Predecesor')
					print(nodosConectados['Predecesor'])
					print('-----------------------------')
					print('nodo sucesor')
					print(nodosConectados['Sucesor'])
					print('-----------------------------')
				elif(command=='f'):
					for x in fingertable:
						print(fingertable[x])
				elif(command=='c'):
					fingertable.update(crearfingertable(fingertable,miID['id'],nodosConectados['Sucesor']))
	else:
		print('se ejecuta con 6 argv')



if __name__ == '__main__':
    main()