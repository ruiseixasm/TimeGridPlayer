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
hat_open = stage_midi.add("hat_open").last().set_time_signature(size_measures=1).player()
snare = stage_midi.add("snare").last().set_time_signature(size_measures=1).player()
kick = stage_midi.add("kick").last().set_time_signature(size_measures=1).player()

# Midi Resource
drum_instrument = stage_midi.add("drum_instrument", type="Note").use_resource("loop").enable_resource().print()

# Ruler arguments and actions
hat_open.rulers()\
    .add({'link': "drum_instrument.key.staff", 'lines': [42]})\
    .add({'link': "drum_instrument.velocity", 'lines': [60, 80]})\
    .add({'link': "drum_instrument.channel.staff", 'lines': [10]})\
    .add({'link': "drum_instrument", 'lines': ["1/16"]})

snare.rulers().add(hat_open.rulers()).link_find("velocity").set_lines([100]).root().link_find("key").set_lines([38])
kick.rulers().add(snare.rulers()).link_find("key").set_lines([35])

# ruler actions
hat_open.rulers().actions().print().repeat(7, "1/8").print().odd().print().offset(1).root().print_lines()
snare.rulers().actions().move_position([0, 4]).copy().set_position([0, 12]).root().print_lines()
kick.rulers().actions().propagate(16, "1/4").root().print_lines()

# master.staff().print()
master.rulers()\
    .add({'link': "hat_open", 'position': [0, 0], 'lines': ["1"]}).add({'link': "hat_open.repeat", 'position': [0, 0], 'lines': [15]})\
    .add({'link': "snare", 'position': [0, 0], 'lines': ["1"]}).add({'link': "snare.repeat", 'position': [0, 0], 'lines': [15]})\
    .add({'link': "kick", 'position': [0, 0], 'lines': ["1"]}).add({'link': "kick.repeat", 'position': [0, 0], 'lines': [15]})\
    .print_lines()
stage_midi.set_time_signature(pulses_per_quarter_note=48)

# master.staff().print()

master.play()

# for note in range(27, 88):
#     key_ruler.set_lines([note]).print_lines()
#     master.play()
