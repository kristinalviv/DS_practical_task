import socket
import json
import logging
import itertools

logging.basicConfig(level=logging.INFO, format='%(asctime)s--%(levelname)s--%(message)s')


class Client:
	def __init__(self, host=socket.gethostbyname('server'), port=4040):
		self.host = host
		self.port = port

	def __str__(self):
		return f'Client connects to  {self.host}:{self.port} contain following messages: {Client.cl_msg_lst}.'

	def __repr__(self):
		return f'Client({self.host}:{self.port})'

	cl_msg_id = itertools.count(1)
	cl_msg_lst = {}

	def create_connection(self, host, port):
		try:
			client_socket = socket.socket()
			print('created socket')
			client_socket.connect((self.host, self.port))
			print('now connected')
			return client_socket
		except Exception as e:
			client_socket.close()
			print('unable to connect')
			print(e)

	def client_app(self, client_socket):
		try:
			while True:
				if input() == 'List()':
					print(client.get_messages())
				else:
					server_message = client_socket.recv(1024).decode()
					if not server_message:
						logging.info('No message from the server side...')
						break
					print(f'Received from the server - {server_message}')
					cl_message_id = next(Client.cl_msg_id)
					Client.cl_msg_lst.update({cl_message_id: f'{server_message}'})
					print('Successfully saved message.')
					logging.info(f'Client approved message! ID is: {cl_message_id}')
					client_socket.send(f'Created id: {cl_message_id}'.encode())
		except Exception as e:
			client_socket.close()
			print('Connection closed')
			print(e)

	@staticmethod
	def close_connection(client_socket):
		client_socket.close()
		print('Connection closed')

	@staticmethod
	def get_messages():
		return Client.cl_msg_lst


if __name__ == "__main__":
	print('started')
	client = Client()
	print('created client')
	print(client)
	client_socket = client.create_connection(client.host, client.port)
	print(client_socket)
	client.client_app(client_socket)
	print(client.get_messages())
	client.close_connection(client_socket)
