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
import midi_tools

class Master(Player.Player):
    
    def __init__(self, name, beats_per_minute=120, size_measures=8, beats_per_measure=4, steps_per_beat=4, pulses_per_quarter_note=24, play_range=[[], []]):
        super().__init__(name, beats_per_minute, size_measures, beats_per_measure, steps_per_beat, pulses_per_quarter_note, play_range) # not self init

class Note(Player.Player):
    
    def __init__(self, name, beats_per_minute=120, size_measures=8, beats_per_measure=4, steps_per_beat=4, pulses_per_quarter_note=24, play_range=[[], []]):
        super().__init__(name, beats_per_minute, size_measures, beats_per_measure, steps_per_beat, pulses_per_quarter_note, play_range) # not self init
        self._midi_synth = midi_tools.Instrument()
        first_position = self._staff.playRange()[0]
        #self._staff_rulers.add({'type': "actions", 'group': "notes", 'position': first_position, 'lines': [self]})
        self._note = {'key': "C", 'octave': 4, 'velocity': 100}

    def finish(self):
        super().finish()
        self._midi_synth.disconnect()

    def start(self):
        super().start()
        self._midi_synth.connect(name="loop")

    ### ACTIONS ###

    def actionTrigger(self, triggered_action, merged_staff_arguments, staff, tick):
        super().actionTrigger(triggered_action, merged_staff_arguments, staff, tick)
        match staff:
            case None: # CLOCKED TRIGGER
                print(f"note OFF:\t{self._note['key']}")
                self._midi_synth.releaseNote(self._note)

            case default: # EXTERNAL TRIGGER OR INTERNAL TRIGGER
                if (not tick['fast_forward'] or True):

                    if (merged_staff_arguments.len() > 0):
                        given_lines = merged_staff_arguments.list()[0]['lines']
                        key_line = merged_staff_arguments.list()[0]['line']
                        key_value = given_lines[key_line]
                        self._note['key'] = key_value # may need tranlation!

                    print(f"note ON:\t{self._note['key']}")
                    self._midi_synth.pressNote(self._note)
                    # needs to convert steps duration accordingly to callers time signature
                    duration_converter = staff.signature()['steps_per_beat'] / self._staff.signature()['steps_per_beat']
                    self.addClockedAction(
                        {'triggered_action': triggered_action, 'staff_arguments': merged_staff_arguments, 'duration': 4 * duration_converter, 'action': self},
                        tick
                    )

class Trigger(Player.Player):
    
    def __init__(self, name):
        super().__init__(name, beats_per_minute=120, size_measures=1, beats_per_measure=1, steps_per_beat=1) # not self init
        #self._staff_rulers.add({'type': "actions", 'group': "triggers", 'lines': [self]})

    ### ACTIONS ###

    def actionTrigger(self, triggered_action, merged_staff_arguments, staff, tick):
        super().actionTrigger(triggered_action, merged_staff_arguments, staff, tick)
        match staff:
            case None: # CLOCKED TRIGGER
                print("CLOCKED TRIGGERED")

            case self._staff: # INTERNAL TRIGGER
                print("INTERNALLY TRIGGERED")

            case default: # EXTERNAL TRIGGER
                print("EXTERNALLY TRIGGERED")
