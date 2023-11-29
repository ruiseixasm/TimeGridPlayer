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
import resources_midi as RESOURCES_MIDI
import lines_scales as LINES_SCALES

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
            self._duration = 4 # steps
            self._note = {'key': "C", 'octave': 4, 'velocity': 100, 'channel': 1}

        ### ACTION ACTIONS ###

        def actionTrigger(self, triggered_action, merged_staff_arguments, staff, tick):
            super().actionTrigger(triggered_action, merged_staff_arguments, staff, tick)

            if staff == None: # CLOCKED TRIGGER

                print(f"note OFF:\t{self._note}")
                if self._player.resource != None:
                    self._player.resource.releaseNote(self._note, self._note['channel']) # WERE THE MIDI NOTE IS TRIGGERED

            else: # EXTERNAL TRIGGER

                if (not tick['fast_forward']):

                    note_duration = self.pickTriggeredLineArgumentValue(merged_staff_arguments, "duration")
                    if (note_duration != None):
                        self._duration = note_duration

                    note_channel = self.pickTriggeredLineArgumentValue(merged_staff_arguments, "channel")
                    if (note_channel != None):
                        self._note['channel'] = note_channel

                    note_velocity = self.pickTriggeredLineArgumentValue(merged_staff_arguments, "velocity")
                    if (note_velocity != None):
                        self._note['velocity'] = note_velocity

                    note_octave = self.pickTriggeredLineArgumentValue(merged_staff_arguments, "octave")
                    if (note_octave != None):
                        self._note['octave'] = note_octave

                    note_key = self.pickTriggeredLineArgumentValue(merged_staff_arguments, "key") # key is mandatory
                    if (note_key != None):
                        self._note['key'] = note_key

                        print(f"note ON:\t{self._note}")
                        if self._player.resource != None:
                            self._player.resource.pressNote(self._note, self._note['channel']) # WERE THE MIDI NOTE IS TRIGGERED

                        self_duration_pulses = self._duration * self._clock_pulses_per_step
                        clock_duration = self_duration_pulses * self._clock_trigger_steps_per_beat_ratio
                        
                        self.addClockedAction(
                            {'triggered_action': triggered_action, 'staff_arguments': merged_staff_arguments,
                             'duration': clock_duration, 'action': self}, tick
                        )
    
    def actionFactoryMethod(self, triggered_action, merged_staff_arguments, staff, tick):
        return Note.Action(self)

