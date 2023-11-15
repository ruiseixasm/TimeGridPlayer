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

import stage as Stage
import player_midi as MIDI
import midi_tools

class StageExtended(Stage.Stage):

    def __init__(self):
        super().__init__()
        
        self._midi_synth = midi_tools.Instrument()
        self._midi_synth.connect(name="loop")

    def __del__(self):
        self._midi_synth.disconnect()

    def add(self, player):
        player_data = {
            'class': player.__class__.__name__,
            'name': player.name,
            'player': player
        }
        self._players.append(player_data)
        player.stage = self
        if player.__class__.__name__ == "Note":
            player.midi_synth = self._midi_synth
        return self
    
    def playerFactoryMethod(self, player_dictionnaire):
        super().playerFactoryMethod(player_dictionnaire)
        match player_dictionnaire['class']:
            case "Note":
                player = MIDI.Note(player_dictionnaire['name'], self._midi_synth)
                player.json_load("", player_dictionnaire)

        return self
    