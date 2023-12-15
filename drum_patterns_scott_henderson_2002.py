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
master = stage_midi.add("master").last().set_time_signature(size_measures=16).set_tempo(80).player()
drum_pattern_1 = stage_midi.add("drum_pattern_1").last().set_time_signature(size_measures=1).player()

# Midi Note
drum_kit = stage_midi.add("drum_kit", type="Note").use_resource("loop").enable_resource().print()
drum_pattern_1.rulers().add({'link': "drum_kit.key", 'lines': [42, 38, 35]})\
    .add({'link': "drum_kit.velocity", 'lines': [50, 100, 100]}).add({'link': "drum_kit.channel.staff", 'lines': [10]}).print_lines()
drum_pattern_1.rulers().empty().add({'link': "drum_kit", 'lines': ["1/16"]}).repeat(7, "1/8").print_lines()
drum_pattern_1.rulers().empty().add({'link': "drum_kit", 'position': [0, 2], 'lines': ["1/16"], 'offset': 1}).copy().set_position([0, 12])
drum_pattern_1.rulers().empty().add({'link': "drum_kit", 'lines': ["1/16"], 'offset': 2}).copy().slide_position("1/2T")
drum_pattern_1.rulers().print().print_lines()

master.rulers().add({'link': "drum_pattern_1.repeat", 'lines': [15]}).add({'link': "drum_pattern_1"}).print_lines()

# master.staff().print()

stage_midi.set_time_signature(pulses_per_quarter_note=48)

# master.staff().print()

master.play()

# for note in range(27, 88):
#     key_ruler.set_lines([note]).print_lines()
#     master.play()
