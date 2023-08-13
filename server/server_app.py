import socket
import logging
import asyncio
from datetime import datetime
import json
from retrying import retry, RetryError

logging.basicConfig(level=logging.INFO, format='%(asctime)s--%(levelname)s--%(message)s')


class ServerApp:
	def __init__(self):
		self.host = socket.gethostbyname('server')

	def __str__(self):
		return f'Server on {self.host} contain following messages: {self.msg_lst}.'

	def __repr__(self):
		return f'ServerApp({self.host}, {self.msg_lst})'

	def __aiter__(self, co):
		return self

	msg_id = 0
	msg_lst = {}

	def create_server_socket(self, port=4040):
		try:
			server_socket = socket.socket()
			server_socket.bind((self.host, port))
			logging.info(f'Server connection is open on {self.host} with {port} port.')
			return server_socket
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
				logging.info(f'Address of connected replica: {str(address)}')
				logging.info(connections)
			return connections, address, listen_counts
		except Exception as e:
			print(e)
			server_socket.close()
			for unique_conn in connections:
				unique_conn.close()

	async def send_message(self, conn, message, message_id):
		conn.send(f'{str(message_id)}-{message}'.encode())
		logging.info('Sent, date=%s:', datetime.now())

	async def error_handling(self, conn):
		try:
			conn.settimeout(3)
			response = conn.recv(1024).decode()
			response = response[-4:]
			logging.info(f'Received response: {response}, date=%s', datetime.now())
			if response == 'FAIL':
				logging.info(f'{conn}, has inconsistency')
				servers_list = self.msg_lst
				conn.send(f'{json.dumps(servers_list)}'.encode())
				logging.info('Removed inconsistency')
		except socket.timeout as e:
			print(f'{conn} - no errors')

	async def remove_inconsistency(self, connections):
		tasks = []
		for unique_conn in connections:
			task = asyncio.create_task(self.error_handling(unique_conn))
			tasks.append(task)
		await asyncio.gather(*tasks, return_exceptions=True)
		logging.info(f'Data is consistent')

	def retry_if_result_none(result):
		"""Return True if retry is needed (in this case result equals 0), False otherwise"""
		return result == 0

	@retry(wait_exponential_multiplier=1000, wait_exponential_max=5000, stop_max_attempt_number=5, retry_on_result=retry_if_result_none)
	def retry(self, conn):
		try:
			response = conn.recv(1024).decode()
			response = response[-4:]
			logging.info(f'Received response: {response}, date=%s', datetime.now())
			if response == 'PASS':
				# logging.info(f'Successfully replicated. ')
				return response
			else:
				logging.info(f'Message was not saved to {conn}')
			return response
		except socket.timeout as s:
			logging.info('conn=%s is dead again', f'{conn}')
			return 0
		except RetryError as re:
			logging.info('error=%s', f'{re}')
		except Exception as e:
			logging.info('RetryError')


	async def proceed_with_retry(self, conns, answer_count, write_concern):
		try:
			for con in conns:
				result = self.retry(con)
				print('result', result)
				print('answer_count', answer_count)
				if result == 'PASS':
					answer_count += 1
				if answer_count >= write_concern:
					logging.info('Write concern fulfilled - date=%s', datetime.now())
					logging.info(f'Replication to {answer_count} nodes was performed successfully.')
				elif answer_count < write_concern:
					logging.info(f"Write concern was not fulfilled.")
					print('msg_id', self.msg_id)
					del self.msg_lst[self.msg_id]
					self.msg_id -= 1
		except RetryError as re:
			logging.info('error=%s', f'{re}')


	async def receive_response(self, conn):
		try:
			response = conn.recv(1024).decode()
			response = response[-4:]
			logging.info(f'Received response: {response}, date=%s', datetime.now())
			if response == 'PASS':
				logging.info(f'Successfully replicated. ')
			else:
				logging.info(f'Message was not saved to {conn}')
			return response
		except socket.timeout as e:
			print(f'{conn} is dead')
			return conn

	async def main(self, connections, message, message_id, answer_count, write_concern):
		logging.info(f'Sending message to the client nodes.')
		try:
			tasks = []
			for number, unique_conn in enumerate(connections, start=1):
				task = asyncio.create_task(self.send_message(unique_conn, message, message_id))
				tasks.append(task)
			await asyncio.gather(*tasks, return_exceptions=True)
			cors = [self.receive_response(unique_conn) for unique_conn in connections]
			failed_cors = []
			for num, cor in enumerate(cors, start=0):
				if answer_count >= write_concern:
					rest = cors[answer_count:]
					for task in rest:
						asyncio.create_task(task).cancel()
					break
				else:
					res = await cor
					if res == 'PASS':
						answer_count += 1
					else:
						failed_cors.append(num)
						continue
			print(f'successful answer count is {answer_count}, write concern is {write_concern}')
			retry = []
			[retry.append(connections[number]) for number in failed_cors]
			if retry:
				return answer_count, retry
			else:
				return answer_count, None
		except Exception as e:
			print(e)
			for unique_conn in connections:
				unique_conn.close()

	def proceed_message(self, server_socket, connections):
		while True:
			try:
				message_data = input('Please enter your message here...:)')
				if message_data in ['exit', 'end', 'quit', 'q']:
					break
				else:
					write_concern = int(message_data[0])
					message = message_data[2:]
					self.msg_id += 1
					message_id = self.msg_id
					self.msg_lst.update({message_id: f"{message}"})
					logging.info(f'Your message is - {message_id} - {message}')
					answer_count = 0
					logging.info(f'Write concern is {write_concern}.')
					answer_count_res, retry = asyncio.run(
						self.main(connections, message, message_id, answer_count, write_concern))
					if retry:
						print('retry', retry)
						loop = asyncio.new_event_loop()
						retry_task = loop.create_task(self.proceed_with_retry(retry, answer_count_res, write_concern))
						print('background task started')
						loop.run_until_complete(retry_task)
					if retry is None:
						if answer_count_res >= write_concern:
							logging.info('Write concern fulfilled - date=%s', datetime.now())
							logging.info(f'Replication to {answer_count_res} nodes was performed successfully.')
						elif answer_count_res < write_concern:
							logging.info(f"Write concern was not fulfilled.")
							del self.msg_lst[self.msg_id]
							self.msg_id -= 1
						asyncio.run(self.remove_inconsistency(connections))
			except socket.timeout as e:
				self.msg_id -= 1
				logging.info(e)
				logging.info(f'Did not save this message. Timeout occurs!')
				for unique_conn in connections:
					unique_conn.close()
				logging.info('Connection closed')
			except Exception as e:
				self.msg_id -= 1
				logging.info(f'Did not save this message. {e}')
				server_socket.close()
				for unique_conn in connections:
					unique_conn.close()
				logging.info('Connection closed')

	def get_messages(self):
		return self.msg_lst


if __name__ == "__main__":
	server = ServerApp()
	server_socket = server.create_server_socket()
	connections, address, listen_counts = server.connect_to_replicas(server_socket)
	server.proceed_message(server_socket, connections)
	logging.info(server.get_messages())
	server_socket.close()
	for unique_conn in connections:
		unique_conn.close()
	logging.info('Connection closed')
