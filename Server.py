
# python imports
import random
import json

# my file imports
from utils import *
from test import *

class Server: 
    # init with a server id
    # @param s_id - server id (letter a-e)
    def __init__(self, s_id):
        # id of this server
        self.id = s_id
        # timeout for starting a new election as random time between 150ms and 300ms
        self.timeout = random.uniform(150,300)
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
    def fail():
        print('fail not yet implemented')

    # function to simulate a recover of this server node after failure
    def recover():
        print('recover not yet implemented')

    # function to simulate a timeout at this server node
    def timeout():
        print('timeout not yet implemented')

    # begin election by setting voted_for to self,
    # incrementing current term, and setting state
    # to candidate
    def begin_election():
        print('begin_elections not yet implemented')
        
    # handle the receiving of request vote message
    def receive_request_vote(self, request_vote_message):
        # turn message back into list
        request_vote_message = json.loads(request_vote_message[1:])
        # get sender 
        message_sender = request_vote_message[1]
        # get index of last entry
        message_log_index = request_vote_message[2]
        # get last entry
        message_log_entry = request_vote_message[3]
        # get new term
        message_term = request_vote_message[4]
        # create empty reply message
        reply = ''
        # make sure we haven't voted yet
        if self.voted_for == None and self.term < int(message_term):
            self.term = message_term
            self.voted_for = message_sender
            reply += create_request_reply(message_sender, self.id, True)
        # if we have already voted, send false reply
        else:
            reply += create_request_reply(message_sender, self.id, False)
    
        print('\tReply:', reply)

    # send append_entries message to all followers
    def send_append_entries():
        print('send_append_entries not yet implemented')

    # handle receiving append_entries message by comparing
    # the last index of received log to local log
    def receive_append_entries():
        print('receive_append_entries not yet implemented')

    # handle request from client
    def receive_client_request():
        print('receive_client_request not yet implemented')

if __name__ == '__main__':
    print('server')
    