class Retrigger(PLAYER.Player):
    
    def __init__(self, name, description="Retrigs a given note along a given duration", resources=None):
        super().__init__(name, description, resources) # not self init
        if resources == None:
            self._resources = RESOURCES_MIDI.Midi()

    class Action(PLAYER.Player.Action):
        
        def __init__(self, player):
            super().__init__(player) # not self init
            self._finish_pulse = self._start_pulse # makes sure the Staff isn't used to make it only a clocked action
            self._rate = 0.5 # steps (1/32)
            self._gate = 0.5 # from 0 t0 1
            self._retrig_duration = 4 # steps (1/4)
            self._note = {'key': "C", 'octave': 4, 'velocity': 100, 'channel': 1}
            self._key_pressed = False

        ### ACTION ACTIONS ###

        def actionTrigger(self, triggered_action, merged_staff_arguments, staff, tick):
            super().actionTrigger(triggered_action, merged_staff_arguments, staff, tick)

            self_rate_pulses = self._rate * self._clock_pulses_per_step
            clock_rate_pulses = self_rate_pulses * self._clock_trigger_steps_per_beat_ratio

            if staff == None: # CLOCKED TRIGGER

                if self._key_pressed:
                    if self._player.resource != None:
                        self._player.resource.releaseNote(self._note, self._note['channel']) # WERE THE MIDI NOTE IS TRIGGERED
                    clock_retrig_duration = (clock_rate_pulses - round(clock_rate_pulses * self._gate)) * self._clock_trigger_steps_per_beat_ratio
                elif self._remaining_pulses_duration > 0:
                    if self._player.resource != None:
                        self._player.resource.pressNote(self._note, self._note['channel']) # WERE THE MIDI NOTE IS TRIGGERED
                    clock_retrig_duration = round(clock_rate_pulses * self._gate) * self._clock_trigger_steps_per_beat_ratio
                else:
                    clock_retrig_duration = 0

                self._key_pressed = not self._key_pressed # alternates

                clock_retrig_duration = min(self._remaining_pulses_duration, clock_retrig_duration)

                if self._remaining_pulses_duration > 0:

                    self.addClockedAction(
                        {'triggered_action': triggered_action, 'staff_arguments': merged_staff_arguments,
                            'duration': clock_retrig_duration, 'action': self}, tick
                    )
                else:
                    print(f"retrigger OFF:\t{self._note}\tduration: {self._retrig_duration}")

                self._remaining_pulses_duration -= clock_retrig_duration

            else: # EXTERNAL TRIGGER

                if (not tick['fast_forward']):

                    retrig_duration = self.pickTriggeredLineArgumentValue(merged_staff_arguments, "duration")
                    if (retrig_duration != None):
                        self._retrig_duration = retrig_duration
                    self._remaining_pulses_duration = self._retrig_duration * self._clock_pulses_per_step

                    retrig_rate = self.pickTriggeredLineArgumentValue(merged_staff_arguments, "rate")
                    if (retrig_rate != None):
                        self._rate = max(0, retrig_rate)

                    retrig_gate = self.pickTriggeredLineArgumentValue(merged_staff_arguments, "gate")
                    if (retrig_gate != None):
                        self._gate = min(1, max(0, retrig_gate))

                    retrig_channel = self.pickTriggeredLineArgumentValue(merged_staff_arguments, "channel")
                    if (retrig_channel != None):
                        self._note['channel'] = retrig_channel

                    retrig_velocity = self.pickTriggeredLineArgumentValue(merged_staff_arguments, "velocity")
                    if (retrig_velocity != None):
                        self._note['velocity'] = retrig_velocity

                    retrig_octave = self.pickTriggeredLineArgumentValue(merged_staff_arguments, "octave")
                    if (retrig_octave != None):
                        self._note['octave'] = retrig_octave

                    retrig_key = self.pickTriggeredLineArgumentValue(merged_staff_arguments, "key")
                    if (retrig_key != None):
                        self._note['key'] = retrig_key

                        print(f"retrigger ON:\t{self._note}\tduration: {self._retrig_duration}")
                        if self._player.resource != None:
                            self._player.resource.pressNote(self._note, self._note['channel']) # WERE THE MIDI NOTE IS TRIGGERED
                    
                        self._key_pressed = True
    
                        clock_retrig_duration = round(clock_rate_pulses * self._gate) * self._clock_trigger_steps_per_beat_ratio
                        clock_retrig_duration = min(self._remaining_pulses_duration, clock_retrig_duration)
                        
                        self.addClockedAction(
                            {'triggered_action': triggered_action, 'staff_arguments': merged_staff_arguments,
                             'duration': clock_retrig_duration, 'action': self}, tick
                        )
                        
                        self._remaining_pulses_duration -= clock_retrig_duration

    def actionFactoryMethod(self, triggered_action, merged_staff_arguments, staff, tick):
        return Retrigger.Action(self)

