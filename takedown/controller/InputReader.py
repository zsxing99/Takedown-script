"""
InputReader
--------------------------------------------------
Input Reader that checks and distributes commands. For detailed list of command options, check docs
"""

import sys


def check_file(file_path, mode="r"):
    """
    check if provided file path is able to be accessed
    :return: true if can, false otherwise
    """
    f = None
    try:
        f = open(file_path, mode)
        f.close()
        return True
    except IOError:
        if f:
            f.close()
        return False


class InputReader:

    def __init__(self, command_input=None):
        if command_input is None:
            command_input = sys.argv
        self.raw_input = command_input
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
        :return: true if commands are correct; false if failed
        """
        self.command_type = "find"

        # read required input: search_query and GitHub token
        if len(self.raw_input) < 4:
            self.parse_error_msg = "Missing required parameters. Please refer to 'help' command"
            return False
        else:
            self.required_inputs["search_query"] = self.raw_input[2]
            self.required_inputs["GitHub_token"] = self.raw_input[3]
            print("Checked required parameters.")

        # keep reading optional parameters
        length = len(self.raw_input)
        curr = 4
        while curr < length:
            # -t target
            if self.raw_input[curr] == '-t':
                if curr == length - 1:
                    self.parse_error_msg = "Missing target after flag '-t'"
                    return False
                else:
                    targets = self.raw_input[curr + 1].split("+")
                    for target in targets:
                        if target not in ["repo", "code"]:
                            self.parse_error_msg = "Unrecognized target, check 'help' for details."
                            return False
                    self.optional_inputs["target"] = targets
            elif self.raw_input[curr] == '-i':
                if curr == length - 1:
                    self.parse_error_msg = "Missing target after flag '-i'"
                    return False
                else:
                    files = self.raw_input[curr + 1].split("+")
                    for file in files:
                        if not check_file(file):
                            self.parse_error_msg = "File path '{}' cannot be accessed.".format(file)
                            return False
                    self.optional_inputs["inputs"] = files
                    self.command_type = "find+compare"
            elif self.raw_input[curr] == '-o':
                if curr == length - 1:
                    self.parse_error_msg = "Missing target after flag '-o'"
                    return False
                else:
                    file = self.raw_input[curr + 1]
                    if not check_file(file, "w+"):
                        self.parse_error_msg = "Output file path '{}' cannot be accessed.".format(file)
                        return False
                    self.optional_inputs["output"] = file
            elif self.raw_input[curr] == '-f':
                if curr == length - 1:
                    self.parse_error_msg = "Missing target after flag '-f'"
                    return False
                else:
                    output_format = self.raw_input[curr + 1]
                    if output_format not in ["json", "yaml"]:
                        self.parse_error_msg = "Unrecognized file format. Please check 'help' for details"
                        return False
                    self.optional_inputs["format"] = output_format
            else:
                # skip unrecognized input
                curr += 1
                continue
            curr += 2

        print("Checked optional parameters.")
        return True

    def __command_send(self):
        """
        Command validator and parser for "takedown send"
        :return:
        """
        self.command_type = "send"
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
        if self.parse_error_msg:
            return self.parse_error_msg
        return self.required_inputs, self.optional_inputs
