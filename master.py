import time

def main():
    print("Hello!")

class Master:

    def __init__(self, steps, frames, tempo):
        self.steps = steps
        self.frames = frames
        self.tempo = tempo

        self.timeGrid = []
        self.rulerTypes = ['keys', 'events']
        self.staffLines = 0
        self.staffRulers = []
        self.staffGroups = {'keys': [], 'events': []}
        self.staffEvents = []

        for i in range(self.steps*self.frames):

            frameData = {'sequence': 0, 'position': "", 'step': 0, 'frame': 0, 'time': 0, 'triggered': False}
            frameData['sequence'] = i
            frameData['step'] = int(i/self.frames)
            frameData['frame'] = int(i % self.frames)
            frameData['position'] = str(frameData['step']) + "." + str(frameData['frame'])
            frameData['time'] = self.tempo * frameData['step'] + self.tempo * frameData['frame'] / self.frames

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
    
    def filterRulers(self, types = [], names = [], groups = [], positions = []):
        filtered_rulers = self.staffRulers
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
                    for staffGroup in self.staffGroups[type]:
                        if (staffGroup == ruler['group']):
                            existent_staffgroup = True
                            break
                    if (not existent_staffgroup):
                        self.staffGroups[type].append(ruler['group'])

                ruler['position'] = position
                ruler['sequence'] = self.getPositionSequence(position)
                ruler_lines = len(ruler['lines'])
                if(ruler_lines > self.staffLines):
                    self.staffLines = ruler_lines
            elif (ruler['position'] != None): # remove ruler from staff
                ruler['position'] = position
                ruler['sequence'] = self.getPositionSequence(position)

                placed_rulers = [
                        staffRuler
                            for staffRuler in self.staffRulers if staffRuler['position'] not in [None]
                    ]
                self.staffLines = 0
                for placed_ruler in placed_rulers:
                    ruler_lines = len(placed_ruler['lines'])
                    if(ruler_lines > self.staffLines):
                        self.staffLines = ruler_lines
                group_rulers = [
                        staffRuler
                            for staffRuler in placed_rulers if staffRuler['group'] in [ruler['group']]
                ]
                if (len(group_rulers) == 0):
                    self.staffGroups[type].remove(ruler['group'])

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
            for group in self.staffGroups[type]:
                print(f"{type}\t{group}")

    def stackStaffRulers(self, types = [], groups = [], position = None, sequence = None):
        if (sequence == None and position != None):
            sequence = self.getPositionSequence(position)
        if (len(types) == 0):
            types = self.rulerTypes
        top_rulers = []
        for type in types:
            if (len(groups) == 0):
                groups = self.staffGroups[type]
            for group in groups:
                filtered_rulers = self.filterRulers([type], [], [group])
                left_rulers = []
                for filtered_ruler in filtered_rulers:
                    if (filtered_ruler['sequence'] <= sequence):
                        left_rulers.append(filtered_ruler)
                stack_dictionary = left_rulers[0]
                for left_ruler in left_rulers:
                    if (left_ruler['sequence'] > stack_dictionary['sequence']):
                        stack_dictionary = left_ruler

                stack_dictionary = stack_dictionary.copy() # copy by value
                stack_dictionary = stack_dictionary

                lower_sequence = stack_dictionary['sequence']
                while (not (lower_sequence < 0)):

                    lower_rulers = [
                        staffRuler
                            for staffRuler in left_rulers if staffRuler['sequence'] in [lower_sequence]
                    ]
                    
                    for lower_ruler in lower_rulers:
                        for i in range(len(lower_ruler['lines'])):
                            if (not (i < len(stack_dictionary['lines']))):
                                stack_dictionary['lines'].append(lower_ruler['lines'][i])
                            elif (stack_dictionary['lines'][i] == None):
                                stack_dictionary['lines'][i] = lower_ruler['lines'][i]

                    lower_sequence -= 1

                top_rulers.append(stack_dictionary)
        return top_rulers
    
    def play(self):
        # current timestamp in seconds
        print("Timestamp:", time.time())
        nextFrameID = 0
        startTime = time.time()
        lastTime = time.time() - startTime
        while nextFrameID < len(self.timeGrid):
            if (time.time() - startTime > self.timeGrid[nextFrameID]['time']):
                actualTime = time.time() - startTime
                print(f"{nextFrameID}\t{self.timeGrid[nextFrameID]['position']}\t{actualTime:.6f}\t{actualTime - lastTime:.6f}")

                self.timeGrid[nextFrameID]['triggered'] = True
                nextFrameID += 1
                lastTime = time.time() - startTime

    def tick(self):
        pass
                    
    def __str__(self):
        finalString = ""
        last_time = 0
        for frame in self.timeGrid:
            finalString += f"{frame['sequence']}\t{frame['position']}\t{frame['time']:.6f}\t{frame['time'] - last_time:.6f}\n"
            last_time = frame['time']
        return finalString

if __name__ == "__main__":
    main()