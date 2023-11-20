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

import player as PLAYER
import resources_instruments as INSTRUMENTS

class Master(PLAYER.Player):
    
    def __init__(self, name, description="A conductor of multiple Players"):
        super().__init__(name, description) # not self init

class Note(PLAYER.Player):
    
    def __init__(self, name, description="Plays notes on a given Synth", instruments=None):
        super().__init__(name, description) # not self init
        self._instruments = instruments
        self._instrument = None
        self._enabled_instrument = False

    def __del__(self):
        self.discard_resource()

    @property
    def instruments(self):
        return self._instruments
            
    @instruments.setter
    def instruments(self, instruments):
        self._instruments = instruments
            
    @instruments.deleter
    def instruments(self):
        self._instruments = None

    @property
    def instrument(self):
        return self._instrument
            
    def use_resource(self, name=None):
        if self._instruments != None:
            self._instrument = self._instruments.add(name)
        return self

    def enable_resource(self):
        if self._instruments != None and self._instrument != None and not self._enabled_instrument:
            self._instruments.enable(self._instrument)
            self._enabled_instrument = True
        return self

    def disable_resource(self):
        if self._instruments != None and self._instrument != None and self._enabled_instrument:
            self._instruments.disable(self._instrument)
            self._enabled_instrument = False
        return self

    def discard_resource(self):
        if self._instruments != None and self._instrument != None:
            self.disable_resource()
            self._instruments.remove(self._instrument)
        return self

    def json_dictionnaire(self):
        dictionnaire = super().json_dictionnaire()
        dictionnaire['resource_name'] = self._enabled_instrument['name']
        return dictionnaire

    class Action(PLAYER.Player.Action):
        
        def __init__(self, player):
            super().__init__(player) # not self init
            self._note = {'key': "C", 'octave': 4, 'velocity': 100, 'channel': 1, 'duration': 4}

        ### ACTION ACTIONS ###

        def actionTrigger(self, triggered_action, merged_staff_arguments, staff, tick):
            super().actionTrigger(triggered_action, merged_staff_arguments, staff, tick)
            if staff == None: # CLOCKED TRIGGER
                print(f"note OFF:\t{self._note}")

                if self._player.instrument != None:
                    self._player.instrument.releaseNote(self._note, self._note['channel']) # WERE THE MIDI NOTE IS TRIGGERED

            else: # EXTERNAL TRIGGER
                if (not tick['fast_forward'] or True):

                    note_channel = self.pickTriggeredLineArgumentValue(merged_staff_arguments, "channel")
                    if (note_channel != None):
                        self._note['channel'] = note_channel

                    note_velocity = self.pickTriggeredLineArgumentValue(merged_staff_arguments, "velocity")
                    if (note_velocity != None):
                        self._note['velocity'] = note_velocity

                    note_duration = self.pickTriggeredLineArgumentValue(merged_staff_arguments, "duration")
                    if (note_duration != None):
                        self._note['duration'] = note_duration

                    note_octave = self.pickTriggeredLineArgumentValue(merged_staff_arguments, "octave")
                    if (note_octave != None):
                        self._note['octave'] = note_octave

                    note_key = self.pickTriggeredLineArgumentValue(merged_staff_arguments, "key")
                    if (note_key != None):
                        self._note['key'] = note_key

                        print(f"note ON:\t{self._note}")
                    
                        if self._player.instrument != None:
                            self._player.instrument.pressNote(self._note, self._note['channel']) # WERE THE MIDI NOTE IS TRIGGERED
                    
                        # needs to convert steps duration accordingly to callers time signature
                        duration_converter = staff.time_signature()['steps_per_beat'] / self._staff.time_signature()['steps_per_beat']
                        self.addClockedAction(
                            {'triggered_action': triggered_action, 'staff_arguments': merged_staff_arguments,
                             'duration': self._note['duration'] * duration_converter, 'action': self},
                            tick
                        )
    