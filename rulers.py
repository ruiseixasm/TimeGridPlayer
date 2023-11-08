'''TimeGridPlayer - Time Grid Player triggers Actions on a Staff
Original Copyright (c) 2023 Rui Seixas Monteiro. All right reserved.
This library is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 2.1 of the License, or (at your option) any later version.
This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
Lesser General Public License for more details.'''

import staff

class Rulers():

    def __init__(self, rulers_list = None, staff = None, root_self = None, FROM_RULERS = False):

        self._staff = staff

        self.root_self = self
        if root_self != None:
            self.root_self = root_self # type Rulers

        self._rulers_list = []
        if (rulers_list != None):
            if (FROM_RULERS):
                self._rulers_list = rulers_list
            else:
                for ruler in rulers_list:
                    self.add(ruler)
 
    # + Operator Overloading in Python
    def __add__(self, other):
        '''Works as Union'''
        self_rulers_list = self.list()
        other_rulers_list = other.list()

        return Rulers(self_rulers_list + other_rulers_list, staff = self._staff, root_self = self.root_self, FROM_RULERS = True)
    
    def __sub__(self, other):
        '''Works as exclusion'''
        self_rulers_list = self.list()
        other_rulers_list = other.list()

        exclusion_list = [ ruler for ruler in self_rulers_list if ruler not in other_rulers_list ]

        return Rulers(exclusion_list, staff = self._staff, root_self = self.root_self, FROM_RULERS = True)
    
    def __mul__(self, other):
        '''Works as intersection'''
        self_rulers_list = self.list()
        other_rulers_list = other.list()
        
        intersection_list = [ ruler for ruler in self_rulers_list if ruler in other_rulers_list ]

        return Rulers(intersection_list, staff = self._staff, root_self = self.root_self, FROM_RULERS = True)
    
    def __div__(self, other):
        '''Works as divergence'''
        union_rulers = self.__add__(other)
        intersection_rulers = self.__mul__(other)

        return union_rulers - intersection_rulers
    
    def add(self, ruler): # Must be able to remove removed rulers from the main list
        
        if ruler != None and len(ruler) > 0 and 'type' in ruler and ruler['type'] in ['arguments', 'actions']:

            structured_ruler = {
                'id': None,
                'type': ruler['type'],
                'group': "main",
                'position': [0, 0],
                'lines': [],
                'offset': 0,
                'enabled': True,
                'on_staff': self._staff != None
            }

            for ruler_id in range(self.root_self.len() + 1): # get available ruler id
                existent_rulers = [
                    ruler for ruler in self.root_self._rulers_list if ruler['id'] == ruler_id
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

            self._rulers_list.append(structured_ruler)
            if (self != self.root_self):
                self.root_self._rulers_list.append(structured_ruler)
            if structured_ruler['on_staff']:
                self._staff.add([structured_ruler])

        return self
    
    def add_lines(self, id=None, line=None, amount=1):
        target_rulers = self
        if id != None:
            target_rulers = self.filter(ids=[id])
        for ruler in target_rulers:
            new_lines = [None] * (len(ruler['lines']) + amount)
            if line != None:
                line = min(len(ruler['lines']), line)
            else:
                line = len(ruler['lines'])
            for line_index in range(len(ruler['lines'])):
                if line_index < line:
                    new_lines[line_index] = ruler['lines'][line_index]
                else:
                    new_lines[line_index + amount] = ruler['lines'][line_index]

            ruler['lines'] = new_lines
            
        return self
           
    def copy(self):
        """Shows just the copied rulers"""
        source_rulers = self + self.empty()
        duplicated_rulers = self.duplicate()
        copied_rulers = duplicated_rulers - source_rulers
        return copied_rulers
    
    def empty(self):
        empty_rulers_list = []
        return Rulers(empty_rulers_list, staff = self._staff, root_self = self.root_self, FROM_RULERS = True)
    
    def empty_lines(self):
        for ruler in self._rulers_list:
            ruler['lines'] = []
        return self
  
    def enable(self):
        enabled_rulers_list = self.filter(enabled=False).unique().list()
        for disabled_ruler in enabled_rulers_list:
            disabled_ruler['enabled'] = True
        if self._staff != None:
            self._staff.enable(enabled_rulers_list)
        return self
    
    def enabled(self):
        return self.filter(enabled=True)
    
    def erase_lines(self):
        for rulers in self._rulers_list:
            for index in len(rulers['lines']):
                rulers['lines'][index] = None

        return self
    
    def disable(self):
        disabled_rulers_list = self.filter(enabled=True).unique().list()
        if self._staff != None:
            self._staff.disable(disabled_rulers_list)
        for enabled_ruler in disabled_rulers_list:
            enabled_ruler['enabled'] = False
        return self
    
    def disabled(self):
        return self.filter(enabled=False)
    
    def distribute_position(self, range_steps=None, range_positions=[[None, None], [None, None]]):
        sorted_rulers = self.unique().sort()
        number_intervals = sorted_rulers.len()
        if self._staff != None and number_intervals > 1:
            if range_positions[0][0] != None and range_positions[0][1] != None and range_positions[1][0] != None and range_positions[1][1] != None:
                distance_pulses = self._staff.pulses(range_positions[1]) - self._staff.pulses(range_positions[0]) # total distance
                start_pulses = self._staff.pulses(range_positions[0])
                finish_pulses = start_pulses + round(distance_pulses * (number_intervals - 1) / number_intervals)
            elif range_steps != None:
                distance_pulses = self._staff.pulses([0, range_steps]) # total distance
                start_pulses = self._staff.pulses(sorted_rulers.list()[0]['position'])
                finish_pulses = start_pulses + round(distance_pulses * (number_intervals - 1) / number_intervals)
            else:
                finish_pulses = \
                    self._staff.pulses(sorted_rulers.list()[number_intervals - 1]['position'])\
                    - self._staff.pulses(sorted_rulers.list()[0]['position']) # total distance
                distance_pulses = finish_pulses * number_intervals / (number_intervals - 1)
                start_pulses = self._staff.pulses(sorted_rulers.list()[0]['position'])

            if not finish_pulses < 0 and finish_pulses < self._staff.len():
                sorted_rulers.float()
                for index in range(number_intervals):
                    new_position = self._staff.position(pulses=start_pulses + round(index * distance_pulses / number_intervals))
                    sorted_rulers.list()[index]['position'] = new_position
                sorted_rulers.drop()

        return sorted_rulers
    
    def drop(self):
        if self._staff != None:
            self._staff.add(self.unique().list())
        return self

    def duplicate(self):
        """Duplicates the listed rulers"""
        for ruler in self._rulers_list[:]:
            self.add(ruler.copy())
        return self
    
    def even(self):
        even_rulers_list = self._rulers_list[::2]
        return Rulers(even_rulers_list, staff = self._staff, root_self = self.root_self, FROM_RULERS = True)
    
    def exclude(self, index=0):
        if (self.len() > index):
            excluding_rulers = self.single(self, index)
            return self - excluding_rulers
        return self

    def expand_lines(self, spread=1):
        for ruler in self._rulers_list:
            old_total_lines = len(ruler['lines'])
            if spread > 0:
                new_total_lines = (old_total_lines * (spread + 1))
                new_lines = [None] * new_total_lines
                for line in range(old_total_lines):
                    new_lines[line * (spread + 1)] = ruler['lines'][line]
                ruler['lines'] = new_lines
            else:
                new_total_lines = int(old_total_lines / (-spread + 1))
                new_lines = [None] * new_total_lines
                for line in range(new_total_lines):
                    new_lines[line] = ruler['lines'][line * (-spread + 1)]

        return self
    
    def expand_position(self, spread_steps=4):
        first_position = self._rulers_list[0]['position']
        self.float()
        for ruler_index in range(1, self.len()):
            self._rulers_list[ruler_index]['position'] = self._staff.addPositions(first_position, [0, ruler_index * spread_steps])
        self.drop()
        return self
    
    def float(self):
        if self._staff != None:
            self._staff.remove(self.unique().list())
        return self
    
    def filter(self, ids = [], types = [], groups = [], positions = [], position_range = [], enabled = None, on_staff = None):

        filtered_rulers = self._rulers_list.copy()

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
                        if not (position_lt(ruler['position'], position_range[0]) and position_lt(ruler['position'], position_range[1]))
            ]
        return Rulers(filtered_rulers, staff = self._staff, root_self = self.root_self, FROM_RULERS = True)
    
    def head(self, elements=1):
        head_rulers_list = self._rulers_list[:elements]
        return Rulers(head_rulers_list, staff = self._staff, root_self = self.root_self, FROM_RULERS = True)
    
    def insert_lines(self, id=None, line=None, lines=[None]):
        target_rulers = self
        if id != None:
            target_rulers = self.filter(ids=[id])
        for ruler in target_rulers:
            new_lines = [None] * (len(ruler['lines']) + len(lines))
            if line != None:
                line = min(len(ruler['lines']), line)
            else:
                line = len(ruler['lines'])
            for line_index in range(len(new_lines)):
                if line_index < line:
                    new_lines[line_index] = ruler['lines'][line_index]
                elif line_index < line + len(lines):
                    new_lines[line_index] = lines[line_index - (line + len(lines))]
                else:
                    new_lines[line_index] = ruler['lines'][line_index - len(lines)]

            ruler['lines'] = new_lines

        return self
           
    def list(self):
        return self._rulers_list
    
    def list_lines(self):
        all_lines = []
        for ruler in self._rulers_list:
            all_lines.append(ruler['lines'])
        return all_lines
    
    def len(self):
        return len(self._rulers_list)
    
    def len_lines(self):
        total_lines = 0
        for ruler in self._rulers_list:
            total_lines += len(ruler['lines'])
        return total_lines
    
    def lines(self, index=0):
        single_ruler = self.single(index)
        if single_ruler.len() > 0:
            return self.single(index).list()[0]['lines']
        else:
            return []

    def merge(self):

        type_groups = [] # merge agregates rulers by type and gorup

        for ruler in self._rulers_list:
            ruler_type_group = {'type': ruler['type'], 'group': ruler['group']}
            if ruler_type_group not in type_groups:
                type_groups.append(ruler_type_group)

        merged_rulers = []

        for type_group in type_groups:

            subject_rulers_list = self.filter(types=[type_group['type']], groups=[type_group['group']]).list()
                                
            head_offset = None
            tail_offset = None
            for ruler in subject_rulers_list:
                if head_offset == None or ruler['offset'] < head_offset:
                    head_offset = ruler['offset']
                if tail_offset == None or (len(ruler['lines']) + ruler['offset'] > tail_offset):
                    tail_offset = len(ruler['lines']) - 1 + ruler['offset']

            merged_ruler = {
                'id': subject_rulers_list[0]['id'],
                'type': type_group['type'],
                'group': type_group['group'],
                'position': subject_rulers_list[0]['position'],
                'lines': [None] * (tail_offset - head_offset + 1), # list
                'offset': head_offset,
                'enabled': subject_rulers_list[0]['enabled'],
                'on_staff': False
            }

            for subject_ruler in subject_rulers_list:
                for i in range(len(subject_ruler['lines'])):
                    merged_line = i + subject_ruler['offset'] - merged_ruler['offset']
                    if (merged_ruler['lines'][merged_line] == None):
                        merged_ruler['lines'][merged_line] = subject_ruler['lines'][i]

            merged_rulers.append(merged_ruler)

        return Rulers(merged_rulers, staff = self._staff, root_self = self.root_self, FROM_RULERS = True)
    
    def move_lines(self, increments=1):
        for ruler in self._rulers_list:
            ruler['offset'] += increments

        return self
    
    def move_position(self, position=[None, None]):
        if position[0] != None and position[1] != None:
            sorted_rulers = self.sort(key=position)
            sorted_rulers_size = sorted_rulers.len()
            sorted_rulers_list = sorted_rulers.list()
            first_ruler_position = sorted_rulers_list[0]['position']
            move_steps = self._staff.steps(position) - self._staff.steps(first_ruler_position)
            if move_steps > 0:
                last_staff_step = self._staff.len_steps() - 1
                last_ruler_position = sorted_rulers_list[sorted_rulers_size - 1]['position']
                last_ruler_step = self._staff.steps(last_ruler_position)
                slack_steps = last_staff_step - last_ruler_step
                move_steps = min(slack_steps, move_steps)
            else:
                first_staff_step = 0
                first_ruler_step = self._staff.steps(first_ruler_position)
                slack_steps = first_ruler_step - first_staff_step
                move_steps = -min(slack_steps, -move_steps)

            self.float()
            for ruler in self._rulers_list:
                ruler['position'] = self._staff.addPositions(ruler['position'], [0, move_steps])
            self.drop()

        return self
    
    def odd(self):
        odd_rulers_list = self._rulers_list[1::2]
        return Rulers(odd_rulers_list, staff = self._staff, root_self = self.root_self, FROM_RULERS = True)
    
    def print(self):
        
        if len(self._rulers_list) > 0:
            string_top_length = {'sequence': 0, 'id': 0, 'type': 0, 'group': 0, 'position': 0, 'lines': 0, 'offset': 0, 'enabled': 0, 'on_staff': 0}
            full_string_top_length = 0
            sequence_index = 0
            for ruler in self._rulers_list: # get maximum sizes
                full_string_length = 0
                
                for key, value in string_top_length.items():
                    if key == 'sequence':
                        key_value_length = len(f"{sequence_index}:" + " { ")
                        sequence_index += 1
                    else:
                        ruler_value = ""
                        if key == 'position':
                            ruler_value = [ruler[key][0], round(ruler[key][1], 3)]
                            if ruler_value[1] % 1 == 0:
                                ruler_value = [ruler_value[0], int(ruler_value[1])]
                        if key == 'lines':
                            ruler_value = len(ruler[key])
                        else:
                            ruler_value = ruler[key]

                        key_value_length = len(f"{key}: {ruler_value} ")

                        if key != 'on_staff':
                            key_value_length += len("   ")

                    full_string_length += key_value_length
                    string_top_length[key] = max(string_top_length[key], key_value_length)

                full_string_top_length = max(full_string_top_length, full_string_length)

            print("'" * (full_string_top_length + 1))
            sequence_index = 0
            for ruler in self._rulers_list:

                rule_str = ""
                for key, value in string_top_length.items():
                    if key == 'sequence':
                        key_value_str = f"{sequence_index}:" + " { "
                        sequence_index += 1
                    else:
                        ruler_value = ""
                        if key == 'position':
                            ruler_value = [ruler[key][0], round(ruler[key][1], 3)]
                            if ruler_value[1] % 1 == 0:
                                ruler_value = [ruler_value[0], int(ruler_value[1])]
                        if key == 'lines':
                            ruler_value = len(ruler[key])
                        else:
                            ruler_value = ruler[key]

                        key_value_str = f"{key}: {ruler_value} "

                        if key != 'on_staff':
                            key_value_str += "   "

                    key_value_length = len(key_value_str)
                    rule_str += key_value_str + (" " * (string_top_length[key] - key_value_length))
                rule_str += "}"
                print(rule_str)
            print("'" * (full_string_top_length + 1))

        else:
            print("'" * 7)
            print("[EMPTY]")
            print("'" * 7)
        return self

    def print_lines(self):
        
        rulers_size = self.len()
        if rulers_size > 0:
            rulers_list = self.list()
            head_offset = None
            tail_offset = None
            for ruler in rulers_list:
                if head_offset == None or ruler['offset'] < head_offset:
                    head_offset = ruler['offset']
                if tail_offset == None or (len(ruler['lines']) + ruler['offset'] > tail_offset):
                    tail_offset = len(ruler['lines']) - 1 + ruler['offset']
            total_lines = tail_offset - head_offset + 1
            
            string_top_length = {'sequence': 0, 'id': 0, 'lines': [0] * total_lines}

            # TOTALS +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

            full_string_length = 0
            for line_index in range(head_offset, head_offset + len(string_top_length['lines'])):

                key_value_str = f"{line_index}"

                # if line_index != head_offset + len(string_top_length['lines']) - 1:
                #     key_value_str += "  "

                key_value_length = len(key_value_str)

                full_string_length += key_value_length
                string_top_length['lines'][line_index - head_offset] = max(string_top_length['lines'][line_index - head_offset], key_value_length)

            sequence_index = 0
            for ruler in self._rulers_list: # get maximum sizes

                full_string_length = 0
                for key, value in string_top_length.items():
                    if key == 'sequence':
                        key_value_length = len(f"{sequence_index}:" + " { ")
                        sequence_index += 1

                        full_string_length += key_value_length
                        string_top_length[key] = max(string_top_length[key], key_value_length)
                    else:
                        lines_value = ""
                        if key == 'lines':
                            for line_index in range(head_offset, head_offset + len(string_top_length['lines'])):
                                if not (line_index < ruler['offset'] or line_index > ruler['offset'] + len(ruler['lines']) - 1): # if not out of scope

                                    key_value_str = f"{ruler['lines'][line_index - ruler['offset']]}" if ruler['lines'][line_index - ruler['offset']] != None else "."

                                    # if line_index != ruler['offset'] + len(ruler['lines']) - 1:
                                    #     key_value_str += "  "

                                    key_value_length = len(key_value_str)

                                    full_string_length += key_value_length
                                    string_top_length['lines'][line_index - head_offset] = max(string_top_length['lines'][line_index - head_offset], key_value_length)

                        else: # id
                            lines_value = ruler[key]

                            key_value_length = len(f"{lines_value}    ")

                            full_string_length += key_value_length
                            string_top_length[key] = max(string_top_length[key], key_value_length)

            # OUTPUT PRINT -----------------------------------------------------------------------------------------------------------------------

            lines_str_header = " " * (string_top_length['sequence'] - 3) + "lines:" + " " * (string_top_length['id'] + 1)
            lines_str_tail = ""

            for line_index in range(head_offset, head_offset + len(string_top_length['lines'])):

                key_value_str = f"{line_index}"

                key_value_length = len(key_value_str)
                key_value_str += (" " * (string_top_length['lines'][line_index - head_offset] - key_value_length))

                if line_index != head_offset + len(string_top_length['lines']) - 1:
                    key_value_str += "  "

                # TOTALS AGNOSTIC FOR "[" and "]"
                if True:
                    key_value_str = " " + key_value_str + " "
                else:
                    if line_index == head_offset == head_offset + len(string_top_length['lines']) - 1:
                        key_value_str = "[" + key_value_str + "]"
                    elif line_index == head_offset:
                        key_value_str = "[" + key_value_str + " "
                    elif line_index == head_offset + len(string_top_length['lines']) - 1:
                        key_value_str = " " + key_value_str + "]"
                    else:
                        key_value_str = " " + key_value_str + " "

                lines_str_tail += key_value_str

            full_string_top_length = 0
            for line_length in string_top_length['lines']:
                full_string_top_length += line_length
                
            print("-" * (full_string_top_length + 2) + "----" * (total_lines + 3))

            print(lines_str_header + lines_str_tail)

            print("-" * (full_string_top_length + 2) + "----" * (total_lines + 3))

            sequence_index = 0
            for ruler in self._rulers_list:

                lines_str = ""
                for key, value in string_top_length.items():
                    if key == 'sequence':
                        key_value_str = f"{sequence_index}:" + " { "
                        sequence_index += 1

                        key_value_length = len(key_value_str)
                        lines_str += key_value_str + (" " * (string_top_length[key] - key_value_length))
                    else:
                        if key == 'lines':
                            for line_index in range(head_offset, head_offset + len(string_top_length[key])):
                                if not (line_index < ruler['offset'] or line_index > ruler['offset'] + len(ruler['lines']) - 1): # if not out of scope

                                    key_value_str = f"{ruler['lines'][line_index - ruler['offset']]}" if ruler['lines'][line_index - ruler['offset']] != None else "_"

                                    key_value_length = len(key_value_str)
                                    key_value_str += (" " * (string_top_length['lines'][line_index - head_offset] - key_value_length))

                                    if line_index != ruler['offset'] + len(ruler['lines']) - 1:
                                        key_value_str += "  "

                                    # TOTALS AGNOSTIC FOR "[" and "]"
                                    if True:
                                        key_value_str = " " + key_value_str + " "
                                    else:
                                        if line_index == ruler['offset'] == ruler['offset'] + len(ruler['lines']) - 1:
                                            key_value_str = "[" + key_value_str + "]"
                                        elif line_index == ruler['offset']:
                                            key_value_str = "[" + key_value_str + " "
                                        elif line_index == ruler['offset'] + len(ruler['lines']) - 1:
                                            key_value_str = " " + key_value_str + "]"
                                        else:
                                            key_value_str = " " + key_value_str + " "

                                    lines_str += key_value_str

                                else:
                                    lines_str += " " * (string_top_length['lines'][line_index - head_offset] + 4)
                        else: # id
                            lines_value = ruler[key]
                            key_value_str = f"{key}: {lines_value}    "

                            key_value_length = len(key_value_str)
                            lines_str += key_value_str + (" " * (string_top_length[key] - key_value_length))
                lines_str += " }"

                print(lines_str)

            print("-" * (full_string_top_length + 2) + "----" * (total_lines + 3))

        else:
            print("-" * 7)
            print("[EMPTY]")
            print("-" * 7)
        return self

    def remove(self):
        self.root_self._rulers_list = [ ruler for ruler in self.root_self._rulers_list if ruler not in self._rulers_list ]
        if self._staff != None:
            unique_rulers_list = self.unique().list()
            self._staff.remove(unique_rulers_list)
        self._rulers_list = []
        return self
    
    def remove_lines(self, id=None, line=None, amount=None):
        for ruler in self._rulers_list:
            ruler['lines'] = []
        return self
    
    def reroot(self):
        if self._staff != None:
            extra_root_rulers = (self.root_self - self).unique()
            self._staff.remove(extra_root_rulers.list())
        
        self.root_self = self
        return self
    
    def resetStaff(self):
        if self._staff != None:
            self._staff.clear()
            for staff_ruler in self.root_self.list():
                staff_ruler['on_staff'] = True
            unique_rulers_list = self.root_self.unique().list()
            self._staff.add(unique_rulers_list)

        return self
    
    def reverse(self):
        rulers_list_size = self.len()
        for i in range(int(rulers_list_size/2)):
            temp_ruler = self._rulers_list[i]
            self._rulers_list[i] = self._rulers_list[rulers_list_size - 1 - i]
            self._rulers_list[rulers_list_size - 1 - i] = temp_ruler

        return self
    
    def reverse_lines(self):
        for rulers in self._rulers_list:
            lines_size = len(rulers['lines'])
            for index in range(int(lines_size/2)):
                temp_line = rulers['lines'][index]
                rulers['lines'][index] = rulers['lines'][lines_size - 1 - index]
                rulers['lines'][lines_size - 1 - index] = temp_line

        return self
         
    def reverse_position(self):
        self = self.unique().reverse()
        rulers_list_size = self.len()
        self.float()
        for index in range(int(rulers_list_size/2)):
            temp_position = self._rulers_list[index]['position']
            self._rulers_list[index]['position'] = self._rulers_list[rulers_list_size - 1 - index]['position']
            self._rulers_list[rulers_list_size - 1 - index]['position'] = temp_position
        self.drop()

        return self
    
    def root(self):
        return self.root_self
              
    def rotate(self, increments=1):
        rulers_size = self.len()
        original_rulers_list = self._rulers_list[:]
        for ruler_index in range(rulers_size):
            rotated_index = (ruler_index - increments) % rulers_size
            self._rulers_list[ruler_index] = original_rulers_list[rotated_index]

        return self
    
    def rotate_lines(self, increments=1):
        for rulers in self._rulers_list:
            lines_size = len(rulers['lines'])
            original_lines = rulers['lines'][:]
            for index in range(lines_size):
                rotated_index = (index - increments) % lines_size
                rulers['lines'][index] = original_lines[rotated_index]

        return self
    
    def rotate_position(self, increments=1):
        original_positions = []
        rulers_size = self.len()
        for original_ruler in self._rulers_list:
            original_positions.append(original_ruler['position'].copy())

        self.float()
        for ruler_index in range(rulers_size):
            rotated_index = (ruler_index + increments) % rulers_size
            self._rulers_list[ruler_index]['position'] = original_positions[rotated_index]
        self.drop()

        return self.rotate(increments)
    
    def set_lines(self, lines):
        for ruler in self._rulers_list:
            ruler['lines'] = lines

        return self

    def set_position(self, position=[None, None]):
        if position[0] != None and position[1] != None:
            self.float()
            for ruler in self._rulers_list:
                ruler['position'] = position
            self.drop()

        return self
    
    def single(self, index=0):
        if (self.len() > index):
            ruler_list = [ self._rulers_list[index] ]
            return Rulers(ruler_list, staff = self._staff, root_self = self.root_self, FROM_RULERS = True)
        return self

    def slide_position(self, distance_steps=4):
        if self._staff != None and distance_steps != 0:

            distance_pulses = self._staff.pulses([0, distance_steps])
            if distance_pulses > 0:
                last_position_pulses = self._staff.len() - 1
                for ruler in self._rulers_list:
                    ruler_position_pulses = self._staff.pulses(ruler['position'])
                    distance_pulses = min(distance_pulses, last_position_pulses - ruler_position_pulses)
            elif distance_pulses < 0:
                for ruler in self._rulers_list:
                    ruler_position_pulses = -self._staff.pulses(ruler['position'])
                    distance_pulses = max(distance_pulses, ruler_position_pulses)
            else:
                return self
            
            self.float()

            for ruler in self._rulers_list:
                new_position_pulses = self._staff.pulses(ruler['position']) + distance_pulses # always positive
                ruler['position'] = self._staff.position(pulses=new_position_pulses)

            self.drop()

        return self

    def sort(self, key='position', reverse = False):
        rulers_list = self.list()
        rulers_list_size = self.len()
        if (rulers_list_size > 1):
            for i in range(0, rulers_list_size - 1):
                sorted_list = True
                for j in range(1, rulers_list_size - i):
                    if (key == 'position' and position_gt(rulers_list[j - 1]['position'], rulers_list[j]['position']) \
                        or key == 'id' and rulers_list[j - 1]['id'] > rulers_list[j]['id']):

                        sorted_list = False
                        temp_ruler = rulers_list[j - 1]
                        rulers_list[j - 1] = rulers_list[j]
                        rulers_list[j] = temp_ruler
                if sorted_list:
                    break

        if reverse:
            return self.reverse()
        return self

    def sort_lines(self, function, reverse = False):
        for rulers in self._rulers_list:
            lines_size = len(rulers['lines'])
            for i in range(0, lines_size - 1):
                sorted_list = True
                for j in range(1, lines_size - i):
                    if function(rulers['lines'][j - 1], rulers['lines'][j]):

                        sorted_list = False
                        temp_line = rulers['lines'][j - 1]
                        rulers['lines'][j - 1] = rulers['lines'][j]
                        rulers['lines'][j] = temp_line
                if sorted_list:
                    break

        if reverse:
            return self.reverse_lines()
        return self

    def tail(self, elements=1):
        tail_rulers_list = self._rulers_list[-elements:]
        return Rulers(tail_rulers_list, staff = self._staff, root_self = self.root_self, FROM_RULERS = True)

    def unique(self):
        unique_rulers_list = []
        for ruler in self._rulers_list:
            if ruler not in unique_rulers_list:
                unique_rulers_list.append(ruler)

        return Rulers(unique_rulers_list, staff = self._staff, root_self = self.root_self, FROM_RULERS = True)
       
    # self is the list to work with!

    # def cleanRulers(self):
    #     self = [ ruler for ruler in self if ruler != None ]


# GLOBAL CLASS METHODS

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
