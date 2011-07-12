"""
A class that contains actions to take when the time is right.
For instance there is the default Action class, that presents a minimal
class with no action, and a PlaySound class, which just plays a wave file.
"""

import os
import wave
import ossaudiodev

class Action:
    """
    A simple base class of an action that does nothing.
    
    Actions just need an __init__() method, and a run() method to be
    defined.  The init should take any options the class needs to take,
    and the run method should take no options.
    """
    def __init__(self):
        "Initialize the action with any nessecary arguments defined."
        pass
    def run(self):
        "Run the action."
        pass

class PlaySound(Action):
    """
    Play a wave file.
    """
    def __init__(self, filename=None):
        "If filename is None, then a bell sound will be played."
        self.filename = filename

    def run(self):
        "Play the sound."
        self.__playsound()

    def __playsound(self):
        if self.filename:
            sound = wave.open(filename, 'rb')
        else:
            # get the location of our sounds path
            __pkgpath = os.path.dirname(__file__)
            soundspath = os.path.join(__pkgpath, "sounds")
            sound = wave.open(os.path.join(soundspath, 'bell17.wav'), 'rb')

        nchannels , sampwidth, framerate, nframes, comptype, compname = sound.getparams()
        #print("params for %s:" % sound)
        #print("\tnchannels (number of audio channels) = %s, sampwidth = %s, " % 
        #        (nchannels, sampwidth))
        #print("\tframerate (sampling frequency) = %s, nframes (# of audio frames) = %s, " % 
        #        (framerate, nframes))
        #print("\tcomptype (compression type) = %s, compname (compression name) = %s" % 
        #        (comptype, compname))

        dsp = ossaudiodev.open('/dev/dsp','w')

        try:
            from ossaudiodev import AFMT_S16_NE
        except ImportError:
            # assume little endian
            AFMT_S16_NE = ossaudiodev.AFMT_S16_LE

        dsp.setparameters(AFMT_S16_NE, nchannels, framerate)
        data = sound.readframes(nframes)
        sound.close()
        dsp.write(data)
        dsp.close()
