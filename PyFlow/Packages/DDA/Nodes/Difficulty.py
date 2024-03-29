from PyFlow.Core import NodeBase
from PyFlow.Core.NodeBase import NodePinsSuggestionsHelper
from PyFlow.Core.Common import *


class Difficulty(NodeBase):
    def __init__(self, name):
        super(Difficulty, self).__init__(name)
        self.Performance = self.createInputPin('Performance', 'FloatPin')
        self.Name = self.createInputPin('Name', 'StringPin')

        self.Max = self.createInputPin('Max', 'IntPin')
        self.Min = self.createInputPin('Min', 'IntPin')

        # _____Output_____#
        self.NameOut = self.createOutputPin('Name', 'StringPin')

        self.Send = self.createOutputPin('Data','FloatPin')
        self.Send.enableOptions(PinOptions.AllowAny)

    @staticmethod
    def pinTypeHints():
        helper = NodePinsSuggestionsHelper
        helper.addInputDataType('BoolPin')
        helper.addOutputDataType('BoolPin')
        helper.addInputStruct(StructureType.Single)
        helper.addInputStruct(StructureType.Multi)
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
        if (self.Performance.getData() is not None) and (self.Name.getData() is not None) and (
                self.Max.getData() is not None) and (self.Min.getData() is not None):

            name = self.Name.getData()
            max = self.Max.getData()
            min = self.Min.getData()
            performance = self.Performance.getData()
            difficulty = performance * (max - min) + min

            self.Send.setData(difficulty)
            self.NameOut.setData(name)

