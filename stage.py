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

    def __init__(self):

        self._players = []

    @property
    def players(self):
        return self._players
            
    def add(self, player):
        player_data = {
            'class': player.__class__.__name__,
            'name': player.name,
            'player': player
        }
        self._players.append(player_data)
        player.stage = self
        return self
    
    def playerFactoryMethod(self, player_dictionnaire):
        player = None
        match player_dictionnaire['class']:
            case "Player":
                player = Player.Player(player_dictionnaire['name'])
                player.json_load("", player_dictionnaire)

        return player
    
    def json_dictionnaire(self):
        stage = {
                'part': "stage",
                'class': self.__class__.__name__,
                'players': []
            }
        
        for player_dictionnaire in self._players:
            stage['players'].append( [ player_dictionnaire['player'].json_dictionnaire() ] )

        return stage
    
    def json_load(self, file_name, json_object=None):

        if json_object == None:
            # Opening JSON file
            with open(file_name, 'r') as openfile:
                # Reading from json file
                json_object = json.load(openfile)

        for dictionnaire in json_object:
            if dictionnaire['part'] == "stage":
                for player_dictionnaire in dictionnaire['players']:
                    player = self.playerFactoryMethod(player_dictionnaire)
                    if player != None:
                        self.add(player)
                break

        return self

    def json_save(self, file_name):

        stage = [ self.json_dictionnaire() ]

        # Writing to sample.json
        with open(file_name, "w") as outfile:
            json.dump(stage, outfile)

        return self

    def remove(self, player):
        players = self._players[:]
        for player_data in players:
            if player_data['player'] == player:
                del player.stage
                self._players.remove(player_data)
                break

