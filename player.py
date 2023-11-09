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

import staff as Staff

class Player:

    def __init__(self, name, size_measures = 8, beats_per_measure = 4, steps_per_beat = 4, pulses_per_beat = 24, play_range=[[], []], staff = None):

        self._name = name
        self._staff = staff
        if self._staff == None:
            self._staff = Staff.Staff(size_measures, beats_per_measure, steps_per_beat, pulses_per_beat, play_range)

        self._staff_rulers = self._staff.getRulers()
        self.internal_key_rulers = self._staff_rulers.empty()
        self.external_key_rulers = self._staff_rulers.empty()

        self.play_mode = False
        self.play_pulse = self.rangePulses()['start']

        self.clock = None
        self.clocked_actions = []
        self.next_clocked_pulse = -1

    def addClockedAction(self, clocked_action): # Clocked actions AREN'T rulers!
        if (clocked_action['duration'] != None and clocked_action['action'] != None and self.clock != None):
            clock_tempo = self.clock.getClockTempo()
            pulses_duration = clocked_action['duration'] * self._staff.signature()['pulses_per_step'] # Action pulses per step considered
            clocked_action['pulse'] = round(clock_tempo['pulse'] + pulses_duration)
            clocked_action['source'] = "clock" # to know the source of the trigger
            clocked_action['stack_id'] = len(self.clocked_actions)
            self.clocked_actions.append(clocked_action)

            if (not self.next_clocked_pulse < clock_tempo['pulse']):
                self.next_clocked_pulse = min(self.next_clocked_pulse, clocked_action['pulse'])
            else:
                self.next_clocked_pulse = clocked_action['pulse']

    def connectClock(self, clock):
        self.clock = clock
        self.clock.attach(self)

    def getRulers(self):
        return self._staff_rulers

    def getStaff(self):
        return self._staff

    def play(self):
        ...

    def pulse(self, tempo):
        
        if (self.play_mode):

            if (self.play_pulse < self.rangePulses()['finish']): # plays staff range from start to finish

                position = self._staff.position(pulses=self.play_pulse)
                enabled_key_rulers = self._staff.filter_list(pulse=self.play_pulse)[0]['arguments']['enabled']
                enabled_action_rulers = self._staff.filter_list(pulse=self.play_pulse)[0]['actions']['enabled']

                if self._staff.pulseRemainders(self.play_pulse)['beat'] == 0:
                    # str_position = self._staff.str_position(pulses=position)
                    # print(f"{self.play_pulse}\t{str_position}\t{enabled_key_rulers}\t{enabled_action_rulers}\t{tempo['fast_forward']}\t{tempo['pulse']}\t{self.next_clocked_pulse}")
                    self._staff.print_level_sums(self.play_pulse, 1)

                if (enabled_key_rulers > 0):
                    
                    pulse_key_rulers = self._staff_rulers.filter(types=['arguments'], positions=[position], enabled=True)
                    self.internal_key_rulers = (pulse_key_rulers + self.internal_key_rulers).merge()

                if (enabled_action_rulers > 0):
                    
                    pulse_action_rulers = self._staff_rulers.filter(types=['actions'], positions=[position], enabled=True)
                    merged_staff_arguments = (self.external_key_rulers + self.internal_key_rulers).merge()

                    for triggered_action in pulse_action_rulers.list(): # single ruler actions
                        for action_line in range(len(triggered_action['lines'])):
                            if (triggered_action['lines'][action_line] != None):
                                triggered_action['line'] = action_line
                                triggered_action['source'] = "staff" # to know the source of the trigger
                                for key_ruler in merged_staff_arguments.list():
                                    key_ruler['line'] = action_line + triggered_action['offset'] - key_ruler['offset']
                                    if (key_ruler['line'] < 0 or not (key_ruler['line'] < len(key_ruler['lines']))):
                                        key_ruler['line'] = None # in case key line is out of range of the triggered action line

                                action_object = triggered_action['lines'][action_line]

                                if (action_object == self):        
                                    action_object.actionInternalTrigger(triggered_action, merged_staff_arguments, tempo) # WHERE ACTION IS TRIGGERED
                                else:        
                                    action_object.actionExternalTrigger(triggered_action, merged_staff_arguments, tempo) # WHERE ACTION IS TRIGGERED

                self.play_pulse += 1

            else:
                self.clock.stop()
                self.play_mode = False
                self.play_pulse = self.rangePulses()['start']

        # clock triggers staked to be called
        if (self.next_clocked_pulse == tempo['pulse']):
            clockedActions = [
                clockedAction for clockedAction in self.clocked_actions if clockedAction['pulse'] == tempo['pulse']
            ].copy() # To enable deletion of the original list while looping

            for clockedAction in clockedActions:
                action_object = clockedAction['action']
                if (action_object == self):        
                    action_object.actionInternalTrigger(clockedAction, clockedAction['staff_arguments'], tempo) # WHERE ACTION IS TRIGGERED
                else:        
                    action_object.actionExternalTrigger(clockedAction, clockedAction['staff_arguments'], tempo) # WHERE ACTION IS TRIGGERED
                    
            for clockedAction in clockedActions:
                del(self.clocked_actions[clockedAction['stack_id']])
            if (len(self.clocked_actions) > 0):
                self.next_clocked_pulse = self.clocked_actions[0]['pulse']
                for clocked_action in self.clocked_actions:
                    self.next_clocked_pulse = min(self.next_clocked_pulse, clocked_action['pulse'])

    def rangePulses(self):
        range_pulses = self._staff.playRange()
        start_pulses = self._staff.pulses(range_pulses[0])
        finish_pulses = self._staff.pulses(range_pulses[1])
        return {'start': start_pulses, 'finish': finish_pulses}

    def rulers(self):
        return self._staff_rulers

    def staff(self):
        return self._staff
    
    def stop(self):
        ...


    ### ACTIONS ###

    def actionExternalTrigger(self, triggered_action = {}, merged_staff_arguments = None, tempo = {}):
        self.play_mode = True
        self.external_staff_arguments = merged_staff_arguments # becomes read only, no need to copy

    def actionInternalTrigger(self, triggered_action = {}, merged_staff_arguments = None, tempo = {}):
        ...

    ### CLASS ###
    
    def __str__(self):
        # return self.__class__.__name__
        return self._name
