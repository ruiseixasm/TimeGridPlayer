def main():
    print("Hello!")

class Event:

    def __init__(self, name, steps, frames, play_range=[], MASTER=False):

        self.master = MASTER
        self.play_mode = self.master

        self.name = name
        self.steps = steps
        self.frames = frames

        self.play_range = play_range
        if (len(play_range) == 0):
            self.play_range = [0, self.steps*self.frames - 1]
        elif (len(play_range) == 1):
            self.play_range = [0, play_range[0]]
        else:
            if (self.play_range[0] == None):
                self.play_range[0] = 0
            if (self.play_range[1] == None):
                self.play_range[1] = self.steps*self.frames - 1
        self.nextSequence = self.play_range[0]

        # OPTIMIZERS
        self.rulerTypes = ['keys', 'events']
        self.staffGroups = {'keys': [], 'events': []}

        self.timeGrid = []
        self.staffRulers = []
        self.staffEvents = []

        for i in range(self.steps*self.frames):

            frameData = {'sequence': 0, 'position': "", 'step': 0, 'frame': 0, 'time': 0, 'triggered': False}
            frameData['sequence'] = i
            frameData['step'] = int(i/self.frames)
            frameData['frame'] = int(i % self.frames)
            frameData['position'] = str(frameData['step']) + "." + str(frameData['frame'])

            self.timeGrid.append(frameData)

    def getPositionSequence(self, position):
        if (position != None):
            step_frame = position.split('.')
            step_frame = [int(x) for x in step_frame]
            timeGridFrame = [ timeFrame for timeFrame in self.timeGrid if timeFrame['step'] in [step_frame[0]] ]
            timeGridFrame = [ timeFrame for timeFrame in timeGridFrame if timeFrame['frame'] in [step_frame[1]] ]
            return timeGridFrame[0]['sequence']
        return None

    def addRuler(self, type, name, group, lines):
        if (type in self.rulerTypes and self.getRuler(type, name) == None):
            newRuler = {
                'type': type,
                'name': name,
                'group': group,
                'lines': lines, # list
                'offset': 0,
                'position': None,
                'sequence': None
            }
            self.staffRulers.append(newRuler)
            return True
        return False

    def getRuler(self, type, name):
        for staffRuler in self.staffRulers:
            if staffRuler['name'] == name and staffRuler['type'] == type:
                return staffRuler
        return None
    
    def filterRulers(self, types = [], names = [], groups = [], positions = [], ON_STAFF = False):
        filtered_rulers = self.staffRulers
        if (ON_STAFF):
            filtered_rulers = [
                staffRuler
                    for staffRuler in filtered_rulers if staffRuler['position'] not in [None]
            ]
        if (len(types) > 0):
            filtered_rulers = [
                staffRuler
                    for staffRuler in filtered_rulers if staffRuler['type'] in types
            ]
        if (len(names) > 0):
            filtered_rulers = [
                staffRuler
                    for staffRuler in filtered_rulers if staffRuler['name'] in names
            ]
        if (len(groups) > 0):
            filtered_rulers = [
                staffRuler
                    for staffRuler in filtered_rulers if staffRuler['group'] in groups
            ]
        if (len(positions) > 0):
            filtered_rulers = [
                staffRuler
                    for staffRuler in filtered_rulers if staffRuler['position'] in positions
            ]
        return filtered_rulers

    def placeRuler(self, type, name, position):
        ruler = self.getRuler(type, name)
        if (ruler != None):
            if (position != None): # add ruler to staff
                if (ruler['position'] == None): # not on staff
                    existent_staffgroup = False
                    for staffGroup in self.staffGroups[type]: # REQUIRES self.staffGroups
                        if (staffGroup == ruler['group']):
                            existent_staffgroup = True
                            break
                    if (not existent_staffgroup):
                        self.staffGroups[type].append(ruler['group'])

            elif (ruler['position'] != None): # remove ruler from staff

                placed_rulers = self.filterRulers(ON_STAFF=True)
                group_rulers = [
                        staffRuler
                            for staffRuler in placed_rulers if staffRuler['group'] in [ruler['group']]
                ]
                if (len(group_rulers) == 0):
                    self.staffGroups[type].remove(ruler['group']) # REQUIRES self.staffGroups

            ruler['position'] = position
            ruler['sequence'] = self.getPositionSequence(position)

    def removeRuler(self, type, name):
        self.placeRuler(type, name, None)

    def deleteRuler(self, type, name):
        for i in range(len(self.staffRulers)):
            if self.staffRulers[i]['name'] == name and self.staffRulers[i]['type'] == type:
                del(self.staffRulers[i])
                break
    
    def listRulers(self):
        for staffRuler in self.staffRulers:
            print(staffRuler)
    
    def listStaffGroups(self):
        for type in self.rulerTypes:
            for group in self.staffGroups[type]: # REQUIRES self.staffGroups
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
                    groups = self.staffGroups[type] # REQUIRES self.staffGroups
                for group in groups:
                    filtered_rulers = self.filterRulers([type], [], [group], ON_STAFF=True)
                    left_rulers = []
                    for filtered_ruler in filtered_rulers:
                        if (filtered_ruler['sequence'] <= sequence):
                            left_rulers.append(filtered_ruler)
                    
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
                            'offset': head_offset,
                            'position': position,
                            'sequence': sequence
                        }

                        lower_sequence = sequence

                        while (not (lower_sequence < 0)):

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

            if (self.nextSequence <= self.play_range[1]):

                position = self.timeGrid[self.nextSequence]['position']
                frameStaffEvents = self.filterRulers(types=["events"], positions=[position], ON_STAFF=True)
                if (len(frameStaffEvents) > 0):
                    frameStackedKeys = self.stackStaffRulers(['keys'], [], position)
                    print("\n\n\n")
                    for staffEvent in frameStaffEvents:
                        for line in range(len(staffEvent['lines'])):
                            if (staffEvent['lines'][line] != None):
                                staffEvent['lines'][line](line, frameStackedKeys)
                    print("\n\n\n")

                print(f"{self.nextSequence}\t{position}")

                self.timeGrid[self.nextSequence]['triggered'] = True
                self.nextSequence += 1

            else:
                if (self.master):
                    self.clock.detachAll()
                self.play_mode = False
                self.nextSequence = self.play_range[0]
                    
    def __str__(self):
        finalString = ""
        last_time = 0
        for frame in self.timeGrid:
            finalString += f"{frame['sequence']}\t{frame['position']}\t{frame['time']:.6f}\t{frame['time'] - last_time:.6f}\n"
            last_time = frame['time']
        return finalString
    

class Master(Event):
    
    def __init__(self, name, steps, frames):
        super().__init__(name, steps, frames, MASTER=True)

class Note(Event):
    
    def __init__(self, name, steps, frames):
        super().__init__(name, steps, frames)

    def play(self, line, staffKeys):
        self.note = staffKeys[0]['lines'][line]
        super().play_mode = True

    def on(self):
        print(f"note ON:\t{self.note}")

    def off(self):
        print(f"note OFF:\t{self.note}")

class Trigger(Event):
    
    def __init__(self, name):
        super().__init__(name, 0, 0)

    def play(self, staffKeys):
        ...

    def on(self):
        ...

    def off(self):
        ...

if __name__ == "__main__":
    main()