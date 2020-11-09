import unittest
import os
import yaml
import json
from .InputReader import InputReader
from .InputProcessor import load_previous_outputs_as_inputs


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
                              "-t", "repo+code", "-o", temp_output_file])
        self.assertEqual(reader.prepare(), True)
        required, optional = reader.execute()
        self.assertDictEqual(required, {
            "search_query": "ReactJS Ant Design",
            "GitHub_token": "token - xxxxx"
        })
        self.assertDictEqual(optional, {
            "target": ["repo", "code"],
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
                              "-t", "repo+code", "-i", input1 + "+" + input2])
        self.assertTrue(reader.prepare())
        required, optional = reader.execute()
        self.assertDictEqual(required, {
            "search_query": "ReactJS Ant Design",
            "GitHub_token": "token - xxxxx"
        })
        self.assertDictEqual(optional, {
            "target": ["repo", "code"],
            "inputs": [input1, input2]
        })
        # remove temp file
        os.remove(input1)
        os.remove(input2)

    def test_find_complex_wrong_input__wrong_file_path(self):
        input1 = "./test_input1.tempfile"
        # no file input1
        reader = InputReader(["takedown", "find", "ReactJS Ant Design", "token - xxxxx",
                              "-t", "repo+code", "-i", input1])
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
                              "-t", "repo", "abababa", "nonsence"])
        self.assertTrue(reader.prepare())


