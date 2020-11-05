"""
InputReader
--------------------------------------------------
Input Reader that checks and distributes commands. For detailed list of command options, check docs
"""

import sys


class InputReader:

    def __init__(self):
        self.raw_input = sys.argv
        self.parse_error_msg = None
        self.command_type = None
        self.required_inputs = {}
        self.optional_inputs = {}

    def prepare(self):
        """
        check semantics
        :return: true if commands are correct; false if failed
        """
        if self.raw_input[1] == "find":
            return self.__command_find()
        elif self.raw_input[1] == "send":
            return self.__command_send()
        else:
            return self.__command_help()

    def __command_find(self):
        """
        Command validator and parser for "takedown find"
        :return:
        """
        pass

    def __command_send(self):
        """
        Command validator and parser for "takedown send"
        :return:
        """
        pass

    def __command_help(self):
        """
        Command parser for help
        :return:
        """
        pass

    def execute(self):
        """
        it will be executed only no error in prepare
        :return: return a dict as the { param : key }
        """