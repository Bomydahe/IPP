import interpreter_lib.Error_type as ErrType
import sys


class Instruction:

    def __init__(self, num, stack, frames, labelJump):
        self.labelJump = labelJump
        self._numOfArgs: int = num
        self.frames = frames
        self.stack = stack
        self.Arg1 = None
        self.Arg2 = None
        self.Arg3 = None

    def setArg1(self, arg_type, arg_value):
        self.Arg1 = ArgFactory.resolve(1, arg_type, arg_value, self.frames)

    def getArg1(self):
        return self.Arg1

    def setArg2(self, arg_type, arg_value):
        self.Arg2 = ArgFactory.resolve(2, arg_type, arg_value, self.frames)

    def getArg2(self):
        return self.Arg2

    def setArg3(self, arg_type, arg_value):
        self.Arg3 = ArgFactory.resolve(3, arg_type, arg_value, self.frames)

    def getArg3(self):
        return self.Arg3

    @staticmethod
    def varVsConst_value(obj):
        if isinstance(obj, Const):
            return obj.get_value()
        elif isinstance(obj, Var):
            return obj.get_frame_value()
        else:
            exit(ErrType.exitWithError(ErrType.errWrongOperandType))


class Defvar(Instruction):
    def __init__(self, num, stack, frames, labelJump):
        super().__init__(num, stack, frames, labelJump)

    def execute(self):
        if isinstance(self.Arg1, Var):
            self.Arg1.define()


class Move(Instruction):
    def __init__(self, num, stack, frames, labelJump):
        super().__init__(num, stack, frames, labelJump)

    def execute(self):

        value = self.varVsConst_value(self.Arg2)
        if value == "None":
            self.Arg1.set_value("")
        else:
            self.Arg1.set_value(value)


class CreateFrame(Instruction):
    def __init__(self, num, stack, frames, labelJump):
        super().__init__(num, stack, frames, labelJump)

    def execute(self):
        self.frames.create_frame()


class PUSHFRAME(Instruction):
    def __init__(self, num, stack, frames, labelJump):
        super().__init__(num, stack, frames, labelJump)

    def execute(self):
        self.frames.push_frame()


class POPFRAME(Instruction):
    def __init__(self, num, stack, frames, labelJump):
        super().__init__(num, stack, frames, labelJump)

    def execute(self):
        self.frames.pop_frame()


class CALL(Instruction):
    def __init__(self, num, stack, frames, labelJump):
        super().__init__(num, stack, frames, labelJump)

    def execute(self):
        order_num = self.labelJump.order_num
        label_position = self.labelJump.label_position
        label_dict = self.labelJump.label_dict
        label_position.append(order_num)

        try:
            self.labelJump.order_num = label_dict[self.Arg1.get_value()]
        except KeyError:
            exit(ErrType.exitWithError(ErrType.errSemantics))


class RETURN(Instruction):
    def __init__(self, num, stack, frames, labelJump):
        super().__init__(num, stack, frames, labelJump)

    def execute(self):
        label_position = self.labelJump.label_position

        try:
            self.labelJump.order_num = label_position.pop()
        except IndexError:
            exit(ErrType.exitWithError(ErrType.errMissingValue))


class PUSHS(Instruction):
    def __init__(self, num, stack, frames, labelJump):
        super().__init__(num, stack, frames, labelJump)

    def execute(self):
        self.stack.append(self.varVsConst_value(self.Arg1))


class POPS(Instruction):
    def __init__(self, num, stack, frames, labelJump):
        super().__init__(num, stack, frames, labelJump)

    def execute(self):
        try:
            x = self.stack.pop()
            self.Arg1.set_value(x)

        except IndexError:
            exit(ErrType.exitWithError(ErrType.errMissingValue))


class ADD(Instruction):
    def __init__(self, num, stack, frames, labelJump):
        super().__init__(num, stack, frames, labelJump)

    def execute(self):
        operand_x = self.varVsConst_value(self.Arg2)
        operand_y = self.varVsConst_value(self.Arg3)

        if type(operand_x) == int and type(operand_y) == int:
            self.Arg1[0].set_value(operand_x + operand_y)
        else:
            exit(ErrType.exitWithError(ErrType.errWrongOperandType))


class SUB(Instruction):
    def __init__(self, num, stack, frames, labelJump):
        super().__init__(num, stack, frames, labelJump)

    def execute(self):
        operand_x = self.varVsConst_value(self.Arg2)
        operand_y = self.varVsConst_value(self.Arg3)

        if type(operand_x) == int and type(operand_y) == int:
            self.Arg1[0].set_value(operand_x - operand_y)
        else:
            exit(ErrType.exitWithError(ErrType.errWrongOperandType))


