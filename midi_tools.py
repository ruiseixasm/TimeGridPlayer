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

import rtmidi
import time

class Instrument():
    
    def __init__(self):
        self.output_port = rtmidi.MidiOut()
        self.instrument_port = None
        self.port_index = None
        self.pressed_keys = [False] * 128

    def list(self):
        return self.output_port.get_ports()

    def connect(self, order = None, name = None):
        available_instrument_ports_list = self.list()
        total_available_instruments = self.output_port.get_port_count()
        if (total_available_instruments > 0):
            if order == name == None:
                self.instrument_port = self.output_port.open_port(0)
            elif order != None and total_available_instruments > order:
                self.instrument_port = self.output_port.open_port(order)
            elif name != None:
                for index in range(total_available_instruments):
                    if available_instrument_ports_list[index].find(name) != -1:
                        self.instrument_port = self.output_port.open_port(index)
                        self.port_index = index
                        break

        return self
    
    def disconnect(self):
        if self.instrument_port != None:
            if self.instrument_port.is_port_open():
                self.instrument_port.close_port()
                return True
        return False
    
    def isConnected(self):
        if self.instrument_port != None:
            if self.instrument_port.is_port_open():
                return True
        return False
    
    def getPortName(self):
        if self.isConnected():
            return self.output_port.get_port_name(self.port_index)
        return "None"

    def print(self):
        if self.isConnected():
            print (self.output_port.get_port_name(self.port_index))
        else:
            print ("None")
        return self

    def test(self):
        self.pressNote()
        time.sleep(1)
        self.releaseNote()
        time.sleep(1)
        return self
    
    def sendMessage(self, message=[0x80, 60, 100]):
        if self.isConnected():
            self.instrument_port.send_message(message)
        return self

    def panic(self):
        sleep_time = 0.002 # 2ms
        for channel in range(1, 16 + 1):
            self.controlChange(123, 0, channel)     #1
            time.sleep(sleep_time)
            self.pitchBend(0, channel)              #2
            time.sleep(sleep_time)
            self.controlChange(64, 0, channel)      #3
            time.sleep(sleep_time)
            self.controlChange(1, 0, channel)       #4
            time.sleep(sleep_time)
            self.controlChange(121, 0, channel)     #5
            time.sleep(sleep_time)

            self.releaseAllNotes(channel)            #6

            self.controlChange(7, 100, channel)     #7
            time.sleep(sleep_time)
            self.controlChange(11, 127, channel)    #8
            time.sleep(sleep_time)
                
        return self
    
    def pressNote(self, note={'key': "C", 'octave': 4, 'velocity': 100}, channel=1):
        command = 0x90 | max(0, channel - 1)
        parameter_1 = getMidiNote(note)
        parameter_2 = note['velocity']
        message = [command, parameter_1, parameter_2]
        if not self.pressed_keys[parameter_1]:
            self.pressed_keys[parameter_1] = True
            return self.sendMessage(message)
        return self

    def releaseNote(self, note={'key': "C", 'octave': 4}, channel=1):
        command = 0x80 | max(0, channel - 1)
        parameter_1 = getMidiNote(note)
        parameter_2 = 64
        message = [command, parameter_1, parameter_2]
        self.pressed_keys[parameter_1] = False
        return self.sendMessage(message)
        
    def releaseAllNotes(self, channel=1):
        sleep_time = 0.002 # 2ms
        command = 0x80 | max(0, channel - 1)
        parameter_2 = 0
        for parameter_1 in range(128):
            message = [command, parameter_1, parameter_2]
            self.sendMessage(message)
            self.pressed_keys[parameter_1] = False
            time.sleep(sleep_time)
        return self
        
    def aftertouchNote(self, note={'key': "C", 'octave': 4}, pressure=100, channel=1):
        command = 0xA0 | max(0, channel - 1)
        parameter_1 = getMidiNote(note)
        parameter_2 = pressure
        message = [command, parameter_1, parameter_2]
        return self.sendMessage(message)
    
    def controlChange(self, controller=10, value=64, channel=1): # pan 10 default 64
        command = 0xB0 | max(0, channel - 1)
        parameter_1 = controller
        parameter_2 = value
        message = [command, parameter_1, parameter_2]
        return self.sendMessage(message)
    
    def programChange(self, parameter_1=0, parameter_2=0, channel=1):
        command = 0xC0 | max(0, channel - 1)
        message = [command, parameter_1, parameter_2]
        return self.sendMessage(message)

    def aftertouchChannel(self, pressure=100, channel=1):
        command = 0xD0 | max(0, channel - 1)
        parameter_1 = pressure
        message = [command, parameter_1, 0]
        return self.sendMessage(message)

    def pitchBend(self, bend=0, channel=1): # middle no pitch change is 8192 (-8192 to 8191)
        """The bend range is from -8192 to 8191"""
        command = 0xE0 | max(0, channel - 1)
        amount = max(0, min(16383, bend + 8192)) # 2^14 | 2^14 / 2
        parameter_1 = amount & 0x3FF # LSB
        parameter_2 = amount >> 7 # MSB | 8192 >> 7 = 64
        message = [command, parameter_1, parameter_2]
        return self.sendMessage(message)
    
def getMidiNote(note={'key': "C", 'octave': 4}): # middle C by default
    """Octaves range from -1 to 9"""
    key_str = note['key'].strip().upper()
    midi_key = 0
    # ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    str_keys = ['C', '#', 'D', '#', 'E', 'F', '#', 'G', '#', 'A', '#', 'B']

    for index in range(12):
        if key_str[0] == str_keys[index]:
            midi_key = index
            break

    midi_key += (note['octave'] + 1) * 12 # first octave is -1

    if (len(key_str) > 1):
        if key_str[1] == '#':
            midi_key += 1
        elif key_str[1] == 'B': # upper b meaning flat
            midi_key -= 1

    return min(127, max(0, midi_key))

def getNote(midi_note=60):
    str_keys = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

    note_octave = int(midi_note / 12) - 1
    note_key = str_keys[midi_note % 12]

    return {'key': note_key, 'octave': note_octave}

def transposeNote(note={'key': "C", 'octave': 4}, octaves=0, notes=0):
    midi_note = getMidiNote(note)
    midi_note += octaves * 12 + notes
    midi_note = min(127, max(0, midi_note))
    return getNote(midi_note)


# MIDI beat clock defines the following real-time messages:

# clock (decimal 248, hex 0xF8)
# start (decimal 250, hex 0xFA)
# continue (decimal 251, hex 0xFB)
# stop (decimal 252, hex 0xFC)
