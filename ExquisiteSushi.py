from pprint import pprint   # Imports pprint from pprint

'''
A class used to store a token, its DF
and a tuple that contains the token's
postings.
'''
class ExquisiteSushi:

    '''
    Initializes self.memory to
    an empty dictionary.
    '''
    def __init__(self):
        self.memory = {}

    '''
    Inserts a token as the key to the self.memory
    dictionary and its postings (sandwich) as
    the value. At the same time, also calculates
    the DF of the token.
    '''
    def append(self,word,image):
        if word not in self.memory.keys():
            self.memory[word] = [image]
        else:
            self.memory[word].append(image)

    '''
    Prints the self.memory dictionary.
    '''
    def print_memory(self):
        pprint(self.memory)

    '''
    Returns the self.memory dictionary.
    '''
    def get_memory(self):
        return self.memory
