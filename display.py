import zmq
import hashlib
import os
import sys
import json


def main():
	context = zmq.Context()
	socket = context.socket(zmq.ROUTER)
	socket.bind("tcp://*:4444")
	while True:
		print('servidor activo')
		sender, destino , msg = socket.recv_multipart()
		mensaje_json = json.loads(msg)
		
		print(destino)
		print(mensaje_json)


if __name__ == '__main__':
	main()