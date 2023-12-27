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

import re
import json
import player as PLAYER
import lines_scales as LINES_SCALES

class Staff:

    def __init__(self, player):

        self._player = player
        self._rulers = Staff.Rulers(self)
        self._staff_list = []
        self._time_signature = {}
        self._total_pulses = 0
        self.string_top_lengths = {'measure': 0, 'beat': 0, 'step': 0, 'pulse': 0, 'arguments_enabled': 0, 'arguments_total': 0, 'actions_enabled': 0, 'actions_total': 0}
        self.string_top_length = 0
        self._play_range = [[], []]
        self.set_range([], [])
        self.set()

    @property
    def is_none(self):
        return (self.__class__ == StaffNone)

    @property
    def player(self):
        return self._player
            
    class Rulers():

        def __init__(self, staff, rulers_list=None, root_self=None, start_id=1, last_action_duration=4):

            self._root_self = self
            self._recall_self = self
            if root_self != None:
                self._root_self = root_self # type Rulers
                self._root_self._recall_self = self
            self._staff = staff
            self._rulers_list = []
            if rulers_list != None:
                self._rulers_list = rulers_list

            self._next_id = start_id
            self._last_action_duration = last_action_duration # steps

            self.current_ruler = 0

        @property
        def is_none(self):
            return (self.__class__ == Staff.RulersNone)

        @property
        def player(self):
            return self._staff.player
            
        def __iter__(self):
            return self
        
        def __next__(self):
            if self.current_ruler < len(self._rulers_list):
                result = self._rulers_list[self.current_ruler]
                self.current_ruler += 1
                return result
            else:
                self.current_ruler = 0  # Reset to 0 when limit is reached
                raise StopIteration
        
        # + Operator Overloading in Python
        def __add__(self, other):
            '''Works as Union'''
            self_rulers_list = self.list()
            other_rulers_list = other.list()

            return Staff.Rulers(self._staff, self_rulers_list + other_rulers_list, self._root_self, self._next_id, self._last_action_duration)
        
        def __sub__(self, other):
            '''Works as exclusion'''
            self_rulers_list = self.list()
            other_rulers_list = other.list()

            exclusion_list = [ ruler for ruler in self_rulers_list if ruler not in other_rulers_list ]

            return Staff.Rulers(self._staff, exclusion_list, self._root_self, self._next_id, self._last_action_duration)
        
        def __mul__(self, other):
            '''Works as intersection'''
            self_rulers_list = self.list()
            other_rulers_list = other.list()
            
            intersection_list = [ ruler for ruler in self_rulers_list if ruler in other_rulers_list ]

            return Staff.Rulers(self._staff, intersection_list, self._root_self, self._next_id, self._last_action_duration)
        
        def __div__(self, other):
            '''Works as divergence'''
            union_rulers = self.__add__(other)
            intersection_rulers = self.__mul__(other)

            return union_rulers - intersection_rulers
        
        def _allocate_players(self):
                
                # if ruler_data['type'] == "actions":
                #     link_name += "_" + link_name
                # link_name_re = re.search(r"([a-zA-Z0-9]+)_(.+)", link_name)
                # if link_name_re != None:

            all_rulers = self._root_self
            for enabled_ruler_data in all_rulers:
                link_list = enabled_ruler_data['link'].split(".")
                if len(link_list) > 0:
                    player_name = link_list[0]
                    enabled_ruler_data['player'] = self.player.stage.filter(enabled=True).player(name=player_name)
                    if enabled_ruler_data['player'] == self.player and enabled_ruler_data['type'] == "actions":
                        enabled_ruler_data['player'] = PLAYER.PlayerNone(self.player.stage)

                # also convert positions from notes duration to steps
                enabled_ruler_data['position'][1] = LINES_SCALES.note_to_steps(enabled_ruler_data['position'][1])

            return self

        def _sets_and_automations_rulers_generator(self):
            
            sets_and_automations_rulers_list = []
            auto_set_rulers = self._root_self.arguments().on_staff().enabled().sort(key="position")

            auto_rulers = auto_set_rulers.link_find(".auto")
            auto_rulers_merged = auto_rulers.merge()
            for auto_link_merged in auto_rulers_merged:
                auto_rulers_link = auto_rulers.link(auto_link_merged['link'])
                following_rulers = auto_rulers_link
                for auto_ruler in auto_rulers_link:
                    new_auto_ruler = {
                        'id': auto_ruler['id'],
                        'type': auto_ruler['type'],
                        'link': auto_ruler['link'],
                        'position': auto_ruler['position'],
                        'lines': [
                            auto_ruler['lines'],                    # start     (0)
                            [ None ] * len(auto_ruler['lines']),    # finish    (1)
                            [ 0 ] * len(auto_ruler['lines'])        # pulses    (2)
                        ],
                        'offset': auto_ruler['offset'],
                        'enabled': False, # not intended to be processed by the Staff
                        'on_staff': False, # not intended to be on the Staff
                        'player': auto_ruler['player']
                    }

                    line_finish = 1
                    line_pulses = 2

                    if following_rulers.len() > 1:
                        following_rulers -= following_rulers.filter(ids=[auto_ruler['id']])
                        for following_ruler in following_rulers:
                            distance_pulses = self._staff.pulses(following_ruler['position']) - self._staff.pulses(auto_ruler['position'])
                            for auto_ruler_line in range(len(auto_ruler['lines'])):
                                complete_new_auto_ruler = True
                                if new_auto_ruler['lines'][line_finish][auto_ruler_line] == None:
                                    complete_new_auto_ruler = False
                                    new_auto_ruler['lines'][line_pulses][auto_ruler_line] += distance_pulses
                                    if not auto_ruler['offset'] + auto_ruler_line < following_ruler['offset'] and \
                                        not auto_ruler['offset'] + auto_ruler_line > following_ruler['offset'] + len(following_ruler['lines']) - 1:

                                        new_auto_ruler['lines'][line_finish][auto_ruler_line] = following_ruler['lines'][auto_ruler_line + auto_ruler['offset'] - following_ruler['offset']]
                                if complete_new_auto_ruler:
                                    break

                    sets_and_automations_rulers_list.append(new_auto_ruler)
            
            set_rulers = auto_set_rulers.link_find(".set")
            set_rulers_merged = set_rulers.merge()
            for set_link_merged in set_rulers_merged:
                new_set_ruler = {
                    'id': set_link_merged['id'],
                    'type': set_link_merged['type'],
                    'link': set_link_merged['link'],
                    'position': set_link_merged['position'],
                    'lines': [
                        set_link_merged['lines']
                    ],
                    'offset': set_link_merged['offset'],
                    'enabled': False, # not intended to be processed by the Staff
                    'on_staff': False, # not intended to be on the Staff
                    'player': set_link_merged['player']
                }

                sets_and_automations_rulers_list.append(new_set_ruler)
            
            return Staff.Rulers(self._staff, sets_and_automations_rulers_list, self._root_self, self._next_id, self._last_action_duration)

        def _str_position(self, position, note_notation=None):
            
            position[1] = format_note_duration(position[1], note_notation)
            position_value = [position[0], position[1] if isinstance(position[1], str) else round(position[1], 3)]
            if not isinstance(position[1], str) and position_value[1] % 1 == 0:
                position_value = [position_value[0], int(position_value[1])]
            
            return f"{position_value}"

        def actions(self):
            return self.type(type="actions")

        def action_lines_duration_validator(self, action_lines):
            if len(action_lines) == 0:
                action_lines = [ self._last_action_duration ]
            else:
                for action_line_index in range(len(action_lines)):
                    if action_lines[action_line_index] == None or action_lines[action_line_index] == False:
                        action_lines[action_line_index] = self._last_action_duration
                    else:
                        self._last_action_duration = action_lines[action_line_index]
            return action_lines

        def stack_position(self, type="actions"):
            finish_action_position_steps = 0
            for action_ruler in self.actions():
                action_ruler_position_steps = self._staff.steps(action_ruler['position'])
                for action_duration in action_ruler['lines']:
                    action_duration_steps = self._staff.steps([0, action_duration])
                    finish_action_position_steps = max(finish_action_position_steps, action_ruler_position_steps + action_duration_steps)

            if type == "actions":
                return self._staff.position(finish_action_position_steps)

            start_argument_position_steps = finish_action_position_steps
            for ruler_data in self:
                action_ruler_position_steps = self._staff.steps(ruler_data['position'])
                start_argument_position_steps = min(start_argument_position_steps, action_ruler_position_steps)

            return self._staff.position(start_argument_position_steps)

        def add(self, ruler=None): # Must be able to remove removed rulers from the main list
            if ruler == None:
                ruler = self
            if ruler.__class__ == self.__class__:
                for ruler_data in ruler.list().copy():
                    self.add(ruler_data)
            else:
                if not self.is_none and ruler != None and len(ruler) > 0 and 'link' in ruler and ruler['link'] != None:

                    link_list = ruler['link'].split(".")
                    ruler_type = "arguments"
                    if len(link_list) == 1:
                        ruler_type = "actions"

                    structured_ruler = {
                        'id': self._root_self._next_id,
                        'type': ruler_type,
                        'link': ruler['link'],
                        'position': [0, 0],
                        'lines': [],
                        'offset': None,
                        'enabled': True,
                        'on_staff': False, # at the beginning it's not on the Staff
                        'player': None
                    }
                    self._root_self._next_id += 1

                    if 'position' in ruler and ruler['position'] != None and len(ruler['position']) == 2:
                        structured_ruler['position'] = ruler['position']
                    else:
                        next_action_position = self.stack_position(ruler_type)
                        structured_ruler['position'] = next_action_position
                    if 'lines' in ruler and ruler['lines'] != None:
                        if type(ruler['lines']) != type([]) and type(ruler['lines']) != type({}):
                            structured_ruler['lines'] = [ ruler['lines'] ]
                        elif len(ruler['lines']) > 0:
                            if type(ruler['lines']) == type({}):
                                structured_ruler['lines'] = ruler['lines']['lines']
                                structured_ruler['offset'] = ruler['lines']['offset']
                            else:
                                structured_ruler['lines'] = ruler['lines']
                    if structured_ruler['type'] == "actions":
                        structured_ruler['lines'] = self.action_lines_duration_validator(structured_ruler['lines'])
                    if (structured_ruler['offset'] == None and 'offset' in ruler and ruler['offset'] != None):
                        structured_ruler['offset'] = ruler['offset']
                    if (structured_ruler['offset'] == None):
                        structured_ruler['offset'] = 0
                    if ('enabled' in ruler and ruler['enabled'] != None):
                        structured_ruler['enabled'] = ruler['enabled']

                    self._root_self._rulers_list.append(structured_ruler)
                    if (self != self._root_self):
                        self._rulers_list.append(structured_ruler)
                        self._next_id = self._root_self._next_id
                    self._staff.add([structured_ruler])

            return self
        
        def add_lines(self, line, amount=1, id=None):
            """Add new empty lines lines"""
            target_rulers = self
            if id != None:
                target_rulers = self.filter(ids=[id])
            for ruler in target_rulers:

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
                    if ruler['type'] == "action":
                        ruler['lines'] = self.action_lines_duration_validator(ruler['lines'])
                
            return self
            
        def arguments(self):
            return self.type(type="arguments")

        def beats(self, *beats):
            return self.filter(beats=beats)

        def clone(self):
            type_rulers = [ self.type("arguments"), self.type("actions") ]
            on_staff = self.on_staff()
            on_staff.float()
            for rulers in type_rulers:
                if rulers.len() > 1:
                    first_ruler = rulers.list()[0]
                    for ruler in rulers:
                        ruler['link'] = first_ruler['link']
                        ruler['position'] = first_ruler['position'].copy()
                        ruler['lines'] = first_ruler['lines'].copy()
                        ruler['offset'] = first_ruler['offset']
                        ruler['enabled'] = first_ruler['enabled']
                        ruler['on_staff'] = first_ruler['on_staff']
                        for line in ruler['lines']:
                            if isinstance(line, list) or isinstance(line, dict):
                                line = line.copy()
            on_staff.drop()
            return self

        def clone_lines(self):
            type_rulers = [ self.type("arguments"), self.type("actions") ]
            for rulers in type_rulers:
                if rulers.len() > 1:
                    first_ruler = rulers.list()[0]
                    for ruler in rulers:
                        ruler['lines'] = first_ruler['lines'].copy()
                        ruler['offset'] = first_ruler['offset']
                        for line in ruler['lines']:
                            if isinstance(line, list) or isinstance(line, dict):
                                line = line.copy()
            return self

        def copy(self):
            """Shows just the copied rulers"""
            copied_rulers = self.empty() # creates new empty Ruler object
            for ruler_data in self.list().copy():
                ruler_copy = ruler_data.copy()
                ruler_copy['lines'] = ruler_data['lines'].copy()
                copied_rulers.add(ruler_copy)

            return copied_rulers
        
        def disable(self):
            disabled_rulers_list = self.filter(enabled=True).unique().list()
            # updates disabled on staff
            self._staff.disabled(disabled_rulers_list)
            # disables all rulers
            for enabled_ruler in disabled_rulers_list:
                enabled_ruler['enabled'] = False
            return self
        
        def disabled(self):
            return self.filter(enabled=False)
        
        def distribute(self, range_steps=None, range_positions=[[None, None], [None, None]]):
            sorted_rulers = self.unique().sort()
            number_intervals = sorted_rulers.len()
            if number_intervals > 1:
                if range_positions[0][0] != None and range_positions[0][1] != None and range_positions[1][0] != None and range_positions[1][1] != None:
                    distance_pulses = self._staff.pulses(range_positions[1]) - self._staff.pulses(range_positions[0]) # total distance
                    start_pulses = self._staff.pulses(range_positions[0])
                    finish_pulses = start_pulses + round(distance_pulses * (number_intervals - 1) / number_intervals)
                elif range_steps != None:
                    range_steps = LINES_SCALES.note_to_steps(range_steps)
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
                    on_staff = sorted_rulers.on_staff()
                    on_staff.float()
                    for index in range(number_intervals):
                        new_position = self._staff.position(pulses=start_pulses + round(index * distance_pulses / number_intervals))
                        sorted_rulers.list()[index]['position'] = new_position
                    on_staff.drop()

            return sorted_rulers
        
        def drag(self, tail=None, length=None):

            for ruler_data in self._rulers_list:
                ruler_lines_length = len(ruler_data['lines'])
                ruler_lines_tail = tail
                if ruler_lines_tail == None:
                    ruler_lines_tail = ruler_lines_length
                new_lines_length = length
                if new_lines_length == None:
                    new_lines_length = ruler_lines_length
                
                new_lines = [None] * new_lines_length
                for new_lines_index in range(new_lines_length):
                    tail_lines_index = ruler_lines_length - ruler_lines_tail + new_lines_index % ruler_lines_tail
                    new_lines[new_lines_index] = ruler_data['lines'][tail_lines_index]
                
                ruler_data['lines'] += new_lines

            return self

        def drop(self):
            self._staff.add(self.unique().list())
            return self

        def duplicate(self, times=1):
            """Duplicates the listed rulers"""
            source_rulers_list = self._rulers_list[:]
            for _ in range(times):
                for ruler_data in source_rulers_list:
                    ruler = ruler_data.copy()
                    ruler['lines'] = ruler_data['lines'].copy()
                    self.add(ruler)
            return self
        
        def empty(self):
            empty_rulers_list = []
            return Staff.Rulers(self._staff, empty_rulers_list, self._root_self, self._next_id, self._last_action_duration)
        
        def empty_lines(self):
            for ruler in self._rulers_list:
                ruler['lines'] = []
            return self
    
        def enable(self):
            enabled_rulers_list = self.filter(enabled=False).unique().list()
            # enables all rulers
            for disabled_ruler in enabled_rulers_list:
                disabled_ruler['enabled'] = True
            # updates enabled on staff
            self._staff.enabled(enabled_rulers_list)
            return self
        
        def enabled(self):
            return self.filter(enabled=True)
        
        def erase_lines(self):
            for rulers in self._rulers_list:
                for index in len(rulers['lines']):
                    rulers['lines'][index] = None

            return self
        
        def erase_lines(self, line, amount=1, id=None):
            target_rulers = self
            if id != None:
                target_rulers = self.filter(ids=[id])

            for ruler in target_rulers:

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
            even_rulers_list = self._rulers_list[1::2]
            return Staff.Rulers(self._staff, even_rulers_list, self._root_self, self._next_id, self._last_action_duration)
        
        def every(self, multiple, first=1):
            if multiple > 0:
                if first == None:
                    first = multiple
                if first > 0:
                    first_0 = first - 1
                    every_rulers = []
                    for ruler_index in range(self.len()):
                        if (ruler_index - first_0 + 1) % multiple == 0 and ruler_index >= first_0:
                            every_rulers.append(self._rulers_list[ruler_index])
                    return Staff.Rulers(self._staff, every_rulers, self._root_self, self._next_id, self._last_action_duration)
            return self

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
            on_staff = self.on_staff()
            on_staff.float()
            for ruler_index in range(1, self.len()):
                self._rulers_list[ruler_index]['position'] = self._staff.add_position(first_position, [0, ruler_index * spread_steps])
            on_staff.drop()
            return self
        
        def filter(self, ids=[], type=None, links=[], positions=[], position_range=[], lines=[], measures=[], beats=[], steps=[], enabled=None, on_staff=None, player=None):

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
            if (len(links) > 0 and links != [None]):
                filtered_rulers = [
                    ruler for ruler in filtered_rulers if ruler['link'] in links
                ]
            if (len(positions) > 0 and positions != [None]): # Check for as None for NOT enabled
                for position_index in range(len(positions)):
                    positions[position_index] = LINES_SCALES.note_to_steps(positions[position_index])
                filtered_rulers = [
                    ruler for ruler in filtered_rulers if LINES_SCALES.note_to_steps(ruler['position']) in positions
                ]
            if (len(position_range) == 2 and len(position_range[0]) == 2 and len(position_range[1]) == 2):
                position_range[0][1] = LINES_SCALES.note_to_steps(position_range[0][1])
                position_range[1][1] = LINES_SCALES.note_to_steps(position_range[1][1])
                # Using list comprehension
                filtered_rulers = [
                    ruler for ruler in filtered_rulers
                            if not (position_lt(ruler['position'], position_range[0]) and position_lt(ruler['position'], position_range[1]))
                ]
            if (len(lines) > 0 and lines != [None]):
                filtered_rulers = [
                    ruler for ruler in filtered_rulers if overlapping_lists(range(ruler['offset'], ruler['offset'] + len(ruler['lines'])), lines)
                ]
            if (len(measures) > 0 and measures != [None]):
                filtered_rulers = [
                    ruler for ruler in filtered_rulers if ruler['position'][0] in measures
                ]
            if (len(beats) > 0 and beats != [None]):
                filtered_rulers = [
                    ruler for ruler in filtered_rulers \
                        if self._staff.step_divisions(self._staff.steps(ruler['position']))['beat'] in beats
                ]
            if (len(steps) > 0 and steps != [None]):
                filtered_rulers = [
                    ruler for ruler in filtered_rulers \
                        if self._staff.step_divisions(self._staff.steps(ruler['position']))['step'] in steps
                ]
            if (enabled != None):
                filtered_rulers = [
                    ruler for ruler in filtered_rulers if ruler['enabled'] == enabled
                ]
            if (on_staff != None):
                filtered_rulers = [
                    ruler for ruler in filtered_rulers if ruler['on_staff'] == on_staff
                ]
            if (player != None):
                filtered_rulers = [
                    ruler for ruler in filtered_rulers if ruler['player'] == player
                ]
            return Staff.Rulers(self._staff, filtered_rulers, self._root_self, self._next_id, self._last_action_duration)
        
        def first(self):
            return self.head(1)

        def float(self):
            self._staff.remove(self.unique().list())
            # updates on_staff for all remaining rulers not on staff
            for ruler_list in self.list():
                ruler_list['on_staff'] = False
            return self
        
        def function_lines(self, function = lambda line : line):
            for ruler in self._rulers_list:
                for line_index in range(len(ruler['lines'])):
                    ruler['lines'][line_index] = function(ruler['lines'][line_index])

            return self

        def get_finish_position(self):

            finish_position_steps = 0
            for ruler_data in self._rulers_list:
                ruler_start_position_steps = self._staff.steps(ruler_data['position'])
                if ruler_data['type'] == "arguments":
                    finish_position_steps = max(finish_position_steps, ruler_start_position_steps)
                else:
                    ruler_duration_steps = 0
                    for line_data in ruler_data['lines']:
                        line_duration_steps = LINES_SCALES.note_to_steps(line_data)
                        ruler_duration_steps = max(ruler_duration_steps, line_duration_steps)
                    ruler_finish_position_steps = ruler_start_position_steps + ruler_duration_steps
                    finish_position_steps = max(finish_position_steps, ruler_finish_position_steps)
                
            return self._staff.position(finish_position_steps)

        def get_first_line(self):
            first_line = 0
            if self.len() > 0:
                first_line = self._rulers_list[0]['offset']
                for ruler_data in self._rulers_list:
                    first_line = min(first_line, ruler_data['offset'])
            return first_line

        def get_last_line(self):
            last_line = 0
            if self.len() > 0:
                last_line = self._rulers_list[0]['offset'] + len(self._rulers_list[0]['lines']) - 1
                for ruler_data in self._rulers_list:
                    last_line = max(last_line, ruler_data['offset'] + len(ruler_data['lines']) - 1)
            return last_line

        def get_start_position(self):

            if self.len() > 0:
                start_position_steps = self._staff.steps(self._rulers_list[0]['position'])
                for ruler_data in self._rulers_list:
                    start_position_steps = min(start_position_steps, self._staff.steps(ruler_data['position']))
                
                return self._staff.position(start_position_steps)

            return [0, 0]

        def group(self):
            rulers_list = self.list()
            rulers_length = len(rulers_list)
            if rulers_length > 0:
                for ruler_index in range(rulers_length - 1):
                    rulers_list[ruler_index + 1]['position'] = rulers_list[ruler_index]['position']

            return self

        def head(self, elements=1):
            head_rulers_list = self._rulers_list[:elements]
            return Staff.Rulers(self._staff, head_rulers_list, self._root_self, self._next_id, self._last_action_duration)
        
        def ids(self, *ids):
            return self.filter(ids=ids)

        def insert_lines(self, line, lines=[None], id=None):
            target_rulers = self
            if id != None:
                target_rulers = self.filter(ids=[id])

            for ruler in target_rulers:

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
                    if ruler['type'] == "action":
                        ruler['lines'] = self.action_lines_duration_validator(ruler['lines'])

            return self
       
        def json_dictionnaire(self):
            # cleans the rulers list from any player (objects aren't serializable) (makes it equal to None)
            for ruler_data in self._root_self._rulers_list:
                ruler_data['player'] = None
            return {
                    'part': "rulers",
                    'type': self.__class__.__name__,
                    'rulers_list': self._root_self._rulers_list,
                    'next_id': self._next_id
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
                        rulers_list=dictionnaire['rulers_list'],
                        root_self=None,
                        start_id=dictionnaire['next_id']
                    )
                    on_staff = self.on_staff()
                    on_staff.float()
                    self._staff.clear() # specific staff reset method
                    on_staff.drop()

                    break

            return self

        def json_save(self, file_name="rulers.json"):

            rulers = [ self.json_dictionnaire() ]

            # Writing to sample.json
            with open(file_name, "w") as outfile:
                json.dump(rulers, outfile)

            return self

        def last(self):
            return self.tail(1)

        def len(self):
            return len(self._rulers_list)
        
        def len_lines(self):
            total_lines = 0
            for ruler in self._rulers_list:
                total_lines += len(ruler['lines'])
            return total_lines
        
        def lines(self, *lines):
            return self.filter(lines=lines)

        def lines_data(self, index=0):
            single_ruler = self.single(index)
            lines = {}
            if single_ruler.len() > 0:
                lines['lines'] = single_ruler.list()[0]['lines']
                lines['offset'] = single_ruler.list()[0]['offset']
            return lines

        def link(self, link):
            return self.filter(links=[link])
        
        def link_find(self, name):
            link_name_found = []
            for ruler in self._rulers_list:
                if ruler['link'].find(name) != -1:
                    link_name_found.append(ruler)
            return Staff.Rulers(self._staff, link_name_found, self._root_self, self._next_id, self._last_action_duration)
            
        def link_name_prefix(self, prefix):
            for ruler in self._rulers_list:
                original_link_name = ruler['link']
                prefixed_link_name = prefix + original_link_name
                ruler['link'] = prefixed_link_name
            return self

        def link_name_strip(self, strip):
            for ruler in self._rulers_list:
                original_link_name = ruler['link']
                stripped_link_name = original_link_name.strip(strip)
                ruler['link'] = stripped_link_name
            return self

        def link_name_suffix(self, suffix):
            for ruler in self._rulers_list:
                original_link_name = ruler['link']
                suffixed_link_name = original_link_name + suffix
                ruler['link'] = suffixed_link_name
            return self

        def list(self):
            return self._rulers_list
        
        def list_actions_names(self, enabled=None, actions_names_list=None):
            if actions_names_list == None:
                actions_names_list = []

            actions_rulers = self.filter(type="actions", enabled=enabled, on_staff=True).sort(key='id')
            for ruler in actions_rulers:
                for action_name in ruler['lines']:
                    if action_name != None and action_name not in actions_names_list:
                        actions_names_list.append(action_name)

            return actions_names_list

        def list_lines(self):
            all_lines = []
            for ruler in self._rulers_list:
                all_lines.append(ruler['lines'])
            return all_lines
        
        def measures(self, *measures):
            return self.filter(measures=measures)

        def merge(self, merge_none=False):

            type_links = [] # merge agregates rulers by type and link

            for ruler in self._rulers_list:
                ruler_type_link = {'type': ruler['type'], 'link': ruler['link']}
                if ruler_type_link not in type_links:
                    type_links.append(ruler_type_link)

            merged_rulers = []

            for type_link in type_links:

                subject_rulers_list = self.filter(type=type_link['type'], links=[type_link['link']]).list()
                                    
                head_offset = None
                tail_offset = None
                for ruler in subject_rulers_list:
                    if head_offset == None or ruler['offset'] < head_offset:
                        head_offset = ruler['offset']
                    if tail_offset == None or (len(ruler['lines']) + ruler['offset'] > tail_offset):
                        tail_offset = len(ruler['lines']) - 1 + ruler['offset']

                merged_ruler = {
                    'id': '-',
                    'type': type_link['type'],
                    'link': type_link['link'],
                    'position': subject_rulers_list[0]['position'],
                    'lines': [None] * (tail_offset - head_offset + 1), # list
                    'offset': head_offset,
                    'enabled': subject_rulers_list[0]['enabled'],
                    'on_staff': False,
                    'player': subject_rulers_list[0]['player']
                }
                
                subject_head_offset = None
                subject_tail_offset = None
                for subject_ruler in subject_rulers_list:

                    lines = len(subject_ruler['lines'])
                    actual_subject_head_offset = subject_ruler['offset'] - merged_ruler['offset']
                    actual_subject_tail_offset = actual_subject_head_offset + lines - 1

                    for i in range(lines):
                        merged_line = actual_subject_head_offset + i
                        if (not merge_none and merged_ruler['lines'][merged_line] == None \
                            or merge_none and (subject_head_offset == None or merged_line < subject_head_offset or merged_line > subject_tail_offset)):
                            merged_ruler['lines'][merged_line] = subject_ruler['lines'][i]

                    if subject_head_offset == None:
                        subject_head_offset = actual_subject_head_offset
                        subject_tail_offset = actual_subject_tail_offset
                    else:
                        subject_head_offset = min(subject_head_offset, actual_subject_head_offset)
                        subject_tail_offset = max(subject_tail_offset, actual_subject_tail_offset)

                merged_rulers.append(merged_ruler)

            return Staff.Rulers(self._staff, merged_rulers, self._root_self, self._next_id, self._last_action_duration)
        
        def mirror(self):
            if self.len() > 1:
                first_offset = self.get_first_line()
                last_offset = first_offset
                for ruler_data in self._rulers_list:
                    last_offset = max(last_offset, ruler_data['offset'])
                reversed_offsets_list = list(range(first_offset, last_offset + 1))
                reversed_offsets_list.reverse()
                for ruler_data in self._rulers_list:
                    ruler_data['offset'] = reversed_offsets_list[ruler_data['offset'] - first_offset]

            return self
        
        def move(self, position=[None, None]):
            if isinstance(position, int):
                position = [0, position]

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

                on_staff = self.on_staff()
                on_staff.float()
                for ruler in self._rulers_list:
                    ruler['position'] = self._staff.add_position(ruler['position'], [0, move_steps])
                on_staff.drop()

            return self
        
        def move_lines(self, offset=0):
            for ruler in self._rulers_list:
                ruler['offset'] = offset

            return self
        
        def next_id(self):
            return self._next_id

        def offset(self, offset=1):
            for ruler in self._rulers_list:
                ruler['offset'] += offset

            return self

        def odd(self):
            odd_rulers_list = self._rulers_list[::2]
            return Staff.Rulers(self._staff, odd_rulers_list, self._root_self, self._next_id, self._last_action_duration)
        
        def on_staff(self):
            return self.filter(on_staff=True)

        def populate(self, ruler, span=16):

            link_list = ruler['link'].split(".")
            ruler_type = "arguments"
            if len(link_list) == 1:
                ruler_type = "actions"

            if ruler_type == "arguments":
                return self.add(ruler)

            ruler['lines'] = self.action_lines_duration_validator(ruler['lines'])

            ruler_duration = 0
            if 'lines' in ruler and ruler['lines'] != None and len(ruler['lines']) > 0:
                
                for ruler_line_duration in ruler['lines']:
                    ruler_line_duration_steps = LINES_SCALES.note_to_steps(ruler_line_duration)
                    ruler_duration = max(ruler_duration, ruler_line_duration_steps)

            else:
                ruler_duration = self._last_action_duration

            span_steps = LINES_SCALES.note_to_steps(span)
            ruler_duration_steps = LINES_SCALES.note_to_steps(ruler_duration)

            total_rulers = int(span_steps / ruler_duration_steps)

            for _ in range(total_rulers):
                ruler_copy = ruler.copy()
                ruler_copy['lines'] = ruler['lines'].copy()
                self.add(ruler_copy)

            return self

        def propagate(self, span=16, division=None):
            span = LINES_SCALES.note_to_steps(span)
            if division == None:
                self_start_position_steps = self._staff.steps(self.get_start_position())
                self_finish_position_steps = self._staff.steps(self.get_finish_position())
                division = self_finish_position_steps - self_start_position_steps
            else:
                division = LINES_SCALES.note_to_steps(division)

            total_repeats = int(span / division) - 1
            
            return self.repeat(total_repeats, division)

        def print(self, first_line=None, last_line=None, note_notation=None, full=False):
            
            header_char = "-"
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
                
                string_top_length = {'sequence': 0, 'id': 0, 'link': 0, 'position': 0, 'lines': [0] * total_lines}
                if full:
                    string_top_length = {'sequence': 0, 'id': 0, 'link': 0, 'position': 0, 'type': 0, 'enabled': 0, 'on_staff': 0, 'lines': [0] * total_lines}

                for key in string_top_length.keys():
                    if key != 'lines' and key != 'sequence':
                        string_top_length[key] = len(f"{key}")
                    # elif key == 'lines' and total_lines > 0:
                    #     string_top_length[key][0] = len(f"{key}")

                # TOTALS +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

                full_string_length = 0
                for line_index in range(head_offset, head_offset + len(string_top_length['lines'])):

                    key_value_length = len(f"{line_index}")

                    full_string_length += key_value_length
                    string_top_length['lines'][line_index - head_offset] = max(string_top_length['lines'][line_index - head_offset], key_value_length)

                sequence_index = 1
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

                                        ruler_line_value = ruler['lines'][line_index - ruler['offset']]
                                        if ruler['type'] == "actions":
                                            key_value_str = f"{format_note_duration(ruler_line_value)}" if ruler_line_value != None else "_"
                                        else:
                                            key_value_str = f"{ruler_line_value}" if ruler_line_value != None else "_"

                                        key_value_str = trimString(key_value_str)

                                        key_value_length = len(key_value_str)

                                        string_top_length['lines'][line_index - head_offset] = max(string_top_length['lines'][line_index - head_offset], key_value_length)

                            elif key == 'position':
                                lines_value = self._str_position(ruler['position'])
                                key_value_length = len(f"{lines_value}")

                                string_top_length[key] = max(string_top_length[key], key_value_length)

                            else: # id and link
                                lines_value = ruler[key]

                                key_value_length = len(f"{lines_value}")

                                string_top_length[key] = max(string_top_length[key], key_value_length)

                total_length_headers = 0
                total_length_lines = 0
                total_headers = 0
                total_lines = 0
                for key, value in string_top_length.items():
                    if key == 'lines':
                        for line in value:
                            total_length_lines += line
                            total_lines += 1
                    else:
                        total_length_headers += value
                        total_headers += 1

                # OUTPUT PRINT -----------------------------------------------------------------------------------------------------------------------

                spaces_between = 4

                header_char_length = (total_length_headers + total_length_lines + (total_headers + total_lines) * spaces_between - 2)

                header_type = "  " + self.player.name + "  "
                header_type_length = len(header_type)
                header_left_half_length = int((header_char_length - header_type_length) / 2)
                header_right_half_length = header_left_half_length + (header_char_length - header_type_length) % 2

                print(header_char * header_left_half_length + header_type + header_char * header_right_half_length)

                # HEADER CONTENT

                lines_str = " " * (total_length_headers + total_headers * 4) + "lines"
                
                print (lines_str)
                
                lines_str = ""
                for key, value in string_top_length.items():
                    if key == 'sequence':
                        lines_str += " " * (string_top_length[key] + 4)
                    elif key != 'lines':
                            key_value_str = f"{key}    "
                            key_value_length = len(f"{key}")
                            lines_str += key_value_str + (" " * (string_top_length[key] - key_value_length))
                    
                for line_index in range(head_offset, head_offset + total_lines):

                    key_value_str = f"{line_index}"

                    key_value_length = len(key_value_str)
                    key_value_str += (" " * (string_top_length['lines'][line_index - head_offset] - key_value_length))

                    if line_index != head_offset + total_lines - 1:
                        key_value_str += " " * spaces_between

                    lines_str += key_value_str

                print(lines_str)
                
                print(header_char * header_char_length)

                # BODY CONTENT

                sequence_index = 1
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

                                        ruler_line_value = ruler['lines'][line_index - ruler['offset']]
                                        if ruler['type'] == "actions":
                                            key_value_str = f"{format_note_duration(ruler_line_value)}" if ruler_line_value != None else "_"
                                        else:
                                            key_value_str = f"{ruler_line_value}" if ruler_line_value != None else "_"

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
                                        
                            elif key == 'position':
                                lines_value = self._str_position(ruler['position'])
                                key_value_str = f"{lines_value}    "

                                key_value_length = len(f"{lines_value}")
                                lines_str += key_value_str + (" " * (string_top_length[key] - key_value_length))
                                
                            else: # id and link
                                lines_value = ruler[key]
                                key_value_str = f"{lines_value}    "

                                key_value_length = len(f"{lines_value}")
                                lines_str += key_value_str + (" " * (string_top_length[key] - key_value_length))
                    lines_str += " }"

                    print(lines_str)

                print(header_char * header_char_length)

            else:
                print(header_char * 7)
                print("[EMPTY]")
                print(header_char * 7)
            return self

        def print_resume(self, note_notation=None):
            
            header_char = "'"
            if len(self._rulers_list) > 0:
                string_top_length = {'sequence': 0, 'id': 0, 'link': 0, 'position': 0, 'lines': 0, 'offset': 0, 'type': 0, 'enabled': 0, 'on_staff': 0}
                sequence_index = 1
                for ruler in self._rulers_list: # get maximum sizes
                    
                    for key, value in string_top_length.items():
                        if key == 'sequence':
                            key_value_length = len(f"{sequence_index}")
                            sequence_index += 1
                        else:
                            ruler_value = ""
                            if key == 'position':
                                ruler_value = self._str_position(ruler['position'], note_notation)
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

                header_char_length = full_string_top_length + 94

                header_type = "  " + self.player.name + "  "
                header_type_length = len(header_type)
                header_left_half_length = int((header_char_length - header_type_length) / 2)
                header_right_half_length = header_left_half_length + (header_char_length - header_type_length) % 2

                print(header_char * header_left_half_length + header_type + header_char * header_right_half_length)
                sequence_index = 1
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
                                ruler_value = self._str_position(ruler['position'], note_notation)
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
                print(header_char * header_char_length)

            else:
                print(header_char * 7)
                print("[EMPTY]")
                print(header_char * 7)
            return self

        def quantize(self):
            on_staff = self.on_staff()
            on_staff.float()
            for ruler in self._rulers_list:
                position_steps = self._staff.steps(ruler['position'])
                position_steps = round(position_steps)
                ruler['position'] = self._staff.position(position_steps)
            on_staff.drop()
            return self

        def recall(self):
            return self._root_self._recall_self

        def relink(self, link):
            
            link_list = link.split(".")
            link_type = "arguments"
            if len(link_list) == 1:
                link_type = "actions"

            rulers_type = self.filter(type=link_type)
            for ruler_data in rulers_type:
                ruler_data['link'] = link

            return self

        def remove(self):
            unique_rulers_list = self.unique().list()
            self._staff.remove(unique_rulers_list)
            self._root_self._rulers_list = [ ruler for ruler in self._root_self._rulers_list if ruler not in self._rulers_list ]
            #self._root_self -= self # this will change the root_self to other instance!
            self._rulers_list = []
            return self
        
        def remove_lines(self, line, amount=1):
            
            for ruler in self._rulers_list:

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

                    if new_lines_size > amount and ruler['offset'] == line:
                        ruler['offset'] += amount

                    ruler['lines'] = new_lines

            return self
        
        def repeat(self, times=3, division=None):

            if times > 0:
                repeated_self = self
                for _ in range(times):
                    copy_self = repeated_self.copy()
                    if division == None:
                        repeated_self_finish_position = repeated_self.get_finish_position()
                        repeated_self_finish_position_steps = self._staff.steps(repeated_self_finish_position)
                        copy_self_start_position = copy_self.get_start_position()
                        copy_self_start_position_steps = self._staff.steps(copy_self_start_position)
                        division_position_steps = repeated_self_finish_position_steps - copy_self_start_position_steps
                    else:
                        division_position_steps = LINES_SCALES.note_to_steps(division)
                    for copy_self_ruler in copy_self:
                        copy_self_ruler_position_steps = self._staff.steps(copy_self_ruler['position'])
                        copy_self_ruler['position'] = self._staff.position(copy_self_ruler_position_steps + division_position_steps)
                    repeated_self = copy_self
                    self += repeated_self

            return self

        def reroot(self):
            (self._root_self - self).unique().float()
            self._root_self._rulers_list = self._rulers_list
            return self
        
        def reset(self):
            self._staff.clear()
            for staff_ruler in self._root_self:
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
            on_staff = self.on_staff()
            on_staff.float()
            for index in range(int(rulers_list_size/2)):
                temp_position = self._rulers_list[index]['position']
                self._rulers_list[index]['position'] = self._rulers_list[rulers_list_size - 1 - index]['position']
                self._rulers_list[rulers_list_size - 1 - index]['position'] = temp_position
            on_staff.drop()

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

            on_staff = self.on_staff()
            on_staff.float()
            for ruler_index in range(rulers_size):
                rotated_index = (ruler_index + increments) % rulers_size
                self._rulers_list[ruler_index]['position'] = original_positions[rotated_index]
            on_staff.drop()

            return self.rotate(increments)
        
        def set_line(self, line, value):
            for ruler_data in self._rulers_list:
                ruler_first_line = ruler_data['offset']
                ruler_last_line = ruler_first_line + len(ruler_data['lines']) - 1
                if not (line < ruler_first_line or line > ruler_last_line):
                    ruler_data['lines'][line] = value

            return self

        def set_lines(self, lines, offset=None):

            if type(lines) != type([]) and type(lines) != type({}):
                lines = [ lines ]
            elif type(lines) == type({}):
                offset = lines['offset']
                lines = lines['lines']

            for ruler in self._rulers_list:
                ruler['lines'] = lines
                if offset != None:
                    ruler['offset'] = offset
                if ruler['type'] == "action":
                    ruler['lines'] = self.action_lines_duration_validator(ruler['lines']) # replaces by dots!
                
            return self

        def set_position(self, position=[None, None]):
            if position[0] != None and position[1] != None:
                on_staff = self.on_staff()
                on_staff.float()
                for ruler in self._rulers_list:
                    ruler['position'] = position
                on_staff.drop()

            return self
        
        def set_staff(self, staff):
            self._staff = staff
            return self

        def single(self, index=0):
            if (self.len() > index):
                ruler_list = [ self._rulers_list[index] ]
                return Staff.Rulers(self._staff, ruler_list, self._root_self, self._next_id, self._last_action_duration)
            return self

        def slide(self, distance=4, division=None):

            distance_steps = LINES_SCALES.note_to_steps(distance)


            # if division != None:
            #     division = LINES_SCALES.note_to_steps(division)
            #     if division >= distance_steps:
            #         if distance_steps > 0:
            #             distance_steps %= division
            #         elif distance_steps < 0:


            if distance_steps != 0:

                if division != None:
                    division_steps = LINES_SCALES.note_to_steps(division)
                    division_divisions = self._staff.step_divisions(division_steps)
                    time_signature = self._staff.time_signature()
                    if division_divisions['measure'] > 0:
                        division_quantized = division_divisions['measure'] * time_signature['steps_per_measure']
                    elif division_divisions['beat'] > 0:
                        division_quantized = division_divisions['beat'] * time_signature['steps_per_quarternote']
                    else:
                        division_quantized = division_steps

                    distance_steps %= division_quantized

                if distance_steps > 0:
                    last_position_steps = self._staff.len() - 1
                    for ruler in self._rulers_list:
                        ruler_position_steps = self._staff.steps(ruler['position'])
                        distance_steps = min(distance_steps, last_position_steps - ruler_position_steps)
                elif distance_steps < 0:
                    for ruler in self._rulers_list:
                        ruler_position_steps = -self._staff.steps(ruler['position'])
                        distance_steps = max(distance_steps, ruler_position_steps)
                else:
                    return self
                
                on_staff = self.on_staff()
                on_staff.float()

                for ruler in self._rulers_list:
                    new_position_steps = self._staff.steps(ruler['position']) + distance_steps # always positive
                    ruler['position'] = self._staff.position(steps=new_position_steps)

                on_staff.drop()

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

        def spread(self, increments=1):
            rulers_list_size = self.len()
            for ruler_index in range(rulers_list_size):
                self._rulers_list[ruler_index]['offset'] += ruler_index * increments

            return self

        def stack(self, slack=0):
            slack = LINES_SCALES.note_to_steps(slack)
            actions_rulers_list = self.actions().list()
            actions_rulers_length = len(actions_rulers_list)
            if actions_rulers_length > 0:
                actions_stack_position = actions_rulers_list[0]['position']
                for actions_ruler_index in range(actions_rulers_length - 1):
                    actions_ruler_start_position = actions_rulers_list[actions_ruler_index]['position']
                    actions_ruler_duration_steps = 0
                    for line_duration in actions_rulers_list[actions_ruler_index]['lines']:
                        line_duration_steps = LINES_SCALES.note_to_steps(line_duration)
                        actions_ruler_duration_steps = max(actions_ruler_duration_steps, line_duration_steps)
                    actions_ruler_finish_position = self._staff.add_position(actions_ruler_start_position, [0, actions_ruler_duration_steps])
                    actions_ruler_next_position = self._staff.add_position(actions_ruler_finish_position, [0, slack])

                    actions_rulers_list[actions_ruler_index + 1]['position'] = actions_ruler_next_position

                arguments_start_position = self._staff.add_position(actions_stack_position, [0, slack])
                for arguments_ruler_data in self.arguments():
                    arguments_ruler_data['position'] = arguments_start_position

            return self

        def steps(self, *steps):
            return self.filter(steps=steps)

        def tail(self, elements=1):
            tail_rulers_list = self._rulers_list[-elements:]
            return Staff.Rulers(self._staff, tail_rulers_list, self._root_self, self._next_id, self._last_action_duration)

        def type(self, type="arguments"):
            return self.filter(type=type)

        def unique(self):
            unique_rulers_list = []
            for ruler in self._rulers_list:
                if ruler not in unique_rulers_list:
                    unique_rulers_list.append(ruler)

            return Staff.Rulers(self._staff, unique_rulers_list, self._root_self, self._next_id, self._last_action_duration)
        
        def zone_dictionary(positions=[], position_range=[], lines=[], measures=[], beats=[], steps=[]):
            return {
                'positions': positions,
                'position_range': position_range,
                'lines': lines,
                'measures': measures,
                'beats': beats,
                'steps': steps
            }
        
        def zone(self, zone_dictionary):
            return self.filter(
                positions=zone_dictionary['positions'],
                position_range=zone_dictionary['position_range'],
                lines=zone_dictionary['lines'],
                measures=zone_dictionary['measures'],
                beats=zone_dictionary['beats'],
                steps=zone_dictionary['steps']
            )

    class RulersNone(Rulers):

        def __init__(self, staff):
            super().__init__(staff)

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

        for staff_pulse in self._staff_list: # get maximum sizes
            for key, value in staff_pulse.items():
                if key == 'measure' or key == 'beat' or key == 'step' or key == 'pulse':
                    self.string_top_lengths[key] = max(self.string_top_lengths[key], len(f"{value}"))

        self.string_top_length = 0
        for value in self.string_top_lengths.values():
            self.string_top_length += value

        return self
    
    def _setTopLengths_Sums(self):

        staff_list_sums = self._getStaffSums(self._staff_list)
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
        for staff_pulse in self._staff_list:
            total_actions['enabled'] += staff_pulse['actions']['enabled']
            total_actions['total'] += staff_pulse['actions']['total']
        return total_actions

    def add(self, rulers, enabled_one=1, total_one=1):
        for ruler in rulers:
            pulses = self.pulses(ruler['position'])
            if pulses < self.len():
                if total_one == 1 and ruler['on_staff'] == False:
                    ruler['on_staff'] = True
                    self._staff_list[pulses][ruler['type']]['total'] += total_one
                if ruler['on_staff']:
                    if ruler['enabled']:
                        self._staff_list[pulses][ruler['type']]['enabled'] += enabled_one
                    if total_one == -1:
                        ruler['on_staff'] = False
                        self._staff_list[pulses][ruler['type']]['total'] += total_one
            else:
                ruler['on_staff'] = False
        
        return self._setTopLengths_Sums()
    
    def add_position(self, left_position=[0, 0], right_position=[0, 0]):
        left_position[1] = LINES_SCALES.note_to_steps(left_position[1])
        right_position[1] = LINES_SCALES.note_to_steps(right_position[1])
        left_position_steps = self.steps(left_position)
        right_position_steps = self.steps(right_position)
        total_steps = left_position_steps + right_position_steps
        
        return self.position(steps=total_steps)

    def arguments(self):
        total_arguments = {'enabled': 0, 'total': 0}
        for staff_pulse in self._staff_list:
            total_arguments['enabled'] += staff_pulse['arguments']['enabled']
            total_arguments['total'] += staff_pulse['arguments']['total']
        return total_arguments

    def clear(self):
        for staff_pulse in self._staff_list:
            staff_pulse['arguments'] = {'enabled': 0, 'total': 0}
            staff_pulse['actions'] = {'enabled': 0, 'total': 0}

        return self._setTopLengths_Sums()

    def disabled(self, rulers):
        return self.remove(rulers, total_one=0)
    
    def enabled(self, rulers):
        return self.add(rulers, total_one=0)

    def filterList(self, measure=None, beat=None, step=None, pulse=None, list=None):
        if list != None:
            filtered_list = list[:]
            if pulse != None:
                filtered_list = [
                    pulses for pulses in filtered_list if pulses['pulse'] == pulse
                ]
        else:
            if pulse != None:
                filtered_list = [ self.pulse_data(pulse) ]
            else:
                filtered_list = self._staff_list[:]

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
        return filtered_list

    def getRulers(self):
        return self._rulers

    def json_dictionnaire(self):
        return {
                'part': "staff",
                'type': self.__class__.__name__,
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
                measures = dictionnaire['time_signature']['measures']
                beats_per_measure = dictionnaire['time_signature']['beats_per_measure']
                beats_per_note = dictionnaire['time_signature']['beats_per_note']
                steps_per_quarternote = dictionnaire['time_signature']['steps_per_quarternote']
                pulses_per_quarternote = dictionnaire['time_signature']['pulses_per_quarternote']
                play_range = dictionnaire['play_range']
                
                self.clear()

                self.set_range(start=play_range[0], finish=play_range[1])
                self.set(measures, beats_per_measure, beats_per_note, steps_per_quarternote, pulses_per_quarternote)
            
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
        return round(self._total_pulses / self._time_signature['pulses_per_step'])
    
    def list(self):
        return self._staff_list
    
    def playRange(self):
        return self._play_range

    def playRange_pulses(self, play_range=[[], []]):
        if play_range == [[], []]:
            return [self.pulses(self._play_range[0]), self.pulses(self._play_range[1])]
        return [self.pulses(play_range[0]), self.pulses(play_range[1])]

    def position(self, steps=None, pulses=None):
        if (steps != None):
            step_divisions = self.step_divisions(steps)
            return [step_divisions['measure'], step_divisions['step']]
        elif (pulses != None):
            pulse_divisions = self.pulse_divisions(pulses)
            return [pulse_divisions['measure'], pulse_divisions['step']]
        return [0, 0]
    
    def position_on_staff(self, position):
        position_pulses = self.pulses(position)
        if position_pulses < self._total_pulses:
            return True
        return False

    def print(self):
        if len(self._staff_list) > 0:
            if len(self._staff_list) > 1:
                print("§" * (self.string_top_length + 128))

            for staff_pulse in self._staff_list:
                self.printSinglePulse(staff_pulse['pulse'])

            if len(self._staff_list) > 1:
                print("§" * (self.string_top_length + 128))
        else:
            print("[EMPTY]")
        return self
    
    def printSinglePulse(self, pulse=0, sums='pulse', extra_string=""):

        spaces_between = 6

        staff_pulse = self._staff_list[pulse]
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

    def pulse_data(self, pulse):
        pulse = min(len(self._staff_list) - 1, pulse)
        return self._staff_list[pulse]

    def pulse_divisions(self, pulse=0):
        return {
            'measure': int(pulse / self._time_signature['pulses_per_measure']),
            'beat': int(pulse / self._time_signature['pulses_per_beat']) % self._time_signature['beats_per_measure'],
            'step': int(pulse / self._time_signature['pulses_per_step']) % self._time_signature['steps_per_measure'],
            'pulse': pulse # by definition pulse is pulse
        }
    
    def pulseRemainders(self, pulse=0):
        return {
            'measure': pulse % self._time_signature['pulses_per_measure'],
            'beat': pulse % self._time_signature['pulses_per_beat'],
            'step': pulse % self._time_signature['pulses_per_step'],
            'pulse': 0 # by definition is pulse % pulse = 0
        }
    
    def pulseSums(self, pulse=0, sums='pulse'):
        pulse_sums = {'arguments': {'enabled': 0, 'total': 0}, 'actions': {'enabled': 0, 'total': 0}}

        measure = self._staff_list[pulse]['measure']
        beat = self._staff_list[pulse]['beat']
        step = self._staff_list[pulse]['step']

        match sums:
            case 'measure':
                measure = self._staff_list[pulse]['measure']
                filtered_list = self.filterList(measure=measure)
            case 'beat':
                measure = self._staff_list[pulse]['measure']
                beat = self._staff_list[pulse]['beat']
                filtered_list = self.filterList(measure=measure, beat=beat)
            case 'step':
                measure = self._staff_list[pulse]['measure']
                step = self._staff_list[pulse]['step']
                filtered_list = self.filterList(measure=measure, beat=beat, step=step)
            case default:
                filtered_list = [ self._staff_list[pulse] ]

        for staff_pulse in filtered_list:
            pulse_sums['arguments']['enabled'] += staff_pulse['arguments']['enabled']
            pulse_sums['arguments']['total'] += staff_pulse['arguments']['total']
            pulse_sums['actions']['enabled'] += staff_pulse['actions']['enabled']
            pulse_sums['actions']['total'] += staff_pulse['actions']['total']

        return pulse_sums
    
    def pulses(self, position=[0, 0]): # position: [measure, step]
        return position[0] * self._time_signature['pulses_per_measure'] + round(LINES_SCALES.note_to_steps(position[1]) * self._time_signature['pulses_per_step'])

    def remove(self, rulers, enabled_one=-1, total_one=-1):
        return self.add(rulers, enabled_one, total_one)
    
    def rulers(self):
        return self._rulers

    def set(self, measures=None, beats_per_measure=None, beats_per_note=None, steps_per_quarternote=None, pulses_per_quarternote=None):

        self._rulers.float() # starts by floating all Rulers (makes on_staff = False)

        if self._time_signature == {}:
            self._time_signature['measures'] = measures
            if measures == None:
                self._time_signature['measures'] = 8
            self._time_signature['beats_per_measure'] = beats_per_measure
            if beats_per_measure == None:
                self._time_signature['beats_per_measure'] = 4
            if beats_per_note == None:
                self._time_signature['beats_per_note'] = 4
            self._time_signature['steps_per_quarternote'] = steps_per_quarternote
            if steps_per_quarternote == None:
                self._time_signature['steps_per_quarternote'] = 4
            self._time_signature['pulses_per_quarternote'] = pulses_per_quarternote
            if pulses_per_quarternote == None:
                self._time_signature['pulses_per_quarternote'] = 24
        else:
            if measures != None:
                self._time_signature['measures'] = int(max(1, measures))                                                    # staff total size
            if beats_per_measure != None:
                self._time_signature['beats_per_measure'] = int(max(1, beats_per_measure))                                  # beats in each measure
            if beats_per_note != None:
                self._time_signature['beats_per_note'] = int(max(1, beats_per_note))                                        # beats in each note
            if steps_per_quarternote != None:
                self._time_signature['steps_per_quarternote'] = 1 if steps_per_quarternote == 0 else steps_per_quarternote  # how many steps take each beat
            if pulses_per_quarternote != None:
                self._time_signature['pulses_per_quarternote'] = pulses_per_quarternote                                     # sets de resolution of clock pulses

        self._time_signature['steps_per_beat'] = round(self._time_signature['steps_per_quarternote'] / (self._time_signature['beats_per_note'] / 4))
        self._time_signature['steps_per_measure'] = self._time_signature['steps_per_beat'] * self._time_signature['beats_per_measure']
        self._time_signature['pulses_per_beat'] = round(self._time_signature['pulses_per_quarternote'] / (self._time_signature['beats_per_note'] / 4))
        self._time_signature['pulses_per_measure'] = self._time_signature['pulses_per_beat'] * self._time_signature['beats_per_measure']
        self._time_signature['pulses_per_step'] = round(self._time_signature['pulses_per_quarternote'] / self._time_signature['steps_per_quarternote'])

        self._total_pulses = round(self._time_signature['measures'] * self._time_signature['pulses_per_measure'])

        self._staff_list = []
        for pulse in range(self._total_pulses):
            staff_pulse = self.pulse_divisions(pulse)
            staff_pulse['arguments'] = {'enabled': 0, 'total': 0}
            staff_pulse['actions'] = {'enabled': 0, 'total': 0}
            self._staff_list.append(staff_pulse)

        self._rulers.drop() # ends by dropping all Rulers
        return self.set_range()._setTopLengths()
    
    def set_range(self, start=None, finish=None):
        if self._total_pulses > 0:
            if start == None or start == [] or self._play_range[0] == []:
                self._play_range[0] = [0, 0]
            elif start != None:
                start_pulses = max(0, min(self._total_pulses, self.pulses(start)))
                self._play_range[0] = self.position(pulses=start_pulses)


            if finish == None or finish == [] or self._play_range[1] == []:
                finish_pulses = self._total_pulses
                self._play_range[1] = self.position(pulses=finish_pulses)
            elif finish != None:
                start_pulses = self.pulses(self._play_range[0])
                finish_pulses = max(start_pulses, min(self._total_pulses, self.pulses(finish)))
                self._play_range[1] = self.position(pulses=finish_pulses)

        return self
    
    def setRulers(self, rulers):
        self._rulers = rulers
        return self

    def step_divisions(self, step=0):
        return {
            'measure': int(step / self._time_signature['steps_per_measure']),
            'beat': int(step / self._time_signature['steps_per_beat']) % self._time_signature['beats_per_measure'],
            'step': step % self._time_signature['steps_per_measure']
        }
    
    def steps(self, position=[0, 0]): # position: [measure, step]
        position[1] = LINES_SCALES.note_to_steps(position[1])
        return position[0] * self._time_signature['steps_per_measure'] + position[1]

    def str_position(self, position):
        return str(position[0]) + " " + str(round(position[1], 6))

    def time_signature(self):
        return self._time_signature
    
        # self._time_signature = {
        #     'measures'                    # staff total size
        #     'beats_per_measure'           # beats in each measure
        #     'beats_per_note'              # beats in each measure
        #     'steps_per_quarternote'       # how many steps take each beat
        #     'pulses_per_quarternote'      # sets de resolution of clock pulses

        #     'steps_per_beat'
        #     'steps_per_measure'
        #     'pulses_per_beat'
        #     'pulses_per_measure'
        #     'pulses_per_step'

        # }

class StaffNone(Staff):

    def __init__(self, player):
        super().__init__(player)

        self._rulers = self.RulersNone(self)

# GLOBAL CLASS METHODS

def trimString(full_string):
    string_maxum_size = 16
    long_string_termination = "…"
    trimmed_string = full_string
    if full_string != None and len(full_string) > string_maxum_size:
        trimmed_string = full_string[:string_maxum_size] + long_string_termination
    return trimmed_string

def position_gt(left_position, right_position):
    if len(left_position) == 2 and len(right_position) == 2:
        if (left_position[0] > right_position[0]):
            return True
        if (left_position[0] == right_position[0]):
            if (LINES_SCALES.note_to_steps(left_position[1]) > LINES_SCALES.note_to_steps(right_position[1])):
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

# def converter_PPQN_PPB(pulses_per_quarternote=24, steps_per_quarternote=4): # 4 steps per beat is a constant
#     '''Converts Pulses Per Quarter Note into Pulses Per Beat'''
#     STEPS_PER_QUARTER_NOTE = 4
#     pulses_per_beat = pulses_per_quarternote * (steps_per_quarternote / STEPS_PER_QUARTER_NOTE)
#     return int(pulses_per_beat)

def format_note_duration(note, note_notation=None):
    note_steps = LINES_SCALES.note_to_steps(note)
    if not isinstance(note, str) or (note_notation != None and not note_notation):
        return note_steps
    if isinstance(note, str) or note_notation:
        # test reversity
        steps_to_note = LINES_SCALES.steps_to_note(note_steps)
        note_to_steps = LINES_SCALES.note_to_steps(steps_to_note)
        if note_to_steps == note_steps and note_steps < 16:
            return steps_to_note
        return steps_to_note + "/1"
    if isinstance(note, str):
        return note + "/1"
    
    return note

def overlapping_lists(left_list, right_list):
    for left_element in left_list:
        for right_element in right_list:
            if left_element == right_element:
                return True
    return False
