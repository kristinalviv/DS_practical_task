import itertools
import datetime
import logging


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
        return f'MessageStore message is {self.msg} with {self.msg_id} id.'

    def __repr__(self):
        return f'MessageStore({self.msg})'


    @staticmethod
    def get_messages():
        print(MessageStore.msg_lst)

    @staticmethod
    def create_message():
        creation_time = datetime.datetime.now()
        while True:
            message = input('Please enter your message here...:)')
            new_message = MessageStore(message)
            MessageStore.get_messages()
            print(f'Your message is {new_message.msg} ({new_message.id})')
            # logging.info(f'Created new message with {new_message.msg_id} id at {creation_time}. ({new_message.msg})')





if __name__ == "__main__":
    MessageStore.create_message()
#     logging.basicConfig(filename='messages_app.py.log', level=logging.INFO)