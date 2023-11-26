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

import lines as LINES

class Scales(LINES.Lines):

    def __init__(self):
        super().__init__()

    def chromatic(self, size):
        return self.scale("chromatic", size)
    
    def scale(self, name, root_note="C", size=3):
        root_note = convert_key(root_note)
        bin_scale = get_scale(name, root_note)
        local_scale_keys = scale_keys(bin_scale)
        block_size = len(local_scale_keys)
        for _ in range(block_size + 1):
            if local_scale_keys[0] == root_note:
                break
            local_scale_keys = local_scale_keys[-1:block_size] + local_scale_keys[0:-1]

        offset_blocks = int((size - 1) / 2)
        self._lines['offset'] = -(block_size * offset_blocks)
        self._lines['lines'] = local_scale_keys * size

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