class Arpeggiator(PLAYER.Player):
    
    def __init__(self, name, description="Retrigs a given note along a given duration", resources=None):
        super().__init__(name, description, resources) # not self init
        if resources == None:
            self._resources = RESOURCES_MIDI.Midi()
        self._triggering_staffs = []

    class Action(PLAYER.Player.Action):
        
        def __init__(self, player):
            super().__init__(player) # not self init
            self._finish_pulse = self._start_pulse # makes sure the Staff isn't used to make it only a clocked action
            self._arpeggio_duration = 4 # steps (1/4)
            self._rate = 1.0 # steps (1/16)
            self._gate = 0.5 # from 0 t0 1
            self._note = {'key': "C", 'octave': 4, 'velocity': 100, 'channel': 1}
            self._selected_keys = []
            self._total_selected_keys = 0
            self._active_midi_key = -1

        def add_selected_key(self, midi_key, selected_on_pulse, selected_duration_pulses):
            new_midi_key = {
                    'midi_key': midi_key, 'active': False, 'pressed': False,
                    'selected_on_pulse': selected_on_pulse, 'selected_duration_pulses': selected_duration_pulses,
                    'activated_on_pulse': 0
                }
            if self._total_selected_keys == 0:
                self._selected_keys.append(new_midi_key)
                self._total_selected_keys += 1
            else:
                for selected_key_index in range(self._total_selected_keys):
                    if new_midi_key['midi_key'] == self._selected_keys[selected_key_index]['midi_key']: # avoids duplicates
                        break
                    if selected_key_index == self._total_selected_keys - 1:
                        self._selected_keys.append(new_midi_key)
                        self._total_selected_keys += 1
                    elif new_midi_key['midi_key'] < self._selected_keys[selected_key_index]['midi_key']:
                        self._selected_keys.insert(selected_key_index, new_midi_key)
                        self._total_selected_keys += 1
                        break
            return self

        def deactivate_selected_key(self, midi_key):
            for selected_key in self._selected_keys:
                if selected_key['midi_key'] == midi_key:
                    if selected_key['active']:
                        self.release_selected_key(midi_key)
                        selected_key['active'] = False
                    break
            return self

        def active_selected_key(self):
            
            return self

        def release_selected_key(self, midi_key):
            for selected_key in self._selected_keys:
                if selected_key['midi_key'] == midi_key:
                    if selected_key['pressed']:
                        selected_key['pressed'] = False
                    break
            return self

        def remove_selected_key(self, midi_key):

            for selected_key_index in range(self._total_selected_keys):
                if self._selected_keys[selected_key_index]['midi_key'] == midi_key:
                    del self._selected_keys[selected_key_index]
                    self._total_selected_keys -= 1
                    break

            return self

        def update_selected_keys(self, tick):

            # releases outdated pressed keys
            for selected_key in self._selected_keys:
                if selected_key['pressed']:
                    if selected_key['selected_on_pulse'] + selected_key['selected_duration_pulses'] <= tick['pulse'] or \
                        selected_key['activated_on_pulse'] + self._pressed_duration_pulses <= tick['pulse']:

                        selected_key['pressed'] = False
                        if self._player.resource != None:
                            self._note['key'] = selected_key['midi_key']
                            self._player.resource.releaseNote(self._note, self._note['channel']) # WERE THE MIDI NOTE IS TRIGGERED

            # cleans up outdated keys except the active one
            for selected_key in self._selected_keys[:]:
                if selected_key['selected_on_pulse'] + selected_key['selected_duration_pulses'] <= tick['pulse']:

                    if selected_key['midi_key'] != self._active_midi_key:
                        self._selected_keys.remove(selected_key)
                        self._total_selected_keys -= 1

            # follows the active key to the next one
            if self._active_midi_key == -1:
                if self._total_selected_keys > 0:
                    self._active_midi_key = self._selected_keys[0]['midi_key']
                    self._selected_keys[0]['active'] = True
                    self._selected_keys[0]['activated_on_pulse'] = tick['pulse']

                    if not self._selected_keys[0]['pressed']:
                        self._selected_keys[0]['pressed'] = True
                        if self._player.resource != None:
                            self._note['key'] = self._selected_keys[0]['midi_key']
                            self._player.resource.pressNote(self._note, self._note['channel']) # WERE THE MIDI NOTE IS TRIGGERED

            else:
                for selected_key_index in range(self._total_selected_keys):
                    if self._selected_keys[selected_key_index]['midi_key'] == self._active_midi_key:

                        if self._selected_keys[selected_key_index]['selected_on_pulse'] + self._selected_keys[selected_key_index]['selected_duration_pulses'] <= tick['pulse'] or \
                            self._selected_keys[selected_key_index]['activated_on_pulse'] + self._active_duration_pulses <= tick['pulse']:

                            self._selected_keys[selected_key_index]['active'] = False

                            pick_up_index = (selected_key_index + 1) % self._total_selected_keys # PICK UP FORMULA

                            self._active_midi_key = self._selected_keys[pick_up_index]['midi_key']
                            self._selected_keys[pick_up_index]['active'] = True
                            self._selected_keys[pick_up_index]['activated_on_pulse'] = tick['pulse']

                            if not self._selected_keys[pick_up_index]['pressed']:
                                self._selected_keys[pick_up_index]['pressed'] = True
                                if self._player.resource != None:
                                    self._note['key'] = self._selected_keys[pick_up_index]['midi_key']
                                    self._player.resource.pressNote(self._note, self._note['channel']) # WERE THE MIDI NOTE IS TRIGGERED

                        if self._selected_keys[selected_key_index]['selected_on_pulse'] + self._selected_keys[selected_key_index]['selected_duration_pulses'] <= tick['pulse']:

                            del self._selected_keys[selected_key_index]
                            self._total_selected_keys -= 1

                    break
            
            if self._total_selected_keys == 0:
                self._active_midi_key = -1

            return self

        def next_update_selected_keys_pulse(self):

            next_update_pulse = -1
            if self._total_selected_keys > 0:
                next_update_pulse = self._selected_keys[0]['selected_on_pulse'] + self._selected_keys[0]['selected_duration_pulses']

            for selected_key in self._selected_keys:
                next_update_pulse = min(next_update_pulse, selected_key['selected_on_pulse'] + selected_key['selected_duration_pulses'])
                if selected_key['active']:
                    next_update_pulse = min(next_update_pulse, selected_key['activated_on_pulse'] + self._active_duration_pulses)
                if selected_key['pressed']:
                    next_update_pulse = min(next_update_pulse, selected_key['activated_on_pulse'] + self._pressed_duration_pulses)

            return next_update_pulse

        ### ACTION ACTIONS ###

        def actionTrigger(self, triggered_action, merged_staff_arguments, staff, tick):
            super().actionTrigger(triggered_action, merged_staff_arguments, staff, tick)

            if staff == None: # CLOCKED TRIGGER

                self.update_selected_keys(tick)
                next_update_tick_duration = self.next_update_selected_keys_pulse() - tick['pulse']
                self.addClockedAction(
                    {'triggered_action': triggered_action, 'staff_arguments': merged_staff_arguments,
                        'duration': next_update_tick_duration, 'action': self}, tick
                )
                
            else: # EXTERNAL TRIGGER

                if (not tick['fast_forward']):

                    arpeggio_duration = self.pickTriggeredLineArgumentValue(merged_staff_arguments, "duration")
                    if (arpeggio_duration != None):
                        self._arpeggio_duration = arpeggio_duration

                    arpeggio_rate = self.pickTriggeredLineArgumentValue(merged_staff_arguments, "rate")
                    if (arpeggio_rate != None):
                        self._rate = max(0, arpeggio_rate)

                    arpeggio_gate = self.pickTriggeredLineArgumentValue(merged_staff_arguments, "gate")
                    if (arpeggio_gate != None):
                        self._gate = max(0, arpeggio_gate)

                    arpeggio_channel = self.pickTriggeredLineArgumentValue(merged_staff_arguments, "channel")
                    if (arpeggio_channel != None):
                        self._note['channel'] = arpeggio_channel

                    arpeggio_velocity = self.pickTriggeredLineArgumentValue(merged_staff_arguments, "velocity")
                    if (arpeggio_velocity != None):
                        self._note['velocity'] = arpeggio_velocity

                    arpeggio_octave = self.pickTriggeredLineArgumentValue(merged_staff_arguments, "octave")
                    if (arpeggio_octave != None):
                        self._note['octave'] = arpeggio_octave

                    self._active_duration_pulses = round(self._rate * self._clock_pulses_per_step * self._clock_trigger_steps_per_beat_ratio)
                    self._pressed_duration_pulses = round(self._gate * self._active_duration_pulses)

                    arpeggio_key = self.pickTriggeredLineArgumentValue(merged_staff_arguments, "key")
                    if (arpeggio_key != None):
                        self._note['key'] = arpeggio_key

                        midi_key = RESOURCES_MIDI.getMidiNote(self._note)

                        note_duration_pulses = round(self._arpeggio_duration * self._clock_pulses_per_step * self._clock_trigger_steps_per_beat_ratio)
                        self.add_selected_key(midi_key, tick['pulse'], note_duration_pulses)
                        self.update_selected_keys(tick)

                        next_update_tick_duration = self.next_update_selected_keys_pulse() - tick['pulse']
                        self.addClockedAction(
                            {'triggered_action': triggered_action, 'staff_arguments': merged_staff_arguments,
                             'duration': next_update_tick_duration, 'action': self}, tick
                        )
                        
    def isPlaying(self):
        for triggering_staff in self._triggering_staffs[:]:
            if not triggering_staff['action'].isPlaying():
                self._triggering_staffs.remove(triggering_staff)
        return super().isPlaying()

    def actionFactoryMethod(self, triggered_action, merged_staff_arguments, staff, tick):
        for triggering_staff in self._triggering_staffs:
            if staff == triggering_staff['staff']:
                return triggering_staff['action']
        new_triggering_staff = {
            'staff': staff,
            'action': Arpeggiator.Action(self)
        }
        self._triggering_staffs.append(new_triggering_staff)
        return new_triggering_staff['action']
    
