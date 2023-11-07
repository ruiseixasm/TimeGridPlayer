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

import unittest
import midi_tools

keys_octave = [
    ["C", "C#", "d", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "b"],
    ["C", "Db", "d", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "b"]
]

# small comment just to test the git merge ability

expected_midi_notes = [ i for i in range(11*12) ]
for index in range(128, 132):
    expected_midi_notes[index] = 127

def test_sharp_keys():
    outputed_midi_notes = []
    for octave in range(-1, 10):
        for key in range(12):
            note = {'key': keys_octave[0][key], 'octave': octave}
            outputed_midi_notes.append(midi_tools.getMidiNote(note))
    #print(outputed_midi_notes)
    assert outputed_midi_notes == expected_midi_notes

def test_flat_keys():
    outputed_midi_notes = []
    for octave in range(-1, 10):
        for key in range(12):
            note = {'key': keys_octave[1][key], 'octave': octave}
            outputed_midi_notes.append(midi_tools.getMidiNote(note))
    #print(outputed_midi_notes)
    assert outputed_midi_notes == expected_midi_notes


if __name__ == "__main__":
    test_sharp_keys()
    test_flat_keys()