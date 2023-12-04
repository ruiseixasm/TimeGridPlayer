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
master.set_time_signature(size_measures=16)
# Retrigger
stage_midi.add("retrig", type="Retrigger")
retrig = stage_midi.player("retrig")
retrig.use_resource("loop").enable_resource()
# Arpeggiator
stage_midi.add("arpeggio", type="Arpeggiator")
arpeggio = stage_midi.player("arpeggio")
arpeggio.use_resource("loop").enable_resource()

# MASTER MIDI COMPOSITION
master.rulers().add({'link': "note", 'position': [2, 4], 'lines': [1], 'offset': 2})
master.rulers().add({'link': "note", 'position': [3, 4], 'lines': [1]})
master.rulers().add({'link': "repeat", 'position': [1, 0], 'lines': [1]})
master.rulers().add({'link': "retrig", 'position': [4, 0], 'lines': [1], 'offset': 4})
master.rulers().add({'link': "retrig", 'position': [6, 0], 'lines': [1], 'offset': 4})
master.rulers().add({'link': "arpeggio", 'position': [9, 0], 'lines': [1, 1, 1, 1], 'offset': 4})
master.rulers().filter(type="actions").sort().print().print_lines()

master.rulers().add({'link': "note.channel.staff", 'position': [0, 0], 'lines': [3]})
master.rulers().add({'link': "note.velocity.staff", 'position': [0, 0], 'lines': [120]})
master.rulers().add({'link': "note.duration.staff", 'position': [2, 0], 'lines': ["1/64"]})
master.rulers().add({'link': "note.duration.staff", 'position': [9, 0], 'lines': [28]})
master.rulers().add({'link': "arpeggio.channel", 'position': [0, 0], 'lines': [3]})
master.rulers().add({'link': "arpeggio.velocity.staff", 'position': [0, 0], 'lines': [120]})
master.rulers().add({'link': "arpeggio.duration", 'position': [2, 0], 'lines': [100, "7", "7", "6.5"], 'offset': 4})
master.rulers().add({'link': "arpeggio.gate.auto", 'position': [8, 0], 'lines': [.25, .10, .25, .10, .25, .10], 'offset': 3})
master.rulers().add({'link': "arpeggio.gate.auto", 'position': [14, 0], 'lines': [1, .90, .50, .80], 'offset': 3})
master.rulers().add({'link': "arpeggio.rate.auto", 'position': [7, 0], 'lines': [.25, 4, 1, .5, 2, 8], 'offset': 3})
master.rulers().add({'link': "arpeggio.rate.auto", 'position': [14, 0], 'lines': [4, 4, 4, 1], 'offset': 3})
master.rulers().filter(type="arguments").sort().print().print_lines()

scales.scale("major", "A", 5)
lines_major_scale = scales.lines()
master.rulers().add({'link': "note.key", 'position': [2, 1], 'lines': lines_major_scale}).print_lines(0, 15)
master.rulers().add({'link': "arpeggio.key", 'position': [2, 1], 'lines': lines_major_scale})
master.rulers().add({'link': "note.key", 'position': [1, 0], 'lines': ['c', 'c#', 'd', None, 'e', None]})
master.rulers().add({'link': "note.key", 'position': [3, 0], 'lines': ['d', 'c#', 'd', 'd#', 'e', None], 'offset': -1})
master.rulers().add({'link': "note.key", 'position': [2, 2], 'lines': [None, 'c#', None, None, 'e', None]})
master.rulers().add({'link': "note.key", 'position': [1, 1], 'lines': ['a', 'b', 'd', None, 'f', None], 'offset': -2})
master.rulers().add({'link': "note.key", 'position': [3, 2], 'lines': [None, 'c#', 'd', 'd#', 'e', None]})
master.rulers().add({'link': "note.key", 'position': [4, 0], 'lines': ['a', 'b', 'd', None, 'f', None], 'offset': -4})
master.rulers().arguments().print().print_lines(0, 15).link_name_find(".staff").print()

repeat = stage_midi.player("repeat")
# REPEAT MIDI COMPOSITION
scales.scale("minor", "D", 5)
lines_minor_scale = scales.lines()
repeat.rulers().add({'link': "note", 'position': [0, 0], 'lines': [1]})
repeat.rulers().duplicate(7).duplicate().distribute_position(16).spread_lines().print_lines()
repeat.rulers().add({'link': "note.key", 'position': [0, 0], 'lines': lines_minor_scale}).print_lines(0, 15)
repeat.rulers().add({'link': "note.channel.staff", 'position': [0, 0], 'lines': [3]})
repeat.rulers().add({'link': "note.velocity.staff", 'position': [0, 0], 'lines': [120]})
repeat.rulers().add({'link': "note.duration.staff", 'position': [0, 0], 'lines': ["1/32"]})
repeat.rulers().filter(type="arguments").print().print_lines(0, 15)


master.set_tempo(125)
#master.play([1, 0], [4, 0])

#master.play([1, 0], [4, 0])

#master.play([1, 0], [4, 0])

#master.play([1, 0], [4, 0])

#stage_midi.play([1, 0], [4, 0])

stage_midi.print()

stage_midi.json_save("stage_2.json")
stage_midi.json_load("stage_2.json")

stage_midi.print().filter(names=["note"]).print().disable().print().enable().print()
stage_midi.filter(names=["retrig"]).disable().print()

print("\n\nPLAY NOW\n\n")
stage_midi.play()
#stage_midi.play([1, 0], [4, 0])