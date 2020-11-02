"""
InputReader
--------------------------------------------------
Input Reader that checks and distributes commands. For detailed list of command options, check docs
"""

import sys


class InputReader:

    def __init__(self):
        self.raw_input = sys.argv
        self.command_type = None
        self.required_inputs = {}
        self.optional_inputs = {}

    def command_find(self):
        """
        Command validator for "takedown find"
        :return:
        """