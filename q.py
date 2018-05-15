
# python imports
import random
import sys
import json
import boto3
import threading
import time

# my file imports
import ui
from utils import *
from test import *

class Server: 
    # init with a server id
    # @param s_id - server id (letter a-e)
    def __init__(self):
        # boolean for polling
        self.poll = True
        # boolean for simulating clients
        self.simulate = False

        # get info about client for sqs queue and s3 stable storage
        self.region = 'us-west-2'
        self.secret = '40P15GW5em0iibFLEsX0a1t6eBSanwmEyGL8sy+q'
        self.public = 'AKIAIVCVGBRSVQKRNB3Q'

        # create list of queue urls
        self.q_url = list()

        self.q_url = []
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

        # get sqs queue
        # id of this server
        self.id = s_id
        # timeout for starting a new election as random time between 150ms and 300ms
        # will be set after clearing queue
        self.timeout = time.time()
        # counting timeouts for debugging
        self.timeout_count = 0
        # id of server that this server is voting for in current election
        self.voted_for = None
        # number of known votes for this server in current election
        self.votes = 0
        # current state of this server
        # possible states = {follower, leader, candidate}
        self.state = 'follower'
        # id of leader of this current term
        self.leader = None
        # current known term
        self.term = 0
        # known log of events
        self.log = [] 
        # count of known adds for commiting
        self.adds = []
        # index of last commit on this machine
        self.commit_index = -1

        # client things
        self.players = [[0,0], [0,0]]
        self.ko_rate = 5 

    ## function to randomly decide to generate client request
    def generate_cleint_request(self):
        # roll random number between 0 and 1000
        roll = int(random.uniform(0,100))
        if roll == 1 and self.leader != None:
#            print('\n!!!!!!!creating client request!!!!!!!\n')
            # choose a random action 
            action = int(random.uniform(0,4))
            if action == 0:
                action = 'q'
            elif action == 1:
                action = 'w'
            elif action == 2:
                action = 'a'
            elif action == 3:
                action = 's'

            # choose a random player
            player = 'p' + str(int(random.uniform(1,3)))
           
            # create client request and send to leader
            message = create_client_request(self.leader, player, action)
            self.send_message(message)

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
        response = self.sqs.receive_message(QueueUrl=self.q_url[my_queue],)

            if 'Messages' in response.keys():
                # get message from queue as string
                message = response['Messages'][0]
                # get receipt handle for deletion
                receipt_handle = message['ReceiptHandle']
                # get message text
                message = message.get('Body')
                print(message)

                self.sqs.delete_message(QueueUrl=self.q_url[my_queue], ReceiptHandle=receipt_handle)

    ## sends current log
    def send_message(self, address, message):
        self.sqs.send_message(QueueUrl=self.q_url[address], MessageBody=message)

if __name__ == '__main__':

    # if given input, set as id
    if len(sys.argv) > 1 and sys.argv[1] != 'clear':
        server = Server(sys.argv[1])
        ui = ui.ui(server)
        
        # grab that simulate flag if it exits
        if len(sys.argv) > 2:
            server.simulate = True

        # create list of threads
        threads_L = []

        # create thread for polling
        threads_L.append(threading.Thread(name='poll', target=server.poll_queue))
        threads_L.append(threading.Thread(name='ui', target=ui.run))
            
        # start threads
        for thread in threads_L:
            thread.start()

        # join threads
        for thread in threads_L:
            thread.join()

        time.sleep(5)
        server.clear_queue()
    elif len(sys.argv) > 1 and sys.argv[1] == 'clear':
        server = Server()
        server.clear_queue(True)
    else:
        print('I need some input (0/1/2/3/4/clear)')

