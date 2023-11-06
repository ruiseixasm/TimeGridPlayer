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

def position_gt(left_position, right_position):
    if len(left_position) == 2 and len(right_position) == 2:
        if (left_position[0] > right_position[0]):
            return True
        if (left_position[0] == right_position[0]):
            if (left_position[1] > right_position[1]):
                return True
    return False

def position_lt(left_position, right_position):
    if len(left_position) == 2 and len(right_position) == 2:
        if (left_position[0] < right_position[0]):
            return True
        if (left_position[0] == right_position[0]):
            if (left_position[1] < right_position[1]):
                return True
    return False
    
class Staff:

    def __init__(self, steps = 0, frames_step = 0, play_range=[]):

        self.staff = []
        self.total_pulses = 0
        self.play_range_new = [[], []]
        self.setStaff(size_measures = 8, beats_per_measure = 4, steps_per_beat = 4, pulses_per_beat = 24)

        # TO BE DELETED

        self.steps = max(1, steps)
        self.frames_step = max(1, frames_step)
        self.total_sequences = self.steps*self.frames_step # total amount like the len()
        self.play_range = [
            self.position(0), self.position(self.total_sequences)
        ]
        if len(play_range) == 2:
            if self.position_lt(play_range[0], self.play_range[1]):
                self.play_range[0] = play_range[0]
            if self.position_lt(play_range[1], self.play_range[1]) and not self.position_lt(play_range[1], self.play_range[0]):
                self.play_range[1] = play_range[1]

        self.staff_grid = []
        self.generate()

    def setStaff(self, size_measures = 8, beats_per_measure = 4, steps_per_beat = 4, pulses_per_beat = 24):

        self.size_total_measures = size_measures            # staff total size
        self.beats_per_measure = beats_per_measure          # beats in each measure
        self.steps_per_beat = steps_per_beat                # how many steps take each beat
        self.pulses_per_beat = pulses_per_beat              # sets de resolution of clock pulses
        
        self.total_pulses = self.size_total_measures * self.beats_per_measure * self.pulses_per_beat

        old_staff = self.staff[:]
        self.staff = []
        for pulse in range(self.total_pulses):
            staff_pulse = {
                'measure': int(pulse / (self.pulses_per_beat * self.beats_per_measure)),
                'beat': int(pulse / self.pulses_per_beat) % self.beats_per_measure,
                'step': int(pulse * self.steps_per_beat / self.pulses_per_beat) % (self.steps_per_beat * self.beats_per_measure),
                'pulse': pulse,
                'keys': {'enabled': 0, 'total': 0},
                'actions': {'enabled': 0, 'total': 0}
            }
            self.staff.append(staff_pulse)

        if self.total_pulses > 0:
            for staff_pulse in old_staff:
                for ruler_type in ['keys', 'actions']:
                    if staff_pulse[ruler_type]['total'] > 0:
                        position_pulses = self.pulses([staff_pulse['measure'], staff_pulse['step']])
                        size_total_pulses = self.size_total_measures * self.beats_per_measure * self.pulses_per_beat
                        if not position_pulses < 0 and position_pulses < size_total_pulses:
                            self.staff[position_pulses][ruler_type]['enabled'] = staff_pulse[ruler_type]['enabled']
                            self.staff[position_pulses][ruler_type]['total'] = staff_pulse[ruler_type]['total']

        self.setPlayRange(start=None, finish=None)
        return self
    
    def setPlayRange(self, start=[], finish=[]):
        if self.total_pulses > 0:
            if start == None and self.play_range_new[0] != []:
                start_pulses = min(self.total_pulses - 1, self.pulses(self.play_range_new[0]))
                self.play_range_new[0] = self.position_new(start_pulses)
            elif start == []:
                self.play_range_new[0] = [0, 0]
            elif start != None:
                start_pulses = min(self.total_pulses - 1, self.pulses(start))
                self.play_range_new[0] = self.position_new(start_pulses)
            if finish == None and self.play_range_new[1] != []:
                start_pulses = min(self.total_pulses - 1, self.pulses(self.play_range_new[1]))
                self.play_range_new[1] = self.position_new(start_pulses)
            elif finish == []:
                finish_pulses = self.total_pulses - 1
                self.play_range_new[1] = self.position_new(finish_pulses)
            elif finish != None:
                start_pulses = self.pulses(self.play_range_new[0])
                finish_pulses = max(start_pulses, min(self.total_pulses - 1, self.pulses(start)))
                self.play_range_new[1] = self.position_new(finish_pulses)

        return self
    
    def print_new(self):
        if len(self.staff) > 0:
            for staff_pulse in self.staff:
                print(staff_pulse)
        else:
            print("[EMPTY]")
        return self
    
    def signature_new(self):
        return {
            'beats_per_measure': self.beats_per_measure,
            'steps_per_beat': self.steps_per_beat,
            'pulses_per_beat': self.pulses_per_beat
        }

    def list(self):
        return self.staff
    
    def len_new(self):
        return self.total_pulses

    def pulses(self, position=[None, None]): # position: [measure, step]
        return position[0] * self.beats_per_measure * self.pulses_per_beat + round(position[1] * self.pulses_per_beat / self.steps_per_beat)

    def position_new(self, pulses):
        measures = int(pulses / (self.pulses_per_beat * self.beats_per_measure))
        steps = round(pulses * self.steps_per_beat / self.pulses_per_beat % (self.steps_per_beat * self.beats_per_measure), 6)
        if pulses < 0:
            steps = -round(-pulses * self.steps_per_beat / self.pulses_per_beat % (self.steps_per_beat * self.beats_per_measure), 6)
        return [measures, steps]
    
    def add_new(self, rulers, enabled_one=1, total_one=1):
        for ruler in rulers:
            pulses = self.pulses(ruler['position'])
            if pulses < len(self):
                if ruler['on_staff']:
                    if ruler['enabled']:
                        self.staff[pulses][ruler['type']]['enabled'] += enabled_one
                    self.staff[pulses][ruler['type']]['total'] += total_one
        return self

    def remove_new(self, rulers, enabled_one=-1, total_one=-1):
        return self.add_new(rulers, enabled_one, total_one)
    
    def enable_new(self, rulers):
        return self.add_new(rulers, total_one=0)

    def disable_new(self, rulers):
        return self.remove_new(rulers, total_one=0)
    
    def keys_new(self):
        total_keys = {'enabled': 0, 'total': 0}
        for staff_pulse in self.staff:
            total_keys['enabled'] += staff_pulse['keys']['enabled']
            total_keys['total'] += staff_pulse['keys']['total']
        return total_keys

    def actions_new(self):
        total_actions = {'enabled': 0, 'total': 0}
        for staff_pulse in self.staff:
            total_actions['enabled'] += staff_pulse['actions']['enabled']
            total_actions['total'] += staff_pulse['actions']['total']
        return total_actions

    def playRange(self):
        return self.play_range_new

    def clear_new(self):
        for staff_pulse in self.staff:
            staff_pulse['keys'] = {'enabled': 0, 'total': 0}
            staff_pulse['actions'] = {'enabled': 0, 'total': 0}
        return self













    # TO BE DELETED


    def position_gt(self, left_position, right_position):
        if len(left_position) == 2 and len(right_position) == 2:
            if (left_position[0] > right_position[0]):
                return True
            if (left_position[0] == right_position[0]):
                if (left_position[1] > right_position[1]):
                    return True
        return False

    def position_lt(self, left_position, right_position):
        if len(left_position) == 2 and len(right_position) == 2:
            if (left_position[0] < right_position[0]):
                return True
            if (left_position[0] == right_position[0]):
                if (left_position[1] < right_position[1]):
                    return True
        return False
    
    def str_position(self, position):
        return str(position[0]) + "." + str(position[1])
    
    
    def generate(self):
        self.staff_grid = []
        for sequence in range(self.total_sequences):
            staff_position = {
                'sequence': sequence,
                'position': self.position(sequence),
                'keys': {'enabled': 0, 'total': 0},
                'actions': {'enabled': 0, 'total': 0}
            }
            self.staff_grid.append(staff_position)
        return self
    
    def signature(self):
        return {'steps': self.steps, 'frames_step': self.frames_step}

    def grid(self, sequence):
        if (len(self.staff_grid) > 0):
            return self.staff_grid[sequence]
        
    def add(self, rulers, enabled_one=1, total_one=1):
        for ruler in rulers:
            sequence = self.sequence(ruler['position'])
            if sequence < self.total_sequences:
                if ruler['on_staff']:
                    if ruler['enabled']:
                        self.staff_grid[sequence][ruler['type']]['enabled'] += enabled_one
                    self.staff_grid[sequence][ruler['type']]['total'] += total_one
        return self

    def remove(self, rulers, enabled_one=-1, total_one=-1):
        return self.add(rulers, enabled_one, total_one)
    
    def enable(self, rulers):
        return self.add(rulers, total_one=0)

    def disable(self, rulers):
        return self.remove(rulers, total_one=0)
    
    def keys(self):
        total_keys = {'enabled': 0, 'total': 0}
        for staff_sequence in self.staff_grid:
            total_keys['enabled'] += staff_sequence['keys']['enabled']
            total_keys['total'] += staff_sequence['keys']['total']
        return total_keys

    def actions(self):
        total_actions = {'enabled': 0, 'total': 0}
        for staff_sequence in self.staff_grid:
            total_actions['enabled'] += staff_sequence['actions']['enabled']
            total_actions['total'] += staff_sequence['actions']['total']
        return total_actions

    def sequence(self, position):
        return position[0] * self.frames_step + position[1]
    
    def len(self):
        return self.total_sequences
    
    def position(self, sequence):
        steps = int(sequence / self.frames_step)
        frames = sequence % self.frames_step
        if sequence < 0:
            frames = -(-sequence % self.frames_step)
        return [steps, frames]
    
    def range(self):
        return self.play_range

    def clear(self):
        for staff_position in self.staff_grid:
            staff_position['keys'] = 0
            staff_position['actions'] = 0
        return self

    def print(self):
        if len(self.staff_grid) > 0:
            for staff_position in self.staff_grid:
                print(staff_position)
        else:
            print("[EMPTY]")
        print("\n")
        