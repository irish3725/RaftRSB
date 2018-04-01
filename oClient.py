
class Client:
    
    # init client with given client id
    # @param c_id - client id (number 0 or 1)
    def __init__(c_id):
        # id of this client
        self.id = c_id

    # user interface that will take input and 
    # call requesting functions
    # input mapping:
    #   [q] punch_with_left()
    #   [w] punch_with_right()
    #   [a] block_with_left()
    #   [s] blcok_with_right()
    def ui():
        print('ui not yet implemented')

    # send request to leader server to punch with left
    def punch_with_left():
        print('punch_with_left not yet implemented')

    # send request to leader server to punch with right
    def punch_with_right():
        print('punch_with_right not yet implemented')

    # send request to leader server to block with left
    def block_with_left():
        print('block_with_left not yet implemented')

    # send request to leader server to blcok with right
    def block_with_right():
        print('block_with_right not yet implemented')

if __name__ == '__main__':
    print('Client not at all implemented')

