"""
TakeDown v0.0.1
===============
author: Zesheng Xing
email: zsxing@ucdavis.edu

This Python project is to help people search on some client hosting contents that potential violate the their copyright.
"""

VERSION = "0.1.0"
DESCRIPTION = "A python script that allows users to search potential copyright violated information on GitHub and " \
              "send emails taking down those."
CONTRIBUTORS_INFO = "The project is developed by Zesheng Xing and supervised by Joël Porquet-Lupine at UC Davis, 2020."

USAGE = \
"""
Usage: takedown.py command [args...]
where commands include:

find        search repositories
    python takedown.py find [search_query] [GitHub_token] [-options]
    with following args:
        [search_query]: required. The text used to search.
        [Github_token]: required. The Github token used to raise the rate limit and enable broader search.
        [-t target]: optional. The target of the search query. It could be “repo”, “code”. It is “code” by default. 
                    Concatenate them by “+”, eg. “-t code+repo”.
        [-i input]: optional. The file path of previous output of takedown find. By providing this path, the output 
                    this time will be compared against the previous one.
        [-o output]: optional. The output file path. The result will be printed to the console by default.
        [-f format]: optional. The output format. It could be “yaml” or “json”. It is “yaml” by default
    or using a configuration file:
    python takedown.py find -c <path_to_config_file>
    config file args:
        required args:
            [search_query]: required. The text used to search.
            [Github_token]: required. The Github token used to raise the rate limit and enable broader search.
        optional args:
            [target]: optional. The target of the search query. It could be “repo”, “code”. It is “code” by default. 
                    Concatenate them by “+”, eg. “-t code+repo”.
            [input]: optional. The file path of previous output of takedown find. By providing this path, 
                    the output this time will be compared against the previous one.
            [output]: optional. The output file path. The result will be printed to the console by default.
            [format]: optional. The output format. It could be “yaml” or “json”. It is “yaml” by default

send        send emails based on records
    python takedown send [domain] [port] [inputs] [-options]
    with following args:
        [domain]: required. The domain address to connect
        [port]: required. port of domain to connect
        [inputs]: required. Input files to send email
        [-u username]: optional. username of the account. or ask
        [-p password]: optional. password of the account. or ask
        [-s secure method]: optional. It could be “TLS” or “SSL”, depending on the domain and port connected. 
                            Confirm before using this option.
        [-t tags]: optional. Only the records that matches the tag will be sent with an email
        [-o output]: optional. The output file path. The result will be printed to the console by default.
        [-f format]: optional. The output format. It could be “yaml” or “json”. It is “yaml” by default
        [-en email name]: optional. name used to send email. Otherwise username will be used
        [-es email subject]: optional. subject of the email. Otherwise default email subject is used
        [-ep email preface]: optional. preface of the email. Otherwise default email preface is used
        [-ee email ending]: optional. preface of the email. Otherwise default email preface is used
    or using a configuration file:
    python takedown.py send -c <path_to_config_file>
    config file args:
        required parameters:
            [domain]: required. Domain used to connect smtp service
            [port]: required. Port of domain to connect smtp service
            [inputs]: required. Records based to send emails
        optional parameters:
            [username]: optional. username of the account. or ask
            [password]: optional. password of the account. or ask
            [secure method]: optional. It could be “TLS” or “SSL”, depending on the domain and port connected. 
                            Confirm before using this option.
            [tags]: optional. Only the records that matches the tag will be sent with an email
            [output]: optional. The output file path. The result will be printed to the console by default.
            [format]: optional. The output format. It could be “yaml” or “json”. It is “yaml” by default
            [emai_name]: optional. name used to send email. Otherwise username will be used
            [email_subject]: optional. subject of the email. Otherwise default email subject is used
            [email_preface]: optional. preface of the email. Otherwise default email preface is used
            [email_ending]: optional. preface of the email. Otherwise default email preface is used

help        show instructions and list of options
"""
