import time

class Clock(): # Subject
    def __init__(self, steps_minute, frames_step):
        """create an empty observer list"""
        self._observers = []
        self.tempo = {'steps_minute': steps_minute, 'frames_step': frames_step, 'fast_forward': False}
        self.frame_duration = self.getFrameDuration(steps_minute, frames_step) # in seconds

    def getFrameDuration(self, steps_minute, frames_step): # in seconds
        return 60.0 / steps_minute / frames_step

    def notify(self):
        """Alert the observers"""
        for observer in self._observers:
            observer.pulse(self.tempo) # calls the Observers update method
            #print("PULSE")

    def attach(self, observer):
        """If the observer is not in the list, append it into the list"""
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer):
        """Remove the observer from the observer list"""
        try:
            self._observers.remove(observer)
        except ValueError:
            pass
        
    def detachAll(self):
        """Remove all observers from the observer list"""
        self._observers = []


    def start(self, frames_step = None, clock_range = []):

        first_sequence = 0
        last_sequence = None

        if (frames_step != None and len(clock_range) == 2):
            if (clock_range[0] != None):
                step_frame = clock_range[0].split('.')
                first_sequence = int(step_frame[0]) * frames_step + int(step_frame[1])
            if (clock_range[1] != None):
                step_frame = clock_range[1].split('.')
                last_sequence = int(step_frame[0]) * frames_step + int(step_frame[1]) - 1 # Excludes last sequence

        startTime = None
        nextTime = 0
        frame = 0
        while (len(self._observers) > 0):
            if (frame < first_sequence or (last_sequence != None and frame > last_sequence)):
                self.tempo['fast_forward'] = True
            else:
                self.tempo['fast_forward'] = False
                if (startTime == None):
                    startTime = time.time() # in seconds
                    nextTime = startTime

            if nextTime < time.time() or self.tempo['fast_forward'] == True:
                self.notify()
                frame += 1
                if (startTime != None):
                    #print(f"CLOCK:\t\t{nextTime:.6f}\t{startTime + frame * self.frame_duration:.6f}\t{time.time() - startTime:.6f}")
                    nextTime = startTime + (frame - first_sequence) * self.frame_duration


# MIDI beat clock defines the following real-time messages:

# clock (decimal 248, hex 0xF8)
# start (decimal 250, hex 0xFA)
# continue (decimal 251, hex 0xFB)
# stop (decimal 252, hex 0xFC)



# class Subject:

#     """Represents what is being observed"""

#     def __init__(self):
#         """create an empty observer list"""
#         self._observers = []
 
#     def notify(self, modifier = None):
#         """Alert the observers"""
#         for observer in self._observers:
#             if modifier != observer:
#                 observer.update(self)
 
#     def attach(self, observer):
#         """If the observer is not in the list, append it into the list"""
#         if observer not in self._observers:
#             self._observers.append(observer)
 
#     def detach(self, observer):
#         """Remove the observer from the observer list"""
#         try:
#             self._observers.remove(observer)
#         except ValueError:
#             pass
  
# class Data(Subject): # Obesrvable that triggers the Subject notify!
#     """monitor the object"""
#     def __init__(self, name =''):
#         Subject.__init__(self)
#         self.name = name
#         self._data = 0
 
#     @property
#     def data(self):
#         return self._data
 
#     @data.setter
#     def data(self, value):
#         self._data = value
#         self.notify()
  
# class HexViewer:
#     """updates the Hexviewer"""
#     def update(self, Subject):
#         print('HexViewer: Subject {} has data 0x{:x}'.format(Subject.name, Subject.data))
 
# class OctalViewer:
#     """updates the Octal viewer"""
#     def update(self, Subject):
#         print('OctalViewer: Subject' + str(Subject.name) + 'has data '+str(oct(Subject.data)))
  
# class DecimalViewer:
#     """updates the Decimal viewer"""
#     def update(self, Subject):
#         print('DecimalViewer: Subject % s has data % d' % (Subject.name, Subject.data))
 
# """main function"""
# if __name__ == "__main__":
 
#     """provide the data"""
#     obj1 = Data('Data 1')
#     obj2 = Data('Data 2')
 
#     """Observers"""
#     view1 = DecimalViewer()
#     view2 = HexViewer()
#     view3 = OctalViewer()
 
#     """Observers Subscription on Data Observable"""
#     obj1.attach(view1)
#     obj1.attach(view2)
#     obj1.attach(view3)
 
#     obj2.attach(view1)
#     obj2.attach(view2)
#     obj2.attach(view3)
 
#     """Observable change that triggers notify and update on Observers"""
#     obj1.data = 10
#     obj2.data = 15