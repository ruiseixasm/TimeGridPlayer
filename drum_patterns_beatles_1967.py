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
master = stage_midi.add("master").last().set_time_signature(size_measures=3).set_tempo(126).player()

# Midi Note
drums = stage_midi.add("drums", type="Note").use_resource("loop").enable_resource().print()
master.rulers().add({'link': "drums.key", 'lines': [46, 40, 36]})\
    .add({'link': "drums.channel.staff", 'lines': [10]}).add({'link': "drums.repeat.staff", 'lines': [2]}).print_lines()
master.rulers().empty().populate({'link': "drums", 'lines': ["1/8"]}, "1").set_lines(["1/16"]).print_lines()
master.rulers().empty().add({'link': "drums", 'position': [0, 4], 'lines': ["1/16"], 'offset': 1}).copy().set_position([0, 12])
master.rulers().empty().add({'link': "drums", 'lines': ["1/16"], 'offset': 2}).copy().set_position([0, 8]).copy().set_position([0, 10])
master.rulers().print().print_lines()

stage_midi.print()

master.play()

# for note in range(27, 88):
#     key_ruler.set_lines([note]).print_lines()
#     master.play()
