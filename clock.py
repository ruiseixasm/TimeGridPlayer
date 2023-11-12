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

import time

class Clock():
    def __init__(self, player, beats_per_minute=120, pulses_per_quarter_note = 24, steps_per_beat=4):
        """create an empty observer list"""
        self._player = player
        self.setClock(beats_per_minute, pulses_per_quarter_note, steps_per_beat)

    def getClockTempo(self):
        return self._tempo

    def getPulseDuration(self, beats_per_minute, pulses_per_beat): # in seconds
        return 60.0 / (pulses_per_beat * beats_per_minute)
    
    def setClock(self, beats_per_minute=120, pulses_per_quarter_note = 24, steps_per_beat=4):
        pulses_per_beat = steps_per_beat * round(converter_PPQN_PPB(pulses_per_quarter_note) / steps_per_beat)

        self._tempo = {'beats_per_minute': beats_per_minute, 'steps_per_beat': steps_per_beat, 'pulses_per_quarter_note': pulses_per_quarter_note, \
                      'pulses_per_beat': pulses_per_beat}
        self._pulse_duration = self.getPulseDuration(beats_per_minute, pulses_per_beat) # in seconds

    def start(self, non_fast_forward_range_pulses = []): # Where a non fast forward range is set

        self._non_fast_forward_range_pulses = None
        if non_fast_forward_range_pulses != None and non_fast_forward_range_pulses != [] and len(non_fast_forward_range_pulses) == 2:
            self._non_fast_forward_range_pulses = non_fast_forward_range_pulses

        self._next_pulse = 0
        self._next_pulse_time = time.time()

        self._tick = {'tempo': self._tempo, 'pulse': None, 'clock': self, 'player': self._player, 'fast_forward': False}
        
    def stop(self, FORCE_STOP = False):
        ...

    def tick(self):

        if not self._next_pulse_time > time.time():

            self._tick['pulse'] = self._next_pulse
            self._tick['fast_forward'] = self._non_fast_forward_range_pulses != None \
                and (self._non_fast_forward_range_pulses[0] != None and self._next_pulse < self._non_fast_forward_range_pulses[0] \
                or self._non_fast_forward_range_pulses[1] != None and not self._next_pulse < self._non_fast_forward_range_pulses[1])
        
            if not self._tick['fast_forward']:
                self._next_pulse_time += self._pulse_duration
            else:
                self._next_pulse_time = time.time()
            self._next_pulse += 1

        else:
            self._tick['pulse'] = None

        return self._tick

def converter_PPQN_PPB(pulses_per_quarter_note=24, steps_per_beat=4): # 4 steps per beat is a constant
    '''Converts Pulses Per Quarter Note into Pulses Per Beat'''
    STEPS_PER_QUARTER_NOTE = 4
    pulses_per_beat = pulses_per_quarter_note * (steps_per_beat / STEPS_PER_QUARTER_NOTE)
    return int(pulses_per_beat)
