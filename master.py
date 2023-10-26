
import time

def main():
    print("Hello!")

class Master:
    def __init__(self, steps, frames, tempo):
        self.steps = steps
        self.frames = frames
        self.tempo = tempo

        self.timeGrid = []
        self.staffEvents = []
        self.staffRulers = []

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

                actual_position = [self.timeGrid[nextFrameID]['position']]

                actual_events = [
                    dictionary for dictionary in self.staffEvents if dictionary['position'] in actual_position
                ]

                self.timeGrid[nextFrameID]['triggered'] = True
                nextFrameID += 1
                lastTime = time.time() - startTime

    def tick(self):
        pass
        
    def addRuler(self, name, position, ruler):
        newRuler = {
            'name': name,
            'position': position,
            'ruler': ruler,
            'triggered': False
        }
        self.staffRulers.append(newRuler)
    
    def listRulers(self, position):
        pass

    def addEvents(self, name, position, events):
        newEvents = {
            'name': name,
            'position': position,
            'events': events,
            'triggered': False
        }
        self.staffEvents.append(newEvents)

    def listEvents(self, position):
        pass
                
    def __str__(self):
        finalString = ""
        for frame in self.timeGrid:
            finalString += f"{frame['frame_id']}\t{frame['position']}\t{frame['time']}\n"
        return finalString



if __name__ == "__main__":
    main()