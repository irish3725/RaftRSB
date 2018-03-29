
# python imports
import random
import sys
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
        # create list of queue urls
        self.q_url = list()
        self.q_url.append('https://sqs.us-east-2.amazonaws.com/044793243766/queue0')
        self.q_url.append('https://sqs.us-east-2.amazonaws.com/044793243766/queue1')
        self.q_url.append('https://sqs.us-east-2.amazonaws.com/044793243766/queue2')
        self.q_url.append('https://sqs.us-east-2.amazonaws.com/044793243766/queue3')
        self.q_url.append('https://sqs.us-east-2.amazonaws.com/044793243766/queue4')

        # get access to sqs queue
        self.sqs = boto3.client('sqs', self.region, aws_secret_access_key=self.secret, aws_access_key_id=self.public)

        # create list of sqs queues
        self.q = list()

        # create queue with timeout
        for i in range(5):
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
        # print init output

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
        self.state = 'election'
        self.voted_for = self.id
        self.votes = 1
        print('Beginning election')
        new_term = self.term + 1
        log_entry = []
        log_index = len(self.log) - 1 
        if log_index >= 0:
            log_entry = self.log[log_index]
        for i in range(self.processes):
            if str(i) != self.id:
                message = create_request_message(str(i), self.id, log_index, log_entry, new_term)
                self.send_message(message)
        
    ## receive reply for vote request
    def receive_election_reply(self, election_reply_message):
        if self.state == 'election' and self.voted_for == self.id:
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
                print('I now have', self.votes, 'votes of', int(self.processes / 2 + 1))
            # if we have majority of votes, become leader
            if self.votes > int(self.processes / 2):
                self.votes = 0
                self.leader = self.id
                self.voted_for = None
                self.term += 1
                self.state = 'leader'
#                self.send_append_entries()
                print('I am leader now')
        else:
            print('I\'m not running. Ignoring vote')
            return

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
            self.timeout = time.time() + get_timeout()
        # if we have already voted, send false reply
        else:
            reply += create_request_reply(message_sender, self.id, False)
    
        self.send_message(reply)
        print('\tReply:', reply)

    ## send append_entries message to all followers
    ## @param index, index of last seen entry
    def send_append_entries(self):

        print('sending append entries at', int(time.time()))

        # reset timeout
        self.timeout = time.time() + get_timeout()
        
        index= len(self.log) - 2
        if index < 0:
            index = 0
        # create and send messages to all other processes
        for i in range(0,self.processes):
            if str(i) != self.id:
                message = create_append_message(str(i), self.id, index, self.log[index:], self.term)
                self.send_message(message)

    # handle receiving append_entries message by comparing
    # the last index of received log to local log
    def receive_append_entries(self, append_message):

        # get message
        append_message = json.loads(append_message[1:])
        # get sender
        message_sender = append_message[1]
        # get term
        message_term = append_message[4]
        # if we are in an election, set new leader,
        if message_term > self.term or (message_term == self.term and self.state == 'election'):
            self.leader = message_sender
            self.state = 'follower'
            self.voted_for = None
            self.votes = 0
            self.term = message_term
            print('my new leader is', message_sender)
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
            print('Nothing new here')
            reply += create_append_reply(message_sender, self.id, False)

        print('\tReply:', reply)


    def receive_append_reply(self, reply_message):
        print('receive_append_reply not yet implemeted')

    # handle request from client
    def receive_client_request(self):
        print('receive_client_request not yet implemented')

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
                    print('\nmessage to delete:', message)
                    # delete received message
                    self.sqs.delete_message(QueueUrl=self.q_url[int(self.id)], ReceiptHandle=receipt_handle)

    def poll_queue(self):
        my_queue = int(self.id)
        heartbeat_time = time.time() + 15
        self.clear_queue()
        print('Begin polling...')
        self.timeout = time.time() + random.uniform(5)
        while self.poll:

            if self.state == 'leader' and time.time() > heartbeat_time:
                print('sending  heartbeat')
                heartbeat_time = time.time() + 15
                self.send_append_entries()

            # check for timeout
            if time.time() > self.timeout:
                # if timeout, call timeout 
                self.to()
                self.timeout_count += 1
                if self.timeout_count > 10:
                    self.poll = False
                    
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
                    print('This message is for me:')
                    # check to see if it is a request election
                    if json.loads(message[1:])[0] == "0":
                        print('received request_vote')
                        self.receive_request_vote(message)
                    elif json.loads(message[1:])[0] == "1":
                        print('received request_vote reply')
                        self.receive_election_reply(message)
                    elif json.loads(message[1:])[0] == "2":
                        print('received append entries')
                        self.receive_append_entries(message)
                    elif json.loads(message[1:])[0] == "3":
                        print('received append reply')
                        self.receive_append_reply(message)
                    else:
                        print('don\'t recognize this message:\n\t' + message[1:])
                    # print received message
                    print('\nmessage:', message)
                    # delete received message
                    self.sqs.delete_message(QueueUrl=self.q_url[my_queue], ReceiptHandle=receipt_handle)

    ## timeout method
    def to(self):
        # if timeout, reset these values
        self.votes = 0
        self.voted_for = None
        self.leader = None
        # reset timeout
        self.timeout = time.time() + get_timeout()

        # if we were in an election, wait for a bit
        if self.state == 'election':
            print('my election failed, going back to follower')
            # add an extra 20 seconds to allow for more time in follower than election
            self.timeout += 20
            self.state = 'follower'
        # if we were not in an election, start an election
        else:
            self.state = 'election'
            self.begin_election()

    ## sends current log
    def send_message(self, message):
        # for each process in entry, create message
        print('sending message:', message)
        address = int(message[:1])
        response = self.sqs.send_message(QueueUrl=self.q_url[address], MessageBody=message)

if __name__ == '__main__':

    # if given input, set as id
    if len(sys.argv) > 1 and sys.argv[1] != 'clear':
        server = Server(sys.argv[1])
        # create list of threads
        threads_L = []

        # create thread for polling
        threads_L.append(threading.Thread(name='poll', target=server.poll_queue))
            
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

