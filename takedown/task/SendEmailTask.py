"""
FindRepoTask
--------------------------------------------------
Run tool to send emails based on previous output
    1. Run tool to send takedown email
"""

from .BaseTask import BaseTask
import sys
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import ssl
import getpass
import datetime

"""
Default Settings for emails
---------------------------------------------------
MSG:
From: [username | name]
To: [user]
Subject: [subject]

Body:
[preface]
[generated HTML unordered list of repos]
[ending]
---------------------------------------------------
Customizable parameters:
[username]: provided username from required params
[name]: provided name from optional params
[subject]: "GitHub Takedown Result Regarding your Repositories" | provided from optional params
[preface]: "Hello [user],\n\nour program recently detected following one of more repositories related to this email address violate
            copyright information. Please remove them or turn them into private repositories." 
            | provided from optional params
[ending]: "Thanks,\n [username | name]"
"""

EMAIL_DEFAULT_SUBJECT = "GitHub Takedown Result Regarding your Repositories"
EMAIL_DEFAULT_PREFACE = "<p>Hello {},<br><br>Our program recently detected following one of more repositories " \
                        "related to this email address violate copyright information. Please remove them " \
                        "or turn them into private repositories.</p>"
EMAIL_DEFAULT_ENDING = "<p>Thanks,<br>{}</p>"


class SendEmailTask(BaseTask):

    def __init__(self, **settings):
        super().__init__(**settings)
        self.__dict__.update(settings)
        self.email_client = None
        self.username = None
        self.required_params = None
        self.optional_params = None
        self.pass_prepare = False

    def prepare(self, required_params: dict, optional_params: dict, **kwargs):
        if "domain" not in required_params or "port" not in required_params or "inputs" not in required_params:
            print("Error in send task preparation: missing critical values", file=sys.stderr)
            return self

        self.required_params = required_params
        self.optional_params = optional_params
        self.pass_prepare = True
        return self

    def connect_smtp_server(self):
        domain = self.required_params.get("domain")
        port = self.required_params.get("port")
        server = None
        secure_method = self.optional_params.get("secure_method")

        # encryption if requested
        if secure_method:
            try:
                if secure_method.lower() == "ssl":
                    server = smtplib.SMTP_SSL(domain, port, context=ssl.create_default_context())
                elif secure_method.lower() == "tls":
                    server = smtplib.SMTP(domain, port)
                    server.starttls()
            except Exception as e:
                print("Secure method establishment failed", file=sys.stderr)
                print(str(e), file=sys.stderr)
                if server:
                    server.quit()
                return False
        # no encryption
        else:
            try:
                server = smtplib.SMTP(domain, port)
            except Exception as e:
                print("Connection to SMTP service failed", file=sys.stderr)
                print(str(e), file=sys.stderr)
                if server:
                    server.quit()
                return False

        self.email_client = server
        # try to authenticate
        username = self.optional_params.get("username", None)
        password = self.optional_params.get("password", None)
        if not username:
            username = input("No username entered, please enter your email username:")
        if not password:
            password = getpass.getpass(prompt="No password entered, please enter your email password:")

        self.username = username

        # try to login
        try:
            self.email_client.login(username, password)
        except Exception as e:
            print("SMTP login failed, check error details", file=sys.stderr)
            print(str(e), file=sys.stderr)
            if server:
                server.quit()
                return False

        return True

    def execute(self, **kwargs):
        print("Starting task execution...")
        if not self.pass_prepare:
            print("Preparation failed. Cannot start execution", file=sys.stderr)
            return None

        if not self.connect_smtp_server():
            print("Connection failed. Task abort", file=sys.stderr)
            return None
        else:
            print("Connection established.")

        # sending emails
        inputs = self.required_params.get("inputs", None)
        if not inputs:
            print("No inputs provided. Task abort", file=sys.stderr)
            return None

        tags = self.optional_params.get("tags", None)
        # turn tags into lower case for better match
        if tags:
            tags = list(map(lambda x: x.lower(), tags))
        name = self.optional_params.get("name", self.username)
        subject = self.optional_params.get("subject", EMAIL_DEFAULT_SUBJECT)
        preface = self.optional_params.get("preface", EMAIL_DEFAULT_PREFACE)
        ending = self.optional_params.get("ending", EMAIL_DEFAULT_ENDING)

        for user_key in inputs:
            user = inputs[user_key]
            print("Try sending emails to {}...".format(user_key))
            owner_emails = user["owner__email"]
            repos = user["repos"]

            # construct message
            num_of_repos = 0
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = name
            msg['To'] = user_key

            html = "<html>{}<ul>{}</ul>{}</html>"
            repo_list = []
            for repo_name in repos:
                repo = repos[repo_name]
                if tags is not None and repo["status"].lower() not in tags:
                    continue
                repo_list.append("<li><a href='{}'>{}</a></li>".format(repo["repo__html_url"], repo["repo__name"]))
                # update repo status
                repo["history"].append({
                    "status": repo["status"],
                    "date": repo["date"]
                })
                repo["status"] = "Waiting"
                repo["date"] = datetime.datetime.now()

                num_of_repos += 1

            if num_of_repos == 0:
                print("No repo identified as to send message for this target. Skipped")
                continue

            msg.attach(MIMEText(html.format(preface.format(user_key), "".join(repo_list), ending.format(name)), 'html'))

            owner_emails = list(filter(lambda x: x is not None, owner_emails))
            if len(owner_emails) == 0:
                print("No emails associated with this record. Skipped")
                continue
            failed_sent = None
            try:
                failed_sent = self.email_client.sendmail(self.username, owner_emails, msg.as_string())
                for email in failed_sent:
                    print("Message sent to {} failed, because {}".format(email, str(failed_sent[email])))
            except Exception as e:
                print("Error occurs when sending emails to {}".format(",".join(owner_emails)), file=sys.stderr)
                print(str(e), file=sys.stderr)

        # update outputs
        final_result = {
            "results": []
        }
        for user in inputs.values():
            repos = user.pop("repos")
            final_result["results"].append(
                {
                    **user,
                    "repos": [
                        {**repo_info} for repo_info in repos.values()
                    ]
                }
            )

        return final_result

