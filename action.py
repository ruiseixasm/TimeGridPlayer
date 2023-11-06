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

import staff
import rulers
import midi_tools

class Action:

    def __init__(self, size_measures = 8, beats_per_measure = 4, steps_per_beat = 4, pulses_per_beat = 24, play_range=[[], []]):

        self.rulerTypes = ['keys', 'actions']
        self.staff_grid = staff.Staff(size_measures, beats_per_measure, steps_per_beat, pulses_per_beat, play_range)
        self.staff_rulers = rulers.Rulers(staff_grid=self.staff_grid)
        self.internal_key_rulers = self.staff_rulers.empty()
        self.external_key_rulers = self.staff_rulers.empty()

        self.play_mode = False
        self.play_pulse = self.rangePulses()['start']

        self.clock = None
        self.clocked_actions = []
        self.next_clocked_pulse = -1

    def rangePulses(self):
        range_pulses = self.staff_grid.playRange()
        start_pulses = self.staff_grid.pulses(range_pulses[0])
        finish_pulses = self.staff_grid.pulses(range_pulses[1])
        return {'start': start_pulses, 'finish': finish_pulses}

    def connectClock(self, clock):
        self.clock = clock
        self.clock.attach(self)

    def addClockedAction(self, clocked_action): # Clocked actions AREN'T rulers!
        if (clocked_action['duration'] != None and clocked_action['action'] != None and self.clock != None):
            clock_tempo = self.clock.getClockTempo()
            pulses_duration = clocked_action['duration'] * self.staff_grid.signature()['pulses_per_step'] # Action pulses per step considered
            clocked_action['pulse'] = round(clock_tempo['pulse'] + pulses_duration)
            clocked_action['source'] = "clock" # to know the source of the trigger
            clocked_action['stack_id'] = len(self.clocked_actions)
            self.clocked_actions.append(clocked_action)

            if (not self.next_clocked_pulse < clock_tempo['pulse']):
                self.next_clocked_pulse = min(self.next_clocked_pulse, clocked_action['pulse'])
            else:
                self.next_clocked_pulse = clocked_action['pulse']

    def pulse(self, tempo):
        #print(f"CALLED:\t{self.play_mode}")
        if (self.play_mode):

            #print(f"\tPULSE: {self.play_pulse}")

            if (self.play_pulse < self.rangePulses()['finish']): # plays staff range from start to finish

                position = self.staff_grid.position(self.play_pulse)
                enabled_key_rulers = self.staff_grid.filter_list(pulse=self.play_pulse)[0]['keys']['enabled']
                enabled_action_rulers = self.staff_grid.filter_list(pulse=self.play_pulse)[0]['actions']['enabled']

                str_position = self.staff_grid.str_position(position)
                print(f"{self.play_pulse}\t{str_position}\t{enabled_key_rulers}\t{enabled_action_rulers}\t{tempo['fast_forward']}\t{tempo['pulse']}\t{self.next_clocked_pulse}")

                if (enabled_key_rulers > 0):
                    
                    pulse_key_rulers = self.staff_rulers.filter(types=['keys'], positions=[position], enabled=True)
                    self.internal_key_rulers = (pulse_key_rulers + self.internal_key_rulers).merge()

                if (enabled_action_rulers > 0):
                    
                    pulse_action_rulers = self.staff_rulers.filter(types=['actions'], positions=[position], enabled=True)
                    merged_staff_keys = (self.external_key_rulers + self.internal_key_rulers).merge()

                    print("")
                    for triggered_action in pulse_action_rulers.list(): # single ruler actions
                        for action_line in range(len(triggered_action['lines'])):
                            if (triggered_action['lines'][action_line] != None):
                                triggered_action['line'] = action_line
                                triggered_action['source'] = "staff" # to know the source of the trigger
                                for key_ruler in merged_staff_keys.list():
                                    key_ruler['line'] = action_line + triggered_action['offset'] - key_ruler['offset']
                                    if (key_ruler['line'] < 0 or not (key_ruler['line'] < len(key_ruler['lines']))):
                                        key_ruler['line'] = None # in case key line is out of range of the triggered action line

                                action_object = triggered_action['lines'][action_line]

                                if (action_object == self):        
                                    action_object.actionInternalTrigger(triggered_action, merged_staff_keys, tempo) # WHERE ACTION IS TRIGGERED
                                else:        
                                    action_object.actionExternalTrigger(triggered_action, merged_staff_keys, tempo) # WHERE ACTION IS TRIGGERED
                    print("")

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
                    action_object.actionInternalTrigger(clockedAction, clockedAction['staff_keys'], tempo) # WHERE ACTION IS TRIGGERED
                else:        
                    action_object.actionExternalTrigger(clockedAction, clockedAction['staff_keys'], tempo) # WHERE ACTION IS TRIGGERED
                    
            for clockedAction in clockedActions:
                del(self.clocked_actions[clockedAction['stack_id']])
            if (len(self.clocked_actions) > 0):
                self.next_clocked_pulse = self.clocked_actions[0]['pulse']
                for clocked_action in self.clocked_actions:
                    self.next_clocked_pulse = min(self.next_clocked_pulse, clocked_action['pulse'])


    def rulers(self):
        return self.staff_rulers

    def staff(self):
        return self.staff_grid


    ### ACTIONS ###

    def actionExternalTrigger(self, triggered_action = {}, merged_staff_keys = None, tempo = {}):
        self.play_mode = True
        self.external_staff_keys = merged_staff_keys # becomes read only, no need to copy

    def actionInternalTrigger(self, triggered_action = {}, merged_staff_keys = None, tempo = {}):
        ...

