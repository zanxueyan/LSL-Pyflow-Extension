from datetime import datetime

from PyFlow.Core import NodeBase
from PyFlow.Core.NodeBase import NodePinsSuggestionsHelper
from PyFlow.Core.Common import *
from pylsl import StreamInlet, resolve_streams, pylsl
from PyFlow.Packages.PyFlowBase.Nodes import FLOW_CONTROL_COLOR

import copy
import main2
import sys
import multiprocessing


# LSL_Writer
class SingleStreamReceiver(NodeBase):
    def __init__(self, name):
        super(SingleStreamReceiver, self).__init__(name)
        # Input pins
        self.beginPin = self.createInputPin("Begin", 'ExecPin', None, self.start)
        self.stopPin = self.createInputPin("Stop", 'ExecPin', None, self.stop)

        # Output pins
        self.out = self.createOutputPin("OUT", 'ExecPin')
        self.Send = self.createOutputPin('Data', 'AnyPin', structure=StructureType.Multi)
        self.Send.enableOptions(PinOptions.AllowAny)
        self.Info = self.createOutputPin('Info', 'AnyPin', structure=StructureType.Single)
        self.Info.enableOptions(PinOptions.AllowAny)

        self.inlets = []
        self.bWorking = False
        self.headerColor = FLOW_CONTROL_COLOR

        self.DataBase = dict()
        self.StructDataBase = dict()

        self.Graph_queue = multiprocessing.Queue()
        self.online = False
        self.Prosess = multiprocessing.Process(target=main2.Run, args=(self.Graph_queue,))

        self.start = time.time()
        self.counter = 0

    def Tick(self, delta):
        super(SingleStreamReceiver, self).Tick(delta)
        timer1 = time.time()
        if self.bWorking:
            if time.time() - self.start >= 1:
                self.start = time.time()
                # print("Number of values in one second->" + str(self.counter))

                # print("Struct" + str(self.DataBase))

                # self.Graph_queue.put(self.DataBase)
                # self.DataBase = None
                # self.DataBase = copy.deepcopy(self.StructDataBase)

                self.counter = 0
            if len(self.inlets) != 0:
                for inlet in self.inlets:
                    # Pull a chunk of samples from the inlet
                    samples, timestamps = inlet.pull_chunk(max_samples=int(inlet.info().nominal_srate()))

                    if samples:
                        # Process the received samples
                        for sample, timestamp in zip(samples, timestamps):
                            # Do something with the sample data and timestamp
                            # self.Send.setData(sample)
                            # print(+"Received sample:", sample, "at timestamp:", timestamp)
                            self.addDataToDict(inlet.info().name(), sample)

                self.out.call()
                self.Send.setData(self.DataBase)

            else:
                self.bWorking = False

        if timer1 - time.time() != 0:
            self.counter += 1
            # print("it took |"+str(timer1-time.time())+"| to get the values")

    @staticmethod
    def keywords():
        return []

    @staticmethod
    def description():
        return "Description in rst format."

    def stop(self, *args, **kwargs):
        self.bWorking = False
        self.Prosess.terminate()
        self.Prosess.join()
        self.Prosess = multiprocessing.Process(target=main2.Run, args=(self.Graph_queue,))

    def start(self, *args, **kwargs):
        if self.bWorking:
            self.Prosess.terminate()
            self.Prosess.join()
            self.Prosess = multiprocessing.Process(target=main2.Run, args=(self.Graph_queue,))

        self.bWorking = True
        streams = resolve_streams()
        stream_information = []
        stream_information2 = dict()

        for stream in streams:

            inlet = StreamInlet(stream)

            stream_channels = dict()
            channels = inlet.info().desc().child("channels").child("channel")

            channels_dicts = dict()
            for i in range(inlet.info().channel_count()):
                # Get the channel number (e.g. 1)
                channel = i + 1

                # Get the channel type (e.g. ECG)
                sensor = channels.child_value("label")

                # Get the channel unit (e.g. mV)
                unit = channels.child_value("unit")

                # Store the information in the stream_channels dictionary
                stream_channels.update({channel: [sensor, unit]})
                channels = channels.next_sibling()
                channels_dicts[sensor] = []

            self.DataBase[inlet.info().name()] = channels_dicts

            self.StructDataBase = copy.deepcopy(self.DataBase)

            inlet_info = {
                "Name": inlet.info().name(),
                "Type": inlet.info().type(),
                "Channels": int(inlet.info().channel_count()),
                "Sampling Rate": int(inlet.info().nominal_srate()),
                "Channels Info": stream_channels,
            }
            stream_information.append(inlet_info)
            stream_information2 = {inlet.info().name(): inlet_info}


            self.inlets.append(inlet)

        self.Info.setData(stream_information)
        self.Prosess.start()
        print("->{}".format(stream_information))
        self.Graph_queue.put(stream_information)
        while self.Graph_queue.get() != 1:
            self.Graph_queue.put(stream_information)
        self.online = True

    def addDataToDict(self, key, data):
        for i, row in enumerate(self.DataBase[key]):
            self.DataBase[key][row].append(data[i])
            # if i == 0:
            # print("Lenght"+str(len(self.DataBase[key][row])))

            if (len(self.DataBase[key][row]) > (self.inlets[-1].info().nominal_srate())):
                # print("Lenght" + str(len(self.DataBase[key][row])))
                self.DataBase[key][row].pop(0)
                self.Graph_queue.put(self.DataBase)
                self.DataBase = None
                self.DataBase = copy.deepcopy(self.StructDataBase)

    @staticmethod
    def category():
        return 'Receivers'
