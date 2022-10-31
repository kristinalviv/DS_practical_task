import socket
from messages_app import logging

class Client:
	def __init__(self, host='127.0.0.1', port=4040):
		self.host = host
		self.port = port

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
					f"Approved following server's message ID from client side: '''{server_resp}'''".encode())
		except Exception as e:
			client_socket.close()
			print(e)


if __name__ == "__main__":
	client = Client()
	client_socket = client.create_connection(client.host, client.port)
	client.client_app(client_socket)
	client_socket.close()
