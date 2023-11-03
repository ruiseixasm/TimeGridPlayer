class Rulers(list):

    def __init__(self, rulers_list = None, root_self = None):

        if root_self != None:
            self.root_self = root_self
        else:
            self.root_self = self

        super().__init__(rulers_list)

        print (list)

        self.ruler_types = ['keys', 'actions']
        if rulers != None:
            self = rulers.copy()
        with_removed_rulers = False # to be place in actions

    # self is the list to work with!

    # def cleanRulers(self):
    #     self = [ ruler for ruler in self if ruler != None ]
        
    def addRuler(self, ruler): # Must be able to remove removed rulers from the main list
        
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

                self.append(ruler)

        return self
    
    def removeRulers(self):
        self.root_self = [ self.root_self not in self ]
        self = []
        return self
    
    def filterRulers(self, types = [], groups = [], positions = [], position_range = [], ENABLED_ONLY = False):
        
        filtered_rulers = Rulers(self).copy()
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
        return filtered_rulers
    
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