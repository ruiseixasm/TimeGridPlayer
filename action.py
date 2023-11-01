def main():
    print("Hello!")

class Action:

    def __init__(self, steps, frames_step, play_range=[]):

        self.play_mode = False
        self.external_staff_keys = []

        self.steps = max(1, steps)
        self.frames_step = max(1, frames_step)

        # OPTIMIZERS
        self.rulerTypes = ['keys', 'actions']
        self.rulerGroups = {'keys': [], 'actions': []}

        self.timeGrid = []
        self.staffRulers = []

        for i in range(self.steps*self.frames_step):

            frameData = {
                'sequence': i,
                'position': None,
                'step': int(i/self.frames_step),
                'frame': int(i % self.frames_step),
                'enabled_rulers': {'keys': 0, 'actions': 0}
            }
            frameData['position'] = str(frameData['step']) + "." + str(frameData['frame'])

            self.timeGrid.append(frameData)

        # SET RANGES
        self.play_range_sequences = [0, self.steps*self.frames_step - 1]

        if (len(play_range) == 2):

            if (play_range[0] != None):
                step_frame = play_range[0].split('.')
                self.play_range_sequences[0] = min(self.play_range_sequences[1], int(step_frame[0]) * frames_step + int(step_frame[1]))
            if (play_range[1] != None):
                step_frame = play_range[1].split('.')
                self.play_range_sequences[1] = min(self.play_range_sequences[1], int(step_frame[0]) * frames_step + int(step_frame[1]) - 1) # Excludes last sequence

        first_position = self.timeGrid[self.play_range_sequences[0]]['position']
        last_position = self.timeGrid[self.play_range_sequences[1]]['position']
        self.play_range_positions = [first_position, last_position]

        self.nextSequence = self.play_range_sequences[0]

        self.clock = None
        self.clocked_actions = []
        self.next_clocked_sequence = -1
            
    def __str__(self):
        finalString = ""
        last_time = 0
        for frame in self.timeGrid:
            finalString += f"{frame['sequence']}\t{frame['position']}\n"
        return finalString


    def connectClock(self, clock):
        self.clock = clock
        self.clock.attach(self)

    def addClockedAction(self, clocked_action = {'triggered_action': None, 'staff_keys': None, 'duration': None, 'action': None}):
        if (clocked_action['duration'] != None and clocked_action['action'] != None and self.clock != None):
            step_frame_duration = clocked_action['duration'].split('.')
            clock_tempo = self.clock.getClockTempo()
            sequence_duration = int(step_frame_duration[0]) * self.frames_step + int(step_frame_duration[1]) # Action frames per step considered
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

            #print(f"\tPULSE: {self.nextSequence}")

            if (self.nextSequence <= self.play_range_sequences[1]):

                position = self.timeGrid[self.nextSequence]['position']
                total_key_rulers = self.timeGrid[self.nextSequence]['enabled_rulers']['keys']
                total_action_rulers = self.timeGrid[self.nextSequence]['enabled_rulers']['actions']
                print(f"{self.nextSequence}\t{position}\t{total_key_rulers}\t{total_action_rulers}\t{tempo['fast_forward']}\t{tempo['sequence']}\t{self.next_clocked_sequence}")

                if (total_action_rulers > 0):
                    frameStaffActions = self.filterRulers(types=["actions"], positions=[position], ENABLED_ONLY=True)
                    stacked_staff_keys = self.stackStaffRulers(['keys'], [], position) # list of multiple rulers
                    print("")
                    for triggered_action in frameStaffActions: # single ruler actions
                        for action_line in range(len(triggered_action['lines'])):
                            if (triggered_action['lines'][action_line] != None):
                                triggered_action['line'] = action_line
                                triggered_action['source'] = "staff" # to know the source of the trigger
                                for frameStakedKeysRuler in stacked_staff_keys:
                                    frameStakedKeysRuler['line'] = action_line + triggered_action['offset'] - frameStakedKeysRuler['offset']
                                    if (frameStakedKeysRuler['line'] < 0 or not (frameStakedKeysRuler['line'] < len(frameStakedKeysRuler['lines']))):
                                        frameStakedKeysRuler['line'] = None # in case key line is out of range of the triggered action line

                                action_object = triggered_action['lines'][action_line]
                                if (action_object == self):        
                                    action_object.actionInternalTrigger(triggered_action, stacked_staff_keys, tempo) # WHERE ACTION IS TRIGGERED
                                else:        
                                    action_object.actionExternalTrigger(triggered_action, stacked_staff_keys, tempo) # WHERE ACTION IS TRIGGERED
                    print("")

                self.nextSequence += 1

            else:
                self.clock.stop()
                self.play_mode = False
                self.nextSequence = self.play_range_sequences[0]

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


    def getPositionSequence(self, position):
        if (position != None):
            step_frame = position.split('.')
            step_frame = [int(x) for x in step_frame]
            timeGridFrame = [ timeFrame for timeFrame in self.timeGrid if timeFrame['step'] in [step_frame[0]] ]
            timeGridFrame = [ timeFrame for timeFrame in timeGridFrame if timeFrame['frame'] in [step_frame[1]] ]
            if (len(timeGridFrame) > 0):
                return timeGridFrame[0]['sequence']
        return None
 
    def filterRulers(self, types = [], groups = [], positions = [], sequeces = [], sequeces_range = [], ENABLED_ONLY = False, INSIDE_RANGE = False):
        filtered_rulers = self.staffRulers
        if (ENABLED_ONLY):
            filtered_rulers = [
                staffRuler for staffRuler in filtered_rulers if staffRuler['enabled'] == True
            ]
        if (INSIDE_RANGE):
            # Using list comprehension
            filtered_rulers = [
                staffRuler for staffRuler in filtered_rulers if staffRuler['sequence']
                        if not (staffRuler['sequence'] < self.play_range_positions[0] or staffRuler['sequence'] > self.play_range_positions[1])
            ]
        if (len(types) > 0 and types != [None]):
            filtered_rulers = [
                staffRuler
                    for staffRuler in filtered_rulers if staffRuler['type'] in types
            ]
        if (len(groups) > 0 and groups != [None]):
            filtered_rulers = [
                staffRuler
                    for staffRuler in filtered_rulers if staffRuler['group'] in groups
            ]
        if (len(positions) > 0 and positions != [None]): # Check for as None for NOT enabled
            filtered_rulers = [
                staffRuler
                    for staffRuler in filtered_rulers if staffRuler['position'] in positions
            ]
        if (len(sequeces_range) > 0 and sequeces_range != [None]): # Check for as None for NOT on STAFF
            if (len(sequeces_range) == 1):
                sequeces_range.append(sequeces_range[0])
                sequeces_range[0] = 0
            # Using list comprehension
            filtered_rulers = [
                staffRuler for staffRuler in filtered_rulers if staffRuler['sequence']
                        if not (staffRuler['sequence'] < sequeces_range[0] or staffRuler['sequence'] > sequeces_range[1])
            ]
        if (len(sequeces) > 0 and sequeces != [None]): # Check for as None for NOT on STAFF
            filtered_rulers = [
                staffRuler
                    for staffRuler in filtered_rulers if staffRuler['sequence'] in sequeces
            ]
        return filtered_rulers
    
    # def enableRulers(self, types = [], groups = [], positions = []):
    #     rulers = self.filterRulers(types, groups, positions = [None], ON_STAFF=True) # positions = [None] means NOT enabled
    #     if (len(rulers) > 0):
    #         for ruler in rulers:
    #             ruler['position'] = self.timeGrid[ruler['sequence']]['position']
    #             self.timeGrid[ruler['sequence']]['enabled_rulers'][ruler['type']] += 1
    #     return rulers

    # def disableRulers(self, types = [], groups = [], positions = []):
    #     rulers = self.filterRulers(types, groups, positions, ENABLED_ONLY = True)
    #     if (len(rulers) > 0):
    #         for ruler in rulers:
    #             ruler['position'] = None
    #             if (ruler['sequence'] != None): # avoids compiler error
    #                 self.timeGrid[ruler['sequence']]['enabled_rulers'][ruler['type']] -= 1
    #     return rulers

    def addRuler(self, ruler):
        if ruler != None and len(ruler) > 0:
            if (ruler['type'] in self.rulerTypes):
                if 'group' not in ruler or ruler['group'] == None:
                    ruler['group'] = "main"
                if 'lines' not in ruler or ruler['lines'] == None or len(ruler['lines']) == 0:
                    ruler['lines'] = [None]
                if 'position' not in ruler or ruler['position'] == None: # Needs to add pattern matching
                    ruler['position'] = "0.0"

                rulers = self.filterRulers([type], [group], [position])
                if (len(rulers) > 0):
                    ...
                else:
                    newRuler = {
                        'type': type,
                        'group': group,
                        'lines': lines, # list
                        'position': None,
                        'sequence': None,
                        'offset': 0,
                        'enabled': True
                    }
                    self.staffRulers.append(newRuler)
                    return True
        return False

    def addRuler(self, type, group, position, lines):
        if (type in self.rulerTypes):
            rulers = self.filterRulers([type], [group], [position])
            if (len(rulers) > 0):
                ...
            else:
                newRuler = {
                    'type': type,
                    'group': group,
                    'lines': lines, # list
                    'position': None,
                    'sequence': None,
                    'offset': 0,
                    'enabled': True
                }
                self.staffRulers.append(newRuler)
                return True
        return False

    def addRuler(self, type, position, offset = None):
        ruler = self.getRuler(type)
        if (ruler != None):
            sequence = self.getPositionSequence(position)
            if (position != None): # add ruler to staff
                if (ruler['sequence'] == None): # not on staff
                    existent_staffgroup = False
                    for staffGroup in self.rulerGroups[type]: # REQUIRES self.rulerGroups
                        if (staffGroup == ruler['group']):
                            existent_staffgroup = True
                            break
                    if (not existent_staffgroup):
                        self.rulerGroups[type].append(ruler['group'])

            elif (position == None): # remove ruler from staff

                placed_rulers = self.filterRulers(ENABLED_ONLY=True)
                group_rulers = [
                        staffRuler
                            for staffRuler in placed_rulers if staffRuler['group'] in [ruler['group']]
                ]
                if (len(group_rulers) == 0):
                    self.rulerGroups[type].remove(ruler['group']) # REQUIRES self.rulerGroups

            if (ruler['position'] != None and ruler['sequence'] != None): # already enabled ruler
                self.timeGrid[ruler['sequence']]['enabled_rulers'][ruler['type']] -= 1
            if (sequence != None): # not a removal
                self.timeGrid[sequence]['enabled_rulers'][ruler['type']] += 1

            ruler['position'] = position
            ruler['sequence'] = sequence
            if (offset != None):
                ruler['offset'] = offset
        return ruler

    # def removeRuler(self, type):
    #     self.placeRuler(type, None)

    # def deleteRulers(self, types = [], groups = []):
    #     rulers = self.disableRulers(type, types, groups) # makes sure ruler gets disabled first
    #     for ruler in rulers:
    #         # Using list comprehension
    #         self.rulerGroups[ruler['type']] = [
    #             rulerGroup for rulerGroup in self.rulerGroups[ruler['type']] if not (rulerGroup['group'] == ruler['group'])
    #         ]
    
    def getRuler(self, type, group):
        for staffRuler in self.staffRulers:
            if staffRuler['group'] == group and staffRuler['type'] == type:
                return staffRuler
        return None
   
    def listRulers(self):
        for staffRuler in self.staffRulers:
            print(staffRuler)
    
    def listStaffGroups(self):
        for type in self.rulerTypes:
            for group in self.rulerGroups[type]: # REQUIRES self.rulerGroups
                print(f"{type}\t{group}")

    def stackStaffRulers(self, types = [], groups = [], position = None, sequence = None):

        if (position == None and sequence == None):
            sequence = self.play_range_positions[1]
            position = self.timeGrid[sequence]['position']
        elif (position == None):
            position = self.timeGrid[sequence]['position']
        else:
            sequence = self.getPositionSequence(position)

        if (len(types) == 0):
            types = self.rulerTypes

        stacked_internal_keys = []
        remaining_external_keys = self.external_staff_keys[:] # does a shallow copy
        for type in types:
            if (len(groups) == 0):
                groups = self.rulerGroups[type] # REQUIRES self.rulerGroups

            for group in groups:
                filtered_rulers = self.filterRulers([type], [group], ENABLED_ONLY=True)
                # Using list comprehension
                left_rulers = [
                    ruler for ruler in filtered_rulers if not (ruler['sequence'] > sequence)
                ]
                
                if (len(left_rulers) > 0): # left rulers ONLY!

                    external_rulers = [
                        ruler_keys for ruler_keys in remaining_external_keys if ruler_keys['group'] == group and ruler_keys['type'] == type
                    ]
                    remaining_external_keys = [
                        ruler_keys for ruler_keys in remaining_external_keys if not (ruler_keys['group'] == group and ruler_keys['type'] == type)
                    ]

                    head_offset = 0
                    tail_offset = 0
                    for left_ruler in external_rulers + left_rulers:
                        if left_ruler['offset'] < head_offset:
                            head_offset = left_ruler['offset']
                        if (len(left_ruler['lines']) + left_ruler['offset'] > tail_offset):
                            tail_offset = len(left_ruler['lines']) - 1 + left_ruler['offset']
                    
                    stackedRuler = {
                        'type': type,
                        'group': group,
                        'lines': [None] * (tail_offset - head_offset + 1), # list
                        'position': position,
                        'sequence': sequence,
                        'offset': head_offset
                    }

                    for external_ruler in external_rulers:
                        for i in range(len(external_ruler['lines'])):
                            stacked_line = i + external_ruler['offset'] - stackedRuler['offset']
                            stackedRuler['lines'][stacked_line] = external_ruler['lines'][i]

                    lower_sequence = sequence

                    while (not (lower_sequence < 0)):

                        total_key_rulers = self.timeGrid[lower_sequence]['enabled_rulers']['keys']
                        total_action_rulers = self.timeGrid[lower_sequence]['enabled_rulers']['actions']

                        if (total_key_rulers > 0):

                            lower_rulers = [
                                staffRuler
                                    for staffRuler in left_rulers if staffRuler['sequence'] in [lower_sequence]
                            ]
                            
                            for lower_ruler in lower_rulers:
                                for i in range(len(lower_ruler['lines'])):
                                    stacked_line = i + lower_ruler['offset'] - stackedRuler['offset']
                                    if (stackedRuler['lines'][stacked_line] == None):
                                        stackedRuler['lines'][stacked_line] = lower_ruler['lines'][i]

                        lower_sequence -= 1

                    stacked_internal_keys.append(stackedRuler)
        return stacked_internal_keys + remaining_external_keys
    
    ### OPERATIONS ###

    # def operationSwapRulers(self, type, first_ruler, second_ruler):
    #     rulers = first_ruler + second_ruler
    #     if (len(rulers) == 2):
    #         position = rulers[0]['position']
    #         sequence = rulers[0]['sequence']
    #         rulers[0]['position'] = rulers[1]['position']
    #         rulers[0]['sequence'] = rulers[1]['sequence']
    #         rulers[1]['position'] = position
    #         rulers[1]['sequence'] = sequence
    #     return self

    # def operationSlideRulers(self, increments = [0, 0], modulus_selector = [1, 1], modulus_reference = [0, 0], type = None, group = None, sequeces_range = [], ENABLED_ONLY = False, INSIDE_RANGE = False):

    #     rulers = self.filterRulers(types = [type], groups = [group], sequeces_range = sequeces_range, ENABLED_ONLY = ENABLED_ONLY, ON_STAFF = True, INSIDE_RANGE = INSIDE_RANGE)

    #     lower_slack = self.steps*self.frames_step - 1
    #     upper_slack = lower_slack

    #     modulus_position = modulus_reference[0]
    #     for rule in rulers:
    #         if (modulus_position % modulus_selector[0] == 0):
    #             lower_slack = min(lower_slack, rule['sequence'])
    #             upper_slack = min(upper_slack, self.steps*self.frames_step - 1 - rule['sequence'])
    #         modulus_position += 1

    #     increments[0] = max(-lower_slack, increments[0]) # Horizontal sliding can't slide out of the grid
    #     increments[0] = min(upper_slack, increments[0]) # Horizontal sliding can't slide out of the grid

    #     modulus_position = modulus_reference[0]
    #     for rule in rulers:
    #         if (modulus_position % modulus_selector[0] == 0):
    #             rule['sequence'] += increments[0]
    #             if (rule['position'] != None):
    #                 rule['position'] = self.timeGrid[rule['sequence']]['position']
    #         modulus_position += 1

    #     modulus_position = modulus_reference[1]
    #     for rule in rulers:
    #         if (modulus_position % modulus_selector[1] == 0):
    #             rule['offset'] += increments[1]
    #         modulus_position += 1
            
    #     return self

    # def operationRotateRulers(self, increments = [0, 0], type = None, group = None, sequeces_range = [], ENABLED_ONLY = False, INSIDE_RANGE = False):

    #     rulers = self.filterRulers(types = [type], groups = [group], sequeces_range = sequeces_range, ENABLED_ONLY = ENABLED_ONLY, ON_STAFF = True, INSIDE_RANGE = INSIDE_RANGE)

    #     staff_sequences = []
    #     if (increments[0] != 0):
    #         for rule in rulers:
    #             staff_sequences.append(rule['sequence'])
        
    #     total_sequences = len(staff_sequences)
    #     for rule in rulers:
    #         if (increments[0] != 0):
    #             rule['sequence'] = staff_sequences[increments[0] % total_sequences]
    #             if (rule['position'] != None):
    #                 rule['position'] = self.timeGrid[rule['sequence']]['position']
    #         if (increments[1] != 0):
    #             rule_lines = []
    #             for line in rule['lines']:
    #                 rule_lines.append(line)
    #             total_lines = len(rule_lines)
    #             for line in rule['lines']:
    #                 line = rule_lines[increments[1] % total_lines]

    #     return self

    # def operationFlipRulers(self, mirrors = [False, False], type = None, group = None, sequeces_range = [], ENABLED_ONLY = False, INSIDE_RANGE = False):

    #     rulers = self.filterRulers(types = [type], groups = [group], sequeces_range = sequeces_range, ENABLED_ONLY = ENABLED_ONLY, ON_STAFF = True, INSIDE_RANGE = INSIDE_RANGE)

    #     staff_sequences = []
    #     if (mirrors[0]):
    #         for rule in rulers:
    #             staff_sequences.append(rule['sequence'])
        
    #     upper_sequence = len(staff_sequences) - 1
    #     for rule in rulers:
    #         if (mirrors[0]):
    #             rule['sequence'] = staff_sequences[upper_sequence]
    #             if (rule['position'] != None):
    #                 rule['position'] = self.timeGrid[rule['sequence']]['position']
    #         upper_sequence -= 1
    #         if (mirrors[1]):
    #             rule_lines = []
    #             for line in rule['lines']:
    #                 rule_lines.append(line)
    #             upper_line = len(rule_lines) - 1
    #             for line in rule['lines']:
    #                 line = rule_lines[upper_line]
    #                 upper_line -= 1

    #     return self


    ### ACTIONS ###

    def actionExternalTrigger(self, triggered_action = {}, stacked_staff_keys = [], tempo = {}):
        self.play_mode = True
        self.external_staff_keys = stacked_staff_keys # becomes read only, no need to copy

    def actionInternalTrigger(self, triggered_action = {}, stacked_staff_keys = [], tempo = {}):
        pass

