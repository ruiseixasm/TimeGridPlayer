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

import json

class Staff:

    def __init__(self, player=None):

        self._player = player
        self._rulers = self.Rulers(self)
        self._staff = []
        self._time_signature = {}
        self._total_pulses = 0
        self.string_top_lengths = {'measure': 0, 'beat': 0, 'step': 0, 'pulse': 0, 'arguments_enabled': 0, 'arguments_total': 0, 'actions_enabled': 0, 'actions_total': 0}
        self.string_top_length = 0
        self._play_range = [[], []]
        self.set_range([], [])
        self.set()

    class Rulers():

        def __init__(self, staff, rulers_list=[], root_self=None, start_id=0):

            self._staff = staff

            self._rulers_list = rulers_list
            self._root_self = root_self # type Rulers
            if root_self == None:
                self._root_self = self

            self._next_id = start_id
    
        # + Operator Overloading in Python
        def __add__(self, other):
            '''Works as Union'''
            self_rulers_list = self.list()
            other_rulers_list = other.list()

            return Staff.Rulers(self._staff, self_rulers_list + other_rulers_list, self._root_self)
        
        def __sub__(self, other):
            '''Works as exclusion'''
            self_rulers_list = self.list()
            other_rulers_list = other.list()

            exclusion_list = [ ruler for ruler in self_rulers_list if ruler not in other_rulers_list ]

            return Staff.Rulers(self._staff, exclusion_list, self._root_self)
        
        def __mul__(self, other):
            '''Works as intersection'''
            self_rulers_list = self.list()
            other_rulers_list = other.list()
            
            intersection_list = [ ruler for ruler in self_rulers_list if ruler in other_rulers_list ]

            return Staff.Rulers(self._staff, intersection_list, self._root_self)
        
        def __div__(self, other):
            '''Works as divergence'''
            union_rulers = self.__add__(other)
            intersection_rulers = self.__mul__(other)

            return union_rulers - intersection_rulers
        
        def _str_position(self, position):
            
            position_value = [position[0], round(position[1], 3)]
            if position_value[1] % 1 == 0:
                position_value = [position_value[0], int(position_value[1])]
            
            return f"{position_value}"

        def add(self, ruler): # Must be able to remove removed rulers from the main list
            
            if ruler != None and len(ruler) > 0 and 'type' in ruler and ruler['type'] in ['arguments', 'actions']:

                structured_ruler = {
                    'id': self._next_id,
                    'type': ruler['type'],
                    'group': "main",
                    'position': [0, 0],
                    'lines': [],
                    'offset': 0,
                    'enabled': True,
                    'on_staff': self._staff != None
                }
                self._next_id += 1

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
                if (self != self._root_self):
                    self._root_self._rulers_list.append(structured_ruler)
                if structured_ruler['on_staff']:
                    self._staff.add([structured_ruler])

            return self
        
        def add_lines(self, line, amount=1, id=None):
            """Add new empty lines lines"""
            target_rulers = self
            if id != None:
                target_rulers = self.filter(ids=[id])
            for ruler in target_rulers.list():

                lines_size = len(ruler['lines'])
                first_line = ruler['offset']
                last_line = first_line + lines_size - 1

                if not (line < first_line or line > last_line):
                    
                    new_lines_size = lines_size + amount
                    new_lines = [None] * new_lines_size

                    for line_index in range(lines_size):
                        if line_index < line - ruler['offset']:
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
            return Staff.Rulers(self._staff, empty_rulers_list, self._root_self)
        
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
        
        def erase_lines(self, line, amount=1, id=None):
            target_rulers = self
            if id != None:
                target_rulers = self.filter(ids=[id])
            for ruler in target_rulers.list():

                lines_size = len(ruler['lines'])
                first_line = ruler['offset']
                last_line = first_line + lines_size - 1

                if not (line < first_line or line > last_line):
                    
                    amount = min(amount, lines_size - (line - first_line))

                    for line_index in range(lines_size):
                        if not line_index < line - ruler['offset'] and line_index < line - ruler['offset'] + amount:
                            ruler['lines'][line_index] = None

            return self
        
        def even(self):
            even_rulers_list = self._rulers_list[::2]
            return Staff.Rulers(self._staff, even_rulers_list, self._root_self)
        
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
        
        def filter(self, ids = [], type = None, groups = [], positions = [], position_range = [], enabled = None, on_staff = None):

            filtered_rulers = self._rulers_list.copy()

            if (len(ids) > 0 and ids != [None]):
                filtered_rulers = [
                    ruler for ruler in filtered_rulers if ruler['id'] in ids
                ]
            if (type != None):
                if "actions".find(type) != -1:
                    type = "actions"
                else:
                    type = "arguments"
                filtered_rulers = [
                    ruler for ruler in filtered_rulers if ruler['type'] == type
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
            if (enabled != None):
                filtered_rulers = [
                    ruler for ruler in filtered_rulers if ruler['enabled'] == enabled
                ]
            if (on_staff != None):
                filtered_rulers = [
                    ruler for ruler in filtered_rulers if ruler['on_staff'] == on_staff
                ]
            return Staff.Rulers(self._staff, filtered_rulers, self._root_self)
        
        def group(self, group):
            return self.filter(groups=[group])

        def head(self, elements=1):
            head_rulers_list = self._rulers_list[:elements]
            return Staff.Rulers(self._staff, head_rulers_list, self._root_self)
        
        def insert_lines(self, line, lines=[None], id=None):
            target_rulers = self
            if id != None:
                target_rulers = self.filter(ids=[id])
            for ruler in target_rulers.list():

                lines_size = len(ruler['lines'])
                first_line = ruler['offset']
                last_line = first_line + lines_size - 1

                if not (line < first_line or line > last_line):
                    
                    new_lines_size = lines_size + len(lines)
                    new_lines = [None] * new_lines_size

                    for line_index in range(new_lines_size):
                        if line_index < line - ruler['offset']:
                            new_lines[line_index] = ruler['lines'][line_index]
                        elif line_index < line - ruler['offset'] + len(lines):
                            new_lines[line_index] = lines[line_index - line + ruler['offset']]
                        else:
                            new_lines[line_index] = ruler['lines'][line_index - len(lines)]

                    ruler['lines'] = new_lines

            return self
       
        def json_dictionnaire(self):
            return {
                    'part': "rulers",
                    'class': self.__class__.__name__,
                    'root_self': self.root().list(),
                    'next_id': self.next_id()
                }
     
        def json_load(self, file_name="rulers.json", json_object=None):

            if json_object == None:
                # Opening JSON file
                with open(file_name, 'r') as openfile:
                    # Reading from json file
                    json_object = json.load(openfile)

            for dictionnaire in json_object:
                if dictionnaire['part'] == "rulers":
                    self = Staff.Rulers(
                        staff=self._staff,
                        rulers_list=dictionnaire['root_self'],
                        root_self=dictionnaire['root_self'],
                        start_id=dictionnaire['next_id']
                    )
                    self._staff.clear()
                    self.drop()
                    break

            return self

        def json_save(self, file_name="rulers.json"):

            rulers = [ self.json_dictionnaire() ]

            # Writing to sample.json
            with open(file_name, "w") as outfile:
                json.dump(rulers, outfile)

            return self

        def list(self):
            return self._rulers_list
        
        def list_actions_names(self, enabled=None, actions_names_list=None):
            if actions_names_list == None:
                actions_names_list = []

            actions_rulers = self.filter(type="actions", enabled=enabled, on_staff=True).sort(key='id')
            for ruler in actions_rulers.list():
                for action_name in ruler['lines']:
                    if action_name != None and action_name not in actions_names_list:
                        actions_names_list.append(action_name)

            return actions_names_list

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

                subject_rulers_list = self.filter(type=type_group['type'], groups=[type_group['group']]).list()
                                    
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

            return Staff.Rulers(self._staff, merged_rulers, self._root_self)
        
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
        
        def next_id(self):
            return self._next_id

        def odd(self):
            odd_rulers_list = self._rulers_list[1::2]
            return Staff.Rulers(self._staff, odd_rulers_list, self._root_self)
        
        def player(self):
            return self._staff.player()

        def print(self):
            
            if len(self._rulers_list) > 0:
                string_top_length = {'sequence': 0, 'id': 0, 'type': 0, 'group': 0, 'position': 0, 'lines': 0, 'offset': 0, 'enabled': 0, 'on_staff': 0}
                sequence_index = 0
                for ruler in self._rulers_list: # get maximum sizes
                    
                    for key, value in string_top_length.items():
                        if key == 'sequence':
                            key_value_length = len(f"{sequence_index}")
                            sequence_index += 1
                        else:
                            ruler_value = ""
                            if key == 'position':
                                ruler_value = self._str_position(ruler['position'])
                            elif key == 'lines':
                                ruler_value = len(ruler[key])
                            else:
                                ruler_value = ruler[key]

                            key_value_length = len(f"{ruler_value}")

                        string_top_length[key] = max(string_top_length[key], key_value_length)

                full_string_top_length = 0
                for value in string_top_length.values():
                    full_string_top_length += value

                spaces_between = 4

                print("'" * (full_string_top_length + 95))
                sequence_index = 0
                for ruler in self._rulers_list:

                    ruler_str = ""
                    for key, value in string_top_length.items():
                        if key == 'sequence':
                            key_value_str = f"{sequence_index}"
                            key_value_str = (" " * (string_top_length[key] - len(key_value_str))) + key_value_str + ": { "
                            sequence_index += 1
                        else:
                            ruler_value = ""
                            if key == 'position':
                                ruler_value = self._str_position(ruler['position'])
                                key_value_str = f"{ruler_value}"
                                key_value_str = f"{key}: " + f"{ruler_value}" + (" " * (string_top_length[key] - len(key_value_str)))
                            elif key == 'lines':
                                ruler_value = len(ruler[key])
                                key_value_str = f"{ruler_value}"
                                key_value_str = f"{key}: " + (" " * (string_top_length[key] - len(key_value_str))) + f"{ruler_value}"
                            elif key == 'offset':
                                ruler_value = ruler[key]
                                key_value_str = f"{ruler_value}"
                                key_value_str = f"{key}: " + (" " * (string_top_length[key] - len(key_value_str))) + f"{ruler_value}"
                            else:
                                ruler_value = ruler[key]
                                key_value_str = f"{ruler_value}"
                                key_value_str = f"{key}: " + f"{ruler_value}" + (" " * (string_top_length[key] - len(key_value_str)))

                            if key != 'on_staff':
                                key_value_str += " " * spaces_between

                        ruler_str +=  key_value_str
                    ruler_str += " }"
                    print(ruler_str)
                print("'" * (full_string_top_length + 95))

            else:
                print("'" * 7)
                print("[EMPTY]")
                print("'" * 7)
            return self

        def print_lines(self, first_line=None, last_line=None):
            
            rulers_size = self.len()
            if rulers_size > 0:
                rulers_list = self.list()

                head_offset = first_line
                tail_offset = last_line

                if head_offset == None:
                    for ruler in rulers_list:
                        if head_offset == None or ruler['offset'] < head_offset:
                            head_offset = ruler['offset']
                if tail_offset == None:
                    for ruler in rulers_list:
                        if tail_offset == None or (len(ruler['lines']) + ruler['offset'] > tail_offset):
                            tail_offset = len(ruler['lines']) - 1 + ruler['offset']

                total_lines = tail_offset - head_offset + 1
                
                string_top_length = {'sequence': 0, 'id': 0, 'lines': [0] * total_lines}

                # TOTALS +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

                full_string_length = 0
                for line_index in range(head_offset, head_offset + len(string_top_length['lines'])):

                    key_value_length = len(f"{line_index}")

                    full_string_length += key_value_length
                    string_top_length['lines'][line_index - head_offset] = max(string_top_length['lines'][line_index - head_offset], key_value_length)

                sequence_index = 0
                for ruler in self._rulers_list: # get maximum sizes

                    for key, value in string_top_length.items():
                        if key == 'sequence':
                            key_value_length = len(f"{sequence_index}")
                            sequence_index += 1

                            string_top_length[key] = max(string_top_length[key], key_value_length)
                        else:
                            lines_value = ""
                            if key == 'lines':
                                for line_index in range(head_offset, head_offset + total_lines):
                                    if not (line_index < ruler['offset'] or line_index > ruler['offset'] + len(ruler['lines']) - 1): # if not out of scope

                                        key_value_str = f"{ruler['lines'][line_index - ruler['offset']]}" if ruler['lines'][line_index - ruler['offset']] != None else "_"

                                        key_value_str = trimString(key_value_str)

                                        key_value_length = len(key_value_str)

                                        string_top_length['lines'][line_index - head_offset] = max(string_top_length['lines'][line_index - head_offset], key_value_length)

                            else: # id
                                lines_value = ruler[key]

                                key_value_length = len(f"{lines_value}")

                                string_top_length[key] = max(string_top_length[key], key_value_length)

                
                full_string_top_length = 0
                for key, value in string_top_length.items():
                    if key == 'lines':
                        for line in value:
                            full_string_top_length += line
                    else:
                        full_string_top_length += value


                # OUTPUT PRINT -----------------------------------------------------------------------------------------------------------------------

                spaces_between = 4

                lines_str_header = " " * (string_top_length['sequence'] + 1) + "lines:" + " " * (string_top_length['id'] + 4)
                lines_str_tail = ""

                for line_index in range(head_offset, head_offset + total_lines):

                    key_value_str = f"{line_index}"

                    key_value_length = len(key_value_str)
                    key_value_str += (" " * (string_top_length['lines'][line_index - head_offset] - key_value_length))

                    if line_index != head_offset + total_lines - 1:
                        key_value_str += " " * spaces_between

                    lines_str_tail += key_value_str

                print("-" * (full_string_top_length - 3) + "----" * (total_lines + 3))

                print(lines_str_header + lines_str_tail)

                print("-" * (full_string_top_length - 3) + "----" * (total_lines + 3))

                sequence_index = 0
                for ruler in self._rulers_list:

                    lines_str = ""
                    for key, value in string_top_length.items():
                        if key == 'sequence':
                            key_value_str = f"{sequence_index}"
                            sequence_index += 1

                            key_value_length = len(key_value_str)
                            lines_str += (" " * (string_top_length[key] - key_value_length)) + key_value_str +  ": { "
                        else:
                            if key == 'lines':
                                for line_index in range(head_offset, head_offset + total_lines):
                                    if not (line_index < ruler['offset'] or line_index > ruler['offset'] + len(ruler['lines']) - 1): # if not out of scope

                                        key_value_str = f"{ruler['lines'][line_index - ruler['offset']]}" if ruler['lines'][line_index - ruler['offset']] != None else "_"

                                        key_value_str = trimString(key_value_str)

                                        key_value_length = len(key_value_str)
                                        key_value_str += (" " * (string_top_length['lines'][line_index - head_offset] - key_value_length))

                                        if line_index != head_offset + total_lines - 1:
                                            key_value_str += " " * spaces_between

                                        lines_str += key_value_str

                                    elif line_index != head_offset + total_lines - 1:
                                        lines_str += " " * (string_top_length['lines'][line_index - head_offset] + 4)
                                    else:
                                        lines_str += " " * (string_top_length['lines'][line_index - head_offset] + 0)
                            else: # id
                                lines_value = ruler[key]
                                key_value_str = f"{key}: {lines_value}   "

                                key_value_length = len(f"{lines_value}")
                                lines_str += key_value_str + (" " * (string_top_length[key] - key_value_length))
                    lines_str += " }"

                    print(lines_str)

                print("-" * (full_string_top_length - 3) + "----" * (total_lines + 3))

            else:
                print("-" * 7)
                print("[EMPTY]")
                print("-" * 7)
            return self

        def remove(self):
            self._root_self._rulers_list = [ ruler for ruler in self._root_self._rulers_list if ruler not in self._rulers_list ]
            if self._staff != None:
                unique_rulers_list = self.unique().list()
                self._staff.remove(unique_rulers_list)
            self._rulers_list = []
            return self
        
        def remove_lines(self, line, amount=1, id=None):
            target_rulers = self
            if id != None:
                target_rulers = self.filter(ids=[id])
            for ruler in target_rulers.list():

                lines_size = len(ruler['lines'])
                first_line = ruler['offset']
                last_line = first_line + lines_size - 1

                if not (line < first_line or line > last_line):
                    
                    amount = min(amount, lines_size - (line - first_line))
                    new_lines_size = lines_size - amount
                    new_lines = [None] * new_lines_size

                    for line_index in range(new_lines_size):
                        if line_index < line - ruler['offset']:
                            new_lines[line_index] = ruler['lines'][line_index]
                        else:
                            new_lines[line_index] = ruler['lines'][line_index + amount]

                    ruler['lines'] = new_lines

            return self
        
        def reroot(self):
            if self._staff != None:
                extra_root_rulers = (self._root_self - self).unique()
                self._staff.remove(extra_root_rulers.list())
            
            self._root_self = self
            self._staff.setRuler(self) # avoids broken links
            return self
        
        def reset(self):
            if self._staff != None:
                self._staff.clear()
                for staff_ruler in self._root_self.list():
                    staff_ruler['on_staff'] = True
                unique_rulers_list = self._root_self.unique().list()
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
        
        def roll_lines(self, increments=1):
            self.rotate_lines(-increments)
            self.move_lines(increments)

            return self

        def root(self):
            return self._root_self
                
        def rotate(self, increments=1):
            """Rotates the placement of the print listing without changing any data"""
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
            """Rotates the position of the rolers by changing the position data"""
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
        
        def set_staff(self, staff):
            self._staff = staff
            return self

        def single(self, index=0):
            if (self.len() > index):
                ruler_list = [ self._rulers_list[index] ]
                return Staff.Rulers(self._staff, ruler_list, self._root_self)
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

        def spread_lines(self, increments=1):
            rulers_list_size = self.len()
            for ruler_index in range(rulers_list_size):
                self._rulers_list[ruler_index]['offset'] += ruler_index * increments

            return self

        def tail(self, elements=1):
            tail_rulers_list = self._rulers_list[-elements:]
            return Staff.Rulers(self._staff, tail_rulers_list, self._root_self)

        def type(self, type="arguments"):
            return self.filter(type=type)

        def unique(self):
            unique_rulers_list = []
            for ruler in self._rulers_list:
                if ruler not in unique_rulers_list:
                    unique_rulers_list.append(ruler)

            return Staff.Rulers(self._staff, unique_rulers_list, self._root_self)
        
# Staff METHODS ###############################################################################################################################

    def _getStaffSums(self, staff_list): # outputs single staff pulse
        staff_list_sums = {'arguments': {'enabled': 0, 'total': 0}, 'actions': {'enabled': 0, 'total': 0}}
        for staff_pulse in staff_list:
            staff_list_sums['arguments']['enabled'] += staff_pulse['arguments']['enabled']
            staff_list_sums['arguments']['total'] += staff_pulse['arguments']['total']
            staff_list_sums['actions']['enabled'] += staff_pulse['actions']['enabled']
            staff_list_sums['actions']['total'] += staff_pulse['actions']['total']

        return staff_list_sums
    
    def _setTopLengths(self):
        return self._setTopLengths_Values()._setTopLengths_Sums()

    def _setTopLengths_Values(self):

        for key, value in self.string_top_lengths.items():
            if key == 'measure' or key == 'beat' or key == 'step' or key == 'pulse':
                self.string_top_length = 0

        for staff_pulse in self._staff: # get maximum sizes
            for key, value in staff_pulse.items():
                if key == 'measure' or key == 'beat' or key == 'step' or key == 'pulse':
                    self.string_top_lengths[key] = max(self.string_top_lengths[key], len(f"{value}"))

        self.string_top_length = 0
        for value in self.string_top_lengths.values():
            self.string_top_length += value

        return self
    
    def _setTopLengths_Sums(self):

        staff_list_sums = self._getStaffSums(self._staff)
        self.string_top_lengths['arguments_enabled'] = \
            max(self.string_top_lengths['arguments_enabled'], len(f"{staff_list_sums['arguments']['enabled']}"))
        self.string_top_lengths['arguments_total'] = \
            max(self.string_top_lengths['arguments_total'], len(f"{staff_list_sums['arguments']['total']}"))
        self.string_top_lengths['actions_enabled'] = \
            max(self.string_top_lengths['actions_enabled'], len(f"{staff_list_sums['actions']['enabled']}"))
        self.string_top_lengths['actions_total'] = \
            max(self.string_top_lengths['actions_total'], len(f"{staff_list_sums['actions']['total']}"))

        self.string_top_length = 0
        for value in self.string_top_lengths.values():
            self.string_top_length += value

        return self
    
    def actions(self):
        total_actions = {'enabled': 0, 'total': 0}
        for staff_pulse in self._staff:
            total_actions['enabled'] += staff_pulse['actions']['enabled']
            total_actions['total'] += staff_pulse['actions']['total']
        return total_actions

    def add(self, rulers, enabled_one=1, total_one=1):
        for ruler in rulers:
            pulses = self.pulses(ruler['position'])
            if pulses < self.len():
                if ruler['on_staff']:
                    if ruler['enabled']:
                        self._staff[pulses][ruler['type']]['enabled'] += enabled_one
                    self._staff[pulses][ruler['type']]['total'] += total_one
        
        return self._setTopLengths_Sums()
    
    def addPositions(self, position_1=[0, 0], position_2=[0, 0]):

        steps_1 = self.steps(position_1)
        steps_2 = self.steps(position_2)
        total_steps = steps_1 + steps_2
        
        return self.position(steps=total_steps)

    def arguments(self):
        total_arguments = {'enabled': 0, 'total': 0}
        for staff_pulse in self._staff:
            total_arguments['enabled'] += staff_pulse['arguments']['enabled']
            total_arguments['total'] += staff_pulse['arguments']['total']
        return total_arguments

    def clear(self):
        for staff_pulse in self._staff:
            staff_pulse['arguments'] = {'enabled': 0, 'total': 0}
            staff_pulse['actions'] = {'enabled': 0, 'total': 0}

        return self._setTopLengths_Sums()

    def disable(self, rulers):
        return self.remove(rulers, total_one=0)
    
    def enable(self, rulers):
        return self.add(rulers, total_one=0)

    def filterList(self, measure=None, beat=None, step=None, pulse=None, list=None):
        if list != None:
            filtered_list = list[:]
        else:
            filtered_list = self._staff[:]

        if measure != None:
            filtered_list = [
                pulses for pulses in filtered_list if pulses['measure'] == measure
            ]
        if beat != None:
            filtered_list = [
                pulses for pulses in filtered_list if pulses['beat'] == beat
            ]
        if step != None:
            filtered_list = [
                pulses for pulses in filtered_list if pulses['step'] == step
            ]
        if pulse != None:
            filtered_list = [
                pulses for pulses in filtered_list if pulses['pulse'] == pulse
            ]
        return filtered_list

    def getRulers(self):
        return self._rulers

    def json_dictionnaire(self):
        return {
                'part': "staff",
                'class': self.__class__.__name__,
                'time_signature': self._time_signature,
                'total_pulses': self._total_pulses,
                'play_range': self._play_range,
                'rulers': [ self._rulers.json_dictionnaire() ]
            }

    def json_load(self, file_name="staff.json", json_object=None):
        
        if json_object == None:
            # Opening JSON file
            with open(file_name, 'r') as openfile:
                # Reading from json file
                json_object = json.load(openfile)

        for dictionnaire in json_object:
            if dictionnaire['part'] == "staff":
                size_measures = dictionnaire['time_signature']['size_measures']
                beats_per_measure = dictionnaire['time_signature']['beats_per_measure']
                steps_per_beat = dictionnaire['time_signature']['steps_per_beat']
                pulses_per_quarter_note = dictionnaire['time_signature']['pulses_per_quarter_note']
                play_range = dictionnaire['play_range']
                
                self.clear()

                self.set_range(start=play_range[0], finish=play_range[1])
                self.set(size_measures, beats_per_measure, steps_per_beat, pulses_per_quarter_note)
            
                self._rulers = self._rulers.json_load(file_name, dictionnaire['rulers'])

                break

        return self

    def json_save(self, file_name="staff.json"):
        staff = [ self.json_dictionnaire() ]
            
        # Writing to sample.json
        with open(file_name, "w") as outfile:
            json.dump(staff, outfile)

        return self

    def len(self):
        return self._total_pulses
    
    def len_steps(self):
        return self._total_pulses * self._time_signature['steps_per_beat'] / self._time_signature['pulses_per_beat']
    
    def list(self):
        return self._staff
    
    def player(self):
        return self._player

    def playRange(self):
        return self._play_range

    def playRange_pulses(self, play_range=[[], []]):
        if play_range == [[], []]:
            return [self.pulses(self._play_range[0]), self.pulses(self._play_range[1])]
        return [self.pulses(play_range[0]), self.pulses(play_range[1])]

    def position(self, steps=None, pulses=None):
        if (steps != None):
            measures = int(steps / (self._time_signature['steps_per_beat'] * self._time_signature['beats_per_measure']))
            steps = steps % (self._time_signature['steps_per_beat'] * self._time_signature['beats_per_measure'])
            if steps < 0:
                steps = -(-steps % (self._time_signature['steps_per_beat'] * self._time_signature['beats_per_measure']))
        elif (pulses != None):
            measures = int(pulses / (self._time_signature['pulses_per_beat'] * self._time_signature['beats_per_measure']))
            steps = pulses * self._time_signature['steps_per_beat'] / self._time_signature['pulses_per_beat'] % \
                (self._time_signature['steps_per_beat'] * self._time_signature['beats_per_measure'])
            if pulses < 0:
                steps = -(-pulses * self._time_signature['steps_per_beat'] / self._time_signature['pulses_per_beat'] % \
                          (self._time_signature['steps_per_beat'] * self._time_signature['beats_per_measure']))
        return [measures, steps]
    
    def print(self):
        if len(self._staff) > 0:
            if len(self._staff) > 1:
                print("§" * (self.string_top_length + 128))

            for staff_pulse in self._staff:
                self.printSinglePulse(staff_pulse['pulse'])

            if len(self._staff) > 1:
                print("§" * (self.string_top_length + 128))
        else:
            print("[EMPTY]")
        return self
    
    def printSinglePulse(self, pulse=0, sums='pulse', extra_string=""):

        spaces_between = 6

        staff_pulse = self._staff[pulse]
        pulse_sums = self.pulseSums(staff_pulse['pulse'], sums)

        pulse_str = "{ "
        for key, value in staff_pulse.items():
            if key == 'arguments':
                enabled_value_str = f"{pulse_sums['arguments']['enabled']}"
                enabled_value_length = len(enabled_value_str)
                enabled_value_str = "arguments: { enabled: " + (" " * (self.string_top_lengths['arguments_enabled'] - enabled_value_length)) + enabled_value_str
                enabled_value_str += " " * int(spaces_between / 2)
                total_value_str = f"{pulse_sums['arguments']['total']}"
                total_value_length = len(total_value_str)
                total_value_str = "total: " + (" " * (self.string_top_lengths['arguments_total'] - total_value_length)) + total_value_str + " }"
                pulse_str += enabled_value_str + total_value_str + " " * spaces_between
            elif key == 'actions':
                enabled_value_str = f"{pulse_sums['actions']['enabled']}"
                enabled_value_length = len(enabled_value_str)
                enabled_value_str = "actions: { enabled: " + (" " * (self.string_top_lengths['actions_enabled'] - enabled_value_length)) + enabled_value_str
                enabled_value_str += " " * int(spaces_between / 2)
                total_value_str = f"{pulse_sums['actions']['total']}"
                total_value_length = len(total_value_str)
                total_value_str = "total: " + (" " * (self.string_top_lengths['actions_total'] - total_value_length)) + total_value_str + " }"
                pulse_str += enabled_value_str + total_value_str + " " * 0
            else:
                key_value_str = f"{value}"
                key_value_length = len(key_value_str)
                key_value_str = (" " * (self.string_top_lengths[key] - key_value_length)) + key_value_str
                key_value_str = f"{key}: " + key_value_str
                pulse_str += key_value_str + " " * spaces_between
        pulse_str += " }"
        print(pulse_str + extra_string)

        return self

    def pulseRemainders(self, pulse=0):
        return {
            'measure': pulse % (self._time_signature['pulses_per_beat'] * self._time_signature['beats_per_measure']),
            'beat': pulse % self._time_signature['pulses_per_beat'],
            'step': pulse % (self._time_signature['pulses_per_beat'] / self._time_signature['steps_per_beat']),
            'pulse': 0 # by definition is pulse % pulse = 0
        }
    
    def pulseSums(self, pulse=0, sums='pulse'):
        pulse_sums = {'arguments': {'enabled': 0, 'total': 0}, 'actions': {'enabled': 0, 'total': 0}}

        measure = self._staff[pulse]['measure']
        beat = self._staff[pulse]['beat']
        step = self._staff[pulse]['step']

        match sums:
            case 'measure':
                measure = self._staff[pulse]['measure']
                filtered_list = self.filterList(measure=measure)
            case 'beat':
                measure = self._staff[pulse]['measure']
                beat = self._staff[pulse]['beat']
                filtered_list = self.filterList(measure=measure, beat=beat)
            case 'step':
                measure = self._staff[pulse]['measure']
                step = self._staff[pulse]['step']
                filtered_list = self.filterList(measure=measure, beat=beat, step=step)
            case default:
                filtered_list = [ self._staff[pulse] ]

        for staff_pulse in filtered_list:
            pulse_sums['arguments']['enabled'] += staff_pulse['arguments']['enabled']
            pulse_sums['arguments']['total'] += staff_pulse['arguments']['total']
            pulse_sums['actions']['enabled'] += staff_pulse['actions']['enabled']
            pulse_sums['actions']['total'] += staff_pulse['actions']['total']

        return pulse_sums
    
    def pulses(self, position=[0, 0]): # position: [measure, step]
        return position[0] * self._time_signature['beats_per_measure'] * self._time_signature['pulses_per_beat'] + \
            round(position[1] * self._time_signature['pulses_per_beat'] / self._time_signature['steps_per_beat'])

    def remove(self, rulers, enabled_one=-1, total_one=-1):
        return self.add(rulers, enabled_one, total_one)
    
    def rulers(self):
        return self._rulers

    def set(self, size_measures=None, beats_per_measure=None, steps_per_beat=None, pulses_per_quarter_note=None):

        if self._time_signature == {}:
            self._time_signature['size_measures'] = size_measures
            if size_measures == None:
                self._time_signature['size_measures'] = 8
            self._time_signature['beats_per_measure'] = beats_per_measure
            if beats_per_measure == None:
                self._time_signature['beats_per_measure'] = 4
            self._time_signature['steps_per_beat'] = steps_per_beat
            if steps_per_beat == None:
                self._time_signature['steps_per_beat'] = 4
            self._time_signature['pulses_per_quarter_note'] = pulses_per_quarter_note
            if pulses_per_quarter_note == None:
                self._time_signature['pulses_per_quarter_note'] = 24
        else:
            if size_measures != None:
                self._time_signature['size_measures'] = int(max(1, size_measures))                      # staff total size
            if beats_per_measure != None:
                self._time_signature['beats_per_measure'] = int(max(1, beats_per_measure))              # beats in each measure
            if steps_per_beat != None:
                self._time_signature['steps_per_beat'] = 1 if steps_per_beat == 0 else steps_per_beat   # how many steps take each beat
            if pulses_per_quarter_note != None:
                self._time_signature['pulses_per_quarter_note'] = pulses_per_quarter_note               # sets de resolution of clock pulses

        self._time_signature['pulses_per_beat'] = self._time_signature['steps_per_beat'] * \
            round(converter_PPQN_PPB(self._time_signature['pulses_per_quarter_note']) / self._time_signature['steps_per_beat'])

        self._total_pulses = self._time_signature['size_measures'] * \
            self._time_signature['beats_per_measure'] * self._time_signature['pulses_per_beat']

        old_staff = self._staff[:]
        self._staff = []
        for pulse in range(self._total_pulses):
            staff_pulse = {
                'measure': int(pulse / (self._time_signature['pulses_per_beat'] * self._time_signature['beats_per_measure'])),
                'beat': int(pulse / self._time_signature['pulses_per_beat']) % self._time_signature['beats_per_measure'],
                'step': int(pulse * self._time_signature['steps_per_beat'] / \
                            self._time_signature['pulses_per_beat']) % \
                                (self._time_signature['steps_per_beat'] * self._time_signature['beats_per_measure']),
                'pulse': pulse,
                'arguments': {'enabled': 0, 'total': 0},
                'actions': {'enabled': 0, 'total': 0}
            }
            self._staff.append(staff_pulse)

        if self._total_pulses > 0:
            for staff_pulse in old_staff:
                for ruler_type in ['arguments', 'actions']:
                    if staff_pulse[ruler_type]['total'] > 0:
                        position_pulses = self.pulses([staff_pulse['measure'], staff_pulse['step']])
                        size_total_pulses = self._time_signature['size_measures'] * \
                            self._time_signature['beats_per_measure'] * self._time_signature['pulses_per_beat']
                        if not position_pulses < 0 and position_pulses < size_total_pulses:
                            self._staff[position_pulses][ruler_type]['enabled'] = staff_pulse[ruler_type]['enabled']
                            self._staff[position_pulses][ruler_type]['total'] = staff_pulse[ruler_type]['total']

        return self.set_range()._setTopLengths()
    
    def set_range(self, start=None, finish=None):
        if self._total_pulses > 0:
            if start == [] or self._play_range[0] == []:
                self._play_range[0] = [0, 0]
            elif start == None and self._play_range[0] != []:
                start_pulses = min(self._total_pulses, self.pulses(self._play_range[0]))
                self._play_range[0] = self.position(pulses=start_pulses)
            elif start != None:
                start_pulses = min(self._total_pulses, self.pulses(start))
                self._play_range[0] = self.position(pulses=start_pulses)

            if finish == [] or self._play_range[1] == []:
                finish_pulses = self._total_pulses
                self._play_range[1] = self.position(pulses=finish_pulses)
            elif finish == None and self._play_range[1] != []:
                start_pulses = min(self._total_pulses, self.pulses(self._play_range[1]))
                self._play_range[1] = self.position(pulses=start_pulses)
            elif finish != None:
                start_pulses = self.pulses(self._play_range[0])
                finish_pulses = max(start_pulses, min(self._total_pulses, self.pulses(finish)))
                self._play_range[1] = self.position(pulses=finish_pulses)

        return self
    
    def setRulers(self, rulers):
        self._rulers = rulers
        return self

    def steps(self, position=[0, 0]): # position: [measure, step]
        return position[0] * self._time_signature['beats_per_measure'] * self._time_signature['steps_per_beat'] + position[1]

    def str_position(self, position):
        return str(position[0]) + " " + str(round(position[1], 6))

    def time_signature(self):
        return self._time_signature

# GLOBAL CLASS METHODS

def trimString(full_string):
    string_maxum_size = 16
    long_string_termination = "…"
    trimmed_string = full_string
    if len(full_string) > string_maxum_size:
        trimmed_string = full_string[:string_maxum_size] + long_string_termination
    return trimmed_string

def position_gt(left_position, right_position):
    if len(left_position) == 2 and len(right_position) == 2:
        if (left_position[0] > right_position[0]):
            return True
        if (left_position[0] == right_position[0]):
            if (left_position[1] > right_position[1]):
                return True
    return False

def position_lt(left_position, right_position):
    if len(left_position) == 2 and len(right_position) == 2:
        if (left_position[0] < right_position[0]):
            return True
        if (left_position[0] == right_position[0]):
            if (left_position[1] < right_position[1]):
                return True
    return False

def converter_PPQN_PPB(pulses_per_quarter_note=24, steps_per_beat=4): # 4 steps per beat is a constant
    '''Converts Pulses Per Quarter Note into Pulses Per Beat'''
    STEPS_PER_QUARTER_NOTE = 4
    pulses_per_beat = pulses_per_quarter_note * (steps_per_beat / STEPS_PER_QUARTER_NOTE)
    return int(pulses_per_beat)
