def main():
    print("Hello!")

class Event:

    def __init__(self, name, steps, frames, play_range=[], MASTER=False):

        self.master = MASTER
        self.play_mode = self.master

        self.name = name
        self.steps = max(1, steps)
        self.frames = max(1, frames)

        # OPTIMIZERS
        self.rulerTypes = ['keys', 'events']
        self.rulerGroups = {'keys': [], 'events': []}

        self.timeGrid = []
        self.staffRulers = []
        self.staffEvents = []

        for i in range(self.steps*self.frames):

            frameData = {
                'sequence': i,
                'position': None,
                'step': int(i/self.frames),
                'frame': int(i % self.frames),
                'enabled_rulers': {'keys': 0, 'events': 0}
            }
            frameData['position'] = str(frameData['step']) + "." + str(frameData['frame'])

            self.timeGrid.append(frameData)

        # SET RANGES
        self.play_range_sequences = [0, self.steps*self.frames - 1]
        if (len(play_range) == 1):
            last_sequence = self.getPositionSequence(play_range[0])
            if (last_sequence != None):
                self.play_range_sequences[1] = last_sequence
        elif (len(play_range) > 1):
            if (play_range[0] != None):
                first_sequence = self.getPositionSequence(play_range[0])
                if (first_sequence != None):
                    self.play_range_sequences[0] = first_sequence
            if (play_range[1] != None): # NEEDS TO BE MAJORATED TO THE RESPECTIVE FRAME (-1)
                last_sequence = self.getPositionSequence(play_range[0])
                if (last_sequence != None):
                    self.play_range_sequences[1] = last_sequence
                
        start_position = self.timeGrid[self.play_range_sequences[0]]['position']
        finish_position = self.timeGrid[self.play_range_sequences[1]]['position']
        self.play_range_positions = [start_position, finish_position]

        self.nextSequence = self.play_range_sequences[0]


    def getPositionSequence(self, position):
        if (position != None):
            step_frame = position.split('.')
            step_frame = [int(x) for x in step_frame]
            timeGridFrame = [ timeFrame for timeFrame in self.timeGrid if timeFrame['step'] in [step_frame[0]] ]
            timeGridFrame = [ timeFrame for timeFrame in timeGridFrame if timeFrame['frame'] in [step_frame[1]] ]
            if (len(timeGridFrame) > 0):
                return timeGridFrame[0]['sequence']
        return None
 
    def filterRulers(self, types = [], groups = [], names = [], positions = [], ENABLED_ONLY = False, DISABLED_ONLY=False, ON_STAFF = False):
        filtered_rulers = self.staffRulers
        if (ENABLED_ONLY):
            filtered_rulers = [
                staffRuler
                    for staffRuler in filtered_rulers if staffRuler['position'] not in [None] # Without a given position it's considered disabled!
            ]
        if (DISABLED_ONLY):
            filtered_rulers = [
                staffRuler
                    for staffRuler in filtered_rulers if staffRuler['position'] in [None] # Without a given position it's considered disabled!
            ]
        if (ON_STAFF):
            filtered_rulers = [
                staffRuler
                    for staffRuler in filtered_rulers if staffRuler['sequence'] not in [None] # Without a given position it's considered disabled!
            ]
        if (len(types) > 0):
            filtered_rulers = [
                staffRuler
                    for staffRuler in filtered_rulers if staffRuler['type'] in types
            ]
        if (len(groups) > 0):
            filtered_rulers = [
                staffRuler
                    for staffRuler in filtered_rulers if staffRuler['group'] in groups
            ]
        if (len(names) > 0):
            filtered_rulers = [
                staffRuler
                    for staffRuler in filtered_rulers if staffRuler['name'] in names
            ]
        if (len(positions) > 0):
            filtered_rulers = [
                staffRuler
                    for staffRuler in filtered_rulers if staffRuler['position'] in positions
            ]
        return filtered_rulers
    
    def enableRulers(self, types = [], groups = [], names = [], positions = []):
        rulers = self.filterRulers(types, groups, names, positions, DISABLED_ONLY = True, ON_STAFF=True)
        if (len(rulers) > 0):
            for ruler in rulers:
                ruler['position'] = self.timeGrid[ruler['sequence']]['position']
                self.timeGrid[ruler['sequence']]['enabled_rulers'][ruler['type']] += 1
        return rulers


    def disableRulers(self, types = [], groups = [], names = [], positions = []):
        rulers = self.filterRulers(types, groups, names, positions, ENABLED_ONLY = True)
        if (len(rulers) > 0):
            for ruler in rulers:
                ruler['position'] = None
                if (ruler['sequence'] != None): # avoids compiler error
                    self.timeGrid[ruler['sequence']]['enabled_rulers'][ruler['type']] -= 1
        return rulers

    def placeRuler(self, type, name, position, offset = None):
        ruler = self.getRuler(type, name)
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

    def removeRuler(self, type, name):
        self.placeRuler(type, name, None)

    def deleteRulers(self, types = [], groups = [], names = []):
        rulers = self.disableRulers(type, types, groups, names) # makes sure ruler gets disabled first
        for ruler in rulers:
            # Using list comprehension
            self.rulerGroups[ruler['type']] = [
                rulerGroup for rulerGroup in self.rulerGroups[ruler['type']] if not (rulerGroup['name'] == ruler['name'])
            ]
    
    def addRuler(self, type, group, name, lines):
        if (type in self.rulerTypes and self.getRuler(type, name) == None):
            newRuler = {
                'type': type,
                'group': group,
                'name': name,
                'lines': lines, # list
                'position': None,
                'sequence': None,
                'offset': 0
            }
            self.staffRulers.append(newRuler)
            return True
        return False

    def getRuler(self, type, name):
        for staffRuler in self.staffRulers:
            if staffRuler['name'] == name and staffRuler['type'] == type:
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
        top_rulers = []
        if (sequence != None or position != None):
            if (position == None or sequence != None):
                position = self.timeGrid[sequence]['position']
            if (sequence == None):
                sequence = self.getPositionSequence(position)
            if (len(types) == 0):
                types = self.rulerTypes
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

                        head_offset = 0
                        tail_offset = 0
                        for left_ruler in left_rulers:
                            if left_ruler['offset'] < head_offset:
                                head_offset = left_ruler['offset']
                            if (len(left_ruler['lines']) + left_ruler['offset'] > tail_offset):
                                tail_offset = len(left_ruler['lines']) - 1 + left_ruler['offset']
                        
                        stackedRuler = {
                            'type': type,
                            'name': self.name,
                            'group': group,
                            'lines': [None] * (tail_offset - head_offset + 1), # list
                            'position': position,
                            'sequence': sequence,
                            'offset': head_offset
                        }

                        lower_sequence = sequence

                        while (not (lower_sequence < 0)):

                            total_key_rulers = self.timeGrid[lower_sequence]['enabled_rulers']['keys']
                            total_event_rulers = self.timeGrid[lower_sequence]['enabled_rulers']['keys']

                            if (total_key_rulers > 0):

                                lower_rulers = [
                                    staffRuler
                                        for staffRuler in left_rulers if staffRuler['sequence'] in [lower_sequence]
                                ]
                                
                                for lower_ruler in lower_rulers:
                                    for i in range(len(lower_ruler['lines'])):
                                        line = i + lower_ruler['offset']
                                        if (stackedRuler['lines'][line] == None):
                                            stackedRuler['lines'][line] = lower_ruler['lines'][i]

                            lower_sequence -= 1

                        top_rulers.append(stackedRuler)
        return top_rulers
    
    def play(self):
        self.play_mode = True

    def connectClock(self, clock):
        self.clock = clock
        self.clock.attach(self)

    def pulse(self, tempo):
        #print(f"CALLED:\t{self.play_mode}")
        if (self.play_mode):

            #print(f"\tPULSE: {self.nextSequence}")

            if (self.nextSequence <= self.play_range_sequences[1]):

                position = self.timeGrid[self.nextSequence]['position']
                total_key_rulers = self.timeGrid[self.nextSequence]['enabled_rulers']['keys']
                total_event_rulers = self.timeGrid[self.nextSequence]['enabled_rulers']['events']
                print(f"{self.nextSequence}\t{position}\t{total_key_rulers}\t{total_event_rulers}")

                if (total_event_rulers > 0):
                    frameStaffEvents = self.filterRulers(types=["events"], positions=[position], ENABLED_ONLY=True)
                    frameStackedKeys = self.stackStaffRulers(['keys'], [], position) # list of multiple rulers
                    print("")
                    for staffEvent in frameStaffEvents: # single ruler events
                        for event_line in range(len(staffEvent['lines'])):
                            if (staffEvent['lines'][event_line] != None):
                                staffEvent['line'] = event_line
                                for frameStakedKeysRuler in frameStackedKeys:
                                    frameStakedKeysRuler['line'] = event_line + staffEvent['offset'] - frameStakedKeysRuler['offset']
                                    if (frameStakedKeysRuler['line'] < 0 or not (frameStakedKeysRuler['line'] < len(frameStakedKeysRuler['lines']))):
                                        frameStakedKeysRuler['line'] = None
                                staffEvent['lines'][event_line](staffEvent, frameStackedKeys)
                    print("")

                self.nextSequence += 1

            else:
                if (self.master):
                    self.clock.detachAll()
                self.play_mode = False
                self.nextSequence = self.play_range_sequences[0]
                    
    def __str__(self):
        finalString = ""
        last_time = 0
        for frame in self.timeGrid:
            finalString += f"{frame['sequence']}\t{frame['position']}\n"
        return finalString
    

