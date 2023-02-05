import socket
import itertools
import logging

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

	def create_server_socket(self, port=4040):
		try:
			socket.setdefaulttimeout(20)  # set 60 seconds timeout
			server_socket = socket.socket()
			server_socket.bind((self.host, port))
			print(f'Server connection is open on {self.host} with {port} port.')
			return socket, server_socket
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

	def message_approval(self, socket, connections):
		max_retry = 2
		answer_count = 0
		while max_retry > 0:
			print("I'm here")
			for number, unique_conn in enumerate(connections, start=1):
				try:
					id_received = unique_conn.recv(1024).decode()
					logging.info(f'Received ID from {number} node is {id_received}')
					answer_count += 1
				except socket.timeout as e:
					logging.info(e)
					logging.info(f'Did not save this message. Timeout occurs!')
					max_retry -= 1
					print(max_retry)
					break
				except Exception as e:
					logging.info(e)
			logging.info(f'Finished, received answer(s) is (are) {answer_count}.')
			return answer_count

	def proceed_message(self, socket, server_socket, connections):
		write_concern = 3
		while True:
			try:
				message = input('Please enter your message here...:)')
				if message in ['exit', 'end', 'quit', 'q']:
					break
				else:
					logging.info(f'Your message is - {message}')
					logging.info('Sending message to the client...')
					for unique_conn in connections:
						unique_conn.send(f'{message}'.encode())
					logging.info('Successfully sent to clients...')
					logging.info(f'Write concern is {write_concern}.')
					logging.info(f'Starting receiving answer from client nodes...')
					# maybe it should be method
					# for number, unique_conn in enumerate(connections, start=1):
					# 	try:
					# 		id_received = unique_conn.recv(1024).decode()
					# 		logging.info(f'Received ID from {number} node is {id_received}')
					# 		answer_count += 1
					# 	except socket.timeout as e:
					# 		logging.info(e)
					# 		logging.info(f'Did not save this message. Timeout occurs!')
					# 	except Exception as e:
					# 		logging.info(e)
					# logging.info(f'Finished, received answer(s) is (are) {answer_count}.')
					# maybe it should be method
					answer_count = ServerApp.message_approval(socket, server_socket, connections)
					if answer_count >= write_concern:
						logging.info('Write concern fulfilled. ')
						ServerApp.msg_lst.update({next(ServerApp.msg_id): f'{message}'})
						for unique_conn in connections:
							unique_conn.send(f'Approved'.encode())
						logging.info('Successfully sent approval to clients...')
					else:
						logging.info('Write concern was NOT fulfilled. Message was not saved')
						logging.info(f'Starting {retry} retry')
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
	socket, server_socket = server.create_server_socket()
	connections, address, listen_counts = server.connect_to_replicas(server_socket)
	server.proceed_message(socket, server_socket, connections)
	print(ServerApp.get_messages())
	server_socket.close()
	for unique_conn in connections:
		unique_conn.close()
	print('Connection closed')
