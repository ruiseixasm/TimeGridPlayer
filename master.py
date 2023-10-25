
import time

def main():
    print("Hello!")

class Master:
    def __init__(self, steps, frames, tempo):
        self.steps = steps
        self.frames = frames
        self.tempo = tempo
        self.timeGrid = []
        self.eventGrid = []
        for i in range(self.steps*self.frames):

            frameData = {'frame-id': 0, 'tag': "", 'step': 0, 'frame': 0, 'time': 0, 'triggered': False}
            frameData['frame_id'] = i
            frameData['step'] = int(i/self.frames)
            frameData['frame'] = int(i % self.frames)
            frameData['tag'] = str(frameData['step']) + "." + str(frameData['frame'])
            frameData['time'] = self.tempo * frameData['step'] + self.tempo * frameData['frame'] / self.frames

            self.timeGrid.append(frameData)

    def play(self):
        # current timestamp in seconds
        startTime = time.time()
        print("Timestamp:", startTime)
        nextFrameID = 0
        while nextFrameID < len(self.timeGrid):
            if (time.time() - startTime > self.timeGrid[nextFrameID]['time']):
                print(f"{nextFrameID}\t{time.time() - startTime}")
                self.timeGrid[nextFrameID]['triggered'] = True
                nextFrameID += 1

                
    def __str__(self):
        finalString = ""
        for frame in self.timeGrid:
            finalString += f"{frame['frame_id']}\t{frame['tag']}\t{frame['time']}\n"
        return finalString



if __name__ == "__main__":
    main()