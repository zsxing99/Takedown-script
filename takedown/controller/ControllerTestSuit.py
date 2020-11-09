import unittest
import os
from .InputReader import InputReader


class InputReaderTester(unittest.TestCase):

    def test_find_simple_correct_input(self):
        reader = InputReader(["takedown", "find", "ReactJS Ant Design", "token - xxxxx", ])
        self.assertEqual(reader.prepare(), True)
        required, optional = reader.execute()
        self.assertDictEqual(required, {
            "search_query": "ReactJS Ant Design",
            "GitHub_token": "token - xxxxx"
        })

    def test_find_simple_wrong_input(self):
        reader = InputReader(["takedown", "find", "ReactJS Ant Design", ])
        self.assertEqual(reader.prepare(), False)
        err_msg = reader.execute()
        self.assertEqual(err_msg, "Missing required parameters. Please refer to 'help' command")

    def test_find_complex_correct_input__with_output(self):
        temp_output_file = "./test_output.tempfile"
        reader = InputReader(["takedown", "find", "ReactJS Ant Design", "token - xxxxx",
                              "-t", "file+code", "-o", temp_output_file])
        self.assertEqual(reader.prepare(), True)
        required, optional = reader.execute()
        self.assertDictEqual(required, {
            "search_query": "ReactJS Ant Design",
            "GitHub_token": "token - xxxxx"
        })
        self.assertDictEqual(optional, {
            "target": ["file", "code"],
            "output": temp_output_file
        })
        # remove temp file
        os.remove(temp_output_file)

    def test_find_complex_correct_input__with_inputs(self):
        input1 = "./test_input1.tempfile"
        input2 = "./test_input2.tempfile"
        f1 = open(input1, "w+")
        f1.close()
        f2 = open(input2, "w+")
        f2.close()
        reader = InputReader(["takedown", "find", "ReactJS Ant Design", "token - xxxxx",
                              "-t", "file+code", "-i", input1 + "+" + input2])
        self.assertTrue(reader.prepare())
        required, optional = reader.execute()
        self.assertDictEqual(required, {
            "search_query": "ReactJS Ant Design",
            "GitHub_token": "token - xxxxx"
        })
        self.assertDictEqual(optional, {
            "target": ["file", "code"],
            "inputs": [input1, input2]
        })
        # remove temp file
        os.remove(input1)
        os.remove(input2)

    def test_find_complex_wrong_input__wrong_file_path(self):
        input1 = "./test_input1.tempfile"
        # no file input1
        reader = InputReader(["takedown", "find", "ReactJS Ant Design", "token - xxxxx",
                              "-t", "file+code", "-i", input1])
        self.assertFalse(reader.prepare())
        err_msg = reader.execute()
        self.assertEqual(err_msg, "File path '{}' cannot be accessed.".format(input1))

    def test_find_complex_wrong_input__with_missing_parameter(self):
        reader = InputReader(["takedown", "find", "ReactJS Ant Design", "token - xxxxx",
                              "-t", ])
        self.assertFalse(reader.prepare())
        err_msg = reader.execute()
        self.assertEqual(err_msg, "Missing target after flag '-t'")

    def test_find_complex_correct_input__with_redundant_parameter(self):
        reader = InputReader(["takedown", "find", "ReactJS Ant Design", "token - xxxxx",
                              "-t", "file", "abababa", "nonsence"])
        self.assertTrue(reader.prepare())


if __name__ == '__main__':
    unittest.main()
