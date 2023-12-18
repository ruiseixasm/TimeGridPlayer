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

import group as GROUP
import player as PLAYER
import player_midi as PLAYER_MIDI
import lines_scales as LINES_SCALES

trigger = PLAYER.Trigger("trigger")
# trigger.useInternalClock(True)

master = PLAYER.Player("master")
note = PLAYER_MIDI.Note("note")
note.staff().set(size_measures=1)
#note.useInternalClock(True)
#note.resources = PLAYER_MIDI.Midi()
note.use_resource("loop")
note.enable_resource()


repeat = PLAYER.Player("repeat")
repeat.add(note)
scales = LINES_SCALES.Scales()
scales.scale("minor", 5)
lines_minor_scale = scales.lines()
repeat.rulers().add({'type': "actions", 'group': "note", 'position': [0, 0], 'lines': ["note"]})
repeat.rulers().duplicate().duplicate().duplicate().distribute_position(16).spread_lines().print_lines(-10, 10)
repeat.rulers().add({'type': "arguments", 'group': "key", 'position': [0, 0], 'lines': lines_minor_scale})
repeat.rulers().add({'type': "arguments", 'group': "staff_channel", 'position': [0, 0], 'lines': [3]})
repeat.rulers().add({'type': "arguments", 'group': "staff_velocity", 'position': [0, 0], 'lines': [120]})
repeat.rulers().add({'type': "arguments", 'group': "staff_duration", 'position': [0, 0], 'lines': [1]})
#repeat.play([0, 0], [1, 0])

master.add(note)
master.add(repeat)

print("\n\n")

trigger.rulers().add({'type': "actions", 'group': "trigger", 'position': [1, 1], 'lines': ["trigger"]})
trigger.rulers().add({'type': "actions", 'group': "trigger", 'position': [3, 1], 'lines': ["trigger"]})
#trigger.rulers().filter(type="actions").sort().print().print_lines()

# MASTER MIDI COMPOSITION
master.rulers().add({'type': "actions", 'group': "note", 'position': [2, 4], 'lines': ["note"], 'offset': 2})
master.rulers().add({'type': "actions", 'group': "note", 'position': [3, 4], 'lines': ["note"]})
master.rulers().add({'type': "actions", 'group': "repeat", 'position': [1, 0], 'lines': ["repeat"]})
master.rulers().filter(type="actions").sort().print().print_lines()

master.rulers().add({'type': "arguments", 'group': "staff_channel", 'position': [0, 0], 'lines': [3]})
master.rulers().add({'type': "arguments", 'group': "staff_velocity", 'position': [0, 0], 'lines': [120]})
master.rulers().add({'type': "arguments", 'group': "staff_duration", 'position': [0, 0], 'lines': [2]})

scales = LINES_SCALES.Scales()
scales.scale("major", 5)
lines_major_scale = scales.lines()
master.rulers().add({'type': "arguments", 'group': "key", 'position': [2, 1], 'lines': lines_major_scale})
master.rulers().add({'type': "arguments", 'group': "key", 'position': [1, 0], 'lines': ['c', 'c#', 'd', None, 'e', None]})
master.rulers().add({'type': "arguments", 'group': "key", 'position': [3, 0], 'lines': ['d', 'c#', 'd', 'd#', 'e', None], 'offset': -1})
master.rulers().add({'type': "arguments", 'group': "key", 'position': [2, 2], 'lines': [None, 'c#', None, None, 'e', None]})
master.rulers().add({'type': "arguments", 'group': "key", 'position': [1, 1], 'lines': ['a', 'b', 'd', None, 'f', None], 'offset': -2})
master.rulers().add({'type': "arguments", 'group': "key", 'position': [3, 2], 'lines': [None, 'c#', 'd', 'd#', 'e', None]})
#master.rulers().type("arguments").sort().group("key").print().print_lines().spread_lines(0).print_lines().print()

# JSON JSON JSON JSON JSON JSON JSON JSON JSON JSON JSON JSON JSON JSON JSON JSON JSON JSON JSON JSON JSON JSON JSON JSON
# master.json_save("player.json")
# master.json_load("player.json")

#trigger.play()
print("\n\n\nNEXT ITERATION\n\n")
#trigger.play([1, 0], [2, 0])

master.json_save("player_2.json")

import group as GROUP
# group = GROUP.Group()
#group2 = GROUP.Group()
# group.add(master)
#group.add(note)
master.set_tempo(240)

# for _ in range(1):
#     group.print().player().rulers().group("key").sort(reverse=True).print().print_lines(-7, 13)
#     group.play([2, 0], [4, 0])
#     group.play([2, 0], [4, 0], 1)
#     group.player().rulers().type("actions").group("note").sort(reverse=True).print().print_lines(-7, 13)
#     group.player().rulers().group("key").sort(reverse=True).rotate_lines().print_lines(-7, 13)

master.print()
master.print_lower_group()

# group.play([1, 0], [4, 0])
master.play([1, 0], [4, 0])
master.print()
master.print_lower_group()
master.remove(repeat)
master.play([1, 0], [4, 0])
#group.print()

# group.json_save("group_3.json")
# group.json_load("group_3.json")

#master.rulers().print().print_lines()
#master.staff().print()

#group.print().player().rulers().print().print_lines().player().play()

