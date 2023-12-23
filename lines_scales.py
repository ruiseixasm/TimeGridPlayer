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

import math
import lines as LINES

class Scales(LINES.Lines):

    def __init__(self):
        super().__init__()

    def chromatic(self, octaves):
        return self.scale("chromatic", octaves)
    
    def scale(self, name, root_note="C", octaves=3, center_midi_octave=None):
        root_note = int_to_key(root_note)
        root_note = convert_key(root_note)
        bin_scale = get_scale(name, root_note)
        local_scale_keys = scale_keys(bin_scale)
        block_size = len(local_scale_keys)
        for _ in range(block_size + 1):
            if local_scale_keys[0] == root_note:
                break
            local_scale_keys = local_scale_keys[1:block_size] + local_scale_keys[0:1]

        offset_blocks = int((octaves - 1) / 2)
        self._lines['offset'] = -(block_size * offset_blocks)
        self._lines['lines'] = local_scale_keys * octaves

        if center_midi_octave != None and isinstance(center_midi_octave, int):
            midi_octave = max(0, center_midi_octave + 1 - offset_blocks)
            for line_index in range(block_size * octaves):
                self._lines['lines'][line_index] = get_key_position_12(self._lines['lines'][line_index]) + midi_octave * 12
                if line_index > 0 and self._lines['lines'][line_index - 1] > self._lines['lines'][line_index]:
                    self._lines['lines'][line_index] += 12
                    midi_octave += 1

        return self
    
# GLOBAL CLASS METHODS

chromatic_keys = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
#                                            C#    D#       F#    G#    A#
scales = [ #                              C     D     E  F     G     A     B
    {'name': "chromatic",       'scale': [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]},
    {'name': "major",           'scale': [1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1]},
    {'name': "harmonic",        'scale': [1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 0, 1]},
    {'name': "melodic",         'scale': [1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1]},
    {'name': "octatonic_hw",    'scale': [1, 1, 0, 1, 1, 0, 1, 0, 0, 1, 1, 0]},
    {'name': "octatonic_wh",    'scale': [1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1]},
    {'name': "pentatonic_maj",  'scale': [1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 0]},
    {'name': "pentatonic_min",  'scale': [1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0]},
    {'name': "diminished",      'scale': [1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1]},
    {'name': "augmented",       'scale': [1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1]},
    {'name': "blues",           'scale': [1, 0, 0, 1, 0, 1, 1, 1, 0, 0, 1, 0]}
]

diatonic_rotations = [
    {'name': "major",       'mode': "C",    'rotation':   0},
    {'name': "dorian",      'mode': "D",    'rotation':  -2},
    {'name': "phrygian",    'mode': "E",    'rotation':  -4},
    {'name': "lydian",      'mode': "F",    'rotation':  -5},
    {'name': "mixolydian",  'mode': "G",    'rotation':  -7},
    {'name': "minor",       'mode': "A",    'rotation':  -9},
    {'name': "locrian",     'mode': "B",    'rotation': -11}
]

keys_conversion = {
    "CB": "B",
    "DB": "C#",
    "EB": "D#",
    "FB": "E",
    "GB": "F#",
    "AB": "G#",
    "BB": "A#",
    "E#": "F",
    "B#": "C"
}

def convert_key(key="C"):
    key_str = key.strip().upper()
    for dict_key, dict_value in keys_conversion.items():
        if dict_key == key_str:
            key_str = dict_value
            break
    return key_str

def get_scale(name, key="C"):
    name = name.strip().lower()
    rotation = None
    for diatonic_rotation in diatonic_rotations:
        if diatonic_rotation['name'] == name:
            rotation = diatonic_rotation['rotation']
            break
    if rotation != None:
        name = "major"
    bin_scale = scales[0]['scale'] # chromatic scale by default
    for scale in scales:
        if scale['name'] == name:
            bin_scale = scale['scale']
            break
    if rotation == None:
        rotation = 0
    rotation += get_key_position_12(key)
    bin_scale = rotate_bin_scale_12(bin_scale, rotation)
    return bin_scale # chromatic scale by default

def rotate_bin_scale_12(scale, amount):
    return scale[-amount:12] + scale[0:-amount] # from left to right

