import sys


def exitWithError(errorType):
    print(errorType, file=sys.stderr)
    sys.exit(errorType.code)
    

class Error:

    def __init__(self, description, code):
        self.description = description
        self.code = code

    def __str__(self):
        return self.description


errWrongParameters = Error("Missing parameter or illegal combination", 10)
errSourceFile = Error("Invalid source/input file", 11)
errOutputFiles = Error("Cannot open files to write", 12)
errInternalError = Error("Internal error", 99)
errXmlNotWellFormatted = Error("Wrong XML syntax, not well formatted", 31)
errXmlStructureSyntaxLex = Error("Wrong XML structure or syntactic/lexical error", 32)
errSemantics = Error("semantics error in XML, e.g. not defined label or redefinition of label", 52)
errWrongOperandType = Error("Wrong operand type", 53)
errVariableNotDefined = Error("Accessing not defined variable, frame exists", 54)
errFrameNotExists = Error("Frame not exists", 55)
errMissingValue = Error("Missing value in variable or stack", 56)
errWrongOperandValue = Error("Wrong operand value, e.g. division by zero", 57)
errWrongStringManipulation = Error("Wrong string manipulation", 58)
