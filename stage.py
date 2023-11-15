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

import player as Player
import player_midi as MIDI

class Stage:

    def __init__(self):

        self._players = []

    @property
    def players(self):
        return self._players
            
    def add(self, player):
        player_data = {
            'name': player.name,
            'player': player
        }
        self._players.append(player_data)
        player.stage = self
        return self
    
    def remove(self, player):
        players = self._players[:]
        for player_data in players:
            if player_data['player'] == player:
                del player.stage
                self._players.remove(player_data)
                break

