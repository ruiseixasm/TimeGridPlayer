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

import stage as STAGE
import player_midi as PlayerMIDI
import resources_instruments as MIDI_INS

class StageExtended(STAGE.Stage):

    def __init__(self, start_id=0):
        super().__init__(start_id=start_id)
        
        self._midi_instruments = MIDI_INS.Intruments()

    def add(self, player):
        super().add(player)
        if self._owner_player == None and player.__class__.__name__ == "Note": # checks condition as Main Stage
            if player.synth_name != None:
                player.midi_synth = self._midi_instruments.get(player.synth_name)
        return self
    
    def _playerFactoryMethod(self, player_dictionnaire):
        player = super()._playerFactoryMethod(player_dictionnaire)
        match player_dictionnaire['class']:
            case "Master":
                player = PlayerMIDI.Note(player_dictionnaire['name'], player_dictionnaire['description'])
            case "Note":
                player = PlayerMIDI.Note(player_dictionnaire['name'], player_dictionnaire['description'], player_dictionnaire['synth_name'])

        return player