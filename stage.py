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
    
    def __init__(self, players_list=None, root_self=None, start_id=1):

        self._players_list = []
        if players_list != None:
            self._players_list = players_list
        self._root_self = self
        if root_self != None:
            self._root_self = root_self

        self._resources = RESOURCES.Resources()

        self._next_id = start_id
        self._default_player_id = start_id
        self.current_player = 0

        self._beats_per_minute = 120
        self._time_signature = {
            'measures': 8,                  # staff total size
            'beats_per_measure': 4,         # beats in each measure
            'beats_per_note': 4,            # beats in each measure
            'steps_per_quarternote': 4,     # how many steps take each beat
            'pulses_per_quarternote': 24    # sets de resolution of clock pulses
        }

        self._play_print_options = {
            'staff': True,
            'error': False,
            'message': False
        }

    @property
    def play_print_options(self):
        return self._play_print_options
            
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

    def _play_print(self, message, type, overhead = 1):
        if self._play_print_options[type]:
            if overhead > 0.90:
                print(message, end="", flush=True)
            else:
                print(message, end="")

# Resources Methods

    def use_resource(self, name=None):
        for player_data in self._players_list:
            player_data['player'].use_resource(name)
            
        return self

    def enable_resource(self):
        for player_data in self._players_list:
            player_data['player'].enable_resource()

        return self
           
    def disable_resource(self):
        for player_data in self._players_list:
            player_data['player'].disable_resource()

        return self

    def discard_resource(self):
        for player_data in self._players_list:
            player_data['player'].discard_resource()

        return self

    def playerFactoryMethod(self, name, description=None, resources=None, type=None):
        if resources == None:
            if description == None:
                return PLAYER.Player(self, name, resources=self._resources)
            return PLAYER.Player(self, name, description, self._resources)
        if description == None:
            return PLAYER.Player(self, name, resources=resources)
        return PLAYER.Player(self, name, description, resources)

    def add(self, name, description=None, resources=None, type=None, default=False):
        if type == None:
            type = "Player"
        existent_player = self._root_self.filter(names=[name]) # name is the identifier
        if existent_player.len() == 0:
            player = self.playerFactoryMethod(name, description, resources, type) # Factory Method
            player.set_tempo(self._beats_per_minute)
            player.set_time_signature(
                    self._time_signature['measures'],
                    self._time_signature['beats_per_measure'],
                    self._time_signature['beats_per_note'],
                    self._time_signature['steps_per_quarternote'],
                    self._time_signature['pulses_per_quarternote']
                )
            player_data = {
                'id': self._root_self._next_id,
                'type': player.__class__.__name__,
                'name': player.name,
                'player': player,
                'enabled': True
            }

            if default:
                self._root_self._default_player_id = self._root_self._next_id
            self._root_self._next_id += 1
            self._root_self._players_list.append(player_data)
            if self != self._root_self:
                self._players_list.append(player_data)
                self._next_id = self._root_self._next_id

        return self
     
    def default_player(self):
        return self._root_self.player(id=self._root_self._default_player_id)

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

    def first(self):
        return self.head(1)

    def head(self, elements=1):
        head_players_list = self._players_list[:elements]
        return Stage(head_players_list, self._root_self, self._next_id)
        
    def json_dictionnaire(self):
        stage = {
                'part': "stage",
                'type': self._root_self.__class__.__name__,
                'next_id': self._root_self._next_id,
                'default_player_id': self._root_self._default_player_id,
                'beats_per_minute': self._beats_per_minute,
                'time_signature': self._time_signature,
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
                self._root_self._default_player_id = stage_dictionnaire['default_player_id']
                self._root_self._beats_per_minute = stage_dictionnaire['beats_per_minute']
                self._root_self._time_signature = stage_dictionnaire['time_signature']
                for player_dictionnaire in stage_dictionnaire['players']:
                    player_type = player_dictionnaire['type']
                    player_name = player_dictionnaire['name']
                    description = player_dictionnaire['description']
                    player = self._root_self.playerFactoryMethod(type=player_type, name=player_name, description=description)

                    if player != None:

                        # Populates Players with their Staff, Rulers and Clock data
                        player.json_load(file_name, [ player_dictionnaire ])

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

        return self

    def json_save(self, file_name="stage.json"):

        stage = [ self.json_dictionnaire() ]

        # Writing to sample.json
        with open(file_name, "w") as outfile:
            json.dump(stage, outfile)

        return self

    def last(self):
        return self.tail(1)

    def len(self):
        return len(self._players_list)
            
    def list(self):
        return self._players_list
    
    def play(self, start=None, finish=None, id=None):
        if len(self._players_list) > 0:
            if id != None:
                stage_player = self.filter(ids=[id], enabled=True)
                if stage_player.len() > 0:
                    stage_player.list()[0]['player'].play(start=start, finish=finish)
            elif self == self._root_self:
                defualt_player = self._root_self.filter(ids=[self._root_self._default_player_id])
                if defualt_player.len() > 0 and defualt_player.list()[0]['enabled']:
                    defualt_player.list()[0]['player'].play(start=start, finish=finish)
            elif self._players_list[0]['enabled']:
                self._players_list[0]['player'].play(start=start, finish=finish)
        return self
        
    def player(self, id=None, name=None, enabled=None) -> (PLAYER.Player | PLAYER.PlayerNone):
        selected_player = self.filter(ids=[id], names=[name], enabled=enabled)
        if selected_player.len() > 0:
            return selected_player.list()[0]['player']
        return PLAYER.PlayerNone(self)

    def players(self):
        players_data_list = self.unique().list()
        players_list = []
        for player_data in players_data_list:
            players_list.append(player_data['player'])
        return players_list

    def print(self):

        header_char = "="
        if len(self._players_list) > 0:
            string_top_length = {'sequence': 0, 'id': 0, 'type': 0, 'name': 0, 'description': 0, 'enabled': 0, 'default': 0}
            sequence_index = 1
            for player_data in self: # get maximum sizes
                
                for key, value in string_top_length.items():
                    if key == 'sequence':
                        key_value_length = len(f"{sequence_index}")
                        sequence_index += 1
                    elif key == 'type':
                        key_value_length = len(f"{player_data['player'].__class__.__name__}")
                    elif key == 'description':
                        key_value_length = len(f"{player_data['player'].description}")
                    elif key == 'default':
                        default_player = (player_data['id'] == self._root_self._default_player_id)
                        key_value_length = len(f"{default_player}")
                    else:
                        key_value_length = len(f"{player_data[key]}")

                    string_top_length[key] = max(string_top_length[key], key_value_length)

            full_string_top_length = 0
            for value in string_top_length.values():
                full_string_top_length += value

            spaces_between = 4
            header_char_length = full_string_top_length + 73

            header_type = "   " + self.__class__.__name__ + "   "
            header_type_length = len(header_type)
            header_left_half_length = int((header_char_length - header_type_length) / 2)
            header_right_half_length = header_left_half_length + (header_char_length - header_type_length) % 2

            print(header_char * header_left_half_length + header_type + header_char * header_right_half_length)
            sequence_index = 1
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
                        elif key == 'default':
                            default_player = (player_data['id'] == self._root_self._default_player_id)
                            key_value_str = f"{default_player}"
                        else:
                            key_value_str = f"{player_data[key]}"

                        key_value_str = f"{key}: " + key_value_str + (" " * (string_top_length[key] - len(key_value_str)))

                        if key != 'default':
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
        for player_data in self._players_list[:]:
            player_data['player'].discard_resource()
            self._root_self._players_list.remove(player_data)
        self._players_list.clear()

        return self
    
    def update_player_names(self):
        for player_data in self._root_self._players_list:
            player_data['name'] = player_data['player'].name

        return self

    def set_default_player(self, player):
        root_player = self._root_self.filter(player=player)
        if root_player.len() > 0:
            self._root_self._default_player_id = root_player.list()[0]['id']
        
        return self

    def set_tempo(self, beats_per_minute):
        self._beats_per_minute = beats_per_minute
        for player_data in self._players_list:
            player_data['player'].set_tempo(beats_per_minute=beats_per_minute)
            
        return self

    def set_time_signature(self, measures=None, beats_per_measure=None, beats_per_note=None, steps_per_quarternote=None, pulses_per_quarternote=None):
        if measures != None:
            self._time_signature['measures'] = measures
        if beats_per_measure != None:
            self._time_signature['beats_per_measure'] = beats_per_measure
        if beats_per_note != None:
            self._time_signature['beats_per_note'] = beats_per_note
        if steps_per_quarternote != None:
            self._time_signature['steps_per_quarternote'] = steps_per_quarternote
        if pulses_per_quarternote != None:
            self._time_signature['pulses_per_quarternote'] = pulses_per_quarternote
        for player_data in self._players_list:
            player_data['player'].set_time_signature(measures, beats_per_measure, beats_per_note, steps_per_quarternote, pulses_per_quarternote)
            
        return self

    def tail(self, elements=1):
        tail_players_list = self._players_list[-elements:]
        return Stage(tail_players_list, self._root_self, self._next_id)

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