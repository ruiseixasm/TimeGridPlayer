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

    def __init__(self, size_measures = 8, beats_per_measure = 4, steps_per_beat = 4, pulses_per_beat = 24, play_range=[[], []]):

        self.staff = []
        self.total_pulses = 0
        self.play_range = [[], []]
        if play_range != [[], []]:
            self.setPlayRange(start=play_range[0], finish=play_range[1])
        self.setStaff(size_measures, beats_per_measure, steps_per_beat, pulses_per_beat)

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
                'arguments': {'enabled': 0, 'total': 0},
                'actions': {'enabled': 0, 'total': 0}
            }
            self.staff.append(staff_pulse)

        if self.total_pulses > 0:
            for staff_pulse in old_staff:
                for ruler_type in ['arguments', 'actions']:
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
            if start == [] or self.play_range[0] == []:
                self.play_range[0] = [0, 0]
            elif start == None and self.play_range[0] != []:
                start_pulses = min(self.total_pulses - 1, self.pulses(self.play_range[0]))
                self.play_range[0] = self.position(start_pulses)
            elif start != None:
                start_pulses = min(self.total_pulses - 1, self.pulses(start))
                self.play_range[0] = self.position(start_pulses)

            if finish == [] or self.play_range[1] == []:
                finish_pulses = self.total_pulses - 1
                self.play_range[1] = self.position(finish_pulses)
            elif finish == None and self.play_range[1] != []:
                start_pulses = min(self.total_pulses - 1, self.pulses(self.play_range[1]))
                self.play_range[1] = self.position(start_pulses)
            elif finish != None:
                start_pulses = self.pulses(self.play_range[0])
                finish_pulses = max(start_pulses, min(self.total_pulses - 1, self.pulses(start)))
                self.play_range[1] = self.position(finish_pulses)

        return self
    
    def print(self):
        if len(self.staff) > 0:
            for staff_pulse in self.staff:
                print(staff_pulse)
        else:
            print("[EMPTY]")
        return self
    
    def print_staff_sums(self, staff_list): # outputs single staff pulse
        staff_list_pulses = len(staff_list)
        copy_staff_pulse = staff_list[0].copy() # pulse content copy
        copy_staff_pulse['arguments'] = copy_staff_pulse['arguments'].copy() # arguments content copy
        copy_staff_pulse['actions'] = copy_staff_pulse['actions'].copy() # actions content copy
        if staff_list_pulses > 0:
            for pulse in range(1, staff_list_pulses):
                copy_staff_pulse['arguments']['enabled'] += staff_list[pulse]['arguments']['enabled']
                copy_staff_pulse['arguments']['total'] += staff_list[pulse]['arguments']['total']
                copy_staff_pulse['actions']['enabled'] += staff_list[pulse]['actions']['enabled']
                copy_staff_pulse['actions']['total'] += staff_list[pulse]['actions']['total']
            print(copy_staff_pulse)
        else:
            print("[EMPTY]")
        return self
    
    def print_level_sums(self, pulse=0, level=0):
        if self.len() > 0:
            staff_pulse = self.staff[pulse]
            match level:
                case 0:
                    filtered_list = self.filter_list(measure=staff_pulse['measure'])
                    self.print_staff_sums(filtered_list)
                case 1:
                    filtered_list = self.filter_list(measure=staff_pulse['measure'], beat=staff_pulse['beat'])
                    self.print_staff_sums(filtered_list)
                case 2:
                    filtered_list = self.filter_list(measure=staff_pulse['measure'], beat=staff_pulse['beat'], step=staff_pulse['step'])
                    self.print_staff_sums(filtered_list)
                case 3:
                    self.print_staff_sums(staff_pulse)
                case _: # default
                    print("[EMPTY]")
        else:
            print("[EMPTY]")
        return self
    
    def pulseRemainders(self, pulse=0):
        return {
            'measure': pulse % (self.pulses_per_beat * self.beats_per_measure),
            'beat': pulse % self.pulses_per_beat,
            'step': pulse % (self.pulses_per_beat / self.steps_per_beat),
            'pulse': 0 # by definition is pulse % pulse = 0
        }
    
    def signature(self):
        return {
            'beats_per_measure': self.beats_per_measure,
            'steps_per_beat': self.steps_per_beat,
            'pulses_per_beat': self.pulses_per_beat,
            'pulses_per_step': self.pulses_per_beat / self.steps_per_beat
        }

    def list(self):
        return self.staff
    
    def len(self):
        return self.total_pulses

    def pulses(self, position=[0, 0]): # position: [measure, step]
        return position[0] * self.beats_per_measure * self.pulses_per_beat + round(position[1] * self.pulses_per_beat / self.steps_per_beat)

    def playRange(self):
        return self.play_range

    def playRange_pulses(self, play_range=[[], []]):
        if play_range == [[], []]:
            return [self.pulses(self.play_range[0]), self.pulses(self.play_range[1])]
        return [self.pulses(play_range[0]), self.pulses(play_range[1])]

    def position(self, pulses):
        measures = int(pulses / (self.pulses_per_beat * self.beats_per_measure))
        steps = pulses * self.steps_per_beat / self.pulses_per_beat % (self.steps_per_beat * self.beats_per_measure)
        if pulses < 0:
            steps = -(-pulses * self.steps_per_beat / self.pulses_per_beat % (self.steps_per_beat * self.beats_per_measure))
        return [measures, steps]
    
    def add(self, rulers, enabled_one=1, total_one=1):
        for ruler in rulers:
            pulses = self.pulses(ruler['position'])
            if pulses < self.len():
                if ruler['on_staff']:
                    if ruler['enabled']:
                        self.staff[pulses][ruler['type']]['enabled'] += enabled_one
                    self.staff[pulses][ruler['type']]['total'] += total_one
        return self
    
    def filter_list(self, measure=None, beat=None, step=None, pulse=None):
        filtered_list = self.staff[:]
        if measure != None:
            filtered_list = [
                pulses for pulses in filtered_list if pulses['measure'] == measure
            ]
        if beat != None:
            filtered_list = [
                pulses for pulses in filtered_list if pulses['beat'] == beat
            ]
        if step != None:
            filtered_list = [
                pulses for pulses in filtered_list if pulses['step'] == step
            ]
        if pulse != None:
            filtered_list = [
                pulses for pulses in filtered_list if pulses['pulse'] == pulse
            ]
        return filtered_list

    def remove(self, rulers, enabled_one=-1, total_one=-1):
        return self.add(rulers, enabled_one, total_one)
    
    def enable(self, rulers):
        return self.add(rulers, total_one=0)

    def disable(self, rulers):
        return self.remove(rulers, total_one=0)
    
    def arguments(self):
        total_arguments = {'enabled': 0, 'total': 0}
        for staff_pulse in self.staff:
            total_arguments['enabled'] += staff_pulse['arguments']['enabled']
            total_arguments['total'] += staff_pulse['arguments']['total']
        return total_arguments

    def actions(self):
        total_actions = {'enabled': 0, 'total': 0}
        for staff_pulse in self.staff:
            total_actions['enabled'] += staff_pulse['actions']['enabled']
            total_actions['total'] += staff_pulse['actions']['total']
        return total_actions

    def clear(self):
        for staff_pulse in self.staff:
            staff_pulse['arguments'] = {'enabled': 0, 'total': 0}
            staff_pulse['actions'] = {'enabled': 0, 'total': 0}
        return self

    
    def str_position(self, position):
        return str(position[0]) + " " + str(round(position[1], 6))
   