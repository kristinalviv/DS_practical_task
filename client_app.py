import socket
import json
import server_app
from server_app import logging


class Client:
	def __init__(self, host='127.0.0.1', port=4040):
		self.host = host
		self.port = port

	def __str__(self):
		return f'Client on {self.host}:{self.port} contain following messages: {server_app.ServerApp.msg_lst}.'

	def __repr__(self):
		return f'Client({self.host}:{self.port})'

	stored_messages = {}

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
				server_resp = client_socket.recv(1024).decode()
				if not server_resp:
					logging.info('No message from the server side...')
					break
				print(f'Received from the server - {server_resp}')
				logging.info(f'Client approved message!')
				client_socket.send(
					f"Approved following server's message from client side: '''{server_resp}'''".encode())
				id_received = client_socket.recv(1024).decode()
				logging.info(f'Received approval from the server - {id_received}')
				with open('messages_app.json', 'r') as file:
					stored_data = json.load(file, object_hook=lambda d: {int(k) if k.lstrip('-').isdigit() else k:v for k,v in d.items()})
					file.close()
				last_key_on_client = list(stored_data.keys())[-1]
				print(last_key_on_client)
				id_from_server = id_received.split().__getitem__(2)
				print(id_from_server)
				# print(self.stored_messages.keys()[-1])
				if id_from_server == last_key_on_client:
					self.stored_messages.update(stored_data)
				client_socket.send(
					f"Successfully saved {last_key_on_client} message ID on the client side".encode())
		except Exception as e:
			client_socket.close()
			print('Connection closed')
			print(e)

	@staticmethod
	def close_connection(client_socket):
		print(Client.stored_messages)
		client_socket.close()
		print('Connection closed')


if __name__ == "__main__":
	client = Client()
	client_socket = client.create_connection(client.host, client.port)
	client.client_app(client_socket)
	client.close_connection(client_socket)
