class Rulers():

    def __init__(self, rulers_list = None, root_self = None, FROM_RULERS = False):

        self.ruler_types = ['keys', 'actions']

        self.root_self = self
        if root_self != None:
            self.root_self = root_self # type Rulers

        self.rulers_list = []
        if (rulers_list != None):
            if (FROM_RULERS):
                self.rulers_list = rulers_list
            else:
                for ruler in rulers_list:
                    self.add(ruler)
            
    # + Operator Overloading in Python
    def __add__(self, other):
        self_rulers_list = self.list()
        other_rulers_list = other.list()

        return Rulers(self_rulers_list + other_rulers_list, root_self = self.root_self, FROM_RULERS = True)
    
    # self is the list to work with!

    # def cleanRulers(self):
    #     self = [ ruler for ruler in self if ruler != None ]

    def list(self):
        return self.rulers_list
    
    def len(self):
        return len(self.rulers_list)
        
    def add(self, ruler): # Must be able to remove removed rulers from the main list
        
        if ruler != None and len(ruler) > 0:
            if ('type' in ruler and ruler['type'] in self.ruler_types):
                if 'group' not in ruler or ruler['group'] == None:
                    ruler['group'] = "main"
                if 'position' not in ruler or ruler['position'] == None or len(ruler['position']) != 2:
                    ruler['position'] = [0, 0]
                if 'lines' not in ruler or ruler['lines'] == None or len(ruler['lines']) == 0:
                    ruler['lines'] = [None]
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
                ruler for ruler in filtered_rulers if ruler['enabled'] == True
            ]
        if (len(types) > 0 and types != [None]):
            filtered_rulers = [
                ruler for ruler in filtered_rulers if ruler['type'] in types
            ]
        if (len(groups) > 0 and groups != [None]):
            filtered_rulers = [
                ruler for ruler in filtered_rulers if ruler['group'] in groups
            ]
        if (len(positions) > 0 and positions != [None]): # Check for as None for NOT enabled
            in_position_rulers = []
            for position in positions:
                if len(position) == 2:
                    in_position_rulers += [
                        ruler for ruler in filtered_rulers if self.position_eq(ruler['position'], position)
                    ]
            filtered_rulers = in_position_rulers
        if (len(position_range) == 2 and len(position_range[0]) == 2 and len(position_range[1]) == 2):
            # Using list comprehension
            filtered_rulers = [
                ruler for ruler in filtered_rulers
                        if not (self.position_lt(ruler['position'], position_range[0]) and self.position_lt(ruler['position'], position_range[1]))
            ]
        return Rulers(filtered_rulers, root_self = self.root_self, FROM_RULERS = True)
    
    def print(self):
        if len(self.rulers_list) > 0:
            for ruler in self.rulers_list:
                print(ruler)
        else:
            print("[EMPTY]")
        print("\n")

    def copy(self):
        rulers_list_copy = []
        for ruler in self.rulers_list:
            rulers_list_copy.append(ruler)
        return Rulers(rulers_list_copy, FROM_RULERS = True)
    
    def unique(self):
        unique_rulers_list = []
        for ruler in self.rulers_list:
            if ruler not in unique_rulers_list:
                unique_rulers_list.append(ruler)

        return Rulers(unique_rulers_list, root_self = self.root_self, FROM_RULERS = True)
    
    def reverse(self):
        straight_rulers_list = self.rulers_list
        reversed_rulers_list = [None] * self.len()
        for i in range(self.len()):
            reversed_rulers_list[i] = straight_rulers_list[self.len() - 1 - i]

        return Rulers(reversed_rulers_list, root_self = self.root_self, FROM_RULERS = True)
    
    def sort(self, reverse = False):

        sorted_rulers_list = self.rulers_list.copy()

        if (len(sorted_rulers_list) > 1):
            for i in range(0, len(sorted_rulers_list) - 1):
                sorted_list = True
                for j in range(1, len(sorted_rulers_list) - i):
                    if (self.position_gt(sorted_rulers_list[j - 1]['position'], sorted_rulers_list[j]['position'])):
                        sorted_list = False
                        temp_ruler = sorted_rulers_list[j - 1]
                        sorted_rulers_list[j - 1] = sorted_rulers_list[j]
                        sorted_rulers_list[j] = temp_ruler
                if sorted_list:
                    break

        sorted_rulers = Rulers(sorted_rulers_list, root_self = self.root_self, FROM_RULERS = True)

        if reverse:
            return sorted_rulers.reverse()
        return sorted_rulers

    def merge(self):

        type_groups = [] # merge agregates rulers by type and gorup

        for ruler in self.rulers_list:
            ruler_type_group = {'type': ruler['type'], 'group': ruler['group']}
            listed = False
            for type_group in type_groups:
                if type_group['type'] == ruler_type_group['type'] and type_group['group'] == ruler_type_group['group']:
                    listed = True
                    break

            if not listed:
                type_groups.append(ruler_type_group)

        merged_rulers = []

        for type_group in type_groups:

            subject_rulers = self.filter(types=[type_group['type']], groups=[type_group['group']]).sort(reverse=True).list()
                                
            head_offset = 0
            tail_offset = 0
            for ruler in subject_rulers:
                if ruler['offset'] < head_offset:
                    head_offset = ruler['offset']
                if (len(ruler['lines']) + ruler['offset'] > tail_offset):
                    tail_offset = len(ruler['lines']) - 1 + ruler['offset']

            mergedRuler = {
                'type': type_group['type'],
                'group': type_group['group'],
                'position': subject_rulers[0]['position'],
                'lines': [None] * (tail_offset - head_offset + 1), # list
                'offset': head_offset,
                'enabled': subject_rulers[0]['enabled']
            }

            for subject_ruler in subject_rulers:
                for i in range(len(subject_ruler['lines'])):
                    merged_line = i + subject_ruler['offset'] - mergedRuler['offset']
                    if (mergedRuler['lines'][merged_line] == None):
                        mergedRuler['lines'][merged_line] = subject_ruler['lines'][i]

            merged_rulers.append(mergedRuler)

        return Rulers(merged_rulers, root_self = self.root_self, FROM_RULERS = True)
    


    def getPosition(self, ruler):
        return ruler['position'] 

    def getSequence(self, ruler, frames_step):
        return ruler['position'][0] * frames_step + ruler['position'][1]

    def position_gt(self, left_position, right_position):
        if (left_position[0] > right_position[0]):
            return True
        if (left_position[0] == right_position[0]):
            if (left_position[1] > right_position[1]):
                return True
        return False

    def position_lt(self, left_position, right_position):
        if (left_position[0] < right_position[0]):
            return True
        if (left_position[0] == right_position[0]):
            if (left_position[1] < right_position[1]):
                return True
        return False

    def position_eq(self, left_position, right_position):
        if (left_position[0] == right_position[0] and left_position[1] == right_position[1]):
            return True
        return False
    
    def sortPositions(self, positions, reverse = False):
        sorted_positions = positions[:]
        compare_function = self.position_gt
        if reverse:
            compare_function = self.position_lt
        if (len(sorted_positions) > 1):
            sorted = False
            while (not sorted):
                sorted = True
                for i in range(1, len(sorted_positions)):
                    if (compare_function(sorted_positions[i - 1], sorted_positions[i])):
                        sorted = False
                        temp_position = sorted_positions[i - 1]
                        sorted_positions[i - 1] = sorted_positions[i]
                        sorted_positions[i] = temp_position

        return sorted_positions

# Python has magic methods to define overloaded behaviour of operators. The comparison operators (<, <=, >, >=, == and !=)
# can be overloaded by providing definition to __lt__, __le__, __gt__, __ge__, __eq__ and __ne__ magic methods.
# Following program overloads < and > operators to compare objects of distance class. 