def scale_keys(bin_scale):
    keys = []
    for key in range(12):
        if bin_scale[key] == 1:
            keys.append(chromatic_keys[key])
    return keys

def get_key_position_12(key="C"): # C by default
    key_str = key.strip().upper()
    key_position = 0
    # ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    str_keys = ['C', '#', 'D', '#', 'E', 'F', '#', 'G', '#', 'A', '#', 'B']

    for index in range(12):
        if key_str[0] == str_keys[index]:
            key_position = index
            break

    if (len(key_str) > 1):
        if key_str[1] == '#':
            key_position += 1
        elif key_str[1] == 'B': # upper b meaning flat
            key_position -= 1

    return key_position % 12

def int_to_key(key_int=0):
    if isinstance(key_int, int):
        return chromatic_keys[ key_int % 12 ]
    return key_int

def note_to_steps(note="1/4", steps_per_note=16, resolution=6):
    if isinstance(note, str):
        try:
            return steps_per_note * float(note)
        except ValueError:
            match note:
                case "1": return steps_per_note
                case "1T": return round(12 * steps_per_note/16, resolution)
                case "1/2": return round(8 * steps_per_note/16, resolution)
                case "1/2T": return round(6 * steps_per_note/16, resolution)
                case "1/4": return round(4 * steps_per_note/16, resolution)
                case "1/4T": return round(3 * steps_per_note/16, resolution)
                case "1/8": return round(2 * steps_per_note/16, resolution)
                case "1/8T": return round(1.5 * steps_per_note/16, resolution)
                case "1/16": return round(1 * steps_per_note/16, resolution)
                case "1/16T": return round(0.75 * steps_per_note/16, resolution)
                case "1/32": return round(0.5 * steps_per_note/16, resolution)
                case "1/32T": return round(0.375 * steps_per_note/16, resolution)
                case "1/64": return round(0.25 * steps_per_note/16, resolution)
                case "1/64T": return round(0.1875 * steps_per_note/16, resolution)
                case "1/128": return round(0.125 * steps_per_note/16, resolution)
                case "1/128T": return round(0.09375 * steps_per_note/16, resolution)
                case default: return round(4 * steps_per_note/16, resolution)
    return note
        
def steps_to_note(steps=4, steps_per_note=16, resolution=6):
    if steps > steps_per_note:
        return str(steps/steps_per_note)
    else:
        if steps == steps_per_note: return "1"
        if steps == round(12 * steps_per_note/16, resolution): return "1T"
        if steps == round(8 * steps_per_note/16, resolution): return "1/2"
        if steps == round(6 * steps_per_note/16, resolution): return "1/2T"
        if steps == round(4 * steps_per_note/16, resolution): return "1/4"
        if steps == round(3 * steps_per_note/16, resolution): return "1/4T"
        if steps == round(2 * steps_per_note/16, resolution): return "1/8"
        if steps == round(1.5 * steps_per_note/16, resolution): return "1/8T"
        if steps == round(1 * steps_per_note/16, resolution): return "1/16"
        if steps == round(0.75 * steps_per_note/16, resolution): return "1/16T"
        if steps == round(0.5 * steps_per_note/16, resolution): return "1/32"
        if steps == round(0.375 * steps_per_note/16, resolution): return "1/32T"
        if steps == round(0.25 * steps_per_note/16, resolution): return "1/64"
        if steps == round(0.1875 * steps_per_note/16, resolution): return "1/64T"
        if steps == round(0.125 * steps_per_note/16, resolution): return "1/128"
        if steps == round(0.09375 * steps_per_note/16, resolution): return "1/128T"
        return "1/4"

def round_steps(steps=4, triplets=False):
    rounded_steps = round(math.log2(steps))**2
    if triplets:
        distance_rounded_steps = abs(rounded_steps - steps)
        lower_triplet_steps = rounded_steps * 3/4
        distance_lower_triplet_steps = abs(lower_triplet_steps - steps)
        if distance_lower_triplet_steps < distance_rounded_steps:
            rounded_steps = lower_triplet_steps
        upper_triplet_steps = lower_triplet_steps * 2
        distance_upper_triplet_steps = abs(upper_triplet_steps - steps)
        if distance_upper_triplet_steps < distance_rounded_steps:
            rounded_steps = upper_triplet_steps

    return rounded_steps
