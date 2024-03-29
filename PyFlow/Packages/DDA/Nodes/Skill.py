from PyFlow.Core import NodeBase
from PyFlow.Core.NodeBase import NodePinsSuggestionsHelper
from PyFlow.Core.Common import *


class Skill(NodeBase):
    def __init__(self, name):
        super(Skill, self).__init__(name)
        self.StreamName = self.createInputPin('StreamName', 'StringPin')
        self.Name = self.createInputPin('Name', 'StringPin')

        self.Max = self.createInputPin('Max', 'IntPin')
        self.Min = self.createInputPin('Min', 'IntPin')

        self.Focus = self.createInputPin('Target', 'IntPin')

        self.Data = self.createInputPin('Data', 'AnyPin', structure=StructureType.Multi)
        self.Data.enableOptions(
            PinOptions.AllowMultipleConnections | PinOptions.AllowAny | PinOptions.DictElementSupported)
        self.Data.disableOptions(PinOptions.SupportsOnlyArrays)

        self.Performance = self.createOutputPin('Performance', 'FloatPin')

    @staticmethod
    def pinTypeHints():
        helper = NodePinsSuggestionsHelper()
        helper.addInputDataType('BoolPin')
        helper.addOutputDataType('BoolPin')
        helper.addInputStruct(StructureType.Single)
        helper.addOutputStruct(StructureType.Single)
        return helper

    @staticmethod
    def category():
        return 'Generated from wizard'

    @staticmethod
    def keywords():
        return []

    @staticmethod
    def description():
        return "Description in rst format."

    def compute(self, *args, **kwargs):
        if (self.Data.getData() is not None) and (self.Name.getData() is not None) and (
                self.Max.getData() is not None) and (self.Min.getData() is not None) and (
                self.StreamName.getData() is not None):

            print("Skill issue mate ")
            data = self.Data.getData()
            stream = self.StreamName.getData()
            name = self.Data.getData()
            max = self.Max.getData()
            min = self.Min.getData()

            rawSkill = 0

            try:
                if stream in data:
                    print("Flag1")
                    if name in data[stream]:
                        print("Flag2")
                        if isinstance(data[stream][name], list) and len(data[stream][name]) > 0:
                            nested_list = data[stream][name]
                            rawSkill = nested_list[-1]
                            print("Last element exists:", rawSkill)
                        else:
                            print("No elements in 'name'")
                    else:
                        print("Key 'name' does not exist in the data[stream] dictionary")
                else:
                    print("Key 'stream' does not exist in the data dictionary")
            except TypeError as te:
                print("TypeError:", te)
            except Exception as e:
                print("An error occurred:", e)

            if rawSkill < min:
                performance = 0

            elif rawSkill > max:
                performance = 1

            else:
                performance = (rawSkill - min) / (max - min)

            self.Performance.setData(performance)
