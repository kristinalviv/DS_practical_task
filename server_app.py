import socket
import itertools
import logging
import json

logging.basicConfig(level=logging.INFO, format='%(asctime)s--%(levelname)s--%(message)s')


class ServerApp:
	msg_id = itertools.count()
	msg_lst = {}

	def __init__(self):
		self.host = '127.0.0.1'

	def __str__(self):
		return f'Server on {self.host} contain following messages: {ServerApp.msg_lst}.'

	def __repr__(self):
		return f'ServerApp({self.host}, {ServerApp.msg_lst})'

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
					logging.info(f'Your message is - {message_id} - {message}')
					logging.info('Sending message to the client...')
					conn.send(f'{message}'.encode())
					resp = conn.recv(1024).decode()
					if not resp:
						break
					logging.info(f'{resp}')
					ServerApp.msg_lst.update({message_id: f'{message}'})
					with open('messages_app.json', 'w') as file:
						file.write(json.dumps(ServerApp.msg_lst, indent=4))
						file.write("\n")
						file.close()
					logging.info('Message successfully created. Sending approval to the client...')
					conn.send(f'Created id: {message_id}'.encode())
					resp = conn.recv(1024).decode()
					if not resp:
						break
					logging.info(f'{resp}')
			except Exception as e:
				server_socket.close()
				conn.close()
				print('Connection closed')
				print(f'Could not save your message, {e}')


def get_messages():
	list = ServerApp.msg_lst
	return list



if __name__ == "__main__":
	server = ServerApp()
	server_socket = server.create_server_socket()
	# listen_counts = 1
	conn, address = server.connect_to_replicas(server_socket)
	ServerApp.proceed_message(server, server_socket, conn)
	get_messages()
	print(get_messages())
	server_socket.close()
	conn.close()
	print('Connection closed')
