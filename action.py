import staff
import rulers

class Action:

    def __init__(self, steps = 0, frames_step = 0, play_range=[]):

        self.rulerTypes = ['keys', 'actions']
        self.staff_grid = staff.Staff(steps, frames_step)
        self.staff_rulers = rulers.Rulers(staff_grid=self.staff_grid)
        self.internal_key_rulers = rulers.Rulers()
        self.external_key_rulers = rulers.Rulers()

        self.play_mode = False

        self.play_sequence = self.sequenceRange()[0]

        self.clock = None
        self.clocked_actions = []
        self.next_clocked_sequence = -1
            
    # def __str__(self):
    #     finalString = f"{frame['sequence']}\t{frame['position']}\n"
    #     return finalString


    def sequenceRange(self):
        position_range = self.staff_grid.range()
        start_sequence = self.staff_grid.sequence(position_range[0])
        finish_sequence = self.staff_grid.sequence(position_range[1])
        return [start_sequence, finish_sequence]

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

            if (self.play_sequence < self.sequenceRange()[1]): # plays staff range from start to finish

                position = self.staff_grid.grid(self.play_sequence)['position']
                position = self.staff_grid.str_position(position)
                total_key_rulers = self.staff_grid.grid(self.play_sequence)['keys']
                total_action_rulers = self.staff_grid.grid(self.play_sequence)['actions']

                print(f"{self.play_sequence}\t{position}\t{total_key_rulers}\t{total_action_rulers}\t{tempo['fast_forward']}\t{tempo['sequence']}\t{self.next_clocked_sequence}")

                if (total_action_rulers > 0):
                    
                    next_position = self.staff_grid.position(self.play_sequence + 1)
                    key_rulers = self.staff_rulers.filter(types=['keys'], position_range=[[0 , 0], next_position], ENABLED_ONLY=True)
                    if self.external_key_rulers != None:
                        key_rulers += self.external_key_rulers
                    merged_key_rulers = key_rulers.merge()

                    this_position = self.staff_grid.position(self.play_sequence)
                    sequence_action_rulers = self.staff_rulers.filter(types=['actions'], positions=[this_position], ENABLED_ONLY=True)
                    
                    print("")
                    for triggered_action in sequence_action_rulers.list(): # single ruler actions
                        for action_line in range(len(triggered_action['lines'])):
                            if (triggered_action['lines'][action_line] != None):
                                triggered_action['line'] = action_line
                                triggered_action['source'] = "staff" # to know the source of the trigger
                                for key_ruler in merged_key_rulers.list():
                                    key_ruler['line'] = action_line + triggered_action['offset'] - key_ruler['offset']
                                    if (key_ruler['line'] < 0 or not (key_ruler['line'] < len(key_ruler['lines']))):
                                        key_ruler['line'] = None # in case key line is out of range of the triggered action line

                                action_object = triggered_action['lines'][action_line]

                                if (action_object == self):        
                                    action_object.actionInternalTrigger(triggered_action, merged_key_rulers, tempo) # WHERE ACTION IS TRIGGERED
                                else:        
                                    action_object.actionExternalTrigger(triggered_action, merged_key_rulers, tempo) # WHERE ACTION IS TRIGGERED
                    print("")


                    # frameStaffActions = self.filterRulers(types=["actions"], positions=[position], ENABLED_ONLY=True)
                    # merged_staff_keys = self.stackStaffRulers(['keys'], [], position) # list of multiple rulers
                    # print("")
                    # for triggered_action in frameStaffActions: # single ruler actions
                    #     for action_line in range(len(triggered_action['lines'])):
                    #         if (triggered_action['lines'][action_line] != None):
                    #             triggered_action['line'] = action_line
                    #             triggered_action['source'] = "staff" # to know the source of the trigger
                    #             for frameStakedKeysRuler in merged_staff_keys:
                    #                 frameStakedKeysRuler['line'] = action_line + triggered_action['offset'] - frameStakedKeysRuler['offset']
                    #                 if (frameStakedKeysRuler['line'] < 0 or not (frameStakedKeysRuler['line'] < len(frameStakedKeysRuler['lines']))):
                    #                     frameStakedKeysRuler['line'] = None # in case key line is out of range of the triggered action line


                    #             action_object = triggered_action['lines'][action_line]


                    #             if (action_object == self):        
                    #                 action_object.actionInternalTrigger(triggered_action, merged_staff_keys, tempo) # WHERE ACTION IS TRIGGERED
                    #             else:        
                    #                 action_object.actionExternalTrigger(triggered_action, merged_staff_keys, tempo) # WHERE ACTION IS TRIGGERED
                    # print("")

                self.play_sequence += 1

            else:
                self.clock.stop()
                self.play_mode = False
                self.play_sequence = self.staff_grid.sequence(self.staff_grid.range()[0])

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
        pass

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


  # def getPositionSequence(self, position):
    #     if (position != None):
    #         step_frame = position.split('.')
    #         step_frame = [int(x) for x in step_frame]
    #         timeGridFrame = [ timeFrame for timeFrame in self.timeGrid if timeFrame['step'] in [step_frame[0]] ]
    #         timeGridFrame = [ timeFrame for timeFrame in timeGridFrame if timeFrame['frame'] in [step_frame[1]] ]
    #         if (len(timeGridFrame) > 0):
    #             return timeGridFrame[0]['sequence']
    #     return None
 
    # def addRuler(self, ruler):
    #     if ruler != None and len(ruler) > 0:
    #         if (ruler['type'] in self.rulerTypes):
    #             if 'group' not in ruler or ruler['group'] == None:
    #                 ruler['group'] = "main"
    #             if 'lines' not in ruler or ruler['lines'] == None or len(ruler['lines']) == 0:
    #                 ruler['lines'] = [None]
    #             if 'position' not in ruler or ruler['position'] == None: # Needs to add pattern matching
    #                 ruler['position'] = "0.0"

    #             rulers = self.filterRulers([type], [group], [position])
    #             if (len(rulers) > 0):
    #                 ...
    #             else:
    #                 newRuler = {
    #                     'type': type,
    #                     'group': group,
    #                     'lines': lines, # list
    #                     'position': None,
    #                     'sequence': None,
    #                     'offset': 0,
    #                     'enabled': True
    #                 }
    #                 self.staffRulers.append(newRuler)
    #                 return True
    #     return False

    # def addRuler(self, type, group, position, lines):
    #     if (type in self.rulerTypes):
    #         rulers = self.filterRulers([type], [group], [position])
    #         if (len(rulers) > 0):
    #             ...
    #         else:
    #             newRuler = {
    #                 'type': type,
    #                 'group': group,
    #                 'lines': lines, # list
    #                 'position': None,
    #                 'sequence': None,
    #                 'offset': 0,
    #                 'enabled': True
    #             }
    #             self.staffRulers.append(newRuler)
    #             return True
    #     return False

    # def addRuler(self, type, position, offset = None):
    #     ruler = self.getRuler(type)
    #     if (ruler != None):
    #         sequence = self.getPositionSequence(position)
    #         if (position != None): # add ruler to staff
    #             if (ruler['sequence'] == None): # not on staff
    #                 existent_staffgroup = False
    #                 for staffGroup in self.rulerGroups[type]: # REQUIRES self.rulerGroups
    #                     if (staffGroup == ruler['group']):
    #                         existent_staffgroup = True
    #                         break
    #                 if (not existent_staffgroup):
    #                     self.rulerGroups[type].append(ruler['group'])

    #         elif (position == None): # remove ruler from staff

    #             placed_rulers = self.filterRulers(ENABLED_ONLY=True)
    #             group_rulers = [
    #                     staffRuler
    #                         for staffRuler in placed_rulers if staffRuler['group'] in [ruler['group']]
    #             ]
    #             if (len(group_rulers) == 0):
    #                 self.rulerGroups[type].remove(ruler['group']) # REQUIRES self.rulerGroups

    #         if (ruler['position'] != None and ruler['sequence'] != None): # already enabled ruler
    #             self.timeGrid[ruler['sequence']]['enabled_rulers'][ruler['type']] -= 1
    #         if (sequence != None): # not a removal
    #             self.timeGrid[sequence]['enabled_rulers'][ruler['type']] += 1

    #         ruler['position'] = position
    #         ruler['sequence'] = sequence
    #         if (offset != None):
    #             ruler['offset'] = offset
    #     return ruler

    # def removeRuler(self, type):
    #     self.placeRuler(type, None)

    # def deleteRulers(self, types = [], groups = []):
    #     rulers = self.disableRulers(type, types, groups) # makes sure ruler gets disabled first
    #     for ruler in rulers:
    #         # Using list comprehension
    #         self.rulerGroups[ruler['type']] = [
    #             rulerGroup for rulerGroup in self.rulerGroups[ruler['type']] if not (rulerGroup['group'] == ruler['group'])
    #         ]
    
    # def getRuler(self, type, group):
    #     for staffRuler in self.staffRulers:
    #         if staffRuler['group'] == group and staffRuler['type'] == type:
    #             return staffRuler
    #     return None
   
    # def listRulers(self):
    #     for staffRuler in self.staffRulers:
    #         print(staffRuler)
    
    # def listStaffGroups(self):
    #     for type in self.rulerTypes:
    #         for group in self.rulerGroups[type]: # REQUIRES self.rulerGroups
    #             print(f"{type}\t{group}")

    # def stackStaffRulers(self, types = [], groups = [], position = None, sequence = None):

    #     if (position == None and sequence == None):
    #         sequence = self.play_range_positions[1]
    #         position = self.timeGrid[sequence]['position']
    #     elif (position == None):
    #         position = self.timeGrid[sequence]['position']
    #     else:
    #         sequence = self.getPositionSequence(position)

    #     if (len(types) == 0):
    #         types = self.rulerTypes

    #     stacked_internal_keys = []
    #     remaining_external_keys = self.external_staff_keys[:] # does a shallow copy
    #     for type in types:
    #         if (len(groups) == 0):
    #             groups = self.rulerGroups[type] # REQUIRES self.rulerGroups

    #         for group in groups:
    #             filtered_rulers = self.filterRulers([type], [group], ENABLED_ONLY=True)
    #             # Using list comprehension
    #             left_rulers = [
    #                 ruler for ruler in filtered_rulers if not (ruler['sequence'] > sequence)
    #             ]
                
    #             if (len(left_rulers) > 0): # left rulers ONLY!

    #                 external_rulers = [
    #                     ruler_keys for ruler_keys in remaining_external_keys if ruler_keys['group'] == group and ruler_keys['type'] == type
    #                 ]
    #                 remaining_external_keys = [
    #                     ruler_keys for ruler_keys in remaining_external_keys if not (ruler_keys['group'] == group and ruler_keys['type'] == type)
    #                 ]

    #                 head_offset = 0
    #                 tail_offset = 0
    #                 for left_ruler in external_rulers + left_rulers:
    #                     if left_ruler['offset'] < head_offset:
    #                         head_offset = left_ruler['offset']
    #                     if (len(left_ruler['lines']) + left_ruler['offset'] > tail_offset):
    #                         tail_offset = len(left_ruler['lines']) - 1 + left_ruler['offset']
                    
    #                 stackedRuler = {
    #                     'type': type,
    #                     'group': group,
    #                     'lines': [None] * (tail_offset - head_offset + 1), # list
    #                     'position': position,
    #                     'sequence': sequence,
    #                     'offset': head_offset
    #                 }

    #                 for external_ruler in external_rulers:
    #                     for i in range(len(external_ruler['lines'])):
    #                         stacked_line = i + external_ruler['offset'] - stackedRuler['offset']
    #                         stackedRuler['lines'][stacked_line] = external_ruler['lines'][i]

    #                 lower_sequence = sequence

    #                 while (not (lower_sequence < 0)):

    #                     total_key_rulers = self.timeGrid[lower_sequence]['enabled_rulers']['keys']
    #                     total_action_rulers = self.timeGrid[lower_sequence]['enabled_rulers']['actions']

    #                     if (total_key_rulers > 0):

    #                         lower_rulers = [
    #                             staffRuler
    #                                 for staffRuler in left_rulers if staffRuler['sequence'] in [lower_sequence]
    #                         ]
                            
    #                         for lower_ruler in lower_rulers:
    #                             for i in range(len(lower_ruler['lines'])):
    #                                 stacked_line = i + lower_ruler['offset'] - stackedRuler['offset']
    #                                 if (stackedRuler['lines'][stacked_line] == None):
    #                                     stackedRuler['lines'][stacked_line] = lower_ruler['lines'][i]

    #                     lower_sequence -= 1

    #                 stacked_internal_keys.append(stackedRuler)
    #     return stacked_internal_keys + remaining_external_keys
    
    # def filterRulers(self, types = [], groups = [], positions = [], sequeces = [], sequeces_range = [], ENABLED_ONLY = False, INSIDE_RANGE = False):
    #     filtered_rulers = self.staffRulers
    #     if (ENABLED_ONLY):
    #         filtered_rulers = [
    #             staffRuler for staffRuler in filtered_rulers if staffRuler['enabled'] == True
    #         ]
    #     if (INSIDE_RANGE):
    #         # Using list comprehension
    #         filtered_rulers = [
    #             staffRuler for staffRuler in filtered_rulers if staffRuler['sequence']
    #                     if not (staffRuler['sequence'] < self.play_range_positions[0] or staffRuler['sequence'] > self.play_range_positions[1])
    #         ]
    #     if (len(types) > 0 and types != [None]):
    #         filtered_rulers = [
    #             staffRuler
    #                 for staffRuler in filtered_rulers if staffRuler['type'] in types
    #         ]
    #     if (len(groups) > 0 and groups != [None]):
    #         filtered_rulers = [
    #             staffRuler
    #                 for staffRuler in filtered_rulers if staffRuler['group'] in groups
    #         ]
    #     if (len(positions) > 0 and positions != [None]): # Check for as None for NOT enabled
    #         filtered_rulers = [
    #             staffRuler
    #                 for staffRuler in filtered_rulers if staffRuler['position'] in positions
    #         ]
    #     if (len(sequeces_range) > 0 and sequeces_range != [None]): # Check for as None for NOT on STAFF
    #         if (len(sequeces_range) == 1):
    #             sequeces_range.append(sequeces_range[0])
    #             sequeces_range[0] = 0
    #         # Using list comprehension
    #         filtered_rulers = [
    #             staffRuler for staffRuler in filtered_rulers if staffRuler['sequence']
    #                     if not (staffRuler['sequence'] < sequeces_range[0] or staffRuler['sequence'] > sequeces_range[1])
    #         ]
    #     if (len(sequeces) > 0 and sequeces != [None]): # Check for as None for NOT on STAFF
    #         filtered_rulers = [
    #             staffRuler
    #                 for staffRuler in filtered_rulers if staffRuler['sequence'] in sequeces
    #         ]
    #     return filtered_rulers
    
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