class Master(Action):
    
    def __init__(self, size_measures = 8, beats_per_measure = 4, steps_per_beat = 4, pulses_per_beat = 24, play_range=[[], []]):
        super().__init__(size_measures, beats_per_measure, steps_per_beat, pulses_per_beat, play_range) # not self init

class Note(Action):
    
    def __init__(self, size_measures = 8, beats_per_measure = 4, steps_per_beat = 4, pulses_per_beat = 24, play_range=[[], []]):
        super().__init__(size_measures, beats_per_measure, steps_per_beat, pulses_per_beat, play_range) # not self init
        first_position = self.staff_grid.playRange()[0]
        self.staff_rulers.add({'type': "actions", 'group': "notes", 'position': first_position, 'lines': [self]})

    ### ACTIONS ###

    def actionExternalTrigger(self, triggered_action = {}, merged_staff_keys = None, tempo = {}):
        super().actionExternalTrigger(triggered_action, merged_staff_keys, tempo)
        if (tempo['fast_forward']):
            self.play_mode = False
        if (merged_staff_keys != None and merged_staff_keys.len() > 0):
            given_lines = merged_staff_keys.list()[0]['lines']
            key_line = merged_staff_keys.list()[0]['line']
            key_value = given_lines[key_line]
            self.note = key_value # may need tranlation!

    def actionInternalTrigger(self, triggered_action = {}, merged_staff_keys = None, tempo = {}):
        super().actionInternalTrigger(triggered_action, merged_staff_keys, tempo)
        if (merged_staff_keys != None and merged_staff_keys.len() > 0):
            given_lines = merged_staff_keys.list()[0]['lines']
            key_line = merged_staff_keys.list()[0]['line']
            key_value = given_lines[key_line]
        else:
            key_value = self.note # may need tranlation!
        if (triggered_action['source'] == "staff"):
            print(f"note ON:\t{key_value}")
            self.addClockedAction(clocked_action =
                                  {'triggered_action': triggered_action, 'staff_keys': merged_staff_keys, 'duration': [1, 0], 'action': self}
                                  )
        else:
            print(f"note OFF:\t{key_value}")

class Trigger(Action):
    
    def __init__(self):
        super().__init__(size_measures = 1, beats_per_measure = 1, steps_per_beat = 1) # not self init
        self.staff_rulers.add({'type': "actions", 'group': "triggers", 'lines': [self]})

    ### ACTIONS ###

    def actionExternalTrigger(self, triggered_action = {}, merged_staff_keys = None, tempo = {}):
        super().actionExternalTrigger(triggered_action, merged_staff_keys, tempo)
        print("EXTERNALLY TRIGGERED")

    def actionInternalTrigger(self, triggered_action = {}, merged_staff_keys = None, tempo = {}):
        super().actionInternalTrigger(triggered_action, merged_staff_keys, tempo)
        print("LOCALLY TRIGGERED")

    # def __str__(self):
    #     finalString = f"{pulse['sequence']}\t{pulse['position']}\n"
    #     return finalString
