from datetime import datetime

from PyFlow.Core import NodeBase
from PyFlow.Core.NodeBase import NodePinsSuggestionsHelper
from PyFlow.Core.Common import *
from pylsl import StreamInlet, resolve_streams, pylsl
from PyFlow.Packages.PyFlowBase.Nodes import FLOW_CONTROL_COLOR
#LSL_Writer
class LSL_Reader3(NodeBase):
        def __init__(self, name):
            super(LSL_Reader3, self).__init__(name)
            # Input  Pins
            self.beginPin = self.createInputPin("Begin", 'ExecPin', None, self.start)
            self.stopPin = self.createInputPin("Stop", 'ExecPin', None, self.stop)
            self.StreamName = self.createInputPin("Name", 'StringPin')
            self.Buffer = self.createInputPin("Buffer", 'IntPin')

            # Output  Pins
            self.out = self.createOutputPin("OUT", 'ExecPin')
            self.Send = self.createOutputPin('Data', 'AnyPin', structure=StructureType.Multi)
            self.Send.enableOptions(PinOptions.AllowAny)
            self.Info = self.createOutputPin('Info', 'AnyPin', structure=StructureType.Single)
            self.Info.enableOptions(PinOptions.AllowAny)


            self.inlet = None
            self.bWorking = False
            self.headerColor = FLOW_CONTROL_COLOR

            self.DataBase = dict()
            self.start = time.time()
            self.counter = 0

        def Tick(self, delta):
            super(LSL_Reader3, self).Tick(delta)
            self.data = []
            timer1 = time.time()
            if self.bWorking:
                if int(time.time()) - self.start >= 1:
                    self.start = time.time()
                    print(str(self.inlet.info().nominal_srate())+"Number of values in one second->" + str(self.counter))
                    self.counter = 0

                sample, timestamp = self.inlet.pull_sample()
                new_data = {self.inlet.info().name(): sample}
                self.addDataToDict(self.inlet.info().name(), sample)

                self.out.call()
                self.Send.setData(self.DataBase)

            if timer1-time.time() != 0:
                self.counter += 1
                #print("it took |"+str(timer1-time.time())+"| to get the values")


        @staticmethod
        def keywords():
            return []

        @staticmethod
        def description():
            return "Description in rst format."

        def stop(self, *args, **kwargs):
            self.bWorking = False

        def start(self, *args, **kwargs):

            self.bWorking = True
            streams = resolve_streams()
            stream_information = dict()
            for stream in streams:
                inlet = StreamInlet(stream)


                if inlet.info().name() != self.StreamName.getData():
                    continue
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

                inlet_info = {
                    "Name": inlet.info().name(),
                    "Type": inlet.info().type(),
                    "Channels": int(inlet.info().channel_count()),
                    "Sampling Rate": int(inlet.info().nominal_srate()),
                    "Channels Info": stream_channels,
                }
                stream_information[inlet.info().name()] = inlet_info
                #print(inlet_info)
                self.Info.setData(stream_information)
                #print(str(stream_information))
                self.inlet=inlet


        def addDataToDict(self, key, data):
            for i, row in enumerate(self.DataBase[key]):
                self.DataBase[key][row].append(data[i])

        @staticmethod
        def category():
            return 'FlowControl'