import boto3

s3_client = boto3.client("s3")


def get_bucket(context):
    env = context.env
    workspace = context.workspace
    s3_bucket = "nhse-uec-sm-domain-test-bucket-" + env + workspace
    return s3_bucket


def get_object(context, filename):
    bucket = get_bucket(context)
    response = s3_client.get_object(
        Bucket=bucket,
        Key=filename,
    )
    file_data = response["Body"].read().decode("utf-8")
    return file_data


def download_object(context, filepath, filename):
    bucket = get_bucket(context)
    s3_client.download_file(Bucket=bucket, Key=filename, Filename=filepath)


def put_object(context, filepath, file_name):
    bucket = get_bucket(context)
    s3_client.upload_file(Filename=filepath, Bucket=bucket, Key=file_name)


def delete_object(context, filename):
    bucket = get_bucket(context)
    s3_client.delete_object(Bucket=bucket, Key=filename)
