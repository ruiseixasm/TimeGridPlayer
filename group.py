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

    def __init__(self, players_list=None, root_self=None, start_id=0, owner_player=None):

        self._players_list = []
        if players_list != None:
            self._players_list = players_list
        self._root_self = self
        if root_self != None:
            self._root_self = root_self
        self._owner_player = owner_player # When working as lower group, None when main group

        self._next_id = start_id

        self.current_player = 0

    @property
    def owner(self):
        return self._owner_player
    
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

        return Group(self_players_list + other_players_list, self._root_self, self._next_id, self._owner_player)
        
    def _playerFactoryMethod(self, player_dictionnaire):
        player = None
        match player_dictionnaire['class']:
            case "Player" | "Trigger":
                player = PLAYER.Player(player_dictionnaire['name'], player_dictionnaire['description'])

        return player

    def add(self, player):
        if not player.is_none:
            player_data = {
                'id': self._next_id,
                'class': player.__class__.__name__,
                'name': player.name,
                'player': player,
                'enabled': True
            }
            self._root_self._next_id += 1
            self._root_self._players_list.append(player_data)
            if self != self._root_self:
                self._players_list.append(player_data)
                self._next_id = self._root_self._next_id

            if self._owner_player == None:
                all_sub_players = player.get_all_sub_players_group().unique()
        return self
    
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
    
    def filter(self, ids = [], classes = [], names = [], player = None, enabled = None):

        filtered_players = self._players_list.copy()

        if (len(ids) > 0 and ids != [None]):
            filtered_players = [
                filtered_player for filtered_player in filtered_players if filtered_player['id'] in ids
            ]
        if (len(classes) > 0 and classes != [None]):
            filtered_players = [
                filtered_player for filtered_player in filtered_players if filtered_player['id'] in classes
            ]
        if (len(names) > 0 and names != [None]):
            filtered_players = [
                filtered_player for filtered_player in filtered_players if filtered_player['id'] in names
            ]
        if (player != None):
            filtered_players = [
                filtered_player for filtered_player in filtered_players if filtered_player['player'] == player
            ]
        if (enabled != None):
            filtered_players = [
                filtered_player for filtered_player in filtered_players if filtered_player['enabled'] == enabled
            ]

        return Group(filtered_players, self._root_self, self._next_id, self._owner_player)

    def json_dictionnaire(self):
        group = {
                'part': "group",
                'class': self._root_self.__class__.__name__,
                'next_id': self._root_self._next_id,
                'players': []
            }
        
        for player_dictionnaire in self._root_self._players_list:
            player_json = {}
            player_json['id'] = player_dictionnaire['id']
            player_json['enabled'] = player_dictionnaire['enabled']
            player_json = player_dictionnaire['player'].json_dictionnaire()
            group['players'].append( player_json )

        return group
    
    def json_load(self, file_name="group.json", json_object=None):

        if json_object == None:
            # Opening JSON file
            with open(file_name, 'r') as openfile:
                # Reading from json file
                json_object = json.load(openfile)

        self._root_self._players_list.clear()

        for group_dictionnaire in json_object:
            if group_dictionnaire['part'] == "group":
                self._root_self._next_id = group_dictionnaire['next_id']
                for player_dictionnaire in group_dictionnaire['players']:
                    player = self._root_self._playerFactoryMethod(player_dictionnaire)
                    if player != None:
                        player.json_load(file_name, [ player_dictionnaire ])
                        player_data = {
                            'id': player_dictionnaire['id'],
                            'class': player.__class__.__name__,
                            'name': player.name,
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
                    group_player.list()[0]['player'].play(start=start, finish=finish, enabled_group_players=self.filter(enabled=True))
            elif self._players_list[0]['enabled']:
                self._players_list[0]['player'].play(start=start, finish=finish, enabled_group_players=self.filter(enabled=True))
        return self
            
    def player(self) -> (PLAYER.Player | PLAYER.PlayerNone):
        if len(self._players_list) > 0:
            return self._players_list[0]['player']
        return PLAYER.PlayerNone()

    def print(self):

        header_char = "¤"
        if len(self._players_list) > 0:
            string_top_length = {'sequence': 0, 'id': 0, 'class': 0, 'name': 0, 'description': 0, 'sub-players': 0, 'enabled': 0}
            sequence_index = 0
            for player in self: # get maximum sizes
                
                for key, value in string_top_length.items():
                    if key == 'sequence':
                        key_value_length = len(f"{sequence_index}")
                        sequence_index += 1
                    elif key == 'class':
                        key_value_length = len(f"{player['player'].__class__.__name__}")
                    elif key == 'description':
                        key_value_length = len(f"{player['player'].description}")
                    elif key == 'sub-players':
                        key_value_length = len(f"{player['player'].group.len()}")
                    else:
                        key_value_length = len(f"{player[key]}")

                    string_top_length[key] = max(string_top_length[key], key_value_length)

            full_string_top_length = 0
            for value in string_top_length.values():
                full_string_top_length += value

            spaces_between = 4
            header_char_length = full_string_top_length + 78

            header_class = "   " + self.__class__.__name__ + "   "
            header_class_length = len(header_class)
            header_left_half_length = int((header_char_length - header_class_length) / 2)
            header_right_half_length = header_left_half_length + (header_char_length - header_class_length) % 2

            print(header_char * header_left_half_length + header_class + header_char * header_right_half_length)
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
                        if key == 'class':
                            key_value_str = f"{player['player'].__class__.__name__}"
                        elif key == 'description':
                            key_value_str = trimString(f"{player['player'].description}")
                        elif key == 'sub-players':
                            key_value_str = f"{player['player'].group.len()}"
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
            header_class = self.__class__.__name__
            header_class_length = len(header_class)
            print(header_char * (7 + 1 + header_class_length))
            print(f"[EMPTY] {header_class}")
            print(header_char * (7 + 1 + header_class_length))
        return self

    def remove(self):
        for player_data in self._players_list[:]:
            self._root_self._players_list.remove(player_data)
            break
        self._players_list.clear()

        return self

    def unique(self):
        unique_rulers_list = []
        for player in self._players_list:
            if player not in unique_rulers_list:
                unique_rulers_list.append(player)

        return Group(unique_rulers_list, self._root_self, self._next_id, self._owner_player)
        
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
