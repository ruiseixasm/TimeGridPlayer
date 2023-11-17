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
    {'name': "major", 'mode': "C", 'rotation': 0},
    {'name': "dorian", 'mode': "D", 'rotation': -2},
    {'name': "phrygian", 'mode': "E", 'rotation': -4},
    {'name': "lydian", 'mode': "F", 'rotation': -5},
    {'name': "mixolydian", 'mode': "G", 'rotation': -7},
    {'name': "minor", 'mode': "A", 'rotation': -9},
    {'name': "locrian", 'mode': "B", 'rotation': -11}
]

class Scales(LINES.Lines):

    def __init__(self):
        super().__init__()

    def chromatic(self, size):
        return self.scale("chromatic", size)
    
    def scale(self, name, size):
        bin_scale = get_scale(name)
        local_scale_keys = scale_keys(bin_scale)
        block_size = len(local_scale_keys)
        offset_blocks = int(size / 2)
        self._lines['offset'] = -(block_size * offset_blocks)
        self._lines['lines'] = local_scale_keys * size

        return self
    
# GLOBAL CLASS METHODS

def get_scale(name):
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
    if rotation != None:
        bin_scale = rotate(bin_scale, rotation)
    return bin_scale # chromatic scale by default

def rotate(scale, amount):
    return scale[-amount:12] + scale[0:-amount] # from left to right

def scale_keys(bin_scale):
    keys = []
    for key in range(12):
        if bin_scale[key] == 1:
            keys.append(chromatic_keys[key])
    return keys
