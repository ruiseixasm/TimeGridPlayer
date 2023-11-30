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
import player as PLAYER

class Group:

    def __init__(self, player, players_list=None, root_self=None):

        self._players_list = []
        if players_list != None:
            self._players_list = players_list
        self._root_self = self
        if root_self != None:
            self._root_self = root_self
        self._player = player # When working as lower group, None when main group

        self.current_player = 0

    @property
    def is_none(self):
        return (self.__class__ == GroupNone)

    def __iter__(self):
        return self
    
    def __next__(self):
        if self.current_player < len(self._players_list):
            result = self._players_list[self.current_player]
            self.current_player += 1
            return result
        else:
            self.current_player = 0  # Reset to 0 when limit is reached
            raise StopIteration
        
    # + Operator Overloading in Python
    def __add__(self, other):
        '''Works as Union'''
        self_players_list = self.list()
        other_players_list = other.list()

        return Group(self._player, self_players_list + other_players_list, self._root_self)
    
    def __sub__(self, other):
        '''Works as exclusion'''
        self_players_list = self.list()
        other_players_list = other.list()

        exclusion_list = [ player for player in self_players_list if player not in other_players_list ]

        # exclusion_list = []

        # for self_player in self_players_list:
        #     excluded_player = True
        #     for other_player in other_players_list:
        #         if self_player['type'] == other_player['type'] and self_player['name'] == other_player['name']:
        #             excluded_player = False
        #             break
        #     if excluded_player:
        #         exclusion_list.append(self_player)

        return Group(self._player, exclusion_list, self._root_self)
    
    def __mul__(self, other):
        '''Works as intersection'''
        self_players_list = self.list()
        other_players_list = other.list()
        
        intersection_list = [ player for player in self_players_list if player in other_players_list ]

        # intersection_list = []

        # for self_player in self_players_list:
        #     intersected_player = False
        #     for other_player in other_players_list:
        #         if self_player['type'] == other_player['type'] and self_player['name'] == other_player['name']:
        #             intersected_player = True
        #             break
        #     if intersected_player:
        #         intersection_list.append(self_player)

        return Group(self._player, intersection_list, self._root_self)
    
    def __div__(self, other):
        '''Works as divergence'''
        union_players = self.__add__(other)
        intersection_players = self.__mul__(other)

        return union_players - intersection_players
    
    def add(self, player):

        if player != self._player:

            stage = self._player.stage

            player_data = stage.filter(player=player).list()[0]

            if self._root_self == self._player.lower_group: # add as lower player

                all_upper_self_group = self._player.upper_group.all_players_group()
                player_upper_self_group = all_upper_self_group.filter(player=player)
                if player_upper_self_group.len() > 0:
                    print (f"Player '{player}' already an upper Player of Player '{self._player}'!")
                    return self

                all_lower_player_group = player.lower_group.all_players_group()
                player_lower_player_group = all_lower_player_group.filter(player=self._player)
                if player_lower_player_group.len() > 0:
                    print (f"Player '{self._player}' already a lower Player of Player '{player}'!")
                    return self

                player_already_added = self._player.lower_group.filter(player=player)
                if player_already_added.len() == 0 and not player.is_none:
                    
                    # Updates self LOWER Group (self)
                    self._root_self._players_list.append(player_data)
                    if self != self._root_self:
                        self._players_list.append(player_data)
                    # Updates player UPPER Group
                    player.upper_group.add(self._player)

            elif self._root_self == self._player.upper_group: #  # add as upper player
                
                all_lower_self_group = self._player.lower_group.all_players_group()
                player_lower_self_group = all_lower_self_group.filter(player=player)
                if player_lower_self_group.len() > 0:
                    print (f"Player '{player}' already a lower Player of Player '{self._player}'!")
                    return self

                all_upper_player_group = player.upper_group.all_players_group()
                player_upper_player_group = all_upper_player_group.filter(player=self._player)
                if player_upper_player_group.len() > 0:
                    print (f"Player '{self._player}' already an upper Player of Player '{player}'!")
                    return self

                player_already_added = self._player.upper_group.filter(player=player)
                if player_already_added.len() == 0 and not player.is_none:
                    
                    # Updates self UPPER Group (self)
                    self._root_self._players_list.append(player_data)
                    if self != self._root_self:
                        self._players_list.append(player_data)
                    # Updates player LOWER Group
                    player.lower_group.add(self._player)

        return self
    
    def all_players_count(self):
        
        if self._root_self == self._player.lower_group: # lower players

            all_players = 0 # += operator bellow already does a copy

            if self.len() > 0:
                for player in self:
                    all_players += player['player'].lower_group.all_players_count() + 1

        elif self._root_self == self._player.upper_group: # upper players

            all_players = 0 # += operator bellow already does a copy

            if self.len() > 0:
                for player in self:
                    all_players += player['player'].upper_group.all_players_count() + 1

        return all_players # Last LEAF group is an empty group

    def all_players_group(self):
        
        if self._root_self == self._player.lower_group: # lower players

            all_players = self # += operator bellow already does a copy

            if self.len() > 0:
                for player in self:
                    all_players += player['player'].lower_group.all_players_group()

        elif self._root_self == self._player.upper_group: # upper players

            all_players = self # += operator bellow already does a copy

            if self.len() > 0:
                for player in self:
                    all_players += player['player'].upper_group.all_players_group()

        return all_players # Last LEAF group is an empty group

    def disable(self):
        for player in self._players_list:
            player['enabled'] = False

        return self

    def disabled(self):
        if len(self._players_list) > 0:
            return not self._players_list[0]['enabled']
        return False
    
    def enable(self):
        for player in self._players_list:
            player['enabled'] = True

        return self

    def enabled(self):
        if len(self._players_list) > 0:
            return self._players_list[0]['enabled']
        return False
    
    def filter(self, ids = [], types = [], names = [], player = None, enabled = None):

        filtered_players = self._players_list.copy()

        if (len(ids) > 0 and ids != [None]):
            filtered_players = [
                filtered_player for filtered_player in filtered_players if filtered_player['id'] in ids
            ]
        if (len(types) > 0 and types != [None]):
            filtered_players = [
                filtered_player for filtered_player in filtered_players if filtered_player['type'] in types
            ]
        if (len(names) > 0 and names != [None]):
            filtered_players = [
                filtered_player for filtered_player in filtered_players if filtered_player['name'] in names
            ]
        if (player != None):
            filtered_players = [
                filtered_player for filtered_player in filtered_players if filtered_player['player'] == player
            ]
        if (enabled != None):
            filtered_players = [
                filtered_player for filtered_player in filtered_players if filtered_player['enabled'] == enabled
            ]

        return Group(self._player, filtered_players, self._root_self)

    def json_dictionnaire(self):
        group = {
                'part': "group",
                'type': self._root_self.__class__.__name__,
                'players': []
            }
        
        for player_dictionnaire in self._root_self._players_list:
            player_json = {}
            player_json['id'] = player_dictionnaire['id']
            player_json['type'] = player_dictionnaire['type']
            player_json['name'] = player_dictionnaire['name']
            player_json['enabled'] = player_dictionnaire['enabled']
            group['players'].append( player_json )

        return group
    
    def json_load(self, file_name="group.json", json_object=None, stage=None):

        if json_object == None:
            # Opening JSON file
            with open(file_name, 'r') as openfile:
                # Reading from json file
                json_object = json.load(openfile)

        self._root_self._players_list.clear()

        for group_dictionnaire in json_object:
            if group_dictionnaire['part'] == "group":
                # where each Player is loaded
                for player_dictionnaire in group_dictionnaire['players']:
                    player_type = player_dictionnaire['type']
                    player_name = player_dictionnaire['name']
                    if stage != None:
                        player_staged = stage.filter(types=[player_type], names=[player_name])
                        if player_staged.len() > 0:
                            player = player_staged.list()[0]['player']
                            if player != None:
                                player_data = {
                                    'id': player_dictionnaire['id'],
                                    'type': player_type,
                                    'name': player_name,
                                    'player': player,
                                    'enabled': player_dictionnaire['enabled']
                                }
                                self._root_self._players_list.append(player_data)
                break

        return self

    def json_save(self, file_name="group.json"):

        group = [ self.json_dictionnaire() ]

        # Writing to sample.json
        with open(file_name, "w") as outfile:
            json.dump(group, outfile)

        return self

    def len(self):
        return len(self._players_list)
            
    def list(self):
        return self._players_list
    
    def play(self, start=None, finish=None, id=None):
        if len(self._players_list) > 0:
            if id != None:
                group_player = self.filter(ids = [id], enabled=True)
                if group_player.len() > 0:
                    group_player.list()[0]['player'].play(start=start, finish=finish, enabled_lower_group_players=self.filter(enabled=True))
            elif self._players_list[0]['enabled']:
                self._players_list[0]['player'].play(start=start, finish=finish, enabled_lower_group_players=self.filter(enabled=True))
        return self
            
    def player(self):
        if len(self._players_list) > 0:
            return self._players_list[0]['player']
        return PLAYER.PlayerNone(self._player.stage)

    def print(self):

        header_char = "^"
        if len(self._players_list) > 0:
            string_top_length = {'sequence': 0, 'id': 0, 'type': 0, 'name': 0, 'description': 0, 'sub-players': 0, 'enabled': 0}
            sequence_index = 0
            for player in self: # get maximum sizes
                
                for key, value in string_top_length.items():
                    if key == 'sequence':
                        key_value_length = len(f"{sequence_index}")
                        sequence_index += 1
                    elif key == 'type':
                        key_value_length = len(f"{player['player'].__class__.__name__}")
                    elif key == 'description':
                        key_value_length = len(f"{player['player'].description}")
                    elif key == 'sub-players':
                        key_value_length = len(f"{player['player'].lower_group.all_players_count()}")
                    else:
                        key_value_length = len(f"{player[key]}")

                    string_top_length[key] = max(string_top_length[key], key_value_length)

            full_string_top_length = 0
            for value in string_top_length.values():
                full_string_top_length += value

            spaces_between = 4
            header_char_length = full_string_top_length + 77

            header_type = "   " + self.__class__.__name__ + "   "
            header_type_length = len(header_type)
            header_left_half_length = int((header_char_length - header_type_length) / 2)
            header_right_half_length = header_left_half_length + (header_char_length - header_type_length) % 2

            print(header_char * header_left_half_length + header_type + header_char * header_right_half_length)
            sequence_index = 0
            for player in self._players_list:

                player_str = ""
                for key, value in string_top_length.items():
                    if key == 'sequence':
                        key_value_str = f"{sequence_index}"
                        key_value_str = (" " * (string_top_length[key] - len(key_value_str))) + key_value_str + ": { "
                        sequence_index += 1
                    else:
                        key_value_str = ""
                        if key == 'type':
                            key_value_str = f"{player['player'].__class__.__name__}"
                        elif key == 'description':
                            key_value_str = trimString(f"{player['player'].description}")
                        elif key == 'sub-players':
                            key_value_str = f"{player['player'].lower_group.all_players_count()}"
                        else:
                            key_value_str = f"{player[key]}"

                        if key == 'sub-players':
                            key_value_str = f"{key}: " + (" " * (string_top_length[key] - len(key_value_str))) + key_value_str
                        else:
                            key_value_str = f"{key}: " + key_value_str + (" " * (string_top_length[key] - len(key_value_str)))

                        if key != 'enabled':
                            key_value_str += " " * spaces_between

                    player_str +=  key_value_str
                player_str += " }"
                print(player_str)
            print(header_char * header_char_length)

        else:
            header_type = self.__class__.__name__
            header_type_length = len(header_type)
            print(header_char * (7 + 1 + header_type_length))
            print(f"[EMPTY] {header_type}")
            print(header_char * (7 + 1 + header_type_length))
        return self

    def remove(self):
        
        if self._root_self == self._player.lower_group: # remove lower player

            for player_to_remove in self._players_list[:]: # as copy
                self._root_self._players_list.remove(player_to_remove)
                if self != self._root_self:
                    self._players_list.remove(player_to_remove)
                upper_player_to_remove_group = player_to_remove['player'].upper_group.filter(player=self._player)
                if upper_player_to_remove_group.len() > 0:
                    upper_player_to_remove_group.remove()

        elif self._root_self == self._player.upper_group: # remove upper player

            for player_to_remove in self._players_list[:]: # as copy
                self._root_self._players_list.remove(player_to_remove)
                if self != self._root_self:
                    self._players_list.remove(player_to_remove)
                lower_player_to_remove_group = player_to_remove['player'].lower_group.filter(player=self._player)
                if lower_player_to_remove_group.len() > 0:
                    lower_player_to_remove_group.remove()

        return self

    def unique(self):
        unique_rulers_list = []
        for player in self._players_list:
            if player not in unique_rulers_list:
                unique_rulers_list.append(player)

        return Group(self._player, unique_rulers_list, self._root_self)
        
class GroupNone(Group):

    def __init__(self):
        super().__init__()

# GLOBAL CLASS METHODS

def trimString(full_string):
    string_maxum_size = 60
    long_string_termination = "…"
    trimmed_string = full_string
    if len(full_string) > string_maxum_size:
        trimmed_string = full_string[:string_maxum_size] + long_string_termination
    return trimmed_string
