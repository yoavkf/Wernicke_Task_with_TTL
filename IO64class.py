from ctypes import windll
import configparser
from datetime import datetime
import time


class IO64:
    def __init__(self):
        # TODO fix this::::
        self.params = self.read_configuration()

        self.pinMap, self.maxValue = self.getAnalogPinMap(
            self.params["analogPinMap"])
        # channels = [item for item in self.pinMap if item is not None]
        # self.word_flag_channel = channels[0]
        # self.bit_flag_channel = channels[1]
        # self.data_flag_channel = channels[2:]

        self.address = int(self.params["analogOutAddress"], base=16)
        # self.setAnalogOutputLow(self.address)
        self.setAnalogOutputLow()
        self.setAnalogOutputHigh()
        self.setAnalogOutputLow()
        self.setAnalogOutputHigh()
        self.setAnalogOutputLow()
        
        self.updatetime = datetime.now()

    def read_configuration(self):
        import configparser
        config = configparser.ConfigParser()
        config.read("IO64_config.ini")
        params = {"analogPinMap":          config["DEFAULT"]["analogPinMap"],
                  "analogOutTimeResolution":  float(config["DEFAULT"]["analogOutTimeResolution"]),
                  "bits_per_word":          int(config["DEFAULT"]["bits_per_word"]),
                #   "analogOutPeriod":      (config["DEFAULT"]["analogOutPeriod"]),
                #   "analogOutPeriodRange": (config["DEFAULT"]["analogOutPeriodRange"]),
                #   "analogOutDuration":    config["DEFAULT"]["analogOutDuration"],
                  "analogOutAddress":     config["DEFAULT"]["analogOutAddress"]}
        return params

    def sendDigitalWord(self, value):
        # value = 
        self.setAnalogOutputLow()
        bits = bin(value).replace("0b","")
        add_zeros = self.params["bits_per_word"]-len(bits)
        bits = str(0)*add_zeros + bits
        word_flag = 1
        
        for bit in bits:
            bit_int = int(bit)
            bit_flag = 1
            word = [word_flag, bit_flag, bit_int, bit_int, word_flag, bit_flag, bit_int, bit_int]    
            n = self.encodeWord(word)
            self.setAnalogOutputValue(n)
            # print(word[0:3])

            bit_flag = 0
            word = [word_flag, bit_flag, int(0), int(0), word_flag, bit_flag, int(0), int(0)]    
            n = self.encodeWord(word)
            self.setAnalogOutputValue(n)
        print(bits)
        self.setAnalogOutputLow()

    def encodeWord(self, word):
        for idx, bidx in enumerate(self.pinMap):
            if idx == 0:
                encoded = 0
            if bidx is not None:
                encoded = encoded + (2 ** idx) * int(word[bidx])
        return encoded

    #     return encoded
# %%%%

    # def encodeNumber(self, n):
    #     active_channels=len([x for x in pinMap if x is not None])
    #     bits = "{:08b}".format(n)
    #     bits=bits[-active_channels:]
    #     for idx, bidx in enumerate(self.pinMap):
    #         if idx == 0:
    #             encoded = 0
    #         if bidx is not None:
    #             encoded = encoded + (2 ** idx) * int(bits[7 - bidx])

    #     return encoded
    # output encoded value to LPT1 (address 0xE010)

    def setAnalogOutputValue(self, value):
        windll.inpoutx64.Out32(self.address, value)
        time.sleep(self.params["analogOutTimeResolution"])
        # self.updatetime = datetime.now()
        # self.TTLoutput = value

    def setAnalogOutputHigh(self):
        windll.inpoutx64.Out32(self.address, 255)
        time.sleep(self.params["analogOutTimeResolution"])
        # self.updatetime = datetime.now()
        # self.TTLoutput = 255

    def setAnalogOutputLow(self):
        windll.inpoutx64.Out32(self.address, 0)
        time.sleep(self.params["analogOutTimeResolution"])

        # self.TTLoutput = 0
        # self.updatetime = datetime.now()

    # def getRandomFrameOffset(self, maxOffset, frameRate):
    #     return int(random.uniform(-maxOffset, maxOffset) * frameRate)

    def pinMapFromSpec(self, spec):
        pinMap = list(spec)
        for idx, e in enumerate(pinMap):
            pinMap[idx] = None if e == '-' else int(e)
        return pinMap

    def getAnalogPinMap(self, spec):
        pinMap = self.pinMapFromSpec(spec)
        bitSlots = [int(k) for k in pinMap if k is not None]
        maxPower = max(bitSlots)
        maxValue = 2 ** (maxPower+1) - 1
        if len(bitSlots) != maxPower+1 or len(pinMap) != 8:
            raise ValueError(
                "Invalid analog pin configuration: {}.".format(spec))

        return pinMap, maxValue

    # def sendAnalogoutCode(self, frame_num, lastTriggerFrame, frameRate):
    #     if frame_num == 0:
    #         self.setAnalogOutputValue(self.maxValue, self.pinMap, self.address)
    #     elif frame_num in (2 * self.nPulseFrames, 4 * self.nPulseFrames):
    #         self.setAnalogOutputValue(0, self.pinMap, self.address)
    #     elif frame_num == 3 * self.nPulseFrames:
    #         self.setAnalogOutputValue(nVideos % (
    #             self.maxValue + 1), self.pinMap, self.address)
    #     elif frame_num > 4 * self.nPulseFrames and (frame_num - lastTriggerFrame) == self.nOffsetFrames:
    #         self.setAnalogOutputValue(
    #             self.analogValue, self.pinMap, self.address)
    #         self.analogValue = self.analogValue + \
    #             1 if self.analogValue < self.maxValue-1 else 1
    #         lastTriggerFrame = frame_num
    #         print(self.analogValue)
    #     elif frame_num > 4 * self.nPulseFrames and (frame_num - lastTriggerFrame) == self.nPulseFrames:
    #         self.setAnalogOutputLow(self.address)

    #         # set a new random trigger shift
    #         self.nOffsetFrames = self.nPeriodFrames + \
    #             self.getRandomFrameOffset(self.maxPeriodOffset, frameRate)
    #     return lastTriggerFrame