class Master(Action):
    
    def __init__(self, steps, frames):
        super().__init__(steps, frames) # not self init

class Note(Action):
    
    def __init__(self, steps, frames, play_range=[]):
        super().__init__(steps, frames, play_range) # not self init
        first_position = self.play_range_positions[0]

        if (self.addRuler("actions", "notes", "note_on", [self])):
            self.placeRuler('actions', "note_on", first_position)

    ### ACTIONS ###

    def actionExternalTrigger(self, triggered_action = {}, stacked_staff_keys = [], tempo = {}):
        super().actionExternalTrigger(triggered_action, stacked_staff_keys, tempo)
        if (tempo['fast_forward']):
            self.play_mode = False
        if (len(stacked_staff_keys) > 0):
            given_lines = stacked_staff_keys[0]['lines']
            key_line = stacked_staff_keys[0]['line']
            key_value = given_lines[key_line]
            self.note = key_value # may need tranlation!

    def actionInternalTrigger(self, triggered_action = {}, stacked_staff_keys = [], tempo = {}):
        super().actionInternalTrigger(triggered_action, stacked_staff_keys, tempo)
        if (len(stacked_staff_keys) > 0):
            given_lines = stacked_staff_keys[0]['lines']
            key_line = stacked_staff_keys[0]['line']
            key_value = given_lines[key_line]
        else:
            key_value = self.note # may need tranlation!
        if (triggered_action['source'] == "staff"):
            print(f"note ON:\t{key_value}")
            self.addClockedAction(clocked_action = {'triggered_action': triggered_action.copy(), 'staff_keys': stacked_staff_keys.copy(),
                                                    'duration': "1.0", 'action': self})
        else:
            print(f"note OFF:\t{key_value}")

class Trigger(Action):
    
    def __init__(self):
        super().__init__(0, 0) # not self init
        self.addRuler("actions", "triggers", [self])

    ### ACTIONS ###

    def actionExternalTrigger(self, triggered_action = {}, stacked_staff_keys = [], tempo = {}):
        super().actionExternalTrigger(triggered_action, stacked_staff_keys, tempo)
        print("EXTERNALLY TRIGGERED")

    def actionInternalTrigger(self, triggered_action = {}, stacked_staff_keys = [], tempo = {}):
        super().actionInternalTrigger(triggered_action, stacked_staff_keys, tempo)
        print("LOCALLY TRIGGERED")

if __name__ == "__main__":
    main()