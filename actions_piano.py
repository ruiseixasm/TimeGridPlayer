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
        self._staff_rulers.add({'type': "actions", 'group': "notes", 'position': first_position, 'lines': [self]})
        self._note = {'key': "C", 'octave': 4, 'velocity': 100}

    def finish(self):
        super().finish()
        self._midi_synth.disconnect()

    def start(self):
        super().start()
        self._midi_synth.connect(name="loop")

    ### ACTIONS ###

    def actionExternalTrigger(self, triggered_action = {}, merged_staff_arguments=None, tick = {}):
        super().actionExternalTrigger(triggered_action, merged_staff_arguments, tick)
        if (tick['fast_forward']):
            self._play_mode = False
        if (merged_staff_arguments != None and merged_staff_arguments.len() > 0):
            given_lines = merged_staff_arguments.list()[0]['lines']
            key_line = merged_staff_arguments.list()[0]['line']
            key_value = given_lines[key_line]
            self._note['key'] = key_value # may need tranlation!

    def actionInternalTrigger(self, triggered_action = {}, merged_staff_arguments=None, tick = {}):
        super().actionInternalTrigger(triggered_action, merged_staff_arguments, tick)

        if (merged_staff_arguments != None and merged_staff_arguments.len() > 0):
            given_lines = merged_staff_arguments.list()[0]['lines']
            key_line = merged_staff_arguments.list()[0]['line']
            key_value = given_lines[key_line]
        else:
            key_value = self._note['key'] # may need tranlation!

        if (triggered_action['source'] == "staff"):

            print(f"note ON:\t{key_value}")
            note = {'key': key_value, 'octave': 4, 'velocity': 100}
            self._midi_synth.pressNote(note)
            self.addClockedAction(
                {'triggered_action': triggered_action, 'staff_arguments': merged_staff_arguments, 'duration': 4, 'action': self},
                tick
            )
        else:
            print(f"note OFF:\t{key_value}")
            note = {'key': key_value, 'octave': 4, 'velocity': 100}
            self._midi_synth.releaseNote(note)

class Trigger(Player.Player):
    
    def __init__(self, name):
        super().__init__(name, beats_per_minute=120, size_measures=1, beats_per_measure=1, steps_per_beat=1) # not self init
        self._staff_rulers.add({'type': "actions", 'group': "triggers", 'lines': [self]})

    ### ACTIONS ###

    def actionExternalTrigger(self, triggered_action = {}, merged_staff_arguments=None, tick = {}):
        super().actionExternalTrigger(triggered_action, merged_staff_arguments, tick)
        print("EXTERNALLY TRIGGERED")

    def actionInternalTrigger(self, triggered_action = {}, merged_staff_arguments=None, tick = {}):
        super().actionInternalTrigger(triggered_action, merged_staff_arguments, tick)
        print("LOCALLY TRIGGERED")

    # def __str__(self):
    #     finalString = f"{pulse['pulse']}\t{pulse['position']}\n"
    #     return finalString
