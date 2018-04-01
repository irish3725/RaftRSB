
# python imports
import random
import sys
import json
import boto3
import threading
import time

# my file imports
import cui
from utils import *
from test import *

class Client: 
    # init with a server id
    # @param s_id - server id (letter a-e)
    def __init__(self, s_id='0'):
        # boolean for polling
        self.poll = True

        # get info about client for sqs queue and s3 stable storage
        self.region = 'us-west-2'
        self.secret = '40P15GW5em0iibFLEsX0a1t6eBSanwmEyGL8sy+q'
        self.public = 'AKIAIVCVGBRSVQKRNB3Q'

        # create list of queue urls
        self.q_url = list()
        self.q_url.append('https://sqs.us-east-2.amazonaws.com/044793243766/queue0')
        self.q_url.append('https://sqs.us-east-2.amazonaws.com/044793243766/queue1')
        self.q_url.append('https://sqs.us-east-2.amazonaws.com/044793243766/queue2')
        self.q_url.append('https://sqs.us-east-2.amazonaws.com/044793243766/queue3')
        self.q_url.append('https://sqs.us-east-2.amazonaws.com/044793243766/queue4')
        self.q_url.append('https://sqs.us-east-2.amazonaws.com/044793243766/queue5')
        self.q_url.append('https://sqs.us-east-2.amazonaws.com/044793243766/queue6')

        # get access to sqs queue
        self.sqs = boto3.client('sqs', self.region, aws_secret_access_key=self.secret, aws_access_key_id=self.public)

        # create list of sqs queues
        self.q = list()

        # create queue with timeout
        for i in range(7):
            queue_name = 'queue' + str(i)
            self.q.append(self.sqs.create_queue(QueueName=queue_name))

        # number of running processes
        self.processes = 5

        # id of this server
        self.id = s_id
        # id of leader of this current term
        self.leader = None

    def action(self, action):
        player = 'p' + str(int(self.id) - 4)
        for i in range(0,5):
            message = create_client_request(str(i), player, action)
            self.send_message(message)

    ## print win if won
    def quit(self, win=False):
        self.poll = False
        if win:
            print('\tYou won!')
        else:
            print('\tYou did not win.')

    ## clear queue of messages from last run
    ## @param del_all - if False, only delete messages for this process
    def clear_queue(self, del_all=False):
        my_queue = int(self.id)

        print('clearing queue', end='')
        if del_all:
            print(' of all messages.')
        else:
            print(' of messages for this process.')

        # clear queue for 5 seconds
        clear_timeout = time.time() + 5 
        # receive message
        while time.time() < clear_timeout:
            response = self.sqs.receive_message(QueueUrl=self.q_url[my_queue],)
            if 'Messages' in response.keys():
                # get message from queue as string
                message = response['Messages'][0]
                # get receipt handle for deletion
                receipt_handle = message['ReceiptHandle']
                # get message text
                message = message.get('Body')

                if message[:1] == self.id or del_all:
                    # if we see a new message, increment timeout
                    clear_timeout = time.time() + 5 
                    # print received message
#                    print('\nmessage to delete:', message)
                    # delete received message
                    self.sqs.delete_message(QueueUrl=self.q_url[int(self.id)], ReceiptHandle=receipt_handle)

    def poll_queue(self):
        my_queue = int(self.id)
        self.clear_queue()
        print('Press:\nq - punch left\nw - punch right\na - block left\ns - block right')

        while self.poll:

            # receive message
            response = self.sqs.receive_message(QueueUrl=self.q_url[my_queue],)
            if 'Messages' in response.keys():
                # get message from queue as string
                message = response['Messages'][0]
                # get receipt handle for deletion
                receipt_handle = message['ReceiptHandle']
                # get message text
                message = message.get('Body')

                # check to see if this message is for me
                if message[:1] == self.id:
                    self.timeout = time.time() + get_timeout()
#                       print('This message is for me:')
                    # check to see if it is a request election
                    if json.loads(message[1:])[0] == "7":
#                            print('received request_vote')
                        self.receive_server_message(message)
                    else:
                        print('this message is not for me:\n\t' + message[1:])
                    # remove message from this queue
                    self.sqs.delete_message(QueueUrl=self.q_url[my_queue], ReceiptHandle=receipt_handle)

    ## sends current log
    def send_message(self, message):
        # for each process in entry, create message
#        print('sending message:', message)
        address = int(message[:1])
        response = self.sqs.send_message(QueueUrl=self.q_url[address], MessageBody=message)
    
    ## receive_server_message
    def receive_server_message(self, message):
        message = json.loads(message[1:])
        message_type = message[1]
        message_contents = message[2]

#        print('message type =', message_type)
#        print('message contents =', message_contents)

        if message_type == 'quit':
            self.quit(False)
        elif message_type == 'win':
            win = False
            if message_contents[0] + 5 == int(self.id):
                win = True

            self.quit(win)
        else:
            print(message_contents[1])



if __name__ == '__main__':

    # if given input, set as id
    if len(sys.argv) > 1:
        client = Client(sys.argv[1])
        ui = cui.cui(client)
        # create list of threads
        threads_L = []

        # create thread for polling
        threads_L.append(threading.Thread(name='poll', target=client.poll_queue))
        threads_L.append(threading.Thread(name='ui', target=ui.run))
            
        # start threads
        for thread in threads_L:
            thread.start()

        # join threads
        for thread in threads_L:
            thread.join()

        time.sleep(5)
        client.clear_queue()
    else:
        print('I need some input (5/6)')

