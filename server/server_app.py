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
			print(f'Server connection is open on {self.host} with {port} port.')
			return server_socket
		except Exception as e:
			print(e)
			server_socket.close()

	def connect_to_replicas(self, server_socket, listen_counts=3):
		try:
			connections = []
			server_socket.listen(listen_counts)
			while listen_counts > 0:
				conn, address = server_socket.accept()
				listen_counts -= 1
				connections.append(conn)
				print(f'Address of connected replica: {str(address)}')
				print(connections)
			return connections, address, listen_counts
		except Exception as e:
			print(e)
			server_socket.close()
			for unique_conn in connections:
				unique_conn.close()

	def proceed_message(self, server_socket, connections):
		write_concern = listen_counts - 1
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
					for unique_conn in connections:
						unique_conn.send(f'{message}'.encode())
					logging.info('Successfully sent to clients...')
					answer_count = 0
					logging.info(f'Write concern is {write_concern}.')
					logging.info(f'Starting receiving answer from client nodes. Received answer is {answer_count}.')
					for number, unique_conn in enumerate(connections, start=1):
						id_received = unique_conn.recv(1024).decode()
						logging.info(f'Received ID from {number} node is {id_received}')
						id_from_client = id_received.split().__getitem__(2)
						if int(message_id) == int(id_from_client):
							logging.info(f'Replication to {number} node was performed successfully.')
						else:
							logging.info(f"Replication to {number} node has an error. Server's ID is {message_id}, "
										 f"while Client's ID is {id_from_client}")
						answer_count += 1
					logging.info(f'Finished, received answer(s) is (are) {answer_count}.')
					if answer_count >= (listen_counts - 1):
						logging.info('Write concern fulfilled. ')
			# id_received = conn.recv(1024).decode()
			# if not id_received:
			# 	break
			# logging.info(f'{id_received}')
			# id_from_client = id_received.split().__getitem__(2)
			# if int(message_id) == int(id_from_client):
			# 	logging.info('Replication was performed successfully')
			# else:
			# 	logging.info(f"Replication has an error. Server's ID is {message_id}, "
			# 				 f"while Client's ID is {id_from_client}")
			except Exception as e:
				server_socket.close()
				for unique_conn in connections:
					unique_conn.close()
				print('Connection closed')
				print(f'Could not save your message, {e}')

	@staticmethod
	def get_messages():
		return ServerApp.msg_lst


if __name__ == "__main__":
	server = ServerApp()
	server_socket = server.create_server_socket()
	# listen_counts = 1
	connections, address, listen_counts = server.connect_to_replicas(server_socket)
	server.proceed_message(server_socket, connections)
	print(ServerApp.get_messages())
	server_socket.close()
	for unique_conn in connections:
		unique_conn.close()
	print('Connection closed')
