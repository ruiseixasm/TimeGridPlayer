'''TimeGridPlayer - Time Grid Player Actions on a Staff
Original Copyright (c) 2023 Rui Seixas Monteiro. All right reserved.
This library is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 2.1 of the License, or (at your option) any later version.
This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
Lesser General Public License for more details.'''

import unittest
import midi_tools

notes_octave = [
    ["C", "C#", "d", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "b"],
    ["C", "Db", "d", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "b"]
]

expected_midi_keys = [ i for i in range(11*12) ]
for index in range(128, 132):
    expected_midi_keys[index] = 127

def test_sharp_notes():
    outputed_midi_keys = []
    for octave in range(-1, 10):
        for note in range(12):
            key = {'note': notes_octave[0][note], 'octave': octave}
            outputed_midi_keys.append(midi_tools.getMidiKey(key))
    #print(outputed_midi_keys)
    assert outputed_midi_keys == expected_midi_keys

def test_flat_notes():
    outputed_midi_keys = []
    for octave in range(-1, 10):
        for note in range(12):
            key = {'note': notes_octave[1][note], 'octave': octave}
            outputed_midi_keys.append(midi_tools.getMidiKey(key))
    #print(outputed_midi_keys)
    assert outputed_midi_keys == expected_midi_keys


if __name__ == "__main__":
    test_sharp_notes()
    test_flat_notes()