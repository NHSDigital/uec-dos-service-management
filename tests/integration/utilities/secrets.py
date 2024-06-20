import boto3
import base64
from botocore.exceptions import ClientError
import logging


class SECRETS:
    def __init__(self):
        self.secrets_client = boto3.client("secretsmanager")

    def get_secret_value(self, secret_store_name, env):
        logger = logging.getLogger("cm-logger")
        try:
            response = self.secrets_client.get_secret_value(SecretId=secret_store_name)
        except ClientError as e:
            logger.exception(env, "Error retrieving secrets: {}".format(e))
            raise e
        except Exception as e:
            logger.exception(env, "Error retrieving secrets: {}".format(e))
            raise e
        else:
            if "SecretString" in response:
                return response["SecretString"]
            else:
                return base64.b64decode(response["SecretBinary"])
