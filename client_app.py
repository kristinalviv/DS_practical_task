import socket
import json
import server_app
from server_app import logging
import itertools


class Client:
	def __init__(self, host='127.0.0.1', port=4040):
		self.host = host
		self.port = port

	def __str__(self):
		return f'Client on {self.host}:{self.port} contain following messages: {server_app.ServerApp.msg_lst}.'

	def __repr__(self):
		return f'Client({self.host}:{self.port})'

	cl_msg_id = itertools.count(1)
	cl_msg_lst = {}

	def create_connection(self, host, port):
		try:
			client_socket = socket.socket()
			client_socket.connect((self.host, self.port))
			return client_socket
		except Exception as e:
			client_socket.close()
			print(e)

	def client_app(self, client_socket):
		try:
			while True:
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
	client = Client()
	client_socket = client.create_connection(client.host, client.port)
	client.client_app(client_socket)
	print(client.get_messages())
	client.close_connection(client_socket)
