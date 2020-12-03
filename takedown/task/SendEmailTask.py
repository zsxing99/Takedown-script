"""
FindRepoTask
--------------------------------------------------
Run tool to send emails based on previous output
    1. Run tool to send takedown email
"""

from .BaseTask import BaseTask
import sys
import smtplib
import ssl
import getpass


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
                    server.close()
                return False
        # no encryption
        else:
            try:
                server = smtplib.SMTP(domain, port)
            except Exception as e:
                print("Connection to SMTP service failed", file=sys.stderr)
                print(str(e), file=sys.stderr)
                if server:
                    server.close()
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
                server.close()
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

        for user_key in inputs:
            user = inputs[user_key]
            print("Try sending emails to {}...".format(user_key))
            owner_emails = user["owner__email"]
            repos = user["repos"]

            # construct message
            num_of_repos = 0
            msg = "Hello {},\n".format(user_key)
            # more TODO here

            if num_of_repos == 0:
                print("No repo identified as to send message.")
                continue
            for email in owner_emails:
                if not email:
                    continue
                try:
                    self.email_client.sendmail(self.username, email, msg)
                    print("Message sent to {}".format(email))
                except Exception as e:
                    print("Error occurs when sending emails to {}".format(email), file=sys.stderr)
                    print(str(e), file=sys.stderr)

            # update outputs

        return {}
