import staff
import rulers

class Action:

    def __init__(self, steps = 0, frames_step = 0, play_range=[]):

        self.rulerTypes = ['keys', 'actions']
        self.staff_grid = staff.Staff(steps, frames_step, play_range)
        self.staff_rulers = rulers.Rulers(staff_grid=self.staff_grid)
        self.internal_key_rulers = rulers.Rulers(staff_grid=self.staff_grid)
        self.external_key_rulers = rulers.Rulers(staff_grid=self.staff_grid)

        self.play_mode = False

        self.play_sequence = self.sequenceRange()['start']

        self.clock = None
        self.clocked_actions = []
        self.next_clocked_sequence = -1
            

    def sequenceRange(self):
        position_range = self.staff_grid.range()
        start_sequence = self.staff_grid.sequence(position_range[0])
        finish_sequence = self.staff_grid.sequence(position_range[1])
        return {'start': start_sequence, 'finish': finish_sequence}

    def connectClock(self, clock):
        self.clock = clock
        self.clock.attach(self)

    def addClockedAction(self, clocked_action): # Clocked actions AREN'T rulers!
        if (clocked_action['duration'] != None and clocked_action['action'] != None and self.clock != None):
            clock_tempo = self.clock.getClockTempo()
            sequence_duration = int(clocked_action['duration'][0]) * self.staff_grid.signature()['frames_step'] + int(clocked_action['duration'][1]) # Action frames per step considered
            clocked_action['sequence'] = clock_tempo['sequence'] + sequence_duration
            clocked_action['source'] = "clock" # to know the source of the trigger
            clocked_action['stack_id'] = len(self.clocked_actions)
            self.clocked_actions.append(clocked_action)

            if (not self.next_clocked_sequence < clock_tempo['sequence']):
                self.next_clocked_sequence = min(self.next_clocked_sequence, clocked_action['sequence'])
            else:
                self.next_clocked_sequence = clocked_action['sequence']

    def pulse(self, tempo):
        #print(f"CALLED:\t{self.play_mode}")
        if (self.play_mode):

            #print(f"\tPULSE: {self.play_sequence}")

            if (self.play_sequence < self.sequenceRange()['finish']): # plays staff range from start to finish

                position = self.staff_grid.grid(self.play_sequence)['position']
                total_key_rulers = self.staff_grid.grid(self.play_sequence)['keys']
                total_action_rulers = self.staff_grid.grid(self.play_sequence)['actions']

                str_position = self.staff_grid.str_position(position)
                print(f"{self.play_sequence}\t{str_position}\t{total_key_rulers}\t{total_action_rulers}\t{tempo['fast_forward']}\t{tempo['sequence']}\t{self.next_clocked_sequence}")

                if (total_key_rulers > 0):
                    
                    sequence_key_rulers = self.staff_rulers.filter(types=['keys'], positions=[position], enabled=True)

                    self.internal_key_rulers = (sequence_key_rulers + self.internal_key_rulers).merge()

                if (total_action_rulers > 0):
                    
                    sequence_action_rulers = self.staff_rulers.filter(types=['actions'], positions=[position], enabled=True)
                    merged_staff_keys = (self.external_key_rulers + self.internal_key_rulers).merge()

                    print("")
                    for triggered_action in sequence_action_rulers.list(): # single ruler actions
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

                self.play_sequence += 1

            else:
                self.clock.stop()
                self.play_mode = False
                self.play_sequence = self.sequenceRange()['start']

        # clock triggers staked to be called
        if (self.next_clocked_sequence == tempo['sequence']):
            clockedActions = [
                clockedAction for clockedAction in self.clocked_actions if clockedAction['sequence'] == tempo['sequence']
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
                self.next_clocked_sequence = self.clocked_actions[0]['sequence']
                for clocked_action in self.clocked_actions:
                    self.next_clocked_sequence = min(self.next_clocked_sequence, clocked_action['sequence'])


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
    
    def __init__(self, steps, frames):
        super().__init__(steps, frames) # not self init

class Note(Action):
    
    def __init__(self, steps, frames, play_range=[]):
        super().__init__(steps, frames, play_range) # not self init
        first_position = self.staff_grid.range()[0]
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
        super().__init__(0, 0) # not self init
        self.staff_rulers.add({'type': "actions", 'group': "triggers", 'lines': [self]})

    ### ACTIONS ###

    def actionExternalTrigger(self, triggered_action = {}, merged_staff_keys = None, tempo = {}):
        super().actionExternalTrigger(triggered_action, merged_staff_keys, tempo)
        print("EXTERNALLY TRIGGERED")

    def actionInternalTrigger(self, triggered_action = {}, merged_staff_keys = None, tempo = {}):
        super().actionInternalTrigger(triggered_action, merged_staff_keys, tempo)
        print("LOCALLY TRIGGERED")

    # def __str__(self):
    #     finalString = f"{frame['sequence']}\t{frame['position']}\n"
    #     return finalString
