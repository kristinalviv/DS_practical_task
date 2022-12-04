import socket
import itertools
import logging
import json

logging.basicConfig(level=logging.INFO, format='%(asctime)s--%(levelname)s--%(message)s')


class ServerApp:
	def __init__(self):
		self.host = socket.gethostbyname('server')

	def __str__(self):
		return f'Server on {self.host} contain following messages: {ServerApp.msg_lst}.'

	def __repr__(self):
		return f'ServerApp({self.host}, {ServerApp.msg_lst})'

	msg_id = itertools.count(1)
	msg_lst = {}

	# @property
	# def msg_lst(self):
	# 	return self._msg_lst
	#
	# @msg_lst.setter
	# def msg_lst(self, message_id, message):
	# 	self._msg_lst.update({f'{message_id}': f'{message}'})

	def create_server_socket(self, port=4040):
		try:
			server_socket = socket.socket()
			server_socket.bind((self.host, port))
			# server_socket.bind((self.host, port))
			print(f'Server connection is open on {self.host} with {port} port.')
			return server_socket
		except Exception as e:
			print(e)
			server_socket.close()

	def connect_to_replicas(self, server_socket, listen_counts=1):
		try:
			self.server_socket = server_socket
			self.listen_counts = listen_counts
			server_socket.listen(listen_counts)
			conn, address = server_socket.accept()
			print(f'Address of connected replica: {str(address)}')
			return conn, address
		except Exception as e:
			print(e)
			server_socket.close()
			conn.close()

	def proceed_message(self, server_socket, conn):
		while True:
			try:
				message = input('Please enter your message here...:)')
				if message in ['exit', 'end', 'quit', 'q']:
					break
				else:
					message_id = next(ServerApp.msg_id)
					ServerApp.msg_lst.update({message_id: f'{message}'})
					logging.info(f'Your message is - {message_id} - {message}')
					logging.info('Sending message to the client...')
					conn.send(f'{message}'.encode())
					id_received = conn.recv(1024).decode()
					if not id_received:
						break
					logging.info(f'{id_received}')
					id_from_client = id_received.split().__getitem__(2)
					if int(message_id) == int(id_from_client):
						logging.info('Replication was performed successfully')
					else:
						logging.info(f"Replication has an error. Server's ID is {message_id}, " 
									 f"while Client's ID is {id_from_client}")
			except Exception as e:
				server_socket.close()
				conn.close()
				print('Connection closed')
				print(f'Could not save your message, {e}')

	@staticmethod
	def get_messages():
		return ServerApp.msg_lst



if __name__ == "__main__":
	server = ServerApp()
	server_socket = server.create_server_socket()
	# listen_counts = 1
	conn, address = server.connect_to_replicas(server_socket)
	ServerApp.proceed_message(server, server_socket, conn)
	print(ServerApp.get_messages())
	server_socket.close()
	conn.close()
	print('Connection closed')
