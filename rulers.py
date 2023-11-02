class Rulers():

    def __init__(self, rulers_list = None, root_self = None):

        self.ruler_types = ['keys', 'actions']

        self.rulers_list = []
        if (rulers_list != None):
            for ruler in rulers_list:
                self.add(ruler)
            
        self.root_self = self
        if root_self != None:
            self.root_self = root_self # type Rulers

    # + Operator Overloading in Python
    def __add__(self, other):
        left_list = self.copy().list()
        right_list = other.copy().list()
        add_list = left_list + right_list
        return Rulers(add_list)
    
    # self is the list to work with!

    # def cleanRulers(self):
    #     self = [ ruler for ruler in self if ruler != None ]

    def list(self):
        return self.rulers_list
        
    def add(self, ruler): # Must be able to remove removed rulers from the main list
        
        if ruler != None and len(ruler) > 0:
            if ('type' in ruler and ruler['type'] in self.ruler_types):
                if 'group' not in ruler or ruler['group'] == None:
                    ruler['group'] = "main"
                if 'lines' not in ruler or ruler['lines'] == None or len(ruler['lines']) == 0:
                    ruler['lines'] = [None]
                if 'position' not in ruler or ruler['position'] == None or len(ruler['position']) != 2:
                    ruler['position'] = [0, 0]
                if ('offset' not in ruler or ruler['offset'] == None):
                    ruler['offset'] = 0
                if ('enabled' not in ruler or ruler['enabled'] == None):
                    ruler['enabled'] = True

                self.rulers_list.append(ruler)

        return self
    
    def remove(self):
        self.root_self.rulers_list = [ ruler for ruler in self.root_self.rulers_list if ruler not in self.rulers_list ]
        self.rulers_list = []
        return self
    
    def filter(self, types = [], groups = [], positions = [], position_range = [], ENABLED_ONLY = False):

        filtered_rulers = self.rulers_list.copy()
        if (ENABLED_ONLY):
            filtered_rulers = [
                staffRuler for staffRuler in filtered_rulers if staffRuler['enabled'] == True
            ]
        if (len(types) > 0 and types != [None]):
            filtered_rulers = [
                staffRuler
                    for staffRuler in filtered_rulers if staffRuler['type'] in types
            ]
        if (len(groups) > 0 and groups != [None]):
            filtered_rulers = [
                staffRuler
                    for staffRuler in filtered_rulers if staffRuler['group'] in groups
            ]
        if (len(positions) > 0 and positions != [None]): # Check for as None for NOT enabled
            filtered_rulers = [
                staffRuler
                    for staffRuler in filtered_rulers if staffRuler['position'] in positions
            ]
        if (len(position_range) == 2 and len(position_range[0]) == 2 and len(position_range[1]) == 2):
            # Using list comprehension
            filtered_rulers = [
                staffRuler for staffRuler in filtered_rulers
                        if not (self.position_lt(staffRuler['position'], position_range[0]) or self.position_gt(staffRuler['position'], position_range[1]))
            ]
        return Rulers(filtered_rulers, root_self = self.root_self)
    
    def print(self):
        if len(self.rulers_list) > 0:
            for ruler in self.rulers_list:
                print(ruler)
        else:
            print("[EMPTY]")
        print("\n")

    def copy(self):
        newRulers = Rulers()
        for ruler in self.rulers_list:
            #newRulers.add(ruler.copy())
            newRulers.rulers_list.append(ruler.copy())
        return newRulers

    def getPosition(self, ruler):
        return ruler['position'] 

    def getSequence(self, ruler, frames_step):
        return ruler['position'][0] * frames_step + ruler['position'][1]

    def position_gt(left_position, right_position):
        if (left_position[0] > right_position[0]):
            return True
        if (left_position[0] == right_position[0]):
            if (left_position[1] > right_position[1]):
                return True
        return False

    def position_lt(left_position, right_position):
        if (left_position[0] < right_position[0]):
            return True
        if (left_position[0] == right_position[0]):
            if (left_position[1] < right_position[1]):
                return True
        return False

# Python has magic methods to define overloaded behaviour of operators. The comparison operators (<, <=, >, >=, == and !=)
# can be overloaded by providing definition to __lt__, __le__, __gt__, __ge__, __eq__ and __ne__ magic methods.
# Following program overloads < and > operators to compare objects of distance class. 