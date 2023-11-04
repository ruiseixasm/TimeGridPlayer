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
        if self.staff_grid != None:
            remove_staff_rulers = (self.root_self - self).filter(enabled=True).unique()
            self.staff_grid.remove(remove_staff_rulers.list())
        
        self.root_self = self
        return self
    
    def resetStaff(self):
        if self.staff_grid != None:
            self.staff_grid.clear()
            for staff_ruler in self.root_self.list():
                staff_ruler['on_staff'] = True
            enabled_rulers_list = self.root_self.filter(enabled=True).unique().list()
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
        
        if ruler != None and len(ruler) > 0 and 'type' in ruler and ruler['type'] in self.ruler_types:

            structured_ruler = {
                'id': None,
                'type': ruler['type'],
                'group': "main",
                'position': [0, 0],
                'lines': [None],
                'offset': 0,
                'enabled': True,
                'on_staff': self.staff_grid != None
            }

            for ruler_id in range(self.root_self.len() + 1): # get available ruler id
                existent_rulers = [
                    ruler for ruler in self.root_self.rulers_list if ruler['id'] == ruler_id
                ]
                if len(existent_rulers) == 0: # id not found thus available
                    structured_ruler['id'] = ruler_id
                    break

            if 'group' in ruler and ruler['group'] != None:
                structured_ruler['group'] = ruler['group']
            if 'position' in ruler and ruler['position'] != None and len(ruler['position']) == 2:
                structured_ruler['position'] = ruler['position']
            if 'lines' in ruler and ruler['lines'] != None and len(ruler['lines']) > 0:
                structured_ruler['lines'] = ruler['lines']
            if ('offset' in ruler and ruler['offset'] != None):
                structured_ruler['offset'] = ruler['offset']
            if ('enabled' in ruler and ruler['enabled'] != None):
                structured_ruler['enabled'] = ruler['enabled']

            self.rulers_list.append(structured_ruler)
            if (self != self.root_self):
                self.root_self.rulers_list.append(structured_ruler)
            if structured_ruler['on_staff'] and structured_ruler['enabled'] == True:
                self.staff_grid.add([structured_ruler])

        return self
    
    def remove(self):
        self.root_self.rulers_list = [ ruler for ruler in self.root_self.rulers_list if ruler not in self.rulers_list ]
        if self.staff_grid != None:
            enabled_rulers_list = self.filter(enabled=True).unique().list()
            self.staff_grid.remove(enabled_rulers_list)
        self.rulers_list = []
        return self
    
    def enable(self):
        disabled_rulers = self.filter(enabled=False).unique()
        for disabled_ruler in disabled_rulers.list():
            disabled_ruler['enabled'] = True
        if self.staff_grid != None:
            disabled_staff_rulers = disabled_rulers.filter(on_staff=True)
            self.staff_grid.add(disabled_staff_rulers.list())
        return self
    
    def disable(self):
        enabled_rulers = self.filter(enabled=True).unique()
        for enabled_ruler in enabled_rulers.list():
            enabled_ruler['enabled'] = False
        if self.staff_grid != None:
            enabled_staff_rulers = enabled_rulers.filter(on_staff=True)
            self.staff_grid.remove(enabled_staff_rulers.list())
        return self
    
    def filter(self, ids = [], types = [], groups = [], positions = [], position_range = [], enabled = None, on_staff = None):

        filtered_rulers = self.rulers_list.copy()

        if (enabled != None):
            filtered_rulers = [
                ruler for ruler in filtered_rulers if ruler['enabled'] == enabled
            ]
        if (on_staff != None):
            filtered_rulers = [
                ruler for ruler in filtered_rulers if ruler['on_staff'] == on_staff
            ]
        if (len(ids) > 0 and ids != [None]):
            filtered_rulers = [
                ruler for ruler in filtered_rulers if ruler['id'] in ids
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
            filtered_rulers = [
                ruler for ruler in filtered_rulers if ruler['position'] in positions
            ]
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
    
    def sort(self, key='position', reverse = False):

        sorted_rulers_list = self.rulers_list.copy()

        if (len(sorted_rulers_list) > 1):
            for i in range(0, len(sorted_rulers_list) - 1):
                sorted_list = True
                for j in range(1, len(sorted_rulers_list) - i):
                    if (key == 'position' and self.position_gt(sorted_rulers_list[j - 1]['position'], sorted_rulers_list[j]['position']) \
                        or key == 'id' and sorted_rulers_list[j - 1]['id'] > sorted_rulers_list[j]['id']):

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
            if ruler_type_group not in type_groups:
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

            merged_ruler = {
                'id': subject_rulers[0]['id'],
                'type': type_group['type'],
                'group': type_group['group'],
                'position': subject_rulers[0]['position'],
                'lines': [None] * (tail_offset - head_offset + 1), # list
                'offset': head_offset,
                'enabled': subject_rulers[0]['enabled'],
                'on_staff': False
            }

            for subject_ruler in subject_rulers:
                for i in range(len(subject_ruler['lines'])):
                    merged_line = i + subject_ruler['offset'] - merged_ruler['offset']
                    if (merged_ruler['lines'][merged_line] == None):
                        merged_ruler['lines'][merged_line] = subject_ruler['lines'][i]

            merged_rulers.append(merged_ruler)

        return Rulers(merged_rulers, staff_grid = self.staff_grid, root_self = self.root_self, FROM_RULERS = True)
    
    def single(self, index=0):
        if (self.len() > index):
            ruler_list = [ self.rulers_list[index] ]
            return Rulers(ruler_list, staff_grid = self.staff_grid, root_self = self.root_self, FROM_RULERS = True)
        return self

    def exclude(self, index=0):
        if (self.len() > index):
            excluding_rulers = self.single(self, index)
            return self - excluding_rulers
        return self

    def lines(self, index=0):
        single_ruler = self.single(index)
        if single_ruler.len() > 0:
            return self.single(index).list()[0]['lines']
        else:
            return []

    def duplicate(self):
        """Duplicates the listed rulers"""
        for ruler in self.rulers_list[:]:
            self.add(ruler.copy())
        return self
    
    def copy(self):
        """Shows just the copied rulers"""
        rulers_list_copy = []
        for ruler in self.rulers_list[:]:
            new_ruler = ruler.copy()
            rulers_list_copy.append(new_ruler)
            self.add(new_ruler)
        return Rulers(rulers_list_copy, staff_grid = self.staff_grid, root_self = self.root_self, FROM_RULERS = True)
    
    def move(self, position=[None, None]):
        if position[0] != None and position[1] != None:
            enabled_rulers = self.filter(enabled=True)
            enabled_rulers.disable()
            for ruler in self.rulers_list:
                ruler['position'] = position
            enabled_rulers.enable()
        return self
    
    def slide(self, distance=[None, None]):
        if self.staff_grid != None and distance[0] != None and distance[1] != None \
            and (distance[0] >= 0 and distance[1] >= 0 or distance[0] <= 0 and distance[1] <= 0):

            distance_sequences = self.staff_grid.sequence(distance)
            if distance_sequences > 0:
                last_sequence = self.staff_grid.sequences() - 1
                for ruler in self.rulers_list:
                    ruler_position_sequence = self.staff_grid.sequence(ruler['position'])
                    distance_sequences = min(distance_sequences, last_sequence - ruler_position_sequence)
            elif distance_sequences < 0:
                for ruler in self.rulers_list:
                    ruler_position_sequence = -self.staff_grid.sequence(ruler['position'])
                    distance_sequences = max(distance_sequences, ruler_position_sequence)
            else:
                return self
            
            enabled_rulers = self.filter(enabled=True)
            enabled_rulers.disable()

            for ruler in self.rulers_list:
                new_position_sequence = self.staff_grid.sequence(ruler['position']) + distance_sequences # always positive
                ruler['position'] = self.staff_grid.position(new_position_sequence)

            enabled_rulers.enable()

        return self
    
    def expand(self, distance=[None, None]):
        if self.staff_grid != None and distance[0] != None and distance[1] != None:
            ...
        return self
    
    def distribute(self, range=[[None, None], [None, None]]):
        if self.staff_grid != None and range[0][0] != None and range[0][1] != None and range[1][0] != None and range[1][1] != None:
            ...
        return self
    
    def rotate(self, increment=1):
        return self
    
    def flip(self):
        return self
    
    def odd(self):
        odd_rulers_list = self.rulers_list[::2]
        return Rulers(odd_rulers_list, staff_grid = self.staff_grid, root_self = self.root_self, FROM_RULERS = True)
    
    def even(self):
        even_rulers_list = self.rulers_list[1::2]
        return Rulers(even_rulers_list, staff_grid = self.staff_grid, root_self = self.root_self, FROM_RULERS = True)
    
    def head(self, elements=1):
        head_rulers_list = self.rulers_list[:elements]
        return Rulers(head_rulers_list, staff_grid = self.staff_grid, root_self = self.root_self, FROM_RULERS = True)
    
    def tail(self, elements=1):
        tail_rulers_list = self.rulers_list[-elements:]
        return Rulers(tail_rulers_list, staff_grid = self.staff_grid, root_self = self.root_self, FROM_RULERS = True)

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