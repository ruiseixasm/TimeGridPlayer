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
stage_midi.print()

# Set Scales
scales = LINES_SCALES.Scales()
lines_major_scale = scales.scale("major", "A", 5).lines()
lines_minor_scale = scales.scale("minor", "D", 5).lines()

# add a master player to stage
master = stage_midi.add("master").last().set_time_signature(measures=16).set_tempo(125).last().player()

# Midi Clock
midi_clock = stage_midi.add("clock", type="Clock")

# Midi Note
note = stage_midi.add("note", type="Note").print().last().player()
master.rulers().add({'link': "note", 'position': [2, 4], 'lines': ["1/64"], 'offset': 2})
master.rulers().add({'link': "note", 'position': [3, 4], 'lines': ["1/64"]})
master.rulers().add({'link': "note.key", 'position': [2, 1], 'lines': lines_major_scale})
master.rulers().add({'link': "note.key", 'position': [1, 1], 'lines': ['c', 'c#', 'd', None, 'e', None]})
master.rulers().add({'link': "note.key", 'position': [3, 1], 'lines': ['d', 'c#', 'd', 'd#', 'e', None], 'offset': -1})
master.rulers().add({'link': "note.key", 'position': [2, "1/8"], 'lines': [None, 'c#', None, None, 'e', None]})
master.rulers().add({'link': "note.key", 'position': [1, 1], 'lines': ['a', 'b', 'd', None, 'f', None], 'offset': -2})
master.rulers().add({'link': "note.key", 'position': [3, 2], 'lines': [None, 'c#', 'd', 'd#', 'e', None]})
master.rulers().add({'link': "note.key", 'position': [4, 1], 'lines': ['a', 'b', 'd', None, 'f', None], 'offset': -4})
master.rulers().add({'link': "note.channel.staff", 'position': [1, 1], 'lines': [3]})
master.rulers().add({'link': "note.velocity.staff", 'position': [1, 1], 'lines': [120]})
master.rulers().print(0, 15)

# Retrigger
retrig = stage_midi.add("retrig", type="Retrigger").last().player()
master.rulers().add({'link': "retrig", 'position': [4, 1], 'lines': [28], 'offset': 4})
master.rulers().add({'link': "retrig", 'position': [6, 1], 'lines': [28], 'offset': 4})
master.rulers().add({'link': "retrig.key", 'position': [2, 1], 'lines': lines_major_scale})
master.rulers().add({'link': "retrig.rate.staff", 'position': [2, 1], 'lines': ["1/16"]})
master.rulers().add({'link': "retrig.channel.staff", 'position': [1, 1], 'lines': [3]})

# Arpeggiator
arpeggio = stage_midi.add("arpeggio", type="Arpeggiator").last().player()
master.rulers().add({'link': "arpeggio", 'position': [9, 1], 'lines': [100, "7", "7", "6.5"], 'offset': 4})
master.rulers().add({'link': "arpeggio.key", 'position': [2, 1], 'lines': lines_major_scale})
master.rulers().add({'link': "arpeggio.channel", 'position': [1, 1], 'lines': [3]})
master.rulers().add({'link': "arpeggio.velocity.staff", 'position': [1, 1], 'lines': [120]})
master.rulers().add({'link': "arpeggio.gate.auto", 'position': [8, 1], 'lines': [.25, .10, .25, .10, .25, .10], 'offset': 3})
master.rulers().add({'link': "arpeggio.gate.auto", 'position': [14, 1], 'lines': [1, .90, .50, .80], 'offset': 3})
master.rulers().add({'link': "arpeggio.rate.auto", 'position': [7, 1], 'lines': [.25, 4, 1, .5, 2, 8], 'offset': 3})
master.rulers().add({'link': "arpeggio.rate.auto", 'position': [14, 1], 'lines': [4, 4, 4, 1], 'offset': 3})

# master.rulers().filter(type="actions").sort().print().print(0, 15)
# master.rulers().filter(type="arguments").sort().print().print(0, 15)
master.rulers().arguments().print(0, 15).link_find(".staff").print()

# SPREAD MIDI COMPOSITION
spread = stage_midi.add("spread", type="Master").last().set_time_signature(measures=1).last().player()

spread.rulers().add({'link': "note", 'position': [1, 1], 'lines': ["1/32"]}).last().duplicate(7).duplicate().distribute("1").spread().print() # WHERE MULTIPLE ACTION NOTES ARE SPREAD (REPEATED)
spread.rulers().add({'link': "note.key", 'position': [1, 1], 'lines': lines_minor_scale}).print(0, 15)
spread.rulers().add({'link': "note.channel.staff", 'position': [1, 1], 'lines': [3]})
spread.rulers().add({'link': "note.velocity.staff", 'position': [1, 1], 'lines': [120]})
spread.rulers().filter(type="arguments").print(0, 15)
#spread.play()
master.rulers().add({'link': "spread", 'position': [1, 1], 'lines': [1]})

# CC MIDI MESSAGE
cc = stage_midi.add("cc", type="ControlChange").print().last().player()
master.rulers().add({'link': "cc", 'position': [3, 4], 'lines': [1]})
master.rulers().add({'link': "cc.channel.staff", 'position': [1, 1], 'lines': [3]})
master.rulers().add({'link': "cc.value.auto", 'position': [3, 1], 'lines': [0]})
master.rulers().add({'link': "cc.value.auto", 'position': [5, 1], 'lines': [127]})
master.rulers().add({'link': "cc.value.auto", 'position': [8, 1], 'lines': [64]})


stage_midi.use_resource("loop").enable_resource()
stage_midi.set_time_signature(pulses_per_quarternote=48)
stage_midi.print()

stage_midi.json_save("stage_2.json")
stage_midi.json_load("stage_2.json")

#stage_midi.print().filter(names=["note"]).print().disable().print().enable().print()
#stage_midi.filter(names=["retrig"]).disable().print()

print("\n\nPLAY NOW\n\n")
stage_midi.play()
#stage_midi.play([1, 1], [4, 1])