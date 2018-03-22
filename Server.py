
# python imports
import random
import json
import boto3
import threading
import time

# my file imports
from utils import *
from test import *

class Server: 
    # init with a server id
    # @param s_id - server id (letter a-e)
    def __init__(self, s_id='0'):
        # boolean for polling
        self.poll = True

        # get info about client for sqs queue and s3 stable storage
        self.region = 'us-west-2'
        self.secret = '40P15GW5em0iibFLEsX0a1t6eBSanwmEyGL8sy+q'
        self.public = 'AKIAIVCVGBRSVQKRNB3Q'

        # get access to sqs queue
        self.sqs = boto3.client('sqs', self.region, aws_secret_access_key=self.secret, aws_access_key_id=self.public)

        # create queue with timeout
        self.q = self.sqs.create_queue(QueueName='queue')
        self.q_url = 'https://sqs.us-east-2.amazonaws.com/044793243766/queue'

        # get sqs queue
        # id of this server
        self.id = s_id
        # timeout for starting a new election as random time between 150ms and 300ms
        self.timeout = random.uniform(5,10)
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

    # function to simulate a failure of this server node
    def fail(self):
        print('fail not yet implemented')

    # function to simulate a recover of this server node after failure
    def recover(self):
        print('recover not yet implemented')

    # function to simulate a timeout at this server node
    def timeout(self):
        print('timeout not yet implemented')

    # begin election by setting voted_for to self,
    # incrementing current term, and setting state
    # to candidate
    def begin_election(self):
        new_term = self.term + 1
        log_entry = []
        log_index = len(self.log) - 1 
        if log_index >= 0:
            log_entry = self.log[log_index]
        for i in range(5):
#            if i != int(self.id):
            message = create_request_message(str(i), self.id, log_index, log_entry, new_term)
            self.send_message(message)
        
    def receive_election_reply(self, election_reply_message):
        # turn message back into list
        election_reply_message = json.loads(election_reply_message[1:])
        # get sender
        message_sender = election_reply_message[1]
        # get vote
        vote = election_reply_message[2]
        # if vote is true, increment vote
        if vote:
            print('got vote from', message_sender)
            self.votes += 1
        if self.votes > 0:
            self.votes = 0
            self.leader = '0'
            self.voted_for = None
            self.state = 'leader'
            self.term += 1
            print('I am leader now')

    # handle the receiving of request vote message
    def receive_request_vote(self, request_vote_message):
        # turn message back into list
        request_vote_message = json.loads(request_vote_message[1:])
        # get sender 
        message_sender = request_vote_message[1]
        # get index of last entry
        message_log_index = int(request_vote_message[2])
        # get last entry
        message_log_entry = request_vote_message[3]
        # get new term
        message_term = int(request_vote_message[4])
        # create empty reply message
        reply = ''
        # make sure we haven't voted yet
        if self.voted_for == None and self.term < message_term:
            self.voted_for = message_sender
            self.state = 'election'
            reply += create_request_reply(message_sender, self.id, True)
        # if we have already voted, send false reply
        else:
            reply += create_request_reply(message_sender, self.id, False)
    
        self.send_message(reply)
        print('\tReply:', reply)

    # send append_entries message to all followers
    def send_append_entries(self):
        print('send_append_entries not yet implemented')

    # handle receiving append_entries message by comparing
    # the last index of received log to local log
    def receive_append_entries(self, append_message):
        append_message = json.loads(append_message[1:])
        # get sender
        message_sender = append_message[1]
        # get log_index
        message_log_index = int(append_message[2])
        # get log_after_index
        message_log_after_index = append_message[3] 
        # create empty reply message 
        reply = ''
        # check to see if we have this entry
        print('local last index:', len(self.log) - 1, 'rec log index:', message_log_index, 'log:', self.log, 'message_log:', message_log_after_index)
        if len(self.log) - 1 >= message_log_index and self.log[message_log_index] == message_log_after_index[0]:
            reply += create_append_reply(message_sender, self.id, True)
        else:
            reply += create_append_reply(message_sender, self.id, False)

        print('\tReply:', reply)

    # handle request from client
    def receive_client_request(self):
        print('receive_client_request not yet implemented')


    def poll_queue(self):
        print('Begin polling...')
        while self.poll:
            response = self.sqs.receive_message(QueueUrl=self.q_url,)
            if 'Messages' in response.keys():
                # get message from queue as string
                message = response['Messages'][0]
                # get receipt handle for deletion
                receipt_handle = message['ReceiptHandle']
                # get message text
                message = message.get('Body')

                # check to see if this message is for me
                if message[:1] == self.id:
                    print('This message is for me:')
                    # check to see if it is a request election
                    if json.loads(message[1:])[0] == "0":
                        self.receive_request_vote(message)
                    elif json.loads(message[1:])[0] == "1":
                        print('received election reply')
                        self.receive_election_reply(message)
                    elif json.loads(message[1:])[0] == "2":
                        print('received election reply')
                    elif json.loads(message[1:])[0] == "3":
                        print('received election reply')
                    else:
                        print('don\'t recognize this message:\n\t' + message[1:])
                # print received message
                print('\nmessage:', message)
                # delete received message
                self.sqs.delete_message(QueueUrl=self.q_url, ReceiptHandle=receipt_handle)

    ## sends current log
    def send_message(self, message):
        #messages = []
        # for each process in entry, create message
        #for process in entry[4]:
        #    if process != self.pid:
        #        m = 'new message!!'
        print('sending message:', message)
        response = self.sqs.send_message(QueueUrl=self.q_url, MessageBody=message)

if __name__ == '__main__':
    # create new calendar passing all arguments after self
    server = Server()
    server.begin_election()

    # create list of threads
    threads_L = []

    # create thread for polling
    threads_L.append(threading.Thread(name='poll', target=server.poll_queue))
        
    # start threads
    for thread in threads_L:
        thread.start()

    time.sleep(5)
    server.poll = False

    # join threads
    for thread in threads_L:
        thread.join()

