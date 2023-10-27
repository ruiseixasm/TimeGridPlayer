
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
        self.staffRulers = []
        self.staffEvents = []

        for i in range(self.steps*self.frames):

            frameData = {'frame_id': 0, 'position': "", 'step': 0, 'frame': 0, 'time': 0, 'triggered': False}
            frameData['frame_id'] = i
            frameData['step'] = int(i/self.frames)
            frameData['frame'] = int(i % self.frames)
            frameData['position'] = str(frameData['step']) + "." + str(frameData['frame'])
            frameData['time'] = self.tempo * frameData['step'] + self.tempo * frameData['frame'] / self.frames

            self.timeGrid.append(frameData)


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
        
    def addRuler(self, type, name, group, lines):
        if (type in self.rulerTypes and self.getRuler(type, name) == None):
            newRuler = {
                'type': type,
                'name': name,
                'group': group,
                'lines': lines, # list
                'position': None
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
        self.getRuler(type, name)['position'] = position

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

                
    def __str__(self):
        finalString = ""
        for frame in self.timeGrid:
            finalString += f"{frame['frame_id']}\t{frame['position']}\t{frame['time']}\n"
        return finalString

if __name__ == "__main__":
    main()