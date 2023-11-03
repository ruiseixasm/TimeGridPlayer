import staff

class Rulers():

    def __init__(self, rulers_list = None, staff_grid = None, root_self = None, FROM_RULERS = False):

        self.ruler_types = ['keys', 'actions']
        self.staff_grid = staff_grid

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

    def root(self):
        return self.root_self
            
    def reroot(self):
        self.root_self = self
        return self
    
    def updateStaff(self):
        if self.staff_grid != None:
            self.staff_grid.clear()
            enabled_rulers_list = self.filter(enabled=True).list()
            self.staff_grid.add(enabled_rulers_list)

        return self
            
    # + Operator Overloading in Python
    def __add__(self, other):
        '''Works as Union'''
        self_rulers_list = self.list()
        other_rulers_list = other.list()

        return Rulers(self_rulers_list + other_rulers_list, staff_grid = self.staff_grid, root_self = self.root_self, FROM_RULERS = True)
    
    def __sub__(self, other):
        '''Works as exclusion'''
        self_rulers_list = self.list()
        other_rulers_list = other.list()

        exclusion_list = [ ruler for ruler in self_rulers_list if ruler not in other_rulers_list ]

        return Rulers(exclusion_list, staff_grid = self.staff_grid, root_self = self.root_self, FROM_RULERS = True)
    
    def __mul__(self, other):
        '''Works as intersection'''
        self_rulers_list = self.list()
        other_rulers_list = other.list()
        
        intersection_list = [ ruler for ruler in self_rulers_list if ruler in other_rulers_list ]

        return Rulers(intersection_list, staff_grid = self.staff_grid, root_self = self.root_self, FROM_RULERS = True)
    
    def __div__(self, other):
        '''Works as divergence'''
        union_rulers = self.__add__(other)
        intersection_rulers = self.__mul__(other)

        return union_rulers - intersection_rulers
    
    
    def list(self):
        return self.rulers_list
    
    def len(self):
        return len(self.rulers_list)
    
    def empty(self):
        empty_rulers_list = []
        return Rulers(empty_rulers_list, staff_grid = self.staff_grid, root_self = self.root_self, FROM_RULERS = True)
        
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
                if self.staff_grid != None and ruler['enabled'] == True:
                    self.staff_grid.add([ruler])

        return self
    
    def remove(self):
        self.root_self.rulers_list = [ ruler for ruler in self.root_self.rulers_list if ruler not in self.rulers_list ]
        if self.staff_grid != None:
            enabled_rulers_list = self.filter(enabled=True).list()
            self.staff_grid.remove(enabled_rulers_list)
        self.rulers_list = []
        return self
    
    def duplicate(self):
        for ruler in self.rulers_list[:]:
            self.add(ruler.copy())
        return self
    
    def enable(self):
        disabled_rulers_list = self.filter(enabled=False).list()
        for disabled_ruler in disabled_rulers_list:
            disabled_ruler['enabled'] = True
        self.staff_grid.add(disabled_rulers_list)
        return self
    
    def disable(self):
        enabled_rulers_list = self.filter(enabled=True).list()
        for enabled_ruler in enabled_rulers_list:
            enabled_ruler['enabled'] = False
        self.staff_grid.remove(enabled_rulers_list)
        return self
    
    def filter(self, types = [], groups = [], positions = [], position_range = [], enabled = None):

        filtered_rulers = self.rulers_list.copy()

        if (enabled != None):
            filtered_rulers = [
                ruler for ruler in filtered_rulers if ruler['enabled'] == enabled
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
        return Rulers(filtered_rulers, staff_grid = self.staff_grid, root_self = self.root_self, FROM_RULERS = True)
    
    def print(self):
        if len(self.rulers_list) > 0:
            for ruler in self.rulers_list:
                print(ruler)
        else:
            print("[EMPTY]")
        return self

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

        return Rulers(unique_rulers_list, staff_grid = self.staff_grid, root_self = self.root_self, FROM_RULERS = True)
    
    def reverse(self):
        straight_rulers_list = self.rulers_list
        reversed_rulers_list = [None] * self.len()
        for i in range(self.len()):
            reversed_rulers_list[i] = straight_rulers_list[self.len() - 1 - i]

        return Rulers(reversed_rulers_list, staff_grid = self.staff_grid, root_self = self.root_self, FROM_RULERS = True)
    
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

        sorted_rulers = Rulers(sorted_rulers_list, staff_grid = self.staff_grid, root_self = self.root_self, FROM_RULERS = True)

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

            subject_rulers = self.filter(types=[type_group['type']], groups=[type_group['group']]).list()
                                
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

        return Rulers(merged_rulers, staff_grid = self.staff_grid, root_self = self.root_self, FROM_RULERS = True)
    
    def single(self, index=0):
        if (self.len() > index):
            ruler_list = [ self.self.rulers_list[index] ]
            return Rulers(ruler_list, staff_grid = self.staff_grid, root_self = self.root_self, FROM_RULERS = True)
        return self

    def exclude(self, index=0):
        if (self.len() > index):
            excluding_rulers = self.single(self, index)
            return self - excluding_rulers
        return self

    def expand(self):
        return self
    
    def distribute(self):
        return self
    
    def slide(self):
        return self
    
    def flip(self):
        return self
    
    def rotate(self):
        return self
    


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

    # self is the list to work with!

    # def cleanRulers(self):
    #     self = [ ruler for ruler in self if ruler != None ]

# Python has magic methods to define overloaded behaviour of operators. The comparison operators (<, <=, >, >=, == and !=)
# can be overloaded by providing definition to __lt__, __le__, __gt__, __ge__, __eq__ and __ne__ magic methods.
# Following program overloads < and > operators to compare objects of distance class.


   ### OPERATIONS ###

    # def operationSwapRulers(self, type, first_ruler, second_ruler):
    #     rulers = first_ruler + second_ruler
    #     if (len(rulers) == 2):
    #         position = rulers[0]['position']
    #         sequence = rulers[0]['sequence']
    #         rulers[0]['position'] = rulers[1]['position']
    #         rulers[0]['sequence'] = rulers[1]['sequence']
    #         rulers[1]['position'] = position
    #         rulers[1]['sequence'] = sequence
    #     return self

    # def operationSlideRulers(self, increments = [0, 0], modulus_selector = [1, 1], modulus_reference = [0, 0], type = None, group = None, sequeces_range = [], enabled = False, INSIDE_RANGE = False):

    #     rulers = self.filterRulers(types = [type], groups = [group], sequeces_range = sequeces_range, enabled = enabled, ON_STAFF = True, INSIDE_RANGE = INSIDE_RANGE)

    #     lower_slack = self.steps*self.frames_step - 1
    #     upper_slack = lower_slack

    #     modulus_position = modulus_reference[0]
    #     for rule in rulers:
    #         if (modulus_position % modulus_selector[0] == 0):
    #             lower_slack = min(lower_slack, rule['sequence'])
    #             upper_slack = min(upper_slack, self.steps*self.frames_step - 1 - rule['sequence'])
    #         modulus_position += 1

    #     increments[0] = max(-lower_slack, increments[0]) # Horizontal sliding can't slide out of the grid
    #     increments[0] = min(upper_slack, increments[0]) # Horizontal sliding can't slide out of the grid

    #     modulus_position = modulus_reference[0]
    #     for rule in rulers:
    #         if (modulus_position % modulus_selector[0] == 0):
    #             rule['sequence'] += increments[0]
    #             if (rule['position'] != None):
    #                 rule['position'] = self.timeGrid[rule['sequence']]['position']
    #         modulus_position += 1

    #     modulus_position = modulus_reference[1]
    #     for rule in rulers:
    #         if (modulus_position % modulus_selector[1] == 0):
    #             rule['offset'] += increments[1]
    #         modulus_position += 1
            
    #     return self

    # def operationRotateRulers(self, increments = [0, 0], type = None, group = None, sequeces_range = [], enabled = False, INSIDE_RANGE = False):

    #     rulers = self.filterRulers(types = [type], groups = [group], sequeces_range = sequeces_range, enabled = enabled, ON_STAFF = True, INSIDE_RANGE = INSIDE_RANGE)

    #     staff_sequences = []
    #     if (increments[0] != 0):
    #         for rule in rulers:
    #             staff_sequences.append(rule['sequence'])
        
    #     total_sequences = len(staff_sequences)
    #     for rule in rulers:
    #         if (increments[0] != 0):
    #             rule['sequence'] = staff_sequences[increments[0] % total_sequences]
    #             if (rule['position'] != None):
    #                 rule['position'] = self.timeGrid[rule['sequence']]['position']
    #         if (increments[1] != 0):
    #             rule_lines = []
    #             for line in rule['lines']:
    #                 rule_lines.append(line)
    #             total_lines = len(rule_lines)
    #             for line in rule['lines']:
    #                 line = rule_lines[increments[1] % total_lines]

    #     return self

    # def operationFlipRulers(self, mirrors = [False, False], type = None, group = None, sequeces_range = [], enabled = False, INSIDE_RANGE = False):

    #     rulers = self.filterRulers(types = [type], groups = [group], sequeces_range = sequeces_range, enabled = enabled, ON_STAFF = True, INSIDE_RANGE = INSIDE_RANGE)

    #     staff_sequences = []
    #     if (mirrors[0]):
    #         for rule in rulers:
    #             staff_sequences.append(rule['sequence'])
        
    #     upper_sequence = len(staff_sequences) - 1
    #     for rule in rulers:
    #         if (mirrors[0]):
    #             rule['sequence'] = staff_sequences[upper_sequence]
    #             if (rule['position'] != None):
    #                 rule['position'] = self.timeGrid[rule['sequence']]['position']
    #         upper_sequence -= 1
    #         if (mirrors[1]):
    #             rule_lines = []
    #             for line in rule['lines']:
    #                 rule_lines.append(line)
    #             upper_line = len(rule_lines) - 1
    #             for line in rule['lines']:
    #                 line = rule_lines[upper_line]
    #                 upper_line -= 1

    #     return self