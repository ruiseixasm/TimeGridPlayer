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
import resources_midi as RESOURCES_MIDI
import player_midi as PLAYER_MIDI

class StageMidi(STAGE.Stage):
    
    def __init__(self, players_list=None, root_self=None, start_id=0):
        super().__init__(players_list, root_self, start_id)
        self._resources = RESOURCES_MIDI.Midi()

    def playerFactoryMethod(self, name, description=None, resources=None, type=None):
        match type:
            case "Clock":
                if resources == None:
                    if description == None:
                        return PLAYER_MIDI.Clock(self, name, resources=self._resources)
                    return PLAYER_MIDI.Clock(self, name, description, self._resources)
                if description == None:
                    return PLAYER_MIDI.Clock(self, name, resources=resources)
                return PLAYER_MIDI.Clock(self, name, description, resources)
            case "Master":
                if description == None:
                    return PLAYER_MIDI.Master(self, name)
                return PLAYER_MIDI.Master(self, name, description)
            case "Note":
                if resources == None:
                    if description == None:
                        return PLAYER_MIDI.Note(self, name, resources=self._resources)
                    return PLAYER_MIDI.Note(self, name, description, self._resources)
                if description == None:
                    return PLAYER_MIDI.Note(self, name, resources=resources)
                return PLAYER_MIDI.Note(self, name, description, resources)
            case "Retrigger":
                if resources == None:
                    if description == None:
                        return PLAYER_MIDI.Retrigger(self, name, resources=self._resources)
                    return PLAYER_MIDI.Retrigger(self, name, description, self._resources)
                if description == None:
                    return PLAYER_MIDI.Retrigger(self, name, resources=resources)
                return PLAYER_MIDI.Retrigger(self, name, description, resources)
            case "Arpeggiator":
                if resources == None:
                    if description == None:
                        return PLAYER_MIDI.Arpeggiator(self, name, resources=self._resources)
                    return PLAYER_MIDI.Arpeggiator(self, name, description, self._resources)
                if description == None:
                    return PLAYER_MIDI.Arpeggiator(self, name, resources=resources)
                return PLAYER_MIDI.Arpeggiator(self, name, description, resources)
        return super().playerFactoryMethod(name, description, resources, type)
