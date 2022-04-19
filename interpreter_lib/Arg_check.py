import argparse
import interpreter_lib.Error_type as ErrType
import os


class ArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        self.exit(ErrType.errWrongParameters.code, '%s: error: %s\n' % (self.prog, message))


class Arguments:

    # initializes the arguments
    def __init__(self, arguments):

        self.inputFileName = str
        self.sourceFileName = str
        self.inputFileFull = False
        self.sourceFileFull = False

        self.parser = ArgumentParser(add_help=False)
        self.parser.add_argument('-h', '--help', action='store_true',
                            help="prints usage info, can't be combined with other arguments")
        self.parser.add_argument("-s", "--source", metavar='FILE', type=str, help="--source=file : "
                                                                        "sets the path to the XML representation of source file")
        self.parser.add_argument("--input", metavar='FILE', type=str, help="--input=file : "        
                                                                 "sets path to the file that contains input for interpretation")
        self.args = self.parser.parse_args()
        self.argc = len(arguments)
        self.argsExe()

    def argsExe(self):

        if self.args.help:
            if self.argc == 1:
                self.parser.print_help()
                exit(0)

            else:
                exit(ErrType.exitWithError(ErrType.errWrongParameters))

        if self.args.source:
            if not os.path.isfile(self.args.source):
                exit(ErrType.exitWithError(ErrType.errSourceFile))
            else:
                self.setSourceFileName()
                self.setSourceFileFull()

        if self.args.input:
            if not os.path.isfile(self.args.input):
                exit(ErrType.exitWithError(ErrType.errSourceFile))
            else:
                self.setInputFileName()
                self.setInputFileFull()

        if not self.inputFileFull and not self.sourceFileFull:
            exit(ErrType.exitWithError(ErrType.errWrongParameters))

    def setInputFileName(self):
        self.inputFileName = self.args.input

    def getInputFileName(self):
        return self.inputFileName

    def setSourceFileName(self):
        self.sourceFileName = self.args.source

    def getSourceFileName(self):
        return self.sourceFileName

    def setSourceFileFull(self):
        self.sourceFileFull = True

    def setInputFileFull(self):
        self.inputFileFull = True


