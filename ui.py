import calendar
import utils

class ui:

    ## @param cal - calendar object that will be interated with
    def __init__(self, server):
        self.server = server 

    ## main ui loop
    def run(self):  
        # value to read input into 
        val = ''

        while val != 'q' and val != 'quit' and val != 'exit':
            val = input('(fail/recover/timeout) > ').lower()

            # adding an event
            if val == 'fail':
                self.server.fail()
                val = ''
            if val == 'recover':
                self.server.recover()
                val = ''
            if val == 'timeout':
                self.server.to()
                val = ''

