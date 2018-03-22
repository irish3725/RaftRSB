import boto3
import threading
import time

## Main class for Calendar Application
class channel:

    ## @param my_id - id of this process
    def __init__(self, my_id=0, new_session=True):
        # boolean for stopping queuing eventually
        self.poll = True
        # create sqs connection
        self.sqs = boto3.client('sqs', 'us-west-2',
            aws_secret_access_key='40P15GW5em0iibFLEsX0a1t6eBSanwmEyGL8sy+q',#)
            aws_access_key_id='AKIAIVCVGBRSVQKRNB3Q')
        # create queue with timeout
        self.q = self.sqs.create_queue(QueueName='queue')
        self.q_url = 'https://sqs.us-east-2.amazonaws.com/044793243766/queue'

    def poll_queue(self):
        print('Begin polling...')
        while self.poll:
            response = self.sqs.receive_message(QueueUrl=self.q_url,)
            if 'Messages' in response.keys():
                # get message from queue as string
                message = response['Messages'][0]
                # get receipt handle for deletion
                receipt_handle = message['ReceiptHandle']
                # print received message
                print('\nmessage:', message.get('Body'))
                # delete received message
                self.sqs.delete_message(QueueUrl=self.q_url, ReceiptHandle=receipt_handle)

    ## sends current log
    def send_log(self, entry):
        messages = []
        # for each process in entry, create message
        for process in entry[4]:
            if process != self.pid:
                m = 'new message!!'
                print('sending message:', m)
                response = self.sqs.send_message(QueueUrl=self.q_url, MessageBody=m)

if __name__ == '__main__':
    # create new calendar passing all arguments after self
    channel = channel()

    # create list of threads
    threads_L = []

    # create thread for polling
    threads_L.append(threading.Thread(name='poll', target=channel.poll_queue))
        
    # start threads
    for thread in threads_L:
        thread.start()

    time.sleep(5)
    channel.poll = False

    # join threads
    for thread in threads_L:
        thread.join()

