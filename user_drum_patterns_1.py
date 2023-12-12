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
master = stage_midi.add("master").set_time_signature(size_measures=4).set_tempo(126).player()


# Midi Note
note = stage_midi.add("note", type="Note").use_resource("loop").enable_resource().print()
master.rulers().add({'link': "note", 'lines': ["1/4"]}).add({'link': "note", 'lines': ["1/4"]}).add({'link': "note", 'lines': ["1/4"]}).add({'link': "note", 'lines': ["1/4"]})
master.rulers().copy().move_position([1, 0]).copy().move_position([2, 0]).copy().move_position([3, 0])
master.rulers().add({'link': "note.key", 'position': [0, 0], 'lines': [60]})
master.rulers().add({'link': "note.channel", 'position': [0, 0], 'lines': [10]}).print().print_lines(0, 15)
master.rulers().recall().copy().print().offset_lines(1).print().root().print().lines(1,5).print()
master.rulers().print().measures(0).print().root().print().beats(1).print().root().print().steps(8, 9, 12, 14).print()
#master.staff().print()

key_ruler = master.rulers().link_find("key")

drum_kit = {
    'drums': [33, 35, 36],
    'hi-hats': [42, 44, 46],
    'toms': [41, 43, 45, 47, 48, 50],
    'snares': [38, 40],
    'cymbals': [49, 51, 52, 55, 57, 59]
}

for key, values in drum_kit.items():
    print(key)
    for value in values:
        key_ruler.set_lines([value])
        master.play()

# for note in range(27, 88):
#     key_ruler.set_lines([note]).print_lines()
#     master.play()

stage_midi.print()