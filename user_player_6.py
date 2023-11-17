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
import player as PLAYER
import player_midi as PL_MIDI
import lines_scales as L_SCALES

trigger = PLAYER.Trigger("trigger")
# trigger.useInternalClock(True)

master = PLAYER.Player("master")
note = PL_MIDI.Note("note")
note.staff().set(size_measures=1)
#note.useInternalClock(True)

print("\n\n")

trigger.rulers().add({'type': "actions", 'group': "trigger", 'position': [1, 1], 'lines': ["trigger"]})
trigger.rulers().add({'type': "actions", 'group': "trigger", 'position': [3, 1], 'lines': ["trigger"]})
#trigger.rulers().filter(type="actions").sort().print().print_lines()

# MASTER MIDI COMPOSITION
master.rulers().add({'type': "actions", 'group': "note", 'position': [2, 4], 'lines': ["note"], 'offset': 2})
master.rulers().add({'type': "actions", 'group': "note", 'position': [3, 4], 'lines': ["note"]})
master.rulers().filter(type="actions").sort().print().print_lines()

master.rulers().add({'type': "arguments", 'group': "staff_channel", 'position': [0, 0], 'lines': [3]})
master.rulers().add({'type': "arguments", 'group': "staff_velocity", 'position': [0, 0], 'lines': [120]})
master.rulers().add({'type': "arguments", 'group': "staff_duration", 'position': [0, 0], 'lines': [2]})

scales = L_SCALES.Scales()
scales.scale("major", 5)
lines_major_scale = scales.lines()
master.rulers().add({'type': "arguments", 'group': "key", 'position': [2, 1], 'lines': lines_major_scale})
master.rulers().add({'type': "arguments", 'group': "key", 'position': [1, 0], 'lines': ['c', 'c#', 'd', None, 'e', None]})
master.rulers().add({'type': "arguments", 'group': "key", 'position': [3, 0], 'lines': ['d', 'c#', 'd', 'd#', 'e', None], 'offset': -1})
master.rulers().add({'type': "arguments", 'group': "key", 'position': [2, 2], 'lines': [None, 'c#', None, None, 'e', None]})
master.rulers().add({'type': "arguments", 'group': "key", 'position': [1, 1], 'lines': ['a', 'b', 'd', None, 'f', None], 'offset': -2})
master.rulers().add({'type': "arguments", 'group': "key", 'position': [3, 2], 'lines': [None, 'c#', 'd', 'd#', 'e', None]})
master.rulers().type("arguments").sort().group("key").print().print_lines().spread_lines(0).print_lines().print()

# JSON JSON JSON JSON JSON JSON JSON JSON JSON JSON JSON JSON JSON JSON JSON JSON JSON JSON JSON JSON JSON JSON JSON JSON
# master.json_save("player.json")
# master.json_load("player.json")

#trigger.play()
print("\n\n\nNEXT ITERATION\n\n")
#trigger.play([1, 0], [2, 0])

import stage_extended as STAGE_EXT
stage = STAGE_EXT.StageExtended()
stage.add(master)
stage.add(note)
master.set_tempo(240)

for _ in range(1):
    stage.print().player().rulers().group("key").sort(reverse=True).print().print_lines(-7, 13)
    stage.play([2, 0], [4, 0])
    stage.player().rulers().type("actions").group("note").sort(reverse=True).print().print_lines(-7, 13)
    stage.player().rulers().group("key").sort(reverse=True).rotate_lines().print_lines(-7, 13)

#master.play()

# stage.json_save("stage.json")
#stage.json_load("stage.json")

#master.rulers().print().print_lines()
#master.staff().print()

#stage.print().player().rulers().print().print_lines().player().play()

