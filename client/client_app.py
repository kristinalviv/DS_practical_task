import socket
import json
import logging
import itertools
from datetime import datetime, timedelta
from inputimeout import inputimeout

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
	cl_msg_lst_final = {}
	cl_msg_id_final = itertools.count(1)

	def create_connection(self, host, port):
		try:
			client_socket = socket.socket()
			client_socket.connect((self.host, self.port))
			return client_socket
		except Exception as e:
			client_socket.close()
			print('unable to connect')
			print(e)

	def client_app(self, client_socket):
		try:
			while True:
				try:
					input_value = inputimeout(prompt='If you want to view all messages, type "List" here.. ', timeout=5)
					max_message_time = datetime.now() + timedelta(hours=0, minutes=0, seconds=60)
					if input_value == 'List()':
						print(client.get_messages())
				except Exception as e:
					print(e)
				server_message = client_socket.recv(1024).decode()
				message_time = datetime.now() + timedelta(hours=0, minutes=0, seconds=60)
				if not server_message:
					logging.info('No message from the server side...')
					break
				elif message_time > max_message_time:
					logging.info('Received old message(-s). Skipping it...')
					break
				print(f'Received from the server - {server_message}')
				cl_message_id = next(Client.cl_msg_id)
				Client.cl_msg_lst.update({cl_message_id: f'{server_message}'})
				print('Successfully pre-saved message.')
				logging.info(f'Client approved message! ID is: {cl_message_id}')
				client_socket.send(f'{cl_message_id}'.encode())
				try:
					socket.setdefaulttimeout(20)
					final_approval = client_socket.recv(1024).decode()
					if final_approval == 'Approved':
						print(f'Received {final_approval} message from the server.')
						final_cl_message_id = next(Client.cl_msg_id_final)
						Client.cl_msg_lst_final.update({final_cl_message_id: f'{server_message}'})
						print(f'Message successfully saved')
						socket.setdefaulttimeout(None)
					else:
						print('Turned message ID back since unsaved.')
						count = Client.cl_msg_id.__reduce__()[1][0] - 1
						Client.cl_msg_id = itertools.count(count)
						socket.setdefaulttimeout(None)
				except socket.timeout as e:
					print('Turned message ID back since unsaved.')
					count = Client.cl_msg_id.__reduce__()[1][0] - 1
					Client.cl_msg_id = itertools.count(count)
					socket.setdefaulttimeout(None)


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
		return Client.cl_msg_lst_final


if __name__ == "__main__":
	client = Client()
	print(client)
	client_socket = client.create_connection(client.host, client.port)
	client.client_app(client_socket)
	print(client.get_messages())
	client.close_connection(client_socket)
