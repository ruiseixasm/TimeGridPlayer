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
            ruler['position'] = position
            ruler['sequence'] = self.getPositionSequence(position)
            if (position != None):
                ruler_lines = len(ruler['lines'])
                if(ruler_lines > self.staffLines):
                    self.staffLines = ruler_lines
            else:
                placed_rullers = [
                        staffRuler
                            for staffRuler in self.staffRulers if staffRuler['position'] not in [position]
                    ]
                self.staffLines = 0
                for placed_ruller in placed_rullers:
                    ruler_lines = len(placed_ruller['lines'])
                    if(ruler_lines > self.staffLines):
                        self.staffLines = ruler_lines


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


    def stackStaffRulers(self, type, group, position, sequence = None):
        if (sequence == None and position != None):
            sequence = self.getPositionSequence(position)
        filtered_rulers = self.filterRulers(types = [type], groups = [group])
        left_rulers = []
        for filtered_ruler in filtered_rulers:
            if (filtered_ruler['sequence'] <= sequence):
                left_rulers.append(filtered_ruler)
        top_ruler = []
        top_ruler.append(left_rulers[0])
        for left_ruler in left_rulers:
            if (left_ruler['sequence'] > top_ruler[0]['sequence']):
                top_ruler[0] = left_ruler
        dictionary_copy = top_ruler[0].copy()
        top_ruler[0] = dictionary_copy # copy by value

        lower_sequence = top_ruler[0]['sequence']
        while (not (lower_sequence < 0)):

            lower_rulers = [
                staffRuler
                    for staffRuler in left_rulers if staffRuler['sequence'] in [lower_sequence]
            ]
            
            for lower_ruler in lower_rulers:
                for i in range(len(lower_ruler['lines'])):
                    if (not (i < len(top_ruler[0]['lines']))):
                        top_ruler[0]['lines'].append(lower_ruler['lines'][i])
                    elif (top_ruler[0]['lines'][i] == None):
                        top_ruler[0]['lines'][i] = lower_ruler['lines'][i]

            lower_sequence -= 1
        return top_ruler
    
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