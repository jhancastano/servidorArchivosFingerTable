import zmq
import hashlib
import os
import sys

def hash(idnodo):
	objetohash = hashlib.sha1(idnodo.encode('utf8'))
	cadena = objetohash.hexdigest()	
	print(cadena)
	return cadena

def main():# 1arg=nodoID, 2arg=idsucesor 2arg=puerto sucesor
	if(len(sys.argv)==4):
		print(sys.argv[1])
		nodoID = hash(sys.argv[1])
		coneccion = {'Sucesor':sys.argv[2]+':'+sys.argv[3] ,'Predecesor':'null'}						
		print(coneccion['Sucesor'])
	else:
		print('se ejecuta con 3 argv')


		
if __name__ == '__main__':
    main()