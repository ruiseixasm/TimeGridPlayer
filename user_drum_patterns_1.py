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
master = stage_midi.add("master").set_time_signature(size_measures=1).set_tempo(125)


# Midi Note
note = stage_midi.add("note", type="Note").use_resource("loop").enable_resource().print()

master.rulers().add({'link': "note", 'position': [0, 0], 'lines': [1]}).duplicate(3).distribute("1").print().print_lines(0, 15)
master.rulers().add({'link': "note.key", 'position': [0, 0], 'lines': [60]}).print_lines(0, 15)
master.rulers().add({'link': "note.channel", 'position': [0, 0], 'lines': [10]}).print_lines(0, 15)

for note in range(128):
    ...

master.play()

stage_midi.print()