class Master(Event):
    
    def __init__(self, name, steps, frames):
        super().__init__(name, steps, frames, MASTER=True) # not self init

class Note(Event):
    
    def __init__(self, name, steps, frames, play_range=[]):
        super().__init__(name, steps, frames, play_range) # not self init
        start_position = self.play_range_positions[0]
        finish_position = self.play_range_positions[1]

        if (self.addRuler("events", "notes", "note_on", [self.on])):
            self.placeRuler('events', "note_on", start_position)

        if (self.addRuler("events", "notes", "note_off", [self.off])):
            self.placeRuler('events', "note_off", finish_position)

    def play(self, staffEvent, frameStackedKeys):
        if (len(frameStackedKeys) > 0):
            given_lines = frameStackedKeys[0]['lines']
            key_line = frameStackedKeys[0]['line']
            key_value = given_lines[key_line]
            self.note = key_value # may need tranlation!
            self.play_mode = True

    def on(self, staffEvent, frameStackedKeys):
        print(f"note ON:\t{self.note}")

    def off(self, staffEvent, frameStackedKeys):
        print(f"note OFF:\t{self.note}")

class Trigger(Event):
    
    def __init__(self, name):
        super().__init__(name, 0, 0) # not self init
        self.addRuler("events", "triggers", name, [self.play])

    def play(self, staffEvent, frameStackedKeys):
        print("TRIGGERED")

if __name__ == "__main__":
    main()