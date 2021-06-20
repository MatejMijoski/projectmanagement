from io import BufferedReader
import boto3
from botocore.config import Config

from FilesApp.models import Files
from FilesApp.serializers import FileSerializer
from projectmanagement import settings
from projectmanagement.exceptions import CustomException


def project_file_size(files):
    size = 0
    for file in files:
        size += getattr(file, "size")
    return size


class NonCloseableBufferedReader(BufferedReader):
    def close(self):
        self.flush()


def check_file_if_exists(file_name):
    s3 = boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    )
    content = s3.list_objects_v2(
        Bucket=settings.AWS_STORAGE_BUCKET_NAME, Prefix=file_name
    )
    if content.get("KeyCount") == 0:
        return True
    else:
        return False


def upload_file(data, file_path):
    file = data.pop("file")
    if file.size > 2000000:
        return 400, {
            "error": "The maximum file size is 2 MB. The current file is "
            + "{:.0f}".format(file.size / 1000000)
            + " MB"
        }

    if check_file_if_exists(file_path):  # avoid overwriting existing file
        buffer = NonCloseableBufferedReader(file)
        try:
            s3 = boto3.resource(
                "s3",
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            )
            bucket = s3.Bucket(settings.AWS_STORAGE_BUCKET_NAME)
            bucket.upload_fileobj(buffer, file_path)
        except ValueError as e:
            raise CustomException(
                400, "There was an error with the request. Please try again later.", e
            )
        buffer.detach()
        assert not file.closed
        data["size"] = file.size
        data["path"] = file_path
        file_obj = Files.objects.create(**data)
        return 200, FileSerializer(file_obj).data
    return 400, {"error": "A file with that name already exists for this project."}


def download_file(file_path):
    my_config = Config(
        region_name="us-east-2",
        signature_version="s3v4",
        retries={"max_attempts": 10, "mode": "standard"},
        s3={"addressing_style": "path"},
    )
    s3 = boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        config=my_config,
    )
    return s3.generate_presigned_url(
        "get_object",
        Params={"Bucket": settings.AWS_STORAGE_BUCKET_NAME, "Key": str(file_path)},
        ExpiresIn=1000,
    )


def delete_s3_file(key):
    s3 = boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    )
    return s3.delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=key)
