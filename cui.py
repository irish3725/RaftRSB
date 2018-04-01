import utils

class cui:

    ## @param cal - calendar object that will be interated with
    def __init__(self, client):
        self.client = client 

    ## main ui loop
    def run(self):  
        # value to read input into 
        val = ''

        while val != 'e' and val != 'quit' and val != 'exit':
            val = input('').lower()

            # adding an event
            if val == 'q' or val == 'w' or val == 'a' or val == 's':
                self.client.action(val)
                val = ''

        self.client.poll = False

