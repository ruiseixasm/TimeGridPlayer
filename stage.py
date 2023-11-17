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
import player as Player

class Stage:

    def __init__(self, players_list=None, root_players_list=None, start_id=0):

        self._root_players_list = []
        self._players_list = self._root_players_list
        if players_list != None:
            self._players_list = players_list
        if root_players_list != None:
            self._root_players_list = root_players_list

        self._next_id = start_id

    def _playerFactoryMethod(self, player_dictionnaire):
        player = None
        match player_dictionnaire['class']:
            case "Player" | "Trigger":
                player = Player.Player(player_dictionnaire['name'], player_dictionnaire['description'])

        return player

    def add(self, player):
        player_data = {
            'id': self._next_id,
            'class': player.__class__.__name__,
            'name': player.name,
            'player': player,
            'enabled': True
        }
        self._next_id += 1
        self._root_players_list.append(player_data)
        if player.stage != None:
            player.stage.filter(player=player).remove() # remove from other stage first
        player.stage = self
        return self
    
    def disable(self):
        for player in self._players_list:
            player['enabled'] = False

        return self

    def disabled(self):
        if len(self._players_list) > 0:
            return not self._players_list[0]['enabled']
        return None
    
    def enable(self):
        for player in self._players_list:
            player['enabled'] = True

        return self

    def enabled(self):
        if len(self._players_list) > 0:
            return self._players_list[0]['enabled']
        return None
    
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

        return Stage(filtered_players, self._root_players_list)

    def json_dictionnaire(self):
        stage = {
                'part': "stage",
                'next_id': self._next_id,
                'players': []
            }
        
        for player_dictionnaire in self._root_players_list:
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

        self._root_players_list.clear()

        for stage_dictionnaire in json_object:
            if stage_dictionnaire['part'] == "stage":
                self._next_id = stage_dictionnaire['next_id']
                for player_dictionnaire in stage_dictionnaire['players']:
                    player = self._playerFactoryMethod(player_dictionnaire)
                    if player != None:
                        player.json_load(file_name, [ player_dictionnaire ])
                        player_data = {
                            'id': player_dictionnaire['id'],
                            'class': player.__class__.__name__,
                            'name': player.name,
                            'player': player,
                            'enabled': player_dictionnaire['enabled']
                        }
                        self._root_players_list.append(player_data)
                        player.stage = self
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
    
    def play(self, start=None, finish=None):
        if len(self._players_list) > 0:
            return self._players_list[0]['player'].play(start, finish)
        return self
            
    def player(self):
        if len(self._players_list) > 0:
            return self._players_list[0]['player']
        return None

    def print(self):

        if len(self._players_list) > 0:
            string_top_length = {'sequence': 0, 'id': 0, 'class': 0, 'name': 0, 'description': 0, 'enabled': 0}
            sequence_index = 0
            for player in self._players_list: # get maximum sizes
                
                for key, value in string_top_length.items():
                    if key == 'sequence':
                        key_value_length = len(f"{sequence_index}")
                        sequence_index += 1
                    elif key == 'class':
                        key_value_length = len(f"{player['player'].__class__.__name__}")
                    elif key == 'description':
                        key_value_length = len(f"{player['player'].description}")
                    else:
                        key_value_length = len(f"{player[key]}")

                    string_top_length[key] = max(string_top_length[key], key_value_length)

            full_string_top_length = 0
            for value in string_top_length.values():
                full_string_top_length += value

            spaces_between = 4

            print("=" * (full_string_top_length + 61))
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
                        else:
                            key_value_str = f"{player[key]}"

                        key_value_str = f"{key}: " + key_value_str + (" " * (string_top_length[key] - len(key_value_str)))

                        if key != 'enabled':
                            key_value_str += " " * spaces_between

                    player_str +=  key_value_str
                player_str += " }"
                print(player_str)
            print("=" * (full_string_top_length + 61))

        else:
            print("=" * 7)
            print("[EMPTY]")
            print("=" * 7)
        return self

    def remove(self, player):
        for player_data in self._players_list[:]:
            del player.stage
            self._root_players_list.remove(player_data)
            break
        self._players_list.clear()

        return self

# GLOBAL CLASS METHODS

def trimString(full_string):
    string_maxum_size = 60
    long_string_termination = "…"
    trimmed_string = full_string
    if len(full_string) > string_maxum_size:
        trimmed_string = full_string[:string_maxum_size] + long_string_termination
    return trimmed_string
