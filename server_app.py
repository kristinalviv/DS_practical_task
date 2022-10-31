import socket
# import sys
# sys.path.append('/Users/khrystyna/Desktop/Ucu/DS_practical_task/DS_practical_task')
from messages_app import MessageStore
from messages_app import logging


class ServerApp:
	def __init__(self):
		self.host = '127.0.0.1'

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

	def server_app(self, server_socket, conn):
		while True:
			try:
				new_msg = MessageStore.create_message()
				if new_msg.msg in ['exit', 'end', 'quit', 'q']:
					break
				print(f'{new_msg}')
				logging.info('Sending message to the client...')
				conn.send(f'{new_msg}'.encode())
				resp = conn.recv(1024).decode()
				if not resp:
					break
				logging.info(f'{resp}')
			except Exception as e:
				server_socket.close()
				conn.close()
				print(e)
				print('Connection closed')



if __name__ == "__main__":
	server = ServerApp()
	server_socket = server.create_server_socket()
	# listen_counts = 1
	conn, address = server.connect_to_replicas(server_socket)
	server.server_app(server_socket, conn)
	server_socket.close()
	conn.close()
	print('Connection closed')
