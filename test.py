
import Client
import Server
from utils import *

def test_utils():

    print('\n\t--Test utils--')
    server = Server.Server('a')

    # test create_log_entry   
    server.log.append(create_log_entry('1', '0', 'q'))
    server.log.append(create_log_entry('1', '0', 'w'))
    server.log.append(create_log_entry('1', '0', 's'))
    print('Log:', server.log)

    # test create_request_message
    request_message = create_request_message('b', server.id, '2', server.log[2], '1')
    print('Request:', request_message)

    # test create_request_reply
    request_reply = create_request_reply('a', 'b', True)
    print('Request Reply:', request_reply)
    
    # test create_append_message
    append_message = create_append_message('b', server.id, '1', server.log[1:])
    print('Append Entries:', append_message)

    # test create_append_reply
    append_reply = create_append_reply('a', 'b', True)
    print('Append Entries Reply:', append_reply)

def test_Server():

    print('\n\t--Test Server--')
    server = Server.Server('a')

    # test create_log_entry   
    server.log.append(create_log_entry('1', '0', 'q'))
    server.log.append(create_log_entry('1', '0', 'w'))
    server.log.append(create_log_entry('1', '0', 's'))
    print('Log:', server.log)

    # test create_request_message
    request_message = create_request_message('b', server.id, '2', server.log[2], '1')
    print('Request:', request_message)

    # test create_request_reply
    request_reply = create_request_reply('a', 'b', True)
    print('Request Reply:', request_reply)
    
    # test create_append_message
    append_message = create_append_message('b', server.id, '1', server.log[1:])
    print('Append Entries:', append_message)

    # test create_append_reply
    append_reply = create_append_reply('a', 'b', True)
    print('Append Entries Reply:', append_reply)

    # test receive_request_vote
    print('First receive_request_vote()')
    server.receive_request_vote(request_message)
    print('Second receive_request_vote()')
    server.receive_request_vote(request_message)

if __name__ == '__main__':
    test_utils()
    test_Server()
