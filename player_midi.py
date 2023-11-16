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

class Master(Player.Player):
    
    def __init__(self, name, description="A conductor of multiple Players"):
        super().__init__(name, description) # not self init

class Note(Player.Player):
    
    def __init__(self, name, description="Plays notes on a given Synth", midi_synth=None):
        super().__init__(name, description) # not self init
        self._midi_synth = midi_synth

    @property
    def midi_synth(self):
        return self._midi_synth
            
    @midi_synth.setter
    def midi_synth(self, midi_synth):
        self._midi_synth = midi_synth
            
    @midi_synth.deleter
    def midi_synth(self):
        self._midi_synth = None
            
    class Action(Player.Player.Action):
        
        def __init__(self, player):
            super().__init__(player) # not self init
            self._note = {'key': "C", 'octave': 4, 'velocity': 100, 'channel': 1, 'duration': 4}

        def getArgument(self, merged_staff_arguments, note_argument):
            note_key = None

            argument_ruler = merged_staff_arguments.group(note_argument)
            if argument_ruler.len() > 0 and argument_ruler.list()[0]['line'] != None and \
                    argument_ruler.list()[0]['lines'][argument_ruler.list()[0]['line']] != None:
                
                note_key = argument_ruler.list()[0]['lines'][argument_ruler.list()[0]['line']]

            else:
                argument_ruler = merged_staff_arguments.group("staff_" + note_argument)
                if argument_ruler.len() > 0:
                    note_key = argument_ruler.list()[0]['lines'][0]

            return note_key

        ### ACTION ACTIONS ###

        def actionTrigger(self, triggered_action, merged_staff_arguments, staff, tick):
            super().actionTrigger(triggered_action, merged_staff_arguments, staff, tick)
            if staff == None: # CLOCKED TRIGGER
                print(f"note OFF:\t{self._note}")

                self._player.midi_synth.releaseNote(self._note, self._note['channel']) # WERE THE MIDI NOTE IS TRIGGERED

            else: # EXTERNAL TRIGGER
                if (not tick['fast_forward'] or True):

                    note_channel = self.getArgument(merged_staff_arguments, "channel")
                    if (note_channel != None):
                        self._note['channel'] = note_channel

                    note_velocity = self.getArgument(merged_staff_arguments, "velocity")
                    if (note_velocity != None):
                        self._note['velocity'] = note_velocity

                    note_duration = self.getArgument(merged_staff_arguments, "duration")
                    if (note_duration != None):
                        self._note['duration'] = note_duration

                    note_octave = self.getArgument(merged_staff_arguments, "octave")
                    if (note_octave != None):
                        self._note['octave'] = note_octave

                    note_key = self.getArgument(merged_staff_arguments, "key")
                    if (note_key != None):
                        self._note['key'] = note_key

                        print(f"note ON:\t{self._note}")
                    
                        self._player.midi_synth.pressNote(self._note, self._note['channel']) # WERE THE MIDI NOTE IS TRIGGERED
                    
                        # needs to convert steps duration accordingly to callers time signature
                        duration_converter = staff.time_signature()['steps_per_beat'] / self._staff.time_signature()['steps_per_beat']
                        self.addClockedAction(
                            {'triggered_action': triggered_action, 'staff_arguments': merged_staff_arguments,
                             'duration': self._note['duration'] * duration_converter, 'action': self},
                            tick
                        )
    