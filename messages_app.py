import itertools
# import datetime
import logging
logging.basicConfig(level=logging.INFO, format = '%(asctime)s--%(levelname)s--%(message)s')


class MessageStore:
    """
    This class gets all the messages and save them.
    """

    msg_id = itertools.count()
    msg_lst = {}


    def __init__(self, msg):
        self.id = next(MessageStore.msg_id)
        self.msg = msg
        MessageStore.msg_lst.update({f'{self.id}': f'{self.msg}'})

    def __str__(self):
        return f'Message is {self.msg} with {self.id} id.'

    def __repr__(self):
        return f'MessageStore({self.msg})'


    @staticmethod
    def get_messages():
        print(f'Your messages are: {MessageStore.msg_lst}')

    @staticmethod
    def create_message():
        # creation_time = datetime.datetime.now()
        # while True:
        try:
            message = input('Please enter your message here...:)')
            # if message == 'exit':
            #     break
            # else:
            new_message = MessageStore(message)
            logging.info('Message successfully created')
            # print(f'Your message is {new_message.msg} ({new_message.id})')
            # logging.info(f'Created new message with {new_message.msg_id} id at {creation_time}. ({new_message.msg})')
            return new_message
        except Exception as e:
            print(f'Could not save your message, {e}')




if __name__ == "__main__":
    MessageStore.create_message()
    MessageStore.get_messages()