class InputProcessorTester(unittest.TestCase):

    def setUp(self):
        # define commonly tested samples
        self.test_sample1 = {
            "results": [
                {
                    "owner__username": "haha_example_name",
                    "owner__name": "John",
                    "owner__email": "z@z.com",
                    "owner__html_url": "https://url.example.com",
                    "repos": [
                        {
                            "repo__name": "ECS150",
                            "repo__html_url": "https://url.example.ECS150.com",
                            "status": "New",
                            "latest_detected_date": "2020-10-25 23:44:47.227048"
                        },
                        {
                            "repo__name": "ECS188",
                            "repo__html_url": "https://url.example.ECS188.com",
                            "status": "New",
                            "latest_detected_date": "2020-10-25 23:44:47.227048"
                        },
                        {
                            "repo__name": "HIS17B",
                            "repo__html_url": "https://url.example.HIS17B.com",
                            "status": "Waiting",
                            "latest_detected_date": "2020-10-21 23:44:47.227048"
                        }
                    ]
                },
                {
                    "owner__username": "haha_cat_fish",
                    "owner__name": None,
                    "owner__email": None,
                    "owner__html_url": "https://url.test.com",
                    "repos": [
                        {
                            "repo__name": "pthread",
                            "repo__html_url": "https://url.example.pthread.com",
                            "status": "New",
                            "latest_detected_date": "2020-10-25 23:44:47.227048"
                        }
                    ]
                }
            ]
        }
        self.test_sample1_parsed = {
            "haha_example_name": {
                "owner__username": "haha_example_name",
                "owner__name": "John",
                "owner__email": "z@z.com",
                "owner__html_url": "https://url.example.com",
                "repos": {
                    "ECS150": {
                        "repo__name": "ECS150",
                        "repo__html_url": "https://url.example.ECS150.com",
                        "status": "New",
                        "latest_detected_date": "2020-10-25 23:44:47.227048"
                    },
                    "ECS188": {
                        "repo__name": "ECS188",
                        "repo__html_url": "https://url.example.ECS188.com",
                        "status": "New",
                        "latest_detected_date": "2020-10-25 23:44:47.227048"
                    },
                    "HIS17B": {
                        "repo__name": "HIS17B",
                        "repo__html_url": "https://url.example.HIS17B.com",
                        "status": "Waiting",
                        "latest_detected_date": "2020-10-21 23:44:47.227048"
                    }
                }
            },
            "haha_cat_fish": {
                "owner__username": "haha_cat_fish",
                "owner__name": None,
                "owner__email": None,
                "owner__html_url": "https://url.test.com",
                "repos": {
                    "pthread": {
                        "repo__name": "pthread",
                        "repo__html_url": "https://url.example.pthread.com",
                        "status": "New",
                        "latest_detected_date": "2020-10-25 23:44:47.227048"
                    }
                }
            }
        }
        self.test_sample2 = {
            "results": [
                {
                    "owner__username": "haha_example_name",
                    "owner__name": "John",
                    "owner__email": "z@z.com",
                    "owner__html_url": "https://url.example.com",
                    "repos": [
                        {
                            "repo__name": "HIS17B",
                            "repo__html_url": "https://url.example.HIS17B.com",
                            "status": "Waiting",
                            "latest_detected_date": "2020-10-30 23:44:47.227048"
                        }
                    ]
                },
                {
                    "owner__username": "haha_cat_fish",
                    "owner__name": None,
                    "owner__email": None,
                    "owner__html_url": "https://url.test.com",
                    "repos": [
                        {
                            "repo__name": "pthread",
                            "repo__html_url": "https://url.example.pthread.com",
                            "status": "New",
                            "latest_detected_date": "2020-10-21 23:44:47.227048"
                        }
                    ]
                }
            ]
        }
        self.test_sample12_combined_parsed = {
            "haha_example_name": {
                "owner__username": "haha_example_name",
                "owner__name": "John",
                "owner__email": "z@z.com",
                "owner__html_url": "https://url.example.com",
                "repos": {
                    "ECS150": {
                        "repo__name": "ECS150",
                        "repo__html_url": "https://url.example.ECS150.com",
                        "status": "New",
                        "latest_detected_date": "2020-10-25 23:44:47.227048"
                    },
                    "ECS188": {
                        "repo__name": "ECS188",
                        "repo__html_url": "https://url.example.ECS188.com",
                        "status": "New",
                        "latest_detected_date": "2020-10-25 23:44:47.227048"
                    },
                    "HIS17B": {
                        "repo__name": "HIS17B",
                        "repo__html_url": "https://url.example.HIS17B.com",
                        "status": "Waiting",
                        "latest_detected_date": "2020-10-30 23:44:47.227048"
                    }
                }
            },
            "haha_cat_fish": {
                "owner__username": "haha_cat_fish",
                "owner__name": None,
                "owner__email": None,
                "owner__html_url": "https://url.test.com",
                "repos": {
                    "pthread": {
                        "repo__name": "pthread",
                        "repo__html_url": "https://url.example.pthread.com",
                        "status": "New",
                        "latest_detected_date": "2020-10-25 23:44:47.227048"
                    }
                }
            }
        }

    def test_single_file__correct_input_yaml(self):
        # create temp input file for test
        temp_input_file = open("./input_file1.tempfile", "w+")
        yaml.dump(self.test_sample1, temp_input_file)
        temp_input_file.close()
        # start testing
        temp_input_file = open("./input_file1.tempfile", "r")
        previous_record = load_previous_outputs_as_inputs(["./input_file1.tempfile"])
        temp_input_file.close()
        self.assertDictEqual(previous_record, self.test_sample1_parsed)
        # clean up
        os.remove("./input_file1.tempfile")

    def test_single_file__correct_input_json(self):
        # create temp input file for test
        temp_input_file = open("./input_file1.tempfile", "w+")
        json.dump(self.test_sample1, temp_input_file)
        temp_input_file.close()
        # start testing
        temp_input_file = open("./input_file1.tempfile", "r")
        previous_record = load_previous_outputs_as_inputs(["./input_file1.tempfile"])
        temp_input_file.close()
        self.assertDictEqual(previous_record, self.test_sample1_parsed)
        # clean up
        os.remove("./input_file1.tempfile")

    def test_two_files__correct_input_hybrid_sources(self):
        # create temp input file for test
        temp_input_file = open("./input_file1.tempfile", "w+")
        json.dump(self.test_sample1, temp_input_file)
        temp_input_file.close()
        temp_input_file = open("./input_file2.tempfile", "w+")
        yaml.dump(self.test_sample2, temp_input_file)
        temp_input_file.close()

        # test
        previous_record = load_previous_outputs_as_inputs(["./input_file1.tempfile", "./input_file2.tempfile"])
        self.assertDictEqual(previous_record, self.test_sample12_combined_parsed)

        # remove files
        os.remove("./input_file1.tempfile")
        os.remove("./input_file2.tempfile")

    def test_single_file__wrong_input(self):
        # create temp input file for test
        temp_input_file = open("./input_file1.tempfile", "w+")
        temp_input_file.write("write some garbage info")
        temp_input_file.close()
        # test
        previous_record = load_previous_outputs_as_inputs(["./input_file1.tempfile"])
        self.assertDictEqual(previous_record, {})

        # remove files
        os.remove("./input_file1.tempfile")


if __name__ == '__main__':
    unittest.main()
