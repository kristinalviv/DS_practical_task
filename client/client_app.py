import socket
import logging
import json
from datetime import datetime, timedelta
from inputimeout import inputimeout

logging.basicConfig(level=logging.INFO, format='%(asctime)s--%(levelname)s--%(message)s')


class Client:
	def __init__(self, host=socket.gethostbyname('server'), port=4040):
		self.host = host
		self.port = port

	def __str__(self):
		return f'Client connected to  {self.host}:{self.port} contain following messages: {self.cl_msg_lst}.'

	def __repr__(self):
		return f'Client({self.host}:{self.port})'

	cl_msg_ids = set()
	cl_msg_lst = {}

	def create_connection(self, host, port):
		try:
			client_socket = socket.socket()
			client_socket.connect((self.host, self.port))
			return client_socket
		except Exception as e:
			client_socket.close()
			logging.info('unable to connect')
			print(e)

	def sync(self, client_socket):
		while True:
			print('Before: ', self.cl_msg_lst)
			client_socket.send('ERROR'.encode())
			accurate_messages = json.loads(client_socket.recv(1024).decode())
			print(accurate_messages)
			if accurate_messages.__contains__('-'):
				continue
			else:
				print(accurate_messages, len(accurate_messages), len(self.cl_msg_lst))
				if len(accurate_messages) > len(self.cl_msg_lst):
					continue
				else:
					self.cl_msg_lst.update(dict(accurate_messages))
					print('After: ', self.cl_msg_lst)

	def client_app(self, client_socket):
		try:
			while True:
				try:
					input_value = inputimeout(prompt='If you want to view all messages, type "List" here.. ', timeout=5)
					if input_value == 'List':
						print(client.get_messages())
				except Exception as e:
					print(e)
				server_message = client_socket.recv(1024).decode()
				if not server_message:
					logging.info('No message from the server side...')
					break
				logging.info(f'Received from the server - {server_message}')
				split_message = server_message.split('-')
				message_id = int(split_message[0])
				message = split_message[1:][0]
				if (self.cl_msg_lst.__len__() == 0) & (self.cl_msg_ids.__len__() == 0):
					self.cl_msg_lst.update({message_id: message})
					self.cl_msg_ids.add(message_id)  # per deduplication
					client_socket.send('Replicated'.encode())
				elif message_id not in self.cl_msg_ids and (message_id == max(self.cl_msg_ids) + 1):  # total ordering
					self.cl_msg_lst.update({message_id: message})
					self.cl_msg_ids.add(message_id)  # per deduplication
					client_socket.send('Replicated'.encode())
				else:
					logging.info('Inconsistency found...')
					self.sync(client_socket)

		except Exception as e:
			client_socket.close()
			logging.info('Connection closed')
			print(e)

	@staticmethod
	def close_connection(client_socket):
		client_socket.close()
		logging.info('Connection closed')

	def get_messages(self):
		return self.cl_msg_lst


if __name__ == "__main__":
	client = Client()
	logging.info(client)
	client_socket = client.create_connection(client.host, client.port)
	client.client_app(client_socket)
	logging.info(client.get_messages())
	client.close_connection(client_socket)
