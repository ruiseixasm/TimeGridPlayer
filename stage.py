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

# import os
# import win32api         # pip install pywin32
# import win32process
# import win32con

import json
import resources as RESOURCES
import player as PLAYER

class Stage:
    
    def __init__(self, players_list=None, root_self=None, start_id=0):

        self._players_list = []
        if players_list != None:
            self._players_list = players_list
        self._root_self = self
        if root_self != None:
            self._root_self = root_self

        self._resources = RESOURCES.Resources()

        self._next_id = start_id
        self.current_player = 0

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
        
    def playerFactoryMethod(self, name, description=None, resources=None, type=None):
        if resources == None:
            if description == None:
                return PLAYER.Player(self, name, resources=self._resources)
            return PLAYER.Player(self, name, description, self._resources)
        if description == None:
            return PLAYER.Player(self, name, resources=resources)
        return PLAYER.Player(self, name, description, resources)

    def add(self, name, description=None, resources=None, type=None):
        if type == None:
            type = "Player"
        existent_player = self._root_self.filter(names=[name]) # name is the identifier
        if existent_player.len() == 0:
            player = self.playerFactoryMethod(name, description, resources, type) # Factory Method
            player_data = {
                'id': self._next_id,
                'type': player.__class__.__name__,
                'name': player.name,
                'player': player,
                'enabled': True
            }

            self._root_self._next_id += 1
            self._root_self._players_list.append(player_data)
            if self != self._root_self:
                self._players_list.append(player_data)
                self._next_id = self._root_self._next_id

        return self
    
    def disable(self):
        for player_data in self._players_list:
            player_data['enabled'] = False
        return self

    def enable(self):
        for player_data in self._players_list:
            player_data['enabled'] = True
        return self

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

        return Stage(filtered_players, self._root_self, self._next_id)

    def json_dictionnaire(self):
        stage = {
                'part': "stage",
                'type': self._root_self.__class__.__name__,
                'next_id': self._root_self._next_id,
                'players': []
            }
        
        for player_dictionnaire in self._root_self._players_list:
            player_json = player_dictionnaire['player'].json_dictionnaire()
            player_json['id'] = player_dictionnaire['id']
            player_json['enabled'] = player_dictionnaire['enabled']
            stage['players'].append( player_json )

        return stage
    
    def json_load(self, file_name="stage.json", json_object=None):

        if json_object == None:
            # Opening JSON file
            with open(file_name, 'r') as openfile:
                # Reading from json file
                json_object = json.load(openfile)

        for player_data in self._root_self._players_list:
            player_data['player'].discard_resource()

        self._root_self._players_list.clear()

        for stage_dictionnaire in json_object:
            if stage_dictionnaire['part'] == "stage":
                self._root_self._next_id = stage_dictionnaire['next_id']
                for player_dictionnaire in stage_dictionnaire['players']:
                    player_type = player_dictionnaire['type']
                    player_name = player_dictionnaire['name']
                    description = player_dictionnaire['description']
                    player = self._root_self.playerFactoryMethod(type=player_type, name=player_name, description=description)

                    if player != None:

                        # Enables Resources as needed
                        if player_dictionnaire['resource_name'] != None:
                            player.use_resource(player_dictionnaire['resource_name'])
                            if player_dictionnaire['resource_enabled']:
                                player.enable_resource()

                        player_data = {
                            'id': player_dictionnaire['id'],
                            'type': player_type,
                            'name': player_name,
                            'player': player,
                            'enabled': player_dictionnaire['enabled']
                        }
                        self._root_self._players_list.append(player_data)
                        
                break

        for stage_dictionnaire in json_object:
            if stage_dictionnaire['part'] == "stage":
                
                for player_dictionnaire in stage_dictionnaire['players']:

                    player_staged = self._root_self.filter(ids=[player_dictionnaire['id']])
                    if player_staged.len() > 0:

                        # Rewires Players with their Groups
                        player_staged.list()[0]['player'].json_load(file_name, [ player_dictionnaire ], stage=self._root_self) # injects stage in the dictionnaire
                        
                break

        return self

    def json_save(self, file_name="stage.json"):

        stage = [ self.json_dictionnaire() ]

        # Writing to sample.json
        with open(file_name, "w") as outfile:
            json.dump(stage, outfile)

        return self

    def len(self):
        return len(self._players_list)
            
    def list(self):
        return self._players_list
    
    def play(self, start=None, finish=None, id=None):
        if len(self._players_list) > 0:
            if id != None:
                stage_player = self.filter(ids = [id], enabled=True)
                if stage_player.len() > 0:
                    stage_player.list()[0]['player'].play(start=start, finish=finish, enabled_lower_group_players=self.filter(enabled=True))
            elif self._players_list[0]['enabled']:
                self._players_list[0]['player'].play(start=start, finish=finish, enabled_lower_group_players=self.filter(enabled=True))
        return self
            
    def player(self, name=None, id=None, type=None, enabled=None) -> (PLAYER.Player | PLAYER.PlayerNone):
        selected_player = self.filter(names=[name], ids=[id], types=[type], enabled=enabled)
        if selected_player.len() > 0:
            return selected_player.list()[0]['player']
        return PLAYER.PlayerNone(self)

    def print(self):

        header_char = "="
        if len(self._players_list) > 0:
            string_top_length = {'sequence': 0, 'id': 0, 'type': 0, 'name': 0, 'description': 0, 'sub-players': 0, 'enabled': 0}
            sequence_index = 0
            for player_data in self: # get maximum sizes
                
                for key, value in string_top_length.items():
                    if key == 'sequence':
                        key_value_length = len(f"{sequence_index}")
                        sequence_index += 1
                    elif key == 'type':
                        key_value_length = len(f"{player_data['player'].__class__.__name__}")
                    elif key == 'description':
                        key_value_length = len(f"{player_data['player'].description}")
                    elif key == 'sub-players':
                        key_value_length = len(f"{player_data['player'].lower_group.all_players_count()}")
                    else:
                        key_value_length = len(f"{player_data[key]}")

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
            for player_data in self._players_list:

                player_str = ""
                for key, value in string_top_length.items():
                    if key == 'sequence':
                        key_value_str = f"{sequence_index}"
                        key_value_str = (" " * (string_top_length[key] - len(key_value_str))) + key_value_str + ": { "
                        sequence_index += 1
                    else:
                        key_value_str = ""
                        if key == 'type':
                            key_value_str = f"{player_data['player'].__class__.__name__}"
                        elif key == 'description':
                            key_value_str = trimString(f"{player_data['player'].description}")
                        elif key == 'sub-players':
                            key_value_str = f"{player_data['player'].lower_group.all_players_count()}"
                        else:
                            key_value_str = f"{player_data[key]}"

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

    def print_tree(self):

        sequence_index = 0

        def tree_top_level(player_data, level=0):
            level += 1
            top_level = 0
            
            lower_group = player_data['player'].lower_group

            if lower_group.len() > 0:
                for lower_player in lower_group:
                    top_level = max(max(top_level, tree_top_level(lower_player, level)), level)

            return top_level

        def print_tree_player(player_data, string_top_length, tabs=0):
            
            lower_group = player_data['player'].lower_group

            nonlocal sequence_index
            tabs += 1
            spaces_between = 4
            
            if lower_group.len() > 0:
                for lower_player_data in lower_group:
                    player_str = ""
                    for key, value in string_top_length.items():
                        if key == 'sequence':
                            sequence_index += 1
                            key_value_str = f"{sequence_index}"
                            key_value_str = (" " * (string_top_length[key] - len(key_value_str))) + key_value_str + ": " + "«" * 6 * (tabs - 1) + "««««« " + "{ "
                        else:
                            key_value_str = ""
                            if key == 'type':
                                key_value_str = f"{lower_player_data['type']}"
                            elif key == 'description':
                                key_value_str = trimString(f"{lower_player_data['player'].description}")
                            elif key == 'sub-players':
                                key_value_str = f"{lower_player_data['player'].lower_group.all_players_count()}"
                            else:
                                stage_player = self.filter(types=[lower_player_data['type']], names=[lower_player_data['name']])
                                key_value_str = f"{stage_player.list()[0][key]}"

                            if key == 'sub-players':
                                key_value_str = f"{key}: " + (" " * (string_top_length[key] - len(key_value_str))) + key_value_str
                            else:
                                key_value_str = f"{key}: " + key_value_str + (" " * (string_top_length[key] - len(key_value_str)))

                            if key != 'enabled':
                                key_value_str += " " * spaces_between

                        player_str +=  key_value_str
                    player_str += " }"
                    print(player_str)

                    print_tree_player(lower_player_data, string_top_length, tabs)

        header_char = "«"
        if len(self._players_list) > 0:
            string_top_length = {'sequence': 0, 'id': 0, 'type': 0, 'name': 0, 'sub-players': 0, 'enabled': 0}
            sequence_index = 0
            for player_data in self: # get maximum sizes
                
                for key, value in string_top_length.items():
                    if key == 'sequence':
                        key_value_length = len(f"{sequence_index}")
                        sequence_index += 1
                    elif key == 'type':
                        key_value_length = len(f"{player_data['player'].__class__.__name__}")
                    elif key == 'description':
                        key_value_length = len(f"{player_data['player'].description}")
                    elif key == 'sub-players':
                        key_value_length = len(f"{player_data['player'].lower_group.all_players_count()}")
                    else:
                        key_value_length = len(f"{player_data[key]}")

                    string_top_length[key] = max(string_top_length[key], key_value_length)

            full_string_top_length = 0
            for value in string_top_length.values():
                full_string_top_length += value

            top_level = 0
            total_lines = 0
            for player_data in self:
                if player_data['player'].upper_group.len() == 0: # root players
                    top_level = max(top_level, tree_top_level(player_data))
                    total_lines += 1 + player_data['player'].lower_group.all_players_count()

            sequence_value_length = len(f"{total_lines - 1}")
            string_top_length['sequence'] = max(string_top_length['sequence'], sequence_value_length)

            spaces_between = 4
            header_char_length = full_string_top_length + 60 + len("......" * top_level)

            header_type = "   " + self.__class__.__name__ + "   "
            header_type_length = len(header_type)
            header_left_half_length = int((header_char_length - header_type_length) / 2)
            header_right_half_length = header_left_half_length + (header_char_length - header_type_length) % 2

            sequence_index = 0
            print(header_char * header_left_half_length + header_type + header_char * header_right_half_length)
            for player_data in self._players_list:

                if player_data['player'].upper_group.len() == 0: # root players
                    player_str = ""
                    for key, value in string_top_length.items():
                        if key == 'sequence':
                            key_value_str = f"{sequence_index}"
                            key_value_str = (" " * (string_top_length[key] - len(key_value_str))) + key_value_str + ": { "
                        else:
                            key_value_str = ""
                            if key == 'type':
                                key_value_str = f"{player_data['player'].__class__.__name__}"
                            elif key == 'description':
                                key_value_str = trimString(f"{player_data['player'].description}")
                            elif key == 'sub-players':
                                key_value_str = f"{player_data['player'].lower_group.all_players_count()}"
                            else:
                                key_value_str = f"{player_data[key]}"

                            if key == 'sub-players':
                                key_value_str = f"{key}: " + (" " * (string_top_length[key] - len(key_value_str))) + key_value_str
                            else:
                                key_value_str = f"{key}: " + key_value_str + (" " * (string_top_length[key] - len(key_value_str)))

                            if key != 'enabled':
                                key_value_str += " " * spaces_between

                        player_str +=  key_value_str
                    player_str += " }"
                    print(player_str)

                    print_tree_player(player_data, string_top_length)

                    sequence_index += 1
            print(header_char * header_char_length)

        else:
            header_type = self.__class__.__name__
            header_type_length = len(header_type)
            print(header_char * (7 + 1 + header_type_length))
            print(f"[EMPTY] {header_type}")
            print(header_char * (7 + 1 + header_type_length))

        return self

    def remove(self):
        for player_data in self._players_list[:]:
            player_data['player'].upper_group.remove()
            player_data['player'].lower_group.remove()
            player_data['player'].discard_resource()
            self._root_self._players_list.remove(player_data)
        self._players_list.clear()

        return self
    
    def unique(self):
        unique_rulers_list = []
        for player_data in self._players_list:
            if player_data not in unique_rulers_list:
                unique_rulers_list.append(player_data)

        return Stage(unique_rulers_list, self._root_self, self._next_id)
        
# GLOBAL CLASS METHODS

def trimString(full_string):
    string_maxum_size = 60
    long_string_termination = "…"
    trimmed_string = full_string
    if full_string != None and len(full_string) > string_maxum_size:
        trimmed_string = full_string[:string_maxum_size] + long_string_termination
    return trimmed_string

# def set_high_priority():
#     handle = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, True, os.getpid())
#     win32process.SetPriorityClass(handle, win32process.HIGH_PRIORITY_CLASS) # you could set this to REALTIME_PRIORITY_CLASS etc.

# set_high_priority()

# # the rest of your code after this