class MUL(Instruction):
    def __init__(self, num, stack, frames, labelJump):
        super().__init__(num, stack, frames, labelJump)

    def execute(self):
        operand_x = self.varVsConst_value(self.Arg2)
        operand_y = self.varVsConst_value(self.Arg3)

        if type(operand_x) == int and type(operand_y) == int:
            self.Arg1.set_value(operand_x * operand_y)
        else:
            exit(ErrType.exitWithError(ErrType.errWrongOperandType))


class IDIV(Instruction):
    def __init__(self, num, stack, frames, labelJump):
        super().__init__(num, stack, frames, labelJump)

    def execute(self):
        operand_x = self.varVsConst_value(self.Arg2)
        operand_y = self.varVsConst_value(self.Arg3)

        if type(operand_x) == int and type(operand_y) == int:
            if operand_y == 0:
                exit(ErrType.exitWithError(ErrType.errWrongOperandValue))

            self.Arg1.set_value(operand_x // operand_y)
        else:
            exit(ErrType.exitWithError(ErrType.errWrongOperandType))


class LT(Instruction):
    def __init__(self, num, stack, frames, labelJump):
        super().__init__(num, stack, frames, labelJump)

    def execute(self):
        operand_x = self.varVsConst_value(self.Arg2)
        operand_y = self.varVsConst_value(self.Arg3)

        if type(operand_x) == type(operand_y):
            self.Arg1[0].set_value(operand_x < operand_y)
        else:
            exit(ErrType.exitWithError(ErrType.errWrongOperandType))


class GT(Instruction):
    def __init__(self, num, stack, frames, labelJump):
        super().__init__(num, stack, frames, labelJump)

    def execute(self):
        operand_x = self.varVsConst_value(self.Arg2)
        operand_y = self.varVsConst_value(self.Arg3)

        if type(operand_x) == type(operand_y):
            self.Arg1.set_value(operand_x > operand_y)
        else:
            exit(ErrType.exitWithError(ErrType.errWrongOperandType))


class EQ(Instruction):
    def __init__(self, num, stack, frames, labelJump):
        super().__init__(num, stack, frames, labelJump)

    def execute(self):
        operand_x = self.varVsConst_value(self.Arg2)
        operand_y = self.varVsConst_value(self.Arg3)

        if type(operand_x) == type(operand_y):
            if type(operand_x) == int or type(operand_y) == bool:
                self.Arg1.set_value(operand_x == operand_y)
            else:
                self.Arg1.set_value(len(operand_x) == len(operand_y))
        else:
            exit(ErrType.exitWithError(ErrType.errWrongOperandType))


class AND(Instruction):
    def __init__(self, num, stack, frames, labelJump):
        super().__init__(num, stack, frames, labelJump)

    def execute(self):
        operand_x = self.varVsConst_value(self.Arg2)
        operand_y = self.varVsConst_value(self.Arg3)

        if type(operand_x) == bool and type(operand_y) == bool:
            self.Arg1.set_value(operand_x and operand_y)
        else:
            exit(ErrType.exitWithError(ErrType.errWrongOperandType))


class OR(Instruction):
    def __init__(self, num, stack, frames, labelJump):
        super().__init__(num, stack, frames, labelJump)

    def execute(self):
        operand_x = self.varVsConst_value(self.Arg2)
        operand_y = self.varVsConst_value(self.Arg3)

        if type(operand_x) == bool and type(operand_y) == bool:
            self.Arg1.set_value(operand_x or operand_y)
        else:
            exit(ErrType.exitWithError(ErrType.errWrongOperandType))


class NOT(Instruction):
    def __init__(self, num, stack, frames, labelJump):
        super().__init__(num, stack, frames, labelJump)

    def execute(self):
        operand_x = self.varVsConst_value(self.Arg2)

        if type(operand_x) == bool:
            self.Arg1.set_value(not operand_x)
        else:
            exit(ErrType.exitWithError(ErrType.errWrongOperandType))


class INT2CHAR(Instruction):
    def __init__(self, num, stack, frames, labelJump):
        super().__init__(num, stack, frames, labelJump)

    def execute(self):

        operand_x = self.varVsConst_value(self.Arg2)
        print(self.Arg2.get_type())
        if type(operand_x) == int:
            try:
                self.Arg1.set_value(chr(operand_x))
            except ValueError:
                exit(ErrType.exitWithError(ErrType.errWrongStringManipulation))
        else:
            exit(ErrType.exitWithError(ErrType.errWrongOperandType))


class STRI2INT(Instruction):
    def __init__(self, num, stack, frames, labelJump):
        super().__init__(num, stack, frames, labelJump)

    def execute(self):
        operand_x = self.varVsConst_value(self.Arg2)
        operand_y = self.varVsConst_value(self.Arg3)

        if type(operand_x) != str or type(operand_y) != int:
            exit(ErrType.exitWithError(ErrType.errWrongOperandType))

        try:
            self.Arg1.set_value(ord(operand_x[operand_y]))
        except IndexError:
            exit(ErrType.exitWithError(ErrType.errWrongStringManipulation))


class READ(Instruction):
    def __init__(self, num, stack, frames, labelJump):
        super().__init__(num, stack, frames, labelJump)

    def execute(self):
        print("Jsem READ s argumentem")


class WRITE(Instruction):
    def __init__(self, num, stack, frames, labelJump):
        super().__init__(num, stack, frames, labelJump)

    def execute(self):
        print(self.varVsConst_value(self.Arg1))


class CONCAT(Instruction):
    def __init__(self, num, stack, frames, labelJump):
        super().__init__(num, stack, frames, labelJump)

    def execute(self):
        operand_x = self.varVsConst_value(self.Arg2)
        operand_y = self.varVsConst_value(self.Arg3)

        if type(operand_x) != str or type(operand_y) != str:
            exit(ErrType.exitWithError(ErrType.errWrongOperandType))

        self.Arg1.set_value(operand_x + operand_y)


class STRLEN(Instruction):
    def __init__(self, num, stack, frames, labelJump):
        super().__init__(num, stack, frames, labelJump)

    def execute(self):
        operand_x = self.varVsConst_value(self.Arg2)

        if type(operand_x) != str:
            exit(ErrType.exitWithError(ErrType.errWrongOperandType))

        self.Arg1.set_value(len(operand_x))


class GETCHAR(Instruction):
    def __init__(self, num, stack, frames, labelJump):
        super().__init__(num, stack, frames, labelJump)

    def execute(self):
        operand_x = self.varVsConst_value(self.Arg2)
        operand_y = self.varVsConst_value(self.Arg3)

        if type(operand_x) != str or type(operand_y) != int:
            exit(ErrType.exitWithError(ErrType.errWrongOperandType))

        try:
            self.Arg1.set_value(operand_x[operand_y])
        except IndexError:
            exit(ErrType.exitWithError(ErrType.errWrongStringManipulation))


class SETCHAR(Instruction):
    def __init__(self, num, stack, frames, labelJump):
        super().__init__(num, stack, frames, labelJump)

    def execute(self):
        operand_x = self.varVsConst_value(self.Arg2)
        operand_y = self.varVsConst_value(self.Arg3)
        value = self.Arg1.get_frame_value()

        if type(operand_x) != int or type(operand_y) != str or type(value) != str:
            exit(ErrType.exitWithError(ErrType.errWrongOperandType))

        if len(operand_y) < 1:
            exit(ErrType.exitWithError(ErrType.errWrongStringManipulation))

        value = list(value)

        try:
            value[operand_x] = operand_y[0]
        except IndexError:
            exit(ErrType.exitWithError(ErrType.errWrongStringManipulation))

        self.Arg1.set_value("".join(value))


class TYPE(Instruction):
    def __init__(self, num, stack, frames, labelJump):
        super().__init__(num, stack, frames, labelJump)

    def execute(self):
        typ = self.Arg2.get_value()

        if type(typ) == bool:
            self.Arg1.set_value('bool')
        elif type(typ) == int:
            self.Arg1.set_value('int')
        elif type(typ) == str:
            self.Arg1.set_value('string')
        else:
            self.Arg1.set_value('')


class LABEL(Instruction):
    def __init__(self, num, stack, frames, labelJump):
        super().__init__(num, stack, frames, labelJump)

    def execute(self):
        order_num = self.labelJump.order_num
        label_dict = self.labelJump.label_dict
        label_dict[self.Arg1.get_value()] = order_num


class JUMP(Instruction):
    def __init__(self, num, stack, frames, labelJump):
        super().__init__(num, stack, frames, labelJump)

    def execute(self):
        label_dict = self.labelJump.label_dict
        try:
            self.labelJump.order_num = label_dict[self.Arg1.get_value()]
        except KeyError:
            exit(ErrType.exitWithError(ErrType.errSemantics))


class JUMPIFEQ(Instruction):
    def __init__(self, num, stack, frames, labelJump):
        super().__init__(num, stack, frames, labelJump)

    def execute(self):

        label_dict = self.labelJump.label_dict
        operand_x = self.varVsConst_value(self.Arg2)
        operand_y = self.varVsConst_value(self.Arg3)

        if (type(operand_x) == int and type(operand_y) == int) or \
                (type(operand_x) == bool and type(operand_y) == bool) or \
                (type(operand_x) == str and type(operand_y) == str):
            if operand_x == operand_y:
                try:
                    self.labelJump.order_num = label_dict[self.Arg1.get_value()]
                except KeyError:
                    exit(ErrType.exitWithError(ErrType.errSemantics))
        else:
            exit(ErrType.exitWithError(ErrType.errWrongOperandType))


class JUMPIFNEQ(Instruction):
    def __init__(self, num, stack, frames, labelJump):
        super().__init__(num, stack, frames, labelJump)

    def execute(self):
        label_dict = self.labelJump.label_dict
        operand_x = self.varVsConst_value(self.Arg2)
        operand_y = self.varVsConst_value(self.Arg3)

        if (type(operand_x) == int and type(operand_y) == int) or \
                (type(operand_x) == bool and type(operand_y) == bool) or \
                (type(operand_x) == str and type(operand_y) == str):
            if operand_x != operand_y:
                try:
                    self.labelJump.order_num = label_dict[self.Arg1.get_value()]
                except KeyError:
                    exit(ErrType.exitWithError(ErrType.errSemantics))
        else:
            exit(ErrType.exitWithError(ErrType.errWrongOperandType))


class EXIT(Instruction):
    def __init__(self, num, stack, frames, labelJump):
        super().__init__(num, stack, frames, labelJump)

    def execute(self):
        operand_x = self.varVsConst_value(self.Arg1)
        if type(operand_x) == int:
            if 0 <= operand_x < 50:
                exit(operand_x)
            else:
                exit(ErrType.exitWithError(ErrType.errWrongOperandValue))
        else:
            exit(ErrType.exitWithError(ErrType.errWrongOperandType))


class DPRINT(Instruction):
    def __init__(self, num, stack, frames, labelJump):
        super().__init__(num, stack, frames, labelJump)

    def execute(self):
        operand_x = self.Arg1.get_value()

        print(operand_x, file=sys.stderr)


class BREAK(Instruction):
    def __init__(self, num, stack, frames, labelJump):
        super().__init__(num, stack, frames, labelJump)

    def execute(self):
        print("Stack: {0}\nInstruction counter: {1}\nDefined labels: {2}".format(self.stack,
                                                                                 self.labelJump.order_num,
                                                                                 self.labelJump.label_dict),
              file=sys.stderr)


class InstPass(Instruction):
    def __init__(self, num, stack, frames, labelJump):
        super().__init__(num, stack, frames, labelJump)

    def execute(self):
        pass


class LabelJump:
    def __init__(self):
        self.order_num = 0
        self.label_position = []
        self.label_dict = {}

    def get_order_num(self):
        return self.order_num


class Argument:
    def __init__(self, num, typ: str, value, frames):
        self.frames = frames
        self._num = num
        self._typ = typ
        self._value = value

    def get_value(self):
        return self._value

    def get_type(self):
        return self._typ


class Var(Argument):
    def __init__(self, num, value, frames):
        super().__init__(num, "var", value, frames)
        self.frame, self.name = self._value.split("@")

    def get_frame(self):
        return self.frame

    def get_name(self):
        return self.name

    def define(self):
        if self.frame == "GF":
            self.frames.globalFrame[self.name] = None
        elif self.frame == "LF":
            self.frames.get_local_frame()[self.name] = None
        elif self.frame == "TF":
            self.frames.get_frame()[self.name] = None

    def set_value(self, value):
        if self.frame == "GF" and self.name in self.frames.globalFrame:
            self.frames.globalFrame[self.name] = value
        elif self.frame == "LF" and self.name in self.frames.get_local_frame():
            self.frames.get_local_frame()[self.name] = value
        elif self.frame == "TF" and self.name in self.frames.get_frame():
            self.frames.get_frame()[self.name] = value
        else:
            exit(ErrType.exitWithError(ErrType.errVariableNotDefined))

    def get_value(self):
        try:
            if self.frame == "GF":
                return self.frames.globalFrame[self.name]
            elif self.frame == "LF":
                return self.frames.get_local_frame()[self.name]
            elif self.frame == "TF":
                return self.frames.get_frame()[self.name]
        except KeyError:
            exit(ErrType.exitWithError(ErrType.errVariableNotDefined))

    def get_frame_value(self):
        value = self.get_value()

        if value is None:
            exit(ErrType.exitWithError(ErrType.errMissingValue))
        else:
            return value


class Const(Argument):
    def __init__(self, num, typ, value, frames):
        super().__init__(num, typ, value, frames)


class ArgFactory:
    @classmethod
    def resolve(cls, num: int, typ: str, value, frames):
        if typ == "var":
            return Var(num, value, frames)

        elif typ in ["int", "bool", "string", "nil"]:
            return Const(num, typ, value, frames)

        elif typ == "label":
            return Argument(num, typ, value, frames)

        elif typ == "type":
            return Argument(num, typ, value, frames)

        else:
            print(typ)
            print("uh oh")
            exit(ErrType.exitWithError(ErrType.errXmlNotWellFormatted))


# will solve xml constructions
class Factory:
    @classmethod
    def resolve(cls, string: str, stack, frames, labelJump):
        if string.upper() == "DEFVAR":
            return Defvar(2, stack, frames, labelJump)

        elif string.upper() == "MOVE":
            return Move(2, stack, frames, labelJump)

        elif string.upper() == "CREATEFRAME":
            return CreateFrame(0, stack, frames, labelJump)

        elif string.upper() == "PUSHFRAME":
            return PUSHFRAME(0, stack, frames, labelJump)

        elif string.upper() == "POPFRAME":
            return POPFRAME(0, stack, frames, labelJump)

        elif string.upper() == "CALL":
            return CALL(1, stack, frames, labelJump)

        elif string.upper() == "RETURN":
            return RETURN(0, stack, frames, labelJump)

        elif string.upper() == "PUSHS":
            return PUSHS(1, stack, frames, labelJump)

        elif string.upper() == "POPS":
            return POPS(1, stack, frames, labelJump)

        elif string.upper() == "ADD":
            return ADD(3, stack, frames, labelJump)

        elif string.upper() == "SUB":
            return SUB(3, stack, frames, labelJump)

        elif string.upper() == "MUL":
            return MUL(3, stack, frames, labelJump)

        elif string.upper() == "IDIV":
            return IDIV(3, stack, frames, labelJump)

        elif string.upper() == "LT":
            return LT(3, stack, frames, labelJump)

        elif string.upper() == "GT":
            return GT(3, stack, frames, labelJump)

        elif string.upper() == "EQ":
            return EQ(3, stack, frames, labelJump)

        elif string.upper() == "AND":
            return AND(3, stack, frames, labelJump)

        elif string.upper() == "OR":
            return OR(3, stack, frames, labelJump)

        elif string.upper() == "NOT":
            return NOT(2, stack, frames, labelJump)

        elif string.upper() == "INT2CHAR":
            return INT2CHAR(2, stack, frames, labelJump)

        elif string.upper() == "STRI2INT":
            return STRI2INT(3, stack, frames, labelJump)

        elif string.upper() == "READ":
            return READ(2, stack, frames, labelJump)

        elif string.upper() == "WRITE":
            return WRITE(1, stack, frames, labelJump)

        elif string.upper() == "CONCAT":
            return CONCAT(3, stack, frames, labelJump)

        elif string.upper() == "STRLEN":
            return STRLEN(2, stack, frames, labelJump)

        elif string.upper() == "GETCHAR":
            return GETCHAR(3, stack, frames, labelJump)

        elif string.upper() == "SETCHAR":
            return SETCHAR(3, stack, frames, labelJump)

        elif string.upper() == "TYPE":
            return TYPE(2, stack, frames, labelJump)

        elif string.upper() == "LABEL":
            return LABEL(1, stack, frames, labelJump)

        elif string.upper() == "JUMP":
            return JUMP(1, stack, frames, labelJump)

        elif string.upper() == "JUMPIFEQ":
            return JUMPIFEQ(3, stack, frames, labelJump)

        elif string.upper() == "JUMPIFNEQ":
            return JUMPIFNEQ(3, stack, frames, labelJump)

        elif string.upper() == "EXIT":
            return EXIT(1, stack, frames, labelJump)

        elif string.upper() == "DPRINT":
            return DPRINT(1, stack, frames, labelJump)

        elif string.upper() == "BREAK":
            return BREAK(0, stack, frames, labelJump)

        else:
            print("wtf instrukcia neexistuje ?????????/")
            return
