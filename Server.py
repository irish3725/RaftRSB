
class Server:
    
    # init with a server id
    # @param s_id - server id (letter a-e)
    def __init__(s_id):
        # id of this server
        self.id = s_id
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
        self.log = {}

    # begin election by setting voted_for to self,
    # incrementing current term, and setting state
    # to candidate
    def begin_election():
        print("begin_elections not yet implemented")
        
    # handle the receiving of request vote message
    def receive_request_vote():
        print("receive_request_vote not yet implemented")

    # send append_entries message to all followers
    def send_append_entries():
        print("send_append_entries not yet implemented")

    # handle receiving append_entries message by comparing
    # the last index of received log to local log
    def receive_append_entries():
        print("receive_append_entries not yet implemented")

    # handle request from client
    def receive_client_request():
        print("receive_client_request not yet implemented")

if __name__ == '__main__':
    print('Server not at all implemented.')
