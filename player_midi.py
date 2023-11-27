'''TimeGridPlayer - Time Grid Player triggers Actions on a Staff
Original Copyright (c) 2023 Rui Seixas Monteiro. All right reserved.
This library is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 2.1 of the License, or (at your option) any later version.
This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
Lesser General Public License for more details.'''

import player as PLAYER
import resources as RESOURCES_MIDI

class Clock(PLAYER.Player):
    
    def __init__(self, name, description="Sends clock midi messages", resources=None):
        super().__init__(name, description, resources) # not self init
        self._clock = Clock.Clock(self)
        self._internal_clock = True
        if resources == None:
            self._resources = RESOURCES_MIDI.Midi()

    class Clock(PLAYER.Player.Clock):
        def __init__(self, player):
            super().__init__(player)
            self.set(beats_per_minute=120, steps_per_beat=4, pulses_per_quarter_note=24)

        def stop(self, tick = None):
            self._tick = super().stop(tick)
            if self._player.resource != None:
                # print(f"\tclock stop")
                self._player.resource.clockStop()
                # print(f"\tclock position start")
                self._player.resource.songPositionStart()

            return self._tick
            
        def tick(self, tick = None):
            if tick != None:
                self._pulse_duration = self.getPulseDuration(tick['tempo']['beats_per_minute'], 24) # in seconds

            self._tick = super().tick(tick)

            if self._tick['pulse'] != None: # a pulse of this clock
                if self._player.resource != None:
                    if self._next_pulse == 1:
                        #print(f"\tclock start")
                        self._player.resource.clockStart() # WERE THE MIDI START IS SENT
                    else:
                        #print(f"\tclock pulse")
                        self._player.resource.clock() # WERE THE MIDI CLOCK IS SENT

            return self._tick

    def actionTrigger(self, triggered_action, merged_staff_arguments, staff, tick):
        return self # No trigger actions for Clock Player

class Master(PLAYER.Player):
    
    def __init__(self, name, description="A conductor of multiple Players"):
        super().__init__(name, description) # not self init

        # implement midi clock here

class Note(PLAYER.Player):
    
    def __init__(self, name, description="Plays notes on a given Synth", resources=None):
        super().__init__(name, description, resources) # not self init
        if resources == None:
            self._resources = RESOURCES_MIDI.Midi()

    class Action(PLAYER.Player.Action):
        
        def __init__(self, player):
            super().__init__(player) # not self init
            self._finish_pulse = self._start_pulse # makes sure the Staff isn't used to make it only a clocked action
            self._note = {'key': "C", 'octave': 4, 'velocity': 100, 'channel': 1, 'duration': 4}

        ### ACTION ACTIONS ###

        def actionTrigger(self, triggered_action, merged_staff_arguments, staff, tick):
            super().actionTrigger(triggered_action, merged_staff_arguments, staff, tick)
            if staff == None: # CLOCKED TRIGGER

                print(f"note OFF:\t{self._note}")
                if self._player.resource != None:
                    self._player.resource.releaseNote(self._note, self._note['channel']) # WERE THE MIDI NOTE IS TRIGGERED

            else: # EXTERNAL TRIGGER
                if (not tick['fast_forward'] or True):

                    note_channel = self.pickTriggeredLineArgumentValue(merged_staff_arguments, "channel")
                    if (note_channel != None):
                        self._note['channel'] = note_channel

                    note_velocity = self.pickTriggeredLineArgumentValue(merged_staff_arguments, "velocity")
                    if (note_velocity != None):
                        self._note['velocity'] = note_velocity

                    note_duration = self.pickTriggeredLineArgumentValue(merged_staff_arguments, "duration")
                    if (note_duration != None):
                        self._note['duration'] = note_duration

                    note_octave = self.pickTriggeredLineArgumentValue(merged_staff_arguments, "octave")
                    if (note_octave != None):
                        self._note['octave'] = note_octave

                    note_key = self.pickTriggeredLineArgumentValue(merged_staff_arguments, "key")
                    if (note_key != None):
                        self._note['key'] = note_key

                        print(f"note ON:\t{self._note}")
                        if self._player.resource != None:
                            self._player.resource.pressNote(self._note, self._note['channel']) # WERE THE MIDI NOTE IS TRIGGERED
                    
                        # needs to convert steps duration accordingly to callers time signature
                        duration_converter = staff.time_signature()['steps_per_beat'] / self._staff.time_signature()['steps_per_beat']
                        self.addClockedAction(
                            {'triggered_action': triggered_action, 'staff_arguments': merged_staff_arguments,
                             'duration': self._note['duration'] * duration_converter, 'action': self},
                            tick
                        )
    
    def actionFactoryMethod(self):
        return Note.Action(self)

class Retrig(PLAYER.Player):
    
    def __init__(self, name, description="Retrigs a given note along a given duration", resources=None):
        super().__init__(name, description, resources) # not self init
        if resources == None:
            self._resources = RESOURCES_MIDI.Midi()

    class Action(PLAYER.Player.Action):
        
        def __init__(self, player):
            super().__init__(player) # not self init
            self._finish_pulse = self._start_pulse # makes sure the Staff isn't used to make it only a clocked action
            self._note = {'key': "C", 'octave': 4, 'velocity': 100, 'channel': 1, 'duration': 4}

        ### ACTION ACTIONS ###

        def actionTrigger(self, triggered_action, merged_staff_arguments, staff, tick):
            super().actionTrigger(triggered_action, merged_staff_arguments, staff, tick)
            if staff == None: # CLOCKED TRIGGER

                print(f"note OFF:\t{self._note}")
                if self._player.resource != None:
                    self._player.resource.releaseNote(self._note, self._note['channel']) # WERE THE MIDI NOTE IS TRIGGERED

            else: # EXTERNAL TRIGGER
                if (not tick['fast_forward'] or True):

                    note_channel = self.pickTriggeredLineArgumentValue(merged_staff_arguments, "channel")
                    if (note_channel != None):
                        self._note['channel'] = note_channel

                    note_velocity = self.pickTriggeredLineArgumentValue(merged_staff_arguments, "velocity")
                    if (note_velocity != None):
                        self._note['velocity'] = note_velocity

                    note_duration = self.pickTriggeredLineArgumentValue(merged_staff_arguments, "duration")
                    if (note_duration != None):
                        self._note['duration'] = note_duration

                    note_octave = self.pickTriggeredLineArgumentValue(merged_staff_arguments, "octave")
                    if (note_octave != None):
                        self._note['octave'] = note_octave

                    note_key = self.pickTriggeredLineArgumentValue(merged_staff_arguments, "key")
                    if (note_key != None):
                        self._note['key'] = note_key

                        print(f"note ON:\t{self._note}")
                        if self._player.resource != None:
                            self._player.resource.pressNote(self._note, self._note['channel']) # WERE THE MIDI NOTE IS TRIGGERED
                    
                        # needs to convert steps duration accordingly to callers time signature
                        duration_converter = staff.time_signature()['steps_per_beat'] / self._staff.time_signature()['steps_per_beat']
                        self.addClockedAction(
                            {'triggered_action': triggered_action, 'staff_arguments': merged_staff_arguments,
                             'duration': self._note['duration'] * duration_converter, 'action': self},
                            tick
                        )
    
    def actionFactoryMethod(self):
        return Note.Action(self)
