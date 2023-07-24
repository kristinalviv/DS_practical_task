import socket
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s--%(levelname)s--%(message)s')


class ServerApp:
	def __init__(self):
		self.host = socket.gethostbyname('server')

	def __str__(self):
		return f'Server on {self.host} contain following messages: {ServerApp.msg_lst}.'

	def __repr__(self):
		return f'ServerApp({self.host}, {ServerApp.msg_lst})'

	def __aiter__(self, co):
		return self

	msg_id = 0
	msg_lst = {}

	def create_server_socket(self, port=4040):
		try:
			socket.setdefaulttimeout(20)
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
			print(socket.getdefaulttimeout())
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
		write_concern = 3
		while True:
			try:
				message = input('Please enter your message here...:)')
				if message in ['exit', 'end', 'quit', 'q']:
					break
				else:
					self.msg_id += 1
					message_id = self.msg_id
					success_repl = 0
					logging.info(f'Your message is - {message_id} - {message}')
					logging.info('Sending message to the client...')
					try:
						for unique_conn in connections:
							unique_conn.send(f'{message_id}-{message}'.encode())
						logging.info('Successfully sent to clients...')
						for number, unique_conn in enumerate(connections, start=1):
							response = unique_conn.recv(1024).decode()
							logging.info(f'Received from {number} node response: {response}')
							if response == 'Replicated':
								success_repl += 1
								print(f'Successfully replicated.')
							else:
								logging.info(f'Replication error, received following response:{response}.')
						if success_repl == write_concern:
							logging.info('Write concern fulfilled - date=%s', datetime.now())
							self.msg_lst.update({message_id: f"{message}"})
							logging.info(f'Replication to {success_repl} nodes was performed successfully.')
						elif success_repl < write_concern:
							logging.info(f"Write concern was NOT fulfilled.")
							self.msg_id -= 1
						logging.info(f'Write concern is {write_concern}.')
					except socket.timeout as e:
						message_id -= 1
						logging.info(e)
						logging.info(f'Did not save this message. Timeout occurs!')
					except Exception as e:
						message_id -= 1
						logging.info(f'Did not save this message. {e}')
			except Exception as e:
				message_id -= 1
				server_socket.close()
				for unique_conn in connections:
					unique_conn.close()
				print('Connection closed')
				print(f'Could not save your message, {e}')



if __name__ == "__main__":
	server = ServerApp()
	server_socket = server.create_server_socket()
	connections, address, listen_counts = server.connect_to_replicas(server_socket)
	server.proceed_message(server_socket, connections)
	print(server.__str__())
	server_socket.close()
	for unique_conn in connections:
		unique_conn.close()
	print('Connection closed')
