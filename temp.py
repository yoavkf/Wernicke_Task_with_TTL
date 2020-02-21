class IO64class:
    def __init__(self,config,):

        # TODO fix this::::
        frameRate = int(config["DEFAULT"]["frameRate"])
        self.pinMap, self.maxValue = self.getAnalogPinMap(config["DEFAULT"]["analogPinMap"])
        self.address = int(config["DEFAULT"]["analogOutAddress"], base=16)
        self.setAnalogOutputLow(self.address)

        self.nPulseFrames = int(config["DEFAULT"].getfloat("analogOutDuration") * frameRate)
        self.nPeriodFrames = int(config["DEFAULT"].getfloat("analogOutPeriod") * frameRate)
        videoDuration = config["DEFAULT"].getfloat("videoDuration")

        self.nVideoFrames = int(videoDuration * frameRate)

        # initialize our random frame offset
        self.maxPeriodOffset = config["DEFAULT"].getfloat("analogOutPeriodRange")
        self.nOffsetFrames = self.nPeriodFrames + self.getRandomFrameOffset(self.maxPeriodOffset, frameRate)
        self.update=0
        self.TTLoutput=0
        self.updatetime = datetime.now()
    def encodeNumber(self, n, ainpMap):
        bits = "{:08b}".format(n)
        for idx, bidx in enumerate(ainpMap):
            if idx == 0: encoded = 0
            if bidx is not None: encoded = encoded + (2 ** idx) * int(bits[7 - bidx])

        return encoded
    # output encoded value to LPT1 (address 0xE010)
    def setAnalogOutputValue(self, value, pinMap, address):
        n = self.encodeNumber(value, pinMap)
        windll.inpoutx64.Out32(address, n)
        self.updatetime = datetime.now()
        self.TTLoutput=value
    def setAnalogOutputHigh(self, address):
        windll.inpoutx64.Out32(address, 255)
        self.updatetime=datetime.now()
        self.TTLoutput=255
    def setAnalogOutputLow(self, address):
        windll.inpoutx64.Out32(address, 0)
        self.TTLoutput=0
        self.updatetime = datetime.now()
    def getRandomFrameOffset(self,maxOffset, frameRate):
        return int(random.uniform(-maxOffset, maxOffset) * frameRate)

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
            raise ValueError("Invalid analog pin configuration: {}.".format(spec))

        return pinMap, maxValue

    def sendAnalogoutCode(self, frame_num, lastTriggerFrame, frameRate):
        if frame_num == 0:
            self.setAnalogOutputValue(self.maxValue, self.pinMap, self.address)
        elif frame_num in (2 * self.nPulseFrames, 4 * self.nPulseFrames):
            self.setAnalogOutputValue(0, self.pinMap, self.address)
        elif frame_num == 3 * self.nPulseFrames:
            self.setAnalogOutputValue(nVideos % (self.maxValue + 1), self.pinMap, self.address)
        elif frame_num > 4 * self.nPulseFrames and (frame_num - lastTriggerFrame) == self.nOffsetFrames:
            self.setAnalogOutputValue(self.analogValue, self.pinMap, self.address)
            self.analogValue = self.analogValue + 1 if self.analogValue < self.maxValue-1 else 1
            lastTriggerFrame = frame_num
            print(self.analogValue)
        elif frame_num > 4 * self.nPulseFrames and (frame_num - lastTriggerFrame) == self.nPulseFrames:
            self.setAnalogOutputLow(self.address)

            # set a new random trigger shift
            self.nOffsetFrames = self.nPeriodFrames + self.getRandomFrameOffset(self.maxPeriodOffset, frameRate)
        return lastTriggerFrame