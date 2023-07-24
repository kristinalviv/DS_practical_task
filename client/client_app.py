import socket
import logging
from datetime import datetime, timedelta
from inputimeout import inputimeout

logging.basicConfig(level=logging.INFO, format='%(asctime)s--%(levelname)s--%(message)s')


class Client:
	def __init__(self, host=socket.gethostbyname('server'), port=4040):
		self.host = host
		self.port = port

	def __str__(self):
		return f'Client connected to  {self.host} contain following messages: {Client.cl_msg_lst}.'

	def __repr__(self):
		return f'Client({self.host}:{self.port})'

	cl_msg_id = 0
	cl_msgs = set()
	cl_msg_lst = {}

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
					if input_value == 'List()':
						print(client.get_messages())
				except Exception as e:
					print(e)
				server_message = client_socket.recv(1024).decode()
				max_message_time = datetime.now() + timedelta(hours=0, minutes=0, seconds=20)
				if not server_message:
					logging.info('No message from the server side...')
					break
				print(f'Received from the server - {server_message}')
				split_message = server_message.split('-')
				message_id = split_message[0]
				message = split_message[1:]
				self.cl_msg_lst.update({message_id: f"{message}"})
				client_socket.send('Replicated'.encode())
				print(f'Message successfully saved')
		except Exception as e:
			client_socket.close()
			print('Connection closed')
			print(e)

	@staticmethod
	def close_connection(client_socket):
		client_socket.close()
		print('Connection closed')

	def get_messages(self):
		return self.cl_msg_lst


if __name__ == "__main__":
	client = Client()
	print(client)
	client_socket = client.create_connection(client.host, client.port)
	client.client_app(client_socket)
	print(client.__str__())
	client.close_connection(client_socket)
