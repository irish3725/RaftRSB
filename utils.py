
import json

# creates log entry (list) in the form of:
#   [<term>, <requestor>, <action>]
def create_log_entry(term, requestor, action):
    return([term, requestor, action, '0'])

# returns request_vote (string) message in the form of:
#   <receiver_id>[0, <sender_id>, <log_index>, <log_entry>, <new_term>]
def create_request_message(receiver, sender, log_index, log_entry, new_term):
    message_contents = json.dumps(['0', sender, log_index, log_entry, new_term])
    return(receiver + message_contents)

# returns request_vote_reply (string) message in the form of:
#   <receiver_id>[1, <sender_id>, <voted_for (true, false)>]
def create_request_reply(receiver, sender, vote):
    message_contents = json.dumps(['1', sender, vote])
    return(receiver + message_contents)

# returns append_entries (string) message in the form of:
#   <receiver_id>[2, <sender_id>, <log_index>, <log_after(and including)_index>]
def create_append_message(receiver, sender, log_index, log_after_index):
    message_contents = json.dumps(['2', sender, log_index, log_after_index])
    return(receiver + message_contents)

# returns append_entries_reply (string) message in the form of:
#   <receiver_id>[3, <sender_id>, <appended (true, false)>]
def create_append_reply(receiver, sender, appended):
    message_contents = json.dumps(['3', sender, appended])
    return(receiver + message_contents)

