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
        self.ord_num = int
        self.stdin_input = []
        self.stdin_source = ""
        self.main()

    def main(self):

        if self.arg.sourceFileFull:
            self.file = self.arg.getSourceFileName()
        else:
            self.stdin_source = sys.stdin.read()

        if self.arg.inputFileFull:
            with open(self.arg.getInputFileName()) as f:
                self.stdin_input = f.readlines()

        xml = xmlCheck(self.file, self.stack, self.frames, self.instruction_list, self.labelJump,
                       self.ord_num, self.stdin_source, self.stdin_input)
        xml.start()

        inst_len = len(self.instruction_list)
        if not inst_len:
            exit(ErrType.exitWithError(ErrType.errSourceFile))

        try:
            self.instruction_list = sorted(self.instruction_list, key=lambda e: int(e.ord_num))

        except ValueError:
            exit(ErrType.exitWithError(ErrType.errXmlStructureSyntaxLex))

        self.order_check()

        self.instruction_list.append(None)

        self.set_labels()

        while True:

            if self.instruction_list[self.labelJump.order_num] is None:
                break

            self.instruction_list[self.labelJump.order_num].execute()

            self.labelJump.order_num += 1
            # TODO odstranit po patchi
            # print(self.labelJump.order_num)

    def order_check(self):
        for x, y in enumerate(self.instruction_list[:-1]):
            if self.instruction_list[x + 1].get_ord_num() is None:
                break
            elif int(y.get_ord_num()) > int(self.instruction_list[x + 1].get_ord_num()) or \
                    int(y.get_ord_num()) == int(self.instruction_list[x + 1].get_ord_num()) or \
                    int(y.get_ord_num()) <= 0:
                exit(ErrType.exitWithError(ErrType.errXmlStructureSyntaxLex))

    def set_labels(self):
        label_names = []

        inst_skip = IP.InstPass([], self.stack, self.frames, self.labelJump, self.ord_num)

        for instruction in self.instruction_list:
            if isinstance(instruction, IP.LABEL):
                label_names.append(instruction.Arg1.get_value())
                instruction.execute()
                self.instruction_list[self.labelJump.order_num] = inst_skip

            self.labelJump.order_num += 1

        self.labelJump.order_num = 0

        if not (len(set(label_names)) == len(label_names)):
            exit(ErrType.exitWithError(ErrType.errSemantics))


class xmlCheck:

    def __init__(self, file, stack, frames, instruction_list, labelJump, ord_num, stdin_source, stdin_input):
        self.labelJump = labelJump
        self.instruction_list = instruction_list
        self.xml_file = file
        self.tree = None
        self.root = None
        self.stack = stack
        self.frames = frames
        self.instOrdCounter = 1
        self.ord_num = ord_num
        self.stdin_source = stdin_source
        self.stdin_input = stdin_input
        self.arg_ord = []

    def start(self):
        if self.xml_file is None:
            try:
                tree = ET.ElementTree(ET.fromstring(self.stdin_source))
                self.root = tree.getroot()

            except ET.ParseError:
                exit(ErrType.exitWithError(ErrType.errXmlNotWellFormatted))
        else:
            try:
                tree = ET.parse(self.xml_file)
                self.root = tree.getroot()

            except ET.ParseError:
                exit(ErrType.exitWithError(ErrType.errXmlNotWellFormatted))

        if self.root.tag != 'program':
            exit(ErrType.exitWithError(ErrType.errXmlStructureSyntaxLex))

        for child in self.root:
            attrib = list(child.attrib.items())

            if child.tag != 'instruction':
                exit(ErrType.exitWithError(ErrType.errXmlStructureSyntaxLex))

            child_att_val = list(child.attrib.values())
            self.ord_num = child_att_val[0]
            child_att = list(child.attrib.keys())
            if not ('order' in child_att) or not ('opcode' in child_att) or len(child_att) != 2:
                exit(ErrType.exitWithError(ErrType.errXmlStructureSyntaxLex))

            else:
                self.instruction_list.append(IP.Factory.resolve(attrib[1][1], self.stack, self.frames,
                                                                self.labelJump, self.ord_num, self.stdin_input))

            for sub_elem in child:
                sub_elem_att = sub_elem.attrib

                if 'type' not in sub_elem_att or len(sub_elem_att) != 1:
                    exit(ErrType.exitWithError(ErrType.errXmlStructureSyntaxLex))

                if not (re.match(r"arg[123]", sub_elem.tag)):
                    exit(ErrType.exitWithError(ErrType.errXmlStructureSyntaxLex))

                else:
                    if sub_elem_att['type'] == "int":
                        try:
                            value = int(sub_elem.text)
                        except ValueError:
                            exit(ErrType.exitWithError(ErrType.errXmlStructureSyntaxLex))
                    elif sub_elem_att['type'] == "bool":
                        try:
                            value = bool(sub_elem.text)
                        except ValueError:
                            exit(ErrType.exitWithError(ErrType.errXmlStructureSyntaxLex))
                    elif sub_elem_att['type'] == "string":
                        try:
                            value = str(sub_elem.text)
                        except ValueError:
                            exit(ErrType.exitWithError(ErrType.errXmlStructureSyntaxLex))
                    else:
                        value = sub_elem.text

                    tmp = int(re.search(r'\d+', sub_elem.tag).group())
                    self.arg_ord.append(tmp)
                    if tmp == 1:
                        self.instruction_list[self.instOrdCounter - 1].setArg1(sub_elem_att['type'], value)
                    elif tmp == 2:
                        self.instruction_list[self.instOrdCounter - 1].setArg2(sub_elem_att['type'], value)
                    elif tmp == 3:
                        self.instruction_list[self.instOrdCounter - 1].setArg3(sub_elem_att['type'], value)
                    else:
                        exit(ErrType.exitWithError(ErrType.errXmlStructureSyntaxLex))
            self.arg_ord_check()
            self.arg_ord.clear()
            self.instOrdCounter += 1

    def arg_ord_check(self):
        if len(self.arg_ord) > 3:
            exit(ErrType.exitWithError(ErrType.errXmlStructureSyntaxLex))

        elif len(self.arg_ord) == 3:
            if self.arg_ord[0] == self.arg_ord[1] or \
                    self.arg_ord[1] == self.arg_ord[2] or \
                    self.arg_ord[0] == self.arg_ord[2]:
                exit(ErrType.exitWithError(ErrType.errXmlStructureSyntaxLex))

        elif len(self.arg_ord) == 2:
            if self.arg_ord[0] == self.arg_ord[1] or \
                    self.arg_ord[0] not in [1, 2] or \
                    self.arg_ord[1] not in [1, 2]:
                exit(ErrType.exitWithError(ErrType.errXmlStructureSyntaxLex))

        elif len(self.arg_ord) == 1:
            if self.arg_ord[0] != 1:
                exit(ErrType.exitWithError(ErrType.errXmlStructureSyntaxLex))


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
