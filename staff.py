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

import rulers as Rulers

class Staff:

    def __init__(self, size_measures = 8, beats_per_measure = 4, steps_per_beat = 4, pulses_per_beat = 24, play_range=[[], []]):

        self._rulers = Rulers.Rulers(staff=self)
        self._staff = []
        self.total_pulses = 0
        self.string_top_lengths = {'measure': 0, 'beat': 0, 'step': 0, 'pulse': 0, 'arguments_enabled': 0, 'arguments_total': 0, 'actions_enabled': 0, 'actions_total': 0}
        self.string_top_length = 0
        self.play_range = [[], []]
        if play_range != [[], []]:
            self.setPlayRange(start=play_range[0], finish=play_range[1])
        self.setStaff(size_measures, beats_per_measure, steps_per_beat, pulses_per_beat)

    def _getStaffSums(self, staff_list): # outputs single staff pulse
        staff_list_sums = {'arguments': {'enabled': 0, 'total': 0}, 'actions': {'enabled': 0, 'total': 0}}
        for staff_pulse in staff_list:
            staff_list_sums['arguments']['enabled'] += staff_pulse['arguments']['enabled']
            staff_list_sums['arguments']['total'] += staff_pulse['arguments']['total']
            staff_list_sums['actions']['enabled'] += staff_pulse['actions']['enabled']
            staff_list_sums['actions']['total'] += staff_pulse['actions']['total']

        return staff_list_sums
    
    def _setTopLengths(self):
        return self._setTopLengths_Values()._setTopLengths_Sums()

    def _setTopLengths_Values(self):

        for key, value in self.string_top_lengths.items():
            if key == 'measure' or key == 'beat' or key == 'step' or key == 'pulse':
                self.string_top_length = 0

        for staff_pulse in self._staff: # get maximum sizes
            for key, value in staff_pulse.items():
                if key == 'measure' or key == 'beat' or key == 'step' or key == 'pulse':
                    self.string_top_lengths[key] = max(self.string_top_lengths[key], len(f"{value}"))

        self.string_top_length = 0
        for value in self.string_top_lengths.values():
            self.string_top_length += value

        return self
    
    def _setTopLengths_Sums(self):

        staff_list_sums = self._getStaffSums(self._staff)
        self.string_top_lengths['arguments_enabled'] = staff_list_sums['arguments']['enabled']
        self.string_top_lengths['arguments_total'] = staff_list_sums['arguments']['total']
        self.string_top_lengths['actions_enabled'] = staff_list_sums['actions']['enabled']
        self.string_top_lengths['actions_total'] = staff_list_sums['actions']['total']

        self.string_top_length = 0
        for value in self.string_top_lengths.values():
            self.string_top_length += value

        return self
    
    def actions(self):
        total_actions = {'enabled': 0, 'total': 0}
        for staff_pulse in self._staff:
            total_actions['enabled'] += staff_pulse['actions']['enabled']
            total_actions['total'] += staff_pulse['actions']['total']
        return total_actions

    def add(self, rulers, enabled_one=1, total_one=1):
        for ruler in rulers:
            pulses = self.pulses(ruler['position'])
            if pulses < self.len():
                if ruler['on_staff']:
                    if ruler['enabled']:
                        self._staff[pulses][ruler['type']]['enabled'] += enabled_one
                    self._staff[pulses][ruler['type']]['total'] += total_one
        
        return self._setTopLengths_Sums()
    
    def addPositions(self, position_1=[0, 0], position_2=[0, 0]):

        steps_1 = self.steps(position_1)
        steps_2 = self.steps(position_2)
        total_steps = steps_1 + steps_2
        
        return self.position(steps=total_steps)

    def arguments(self):
        total_arguments = {'enabled': 0, 'total': 0}
        for staff_pulse in self._staff:
            total_arguments['enabled'] += staff_pulse['arguments']['enabled']
            total_arguments['total'] += staff_pulse['arguments']['total']
        return total_arguments

    def clear(self):
        for staff_pulse in self._staff:
            staff_pulse['arguments'] = {'enabled': 0, 'total': 0}
            staff_pulse['actions'] = {'enabled': 0, 'total': 0}

        return self._setTopLengths_Sums()

    def disable(self, rulers):
        return self.remove(rulers, total_one=0)
    
    def enable(self, rulers):
        return self.add(rulers, total_one=0)

    def filterList(self, measure=None, beat=None, step=None, pulse=None, list=None):
        if list != None:
            filtered_list = list[:]
        else:
            filtered_list = self._staff[:]

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

    def getRulers(self):
        return self._rulers

    def len(self):
        return self.total_pulses
    
    def len_steps(self):
        return self.total_pulses * self.steps_per_beat / self.pulses_per_beat
    
    def list(self):
        return self._staff
    
    def playRange(self):
        return self.play_range

    def playRange_pulses(self, play_range=[[], []]):
        if play_range == [[], []]:
            return [self.pulses(self.play_range[0]), self.pulses(self.play_range[1])]
        return [self.pulses(play_range[0]), self.pulses(play_range[1])]

    def position(self, steps=None, pulses=None):
        if (steps != None):
            measures = int(steps / (self.steps_per_beat * self.beats_per_measure))
            steps = steps % (self.steps_per_beat * self.beats_per_measure)
            if steps < 0:
                steps = -(-steps % (self.steps_per_beat * self.beats_per_measure))
        elif (pulses != None):
            measures = int(pulses / (self.pulses_per_beat * self.beats_per_measure))
            steps = pulses * self.steps_per_beat / self.pulses_per_beat % (self.steps_per_beat * self.beats_per_measure)
            if pulses < 0:
                steps = -(-pulses * self.steps_per_beat / self.pulses_per_beat % (self.steps_per_beat * self.beats_per_measure))
        return [measures, steps]
    
    def print(self):
        if len(self._staff) > 0:
            if len(self._staff) > 1:
                print("$" * (self.string_top_length + 132))

            for staff_pulse in self._staff:
                self.printSinglePulse(staff_pulse['pulse'])

            if len(self._staff) > 1:
                print("$" * (self.string_top_length + 132))
        else:
            print("[EMPTY]")
        return self
    
    def printSinglePulse(self, pulse=0, sums='pulse'):

        spaces_between = 6

        staff_pulse = self._staff[pulse]
        pulse_sums = self.pulseSums(staff_pulse['pulse'])

        pulse_str = "{ "
        for key, value in staff_pulse.items():
            if key == 'arguments':
                enabled_value_str = f"{pulse_sums[sums]['arguments']['enabled']}"
                enabled_value_length = len(enabled_value_str)
                enabled_value_str = "arguments: { enabled: " + (" " * (self.string_top_lengths['arguments_enabled'] - enabled_value_length)) + enabled_value_str
                enabled_value_str += " " * int(spaces_between / 2)
                total_value_str = f"{pulse_sums[sums]['arguments']['total']}"
                total_value_length = len(total_value_str)
                total_value_str = "total: " + (" " * (self.string_top_lengths['arguments_total'] - total_value_length)) + total_value_str + " }"
                pulse_str += enabled_value_str + total_value_str + " " * spaces_between
            elif key == 'actions':
                enabled_value_str = f"{pulse_sums[sums]['actions']['enabled']}"
                enabled_value_length = len(enabled_value_str)
                enabled_value_str = "actions: { enabled: " + (" " * (self.string_top_lengths['actions_enabled'] - enabled_value_length)) + enabled_value_str
                enabled_value_str += " " * int(spaces_between / 2)
                total_value_str = f"{pulse_sums[sums]['actions']['total']}"
                total_value_length = len(total_value_str)
                total_value_str = "total: " + (" " * (self.string_top_lengths['actions_total'] - total_value_length)) + total_value_str + " }"
                pulse_str += enabled_value_str + total_value_str + " " * 0
            else:
                key_value_str = f"{value}"
                key_value_length = len(key_value_str)
                key_value_str = (" " * (self.string_top_lengths[key] - key_value_length)) + key_value_str
                key_value_str = f"{key}: " + key_value_str
                pulse_str += key_value_str + " " * spaces_between
        pulse_str += " }"
        print(pulse_str)

        return self

    def print_group_by(self, level=0):
        if self.len() > 0:
            for staff_pulse in self._staff:
                pulse_remainders = self.pulseRemainders(staff_pulse['pulse'])
                match level:
                    case 0:
                        if pulse_remainders['measure'] == 0:
                            self.print_level_sums(staff_pulse['pulse'], level)
                    case 1:
                        if pulse_remainders['beat'] == 0:
                            self.print_level_sums(staff_pulse['pulse'], level)
                    case 2:
                        if pulse_remainders['step'] == 0:
                            self.print_level_sums(staff_pulse['pulse'], level)
                    case 3:
                        print (staff_pulse)
                    case _: # default
                        print("[EMPTY]")
        else:
            print("[EMPTY]")
        return self
    
    def print_level_sums(self, pulse=0, level=0):
        if self.len() > 0:
            staff_pulse = self._staff[pulse]
            match level:
                case 0:
                    filtered_list = self.filterList(measure=staff_pulse['measure'])
                    self.print_staff_sums(filtered_list)
                case 1:
                    filtered_list = self.filterList(measure=staff_pulse['measure'], beat=staff_pulse['beat'])
                    self.print_staff_sums(filtered_list)
                case 2:
                    filtered_list = self.filterList(measure=staff_pulse['measure'], beat=staff_pulse['beat'], step=staff_pulse['step'])
                    self.print_staff_sums(filtered_list)
                case 3:
                    print (staff_pulse)
                case _: # default
                    print("[EMPTY]")
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
    
    def pulseRemainders(self, pulse=0):
        return {
            'measure': pulse % (self.pulses_per_beat * self.beats_per_measure),
            'beat': pulse % self.pulses_per_beat,
            'step': pulse % (self.pulses_per_beat / self.steps_per_beat),
            'pulse': 0 # by definition is pulse % pulse = 0
        }
    
    def pulseSums(self, pulse=0):
        pulse_sums = {
            'measure': {'arguments': {'enabled': 0, 'total': 0}, 'actions': {'enabled': 0, 'total': 0}},
            'beat': {'arguments': {'enabled': 0, 'total': 0}, 'actions': {'enabled': 0, 'total': 0}},
            'step': {'arguments': {'enabled': 0, 'total': 0}, 'actions': {'enabled': 0, 'total': 0}},
            'pulse': {'arguments': {'enabled': 0, 'total': 0}, 'actions': {'enabled': 0, 'total': 0}}
        }

        measure = self._staff[pulse]['measure']
        measure_list = self.filterList(measure=measure)
        for staff_pulse in measure_list:
            pulse_sums['measure']['arguments']['enabled'] += staff_pulse['arguments']['enabled']
            pulse_sums['measure']['arguments']['total'] += staff_pulse['arguments']['total']
            pulse_sums['measure']['actions']['enabled'] += staff_pulse['actions']['enabled']
            pulse_sums['measure']['actions']['total'] += staff_pulse['actions']['total']

        beat = self._staff[pulse]['beat']
        beat_list = self.filterList(beat=beat, list=measure_list)
        for staff_pulse in beat_list:
            pulse_sums['beat']['arguments']['enabled'] += staff_pulse['arguments']['enabled']
            pulse_sums['beat']['arguments']['total'] += staff_pulse['arguments']['total']
            pulse_sums['beat']['actions']['enabled'] += staff_pulse['actions']['enabled']
            pulse_sums['beat']['actions']['total'] += staff_pulse['actions']['total']

        step = self._staff[pulse]['step']
        step_list = self.filterList(step=step, list=beat_list)
        for staff_pulse in step_list:
            pulse_sums['step']['arguments']['enabled'] += staff_pulse['arguments']['enabled']
            pulse_sums['step']['arguments']['total'] += staff_pulse['arguments']['total']
            pulse_sums['step']['actions']['enabled'] += staff_pulse['actions']['enabled']
            pulse_sums['step']['actions']['total'] += staff_pulse['actions']['total']

        pulse_sums['pulse']['arguments']['enabled'] += self._staff[pulse]['arguments']['enabled']
        pulse_sums['pulse']['arguments']['total'] += self._staff[pulse]['arguments']['total']
        pulse_sums['pulse']['actions']['enabled'] += self._staff[pulse]['actions']['enabled']
        pulse_sums['pulse']['actions']['total'] += self._staff[pulse]['actions']['total']

        return pulse_sums
    
    def pulses(self, position=[0, 0]): # position: [measure, step]
        return position[0] * self.beats_per_measure * self.pulses_per_beat + round(position[1] * self.pulses_per_beat / self.steps_per_beat)

    def remove(self, rulers, enabled_one=-1, total_one=-1):
        return self.add(rulers, enabled_one, total_one)
    
    def rulers(self):
        return self._rulers

    def setPlayRange(self, start=[], finish=[]):
        if self.total_pulses > 0:
            if start == [] or self.play_range[0] == []:
                self.play_range[0] = [0, 0]
            elif start == None and self.play_range[0] != []:
                start_pulses = min(self.total_pulses - 1, self.pulses(self.play_range[0]))
                self.play_range[0] = self.position(pulses=start_pulses)
            elif start != None:
                start_pulses = min(self.total_pulses - 1, self.pulses(start))
                self.play_range[0] = self.position(pulses=start_pulses)

            if finish == [] or self.play_range[1] == []:
                finish_pulses = self.total_pulses - 1
                self.play_range[1] = self.position(pulses=finish_pulses)
            elif finish == None and self.play_range[1] != []:
                start_pulses = min(self.total_pulses - 1, self.pulses(self.play_range[1]))
                self.play_range[1] = self.position(pulses=start_pulses)
            elif finish != None:
                start_pulses = self.pulses(self.play_range[0])
                finish_pulses = max(start_pulses, min(self.total_pulses - 1, self.pulses(start)))
                self.play_range[1] = self.position(pulses=finish_pulses)

        return self
    
    def setStaff(self, size_measures = 8, beats_per_measure = 4, steps_per_beat = 4, pulses_per_beat = 24):

        self.size_total_measures = size_measures            # staff total size
        self.beats_per_measure = beats_per_measure          # beats in each measure
        self.steps_per_beat = steps_per_beat                # how many steps take each beat
        self.pulses_per_beat = pulses_per_beat              # sets de resolution of clock pulses
        
        self.total_pulses = self.size_total_measures * self.beats_per_measure * self.pulses_per_beat

        old_staff = self._staff[:]
        self._staff = []
        for pulse in range(self.total_pulses):
            staff_pulse = {
                'measure': int(pulse / (self.pulses_per_beat * self.beats_per_measure)),
                'beat': int(pulse / self.pulses_per_beat) % self.beats_per_measure,
                'step': int(pulse * self.steps_per_beat / self.pulses_per_beat) % (self.steps_per_beat * self.beats_per_measure),
                'pulse': pulse,
                'arguments': {'enabled': 0, 'total': 0},
                'actions': {'enabled': 0, 'total': 0}
            }
            self._staff.append(staff_pulse)

        if self.total_pulses > 0:
            for staff_pulse in old_staff:
                for ruler_type in ['arguments', 'actions']:
                    if staff_pulse[ruler_type]['total'] > 0:
                        position_pulses = self.pulses([staff_pulse['measure'], staff_pulse['step']])
                        size_total_pulses = self.size_total_measures * self.beats_per_measure * self.pulses_per_beat
                        if not position_pulses < 0 and position_pulses < size_total_pulses:
                            self._staff[position_pulses][ruler_type]['enabled'] = staff_pulse[ruler_type]['enabled']
                            self._staff[position_pulses][ruler_type]['total'] = staff_pulse[ruler_type]['total']

        return self.setPlayRange(start=None, finish=None)._setTopLengths()
    
    def signature(self):
        return {
            'beats_per_measure': self.beats_per_measure,
            'steps_per_beat': self.steps_per_beat,
            'pulses_per_beat': self.pulses_per_beat,
            'pulses_per_step': self.pulses_per_beat / self.steps_per_beat
        }

    def steps(self, position=[0, 0]): # position: [measure, step]
        return position[0] * self.beats_per_measure * self.steps_per_beat + position[1]

    def str_position(self, position):
        return str(position[0]) + " " + str(round(position[1], 6))

# GLOBAL CLASS METHODS

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
    