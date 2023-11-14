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
import actions_piano as Piano
import midi_tools

trigger = Player.Trigger("trigger")
# trigger.useInternalClock(True)


midi_synth = midi_tools.Instrument()
midi_synth.connect(name="loop")
master = Piano.Master("master")
note = Piano.Note("notes", midi_synth, 440, 1, 4, 4, play_range=[[0, 0], [1, 0]])
#note.useInternalClock(True)

print("\n\n")

trigger.rulers().add({'type': "actions", 'group': "trigger", 'position': [1, 1], 'lines': [trigger]})
trigger.rulers().add({'type': "actions", 'group': "trigger", 'position': [3, 1], 'lines': [trigger]})
trigger.rulers().filter(type="actions").sort().print().print_lines()

# MASTER MIDI COMPOSITION
master.rulers().add({'type': "actions", 'group': "note", 'position': [2, 1], 'lines': [note]})
master.rulers().add({'type': "actions", 'group': "note", 'position': [4, 1], 'lines': [note]})
master.rulers().filter(type="actions").sort().print().print_lines()

master.rulers().add({'type': "arguments", 'group': "staff_channel", 'position': [0, 0], 'lines': [1]})
master.rulers().add({'type': "arguments", 'group': "staff_velocity", 'position': [0, 0], 'lines': [60]})

master.rulers().add({'type': "arguments", 'group': "key", 'position': [2, 1], 'lines': [None, 'c#', None, None, 'e', None]})
master.rulers().add({'type': "arguments", 'group': "key", 'position': [1, 0], 'lines': ['c', 'c#', 'd', None, 'e', None]})
master.rulers().add({'type': "arguments", 'group': "key", 'position': [3, 0], 'lines': ['d', 'c#', 'd', 'd#', 'e', None], 'offset': -1})
master.rulers().add({'type': "arguments", 'group': "key", 'position': [2, 2], 'lines': [None, 'c#', None, None, 'e', None]})
master.rulers().add({'type': "arguments", 'group': "key", 'position': [1, 1], 'lines': ['a', 'b', 'd', None, 'f', None], 'offset': -2})
master.rulers().add({'type': "arguments", 'group': "key", 'position': [3, 2], 'lines': [None, 'c#', 'd', 'd#', 'e', None]})
master.rulers().filter(type="arguments").sort().print().print_lines(None, 8).spread_lines(-2).print_lines(None, 8).print()

#trigger.play()
print("\n\n\nNEXT ITERATION\n\n")
#trigger.play([1, 0], [2, 0])


master.play()


midi_synth.disconnect()
