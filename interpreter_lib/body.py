from interpreter_lib import instruction_processing as IP
import interpreter_lib.Arg_check as argCheck
import sys
import xml.etree.ElementTree as ET
from interpreter_lib.Arg_check import ErrType
import re


class Interpret:
    def __init__(self):
        self.instruction_list = []
        self.stack = []
        self.frames = Frames()
        self.arg = argCheck.Arguments(sys.argv[1:])
        self.labelJump = IP.LabelJump()
        self.file = None
        self.main()

    def main(self):

        self.file = self.arg.getSourceFileName()
        xml = xmlCheck(self.file, self.stack, self.frames, self.instruction_list, self.labelJump)
        xml.start()

        inst_len = len(self.instruction_list)
        if not inst_len:
            exit(ErrType.exitWithError(ErrType.errSourceFile))

        self.set_labels()

        while True:

            if self.instruction_list[self.labelJump.order_num] is None:
                break

            self.instruction_list[self.labelJump.order_num].execute()

            self.labelJump.order_num += 1
            # TODO odstranit po patchi
            print(self.labelJump.order_num)
            #if self.labelJump.order_num == 8:
                #exit(0)



    def set_labels(self):

        inst_skip = IP.InstPass([], self.stack, self.frames, self.labelJump)

        for instruction in self.instruction_list:
            if isinstance(instruction, IP.LABEL):
                instruction.execute()
                self.instruction_list[self.labelJump.order_num] = inst_skip

            self.labelJump.order_num += 1

        self.labelJump.order_num = 0


class xmlCheck:

    def __init__(self, file, stack, frames, instruction_list, labelJump):
        self.labelJump = labelJump
        self.instruction_list = instruction_list
        self.xml_file = file
        self.tree = None
        self.root = None
        self.stack = stack
        self.frames = frames
        # TODO
        self.instOrdCounter = 1 # problem s poradim instrukci

    def start(self):
        try:
            tree = ET.parse(self.xml_file)
            self.root = tree.getroot()

        except ET.ParseError:
            exit(ErrType.exitWithError(ErrType.errXmlNotWellFormatted))

        if self.root.tag != 'program':
            exit(ErrType.errXmlNotWellFormatted)

        for child in self.root:
            attrib = list(child.attrib.items())
            #TODO
            #if order[0][1] != self.instOrdCounter:
                #exit(ErrType.exitWithError(ErrType.errXmlNotWellFormatted))

            if child.tag != 'instruction':
                exit(ErrType.exitWithError(ErrType.errXmlNotWellFormatted))

            child_att = list(child.attrib.keys())
            if not ('order' in child_att) or not ('opcode' in child_att) or len(child_att) != 2:
                exit(ErrType.exitWithError(ErrType.errXmlNotWellFormatted))

            else:
                self.instruction_list.append(IP.Factory.resolve(attrib[1][1], self.stack, self.frames, self.labelJump))

            tmp = 1
            for sub_elem in child:
                sub_elem_att = sub_elem.attrib

                if 'type' not in sub_elem_att or len(sub_elem_att) != 1:
                    exit(ErrType.exitWithError(ErrType.errXmlNotWellFormatted))

                if not (re.match(r"arg[123]", sub_elem.tag)):
                    exit(ErrType.exitWithError(ErrType.errXmlNotWellFormatted))

                else:
                    if sub_elem_att['type'] == "int":
                        value = int(sub_elem.text)
                    elif sub_elem_att['type'] == "bool":
                        value = bool(sub_elem.text)
                    elif sub_elem_att['type'] == "string":
                        value = str(sub_elem.text)
                    else:
                        value = sub_elem.text

                    if tmp == 1:
                        self.instruction_list[self.instOrdCounter-1].setArg1(sub_elem_att['type'], value)
                    elif tmp == 2:
                        self.instruction_list[self.instOrdCounter - 1].setArg2(sub_elem_att['type'], value)
                    elif tmp == 3:
                        self.instruction_list[self.instOrdCounter - 1].setArg3(sub_elem_att['type'], value)
                    tmp += 1
            self.instOrdCounter += 1


        self.instruction_list.append(None)


class Frames:

    def __init__(self):
        self.globalFrame = {}
        self.frameStack = []
        self.tmpFrame = None

    def create_frame(self):
        self.tmpFrame = {}

    def push_frame(self):
        self.frameStack.append(self.get_frame())
        self.tmpFrame = None

    def pop_frame(self):
        self.tmpFrame = self.get_local_frame()
        self.frameStack.pop()

    def get_frame(self):
        if self.tmpFrame is None:
            exit(ErrType.exitWithError(ErrType.errFrameNotExists))

        return self.tmpFrame

    def get_local_frame(self):
        try:
            return self.frameStack[-1]
        except IndexError:
            exit(ErrType.exitWithError(ErrType.errFrameNotExists))


