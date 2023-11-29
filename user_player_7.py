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

import stage_midi as STAGE_MIDI
import lines_scales as LINES_SCALES

stage_midi = STAGE_MIDI.StageMidi()

# add a master player to stage
stage_midi.add("master")
stage_midi.add("note", type="Note")
stage_midi.add("repeat", type="Master")
stage_midi.add("clock", type="Clock")

note = stage_midi.print().player("note").print()
note.use_resource("loop").enable_resource()
note.print()
midi_clock = stage_midi.print().player("clock").print()
midi_clock.use_resource("loop").enable_resource()
midi_clock.print()

scales = LINES_SCALES.Scales()

master = stage_midi.player("master")
master.set_time_signature(size_measures=12)
# Retrigger
stage_midi.add("retrig", type="Retrigger")
retrig = stage_midi.player("retrig")
retrig.use_resource("loop").enable_resource()
master.add(retrig)
# Arpeggiator
stage_midi.add("arpeggio", type="Arpeggiator")
arpeggio = stage_midi.player("arpeggio")
arpeggio.use_resource("loop").enable_resource()
master.add(arpeggio)

# MASTER MIDI COMPOSITION
master.rulers().add({'type': "actions", 'group': "note", 'position': [2, 4], 'lines': ["note"], 'offset': 2})
master.rulers().add({'type': "actions", 'group': "note", 'position': [3, 4], 'lines': ["note"]})
master.rulers().add({'type': "actions", 'group': "repeat", 'position': [1, 0], 'lines': ["repeat"]})
master.rulers().add({'type': "actions", 'group': "retrig", 'position': [4, 0], 'lines': ["retrig"], 'offset': 4})
master.rulers().add({'type': "actions", 'group': "retrig", 'position': [6, 0], 'lines': ["retrig"], 'offset': 4})
master.rulers().add({'type': "actions", 'group': "arpeggio", 'position': [10, 0], 'lines': ["arpeggio", "arpeggio", "arpeggio", "arpeggio"], 'offset': 4})
master.rulers().filter(type="actions").sort().print().print_lines()

master.rulers().add({'type': "arguments", 'group': "staff_channel", 'position': [0, 0], 'lines': [3]})
master.rulers().add({'type': "arguments", 'group': "staff_velocity", 'position': [0, 0], 'lines': [120]})
master.rulers().add({'type': "arguments", 'group': "staff_duration", 'position': [2, 0], 'lines': [0.25]})
master.rulers().add({'type': "arguments", 'group': "duration", 'position': [2, 0], 'lines': [24, 24, 24, 24], 'offset': 4})
master.rulers().filter(type="arguments").sort().print().print_lines()

scales.scale("major", "A", 5)
lines_major_scale = scales.lines()
master.rulers().add({'type': "arguments", 'group': "key", 'position': [2, 1], 'lines': lines_major_scale}).print_lines(0, 15)
master.rulers().add({'type': "arguments", 'group': "key", 'position': [1, 0], 'lines': ['c', 'c#', 'd', None, 'e', None]})
master.rulers().add({'type': "arguments", 'group': "key", 'position': [3, 0], 'lines': ['d', 'c#', 'd', 'd#', 'e', None], 'offset': -1})
master.rulers().add({'type': "arguments", 'group': "key", 'position': [2, 2], 'lines': [None, 'c#', None, None, 'e', None]})
master.rulers().add({'type': "arguments", 'group': "key", 'position': [1, 1], 'lines': ['a', 'b', 'd', None, 'f', None], 'offset': -2})
master.rulers().add({'type': "arguments", 'group': "key", 'position': [3, 2], 'lines': [None, 'c#', 'd', 'd#', 'e', None]})
master.rulers().add({'type': "arguments", 'group': "key", 'position': [4, 0], 'lines': ['a', 'b', 'd', None, 'f', None], 'offset': -4})
master.rulers().arguments().print().print_lines(0, 15).group_name_find("staff_").print()

repeat = stage_midi.player("repeat")
# REPEAT MIDI COMPOSITION
scales.scale("minor", "D", 5)
lines_minor_scale = scales.lines()
repeat.rulers().add({'type': "actions", 'group': "note", 'position': [0, 0], 'lines': ["note"]})
repeat.rulers().duplicate(7).duplicate().distribute_position(16).spread_lines().print_lines()
repeat.rulers().add({'type': "arguments", 'group': "key", 'position': [0, 0], 'lines': lines_minor_scale}).print_lines(0, 15)
repeat.rulers().add({'type': "arguments", 'group': "staff_channel", 'position': [0, 0], 'lines': [3]})
repeat.rulers().add({'type': "arguments", 'group': "staff_velocity", 'position': [0, 0], 'lines': [120]})
repeat.rulers().add({'type': "arguments", 'group': "staff_duration", 'position': [0, 0], 'lines': [0.5]})
repeat.rulers().filter(type="arguments").print().print_lines(0, 15)


master.set_tempo(124)
#master.play([1, 0], [4, 0])

master.add(repeat)

#master.play([1, 0], [4, 0])

master.add(note)

#master.play([1, 0], [4, 0])

repeat.add(note)

#master.play([1, 0], [4, 0])

#stage_midi.play([1, 0], [4, 0])

stage_midi.print()
stage_midi.print_tree()

stage_midi.json_save("stage_2.json")
stage_midi.json_load("stage_2.json")

stage_midi.print().filter(names=["note"]).print().disable().print().enable().print()
stage_midi.filter(names=["retrig"]).disable().print()
stage_midi.print_tree()

stage_midi.play()
#stage_midi.play([1, 0], [4, 0])