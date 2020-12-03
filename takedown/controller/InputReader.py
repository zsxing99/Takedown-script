"""
InputReader
--------------------------------------------------
Input Reader that checks and distributes commands. For detailed list of command options, check docs
"""

import sys
import os
import configparser
import takedown


def check_file(file_path, mode="r"):
    """
    check if provided file path is able to be accessed
    :return: true if can, false otherwise
    """
    # in case the file will be overwritten
    if mode != 'r':
        if os.path.exists(file_path):
            return True
    else:
        if not os.path.exists(file_path):
            return False
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
        self.config_path = None

    def has_config(self):
        curr = 2
        length = len(self.raw_input)
        while curr < length:
            if self.raw_input[curr] == '-c':
                if curr == length - 1:
                    self.parse_error_msg = "Missing target after flag '-c'"
                else:
                    print("Config file detected.")
                    self.config_path = self.raw_input[curr + 1]
                return True
            curr += 1

        return False

    def parse_config_file(self):
        if self.command_type == "find":
            return self.__parse_config_file_find()
        elif self.command_type == "send":
            return self.__parse_config_file_send()
        else:
            self.parse_error_msg = "Unnecessary config file."
            return False

    def __parse_config_file_find(self):
        if not self.config_path:
            return False
        if not check_file(self.config_path, "r"):
            self.parse_error_msg = "File path '{}' cannot be found.".format(self.config_path)
            return False
        config_reader = configparser.ConfigParser()
        config_reader.read(self.config_path)

        if 'required parameters' not in config_reader:
            self.parse_error_msg = "Missing required parameter section in config file."
            return False

        # check params
        required_params = config_reader['required parameters']

        # check required
        if "GitHub_token" in required_params:
            self.required_inputs["GitHub_token"] = required_params["GitHub_token"]
        else:
            self.parse_error_msg = "Missing required parameters. Please refer to 'help' command"
            return False
        if "search_query" in required_params:
            self.required_inputs["search_query"] = required_params["search_query"]
        else:
            self.parse_error_msg = "Missing required parameters. Please refer to 'help' command"
            return False

        optional_params = None
        # if exists, continue to read
        if 'optional parameters' in config_reader:
            optional_params = config_reader['optional parameters']
        else:
            return True

        # check optional
        if "targets" in optional_params:
            targets = optional_params["targets"].split("+")
            for target in targets:
                if target not in ["repo", "code"]:
                    self.parse_error_msg = "Unrecognized target, check 'help' for details."
                    return False
            self.optional_inputs["targets"] = targets
        if "inputs" in optional_params:
            files = optional_params["inputs"].split("+")
            for file in files:
                if not check_file(file):
                    self.parse_error_msg = "File path '{}' cannot be accessed.".format(file)
                    return False
            self.optional_inputs["inputs"] = files
        if "output" in optional_params:
            file = optional_params["output"]
            if not check_file(file, "w+"):
                self.parse_error_msg = "Output file path '{}' cannot be accessed.".format(file)
                return False
            self.optional_inputs["output"] = file
        if "format" in optional_params:
            output_format = optional_params["format"]
            if output_format not in ["json", "yaml"]:
                self.parse_error_msg = "Unrecognized file format. Please check 'help' for details"
                return False
            self.optional_inputs["format"] = output_format

        return True

    def __parse_config_file_send(self):
        if not self.config_path:
            return False
        if not check_file(self.config_path, "r"):
            self.parse_error_msg = "File path '{}' cannot be found.".format(self.config_path)
            return False
        config_reader = configparser.ConfigParser()
        config_reader.read(self.config_path)

        if 'required parameters' not in config_reader:
            self.parse_error_msg = "Missing required parameter section in config file."
            return False

        # check params
        required_params = config_reader['required parameters']

        # check required
        if "domain" in required_params:
            self.required_inputs["domain"] = required_params["domain"]
        else:
            self.parse_error_msg = "Missing required parameters. Please refer to 'help' command"
            return False
        if "port" in required_params:
            self.required_inputs["port"] = required_params["port"]
        else:
            self.parse_error_msg = "Missing required parameters. Please refer to 'help' command"
            return False
        if "inputs" in required_params:
            inputs = required_params["inputs"].split("+")
            for input_file in inputs:
                if not check_file(input_file):
                    self.parse_error_msg = "Input file: {} cannot be accessed.".format(input_file)
                    return False
            self.required_inputs["inputs"] = inputs
        else:
            self.parse_error_msg = "Missing required parameters. Please refer to 'help' command"
            return False

        optional_params = None
        # if exists, continue to read
        if 'optional parameters' in config_reader:
            optional_params = config_reader['optional parameters']
        else:
            return True

        # check optional
        if "username" in optional_params:
            username = optional_params["username"]
            self.optional_inputs["username"] = username
        if "password" in optional_params:
            password = optional_params["password"]
            self.optional_inputs["password"] = password
        if "secure_method" in optional_params:
            secure_method = optional_params["secure_method"]
            if not secure_method.lower() in ['tls', 'ssl']:
                self.parse_error_msg = "Secure method unknown."
                return False
            self.optional_inputs["secure_method"] = secure_method
        if "tags" in optional_params:
            tags = optional_params["tags"].split("+")
            self.optional_inputs["tags"] = tags
        if "output" in optional_params:
            file = optional_params["output"]
            if not check_file(file, "w+"):
                self.parse_error_msg = "Output file path '{}' cannot be accessed.".format(file)
                return False
            self.optional_inputs["output"] = file
        if "format" in optional_params:
            output_format = optional_params["format"]
            if output_format not in ["json", "yaml"]:
                self.parse_error_msg = "Unrecognized file format. Please check 'help' for details"
                return False
            self.optional_inputs["format"] = output_format
        if "email_name" in optional_params:
            email_name = optional_params["email_name"]
            self.optional_inputs["name"] = email_name
        if "email_subject" in optional_params:
            email_subject = optional_params["email_subject"]
            self.optional_inputs["subject"] = email_subject
        if "email_preface" in optional_params:
            email_preface = optional_params["email_preface"]
            if email_preface.count("{}") != 1:
                self.parse_error_msg = "Incorrect format of preface entered."
                return False
            self.optional_inputs["preface"] = email_preface
        if "email_ending" in optional_params:
            email_ending = optional_params["email_ending"]
            if email_ending.count("{}") != 1:
                self.parse_error_msg = "Incorrect format of ending entered."
                return False
            self.optional_inputs["ending"] = email_ending

        return True

    def prepare(self):
        """
        check semantics
        :return: true if commands are correct; false if failed
        """
        # normal parameters
        if len(self.raw_input) <= 1:
            self.parse_error_msg = "For usage, please check '{} help'.".format(self.raw_input[0])
            self.__print_info()
            return False
        if self.raw_input[1] == "find":
            return self.__command_find()
        elif self.raw_input[1] == "send":
            return self.__command_send()
        else:
            return self.__command_help()

    def __print_info(self):
        print("Takedown version {}".format(takedown.VERSION))
        print(takedown.DESCRIPTION)
        print(takedown.CONTRIBUTORS_INFO)

    def __command_find(self):
        """
        Command validator and parser for "takedown find"
        :return: true if commands are correct; false if failed
        """
        self.command_type = "find"

        # check config files
        if self.has_config():
            return self.parse_config_file()

        # read required input: search_query and GitHub token
        if len(self.raw_input) < 4:
            self.parse_error_msg = "Missing required parameters. Please refer to 'help' command."
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
                    self.optional_inputs["targets"] = targets
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

        # check config files
        if self.has_config():
            return self.parse_config_file()

        # read required input: search_query and GitHub token
        if len(self.raw_input) < 5:
            self.parse_error_msg = "Missing required parameters. Please refer to 'help' command"
            return False
        else:
            self.required_inputs["domain"] = self.raw_input[2]
            self.required_inputs["port"] = self.raw_input[3]
            inputs = self.raw_input[4].split("+")
            for input_file in inputs:
                if not check_file(input_file):
                    self.parse_error_msg = "Input file: {} cannot be accessed.".format(input_file)
                    return False
            self.required_inputs["inputs"] = inputs
            print("Checked required parameters.")

            # keep reading optional parameters
            length = len(self.raw_input)
            curr = 5
            while curr < length:
                # -u username
                if self.raw_input[curr] == '-u':
                    if curr == length - 1:
                        self.parse_error_msg = "Missing target after flag '-u'"
                        return False
                    else:
                        username = self.raw_input[curr + 1]
                        self.optional_inputs["username"] = username
                # -p password
                elif self.raw_input[curr] == '-p':
                    if curr == length - 1:
                        self.parse_error_msg = "Missing target after flag '-p'"
                        return False
                    else:
                        password = self.raw_input[curr + 1]
                        self.optional_inputs["password"] = password
                # -s secure method
                elif self.raw_input[curr] == '-s':
                    if curr == length - 1:
                        self.parse_error_msg = "Missing target after flag '-s'"
                        return False
                    else:
                        secure_method = self.raw_input[curr + 1]
                        if not secure_method.lower() in ['tls', 'ssl']:
                            self.parse_error_msg = "Secure method unknown."
                            return False
                        self.optional_inputs["secure_method"] = secure_method
                # -t tags
                elif self.raw_input[curr] == '-t':
                    if curr == length - 1:
                        self.parse_error_msg = "Missing target after flag '-t'"
                        return False
                    else:
                        tags = self.raw_input[curr + 1].split("+")
                        self.optional_inputs["tags"] = tags
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
                # -en name
                elif self.raw_input[curr] == '-en':
                    if curr == length - 1:
                        self.parse_error_msg = "Missing target after flag '-en'"
                        return False
                    else:
                        name = self.raw_input[curr + 1]
                        self.optional_inputs["name"] = name
                # -es subject
                elif self.raw_input[curr] == '-es':
                    if curr == length - 1:
                        self.parse_error_msg = "Missing target after flag '-es'"
                        return False
                    else:
                        subject = self.raw_input[curr + 1]
                        self.optional_inputs["subject"] = subject
                # -ep preface
                elif self.raw_input[curr] == '-ep':
                    if curr == length - 1:
                        self.parse_error_msg = "Missing target after flag '-ep'"
                        return False
                    else:
                        preface = self.raw_input[curr + 1]
                        if preface.count("{}") != 1:
                            self.parse_error_msg = "Incorrect format of preface entered."
                            return False
                        self.optional_inputs["preface"] = preface
                # -ee ending
                elif self.raw_input[curr] == '-ee':
                    if curr == length - 1:
                        self.parse_error_msg = "Missing target after flag '-ee'"
                        return False
                    else:
                        ending = self.raw_input[curr + 1]
                        if ending.count("{}") != 1:
                            self.parse_error_msg = "Incorrect format of ending entered."
                            return False
                        self.optional_inputs["ending"] = ending
                else:
                    # skip unrecognized input
                    curr += 1
                    continue
                curr += 2

            print("Checked optional parameters.")
            return True

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
