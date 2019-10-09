import logging
from pywren_ibm_cloud.storage.utils import StorageNoSuchKeyError
from azure.storage.blob import BlockBlobService
from azure.common import AzureMissingResourceHttpError

logging.getLogger('azure.storage.common.storageclient').setLevel(logging.CRITICAL)
logger = logging.getLogger(__name__)


class AzureBlobStorageBackend:

    def __init__(self, azure_blob_config):
        self.blob_client = BlockBlobService(account_name=azure_blob_config['account_name'],
                                            account_key=azure_blob_config['account_key'])

    def get_client(self):
        """
        Get ibm_boto3 client.
        :return: ibm_boto3 client
        """
        return self.blob_client

    def put_object(self, bucket_name, key, data):
        """
        Put an object in COS. Override the object if the key already exists.
        :param key: key of the object.
        :param data: data of the object
        :type data: str/bytes
        :return: None
        """
        if isinstance(data, str):
            data = data.encode()
        self.blob_client.create_blob_from_bytes(bucket_name, key, data)

    def get_object(self, bucket_name, key, stream=False, extra_get_args={}):
        """
        Get object from COS with a key. Throws StorageNoSuchKeyError if the given key does not exist.
        :param key: key of the object
        :return: Data of the object
        :rtype: str/bytes
        """
        if 'Range' in extra_get_args:
            bytes_range = extra_get_args.pop('Range')[6:]
            bytes_range = bytes_range.split('-')
            extra_get_args['start_range'] = int(bytes_range[0])
            extra_get_args['end_range'] = int(bytes_range[1])
        try:
            if stream:
                data = self.blob_client.get_blob_to_stream(bucket_name, key, **extra_get_args)
            else:
                data = self.blob_client.get_blob_to_bytes(bucket_name, key, **extra_get_args)
            return data.content
        except AzureMissingResourceHttpError:
            raise StorageNoSuchKeyError(bucket_name, key)


    def head_object(self, bucket_name, key):
        """
        Head object from COS with a key. Throws StorageNoSuchKeyError if the given key does not exist.
        :param key: key of the object
        :return: Data of the object
        :rtype: str/bytes
        """
        blob = self.blob_client.get_blob_properties(bucket_name, key)

        ### adapted to match ibm_cos method
        metadata = {}
        metadata['content-length'] = blob.properties.content_length
        return metadata

    def delete_object(self, bucket_name, key):
        """
        Delete an object from storage.
        :param bucket: bucket name
        :param key: data key
        """
        self.blob_client.delete_blob(bucket_name, key)

    def delete_objects(self, bucket_name, key_list):
        """
        Delete a list of objects from storage.
        :param bucket: bucket name
        :param key_list: list of keys
        """
        for key in key_list:
            self.delete_object(bucket_name, key)

    def head_bucket(self, bucket_name):
        """
        Head bucket from COS with a name. Throws StorageNoSuchKeyError if the given bucket does not exist.
        :param bucket_name: name of the bucket
        """
        try:
           self.blob_client.get_container_metadata(bucket_name)
           return True
        except Exception:
           raise StorageNoSuchKeyError(bucket_name, '')

    def bucket_exists(self, bucket_name):
        """
        Head bucket from COS with a name. Throws StorageNoSuchKeyError if the given bucket does not exist.
        :param bucket_name: name of the bucket
        :return: Data of the object
        :rtype: str/bytes
        """
        try:
           self.blob_client.get_container_metadata(bucket_name)
           return True
        except Exception:
           raise StorageNoSuchKeyError(bucket_name, '')

    def list_objects(self, bucket_name, prefix=None):
        """
        Return a list of objects for the given bucket and prefix.
        :param bucket_name: Name of the bucket.
        :param prefix: Prefix to filter object names.
        :return: List of objects in bucket that match the given prefix.
        :rtype: list of str
        """
        ### adapted to match ibm_cos method
        try:
            blobs = self.blob_client.list_blobs(bucket_name, prefix)
            mod_list = []
            for blob in blobs:
                mod_list.append({
                    'Key' : blob.name,
                    'Size' : blob.properties.content_length
                })
        except Exception:
            StorageNoSuchKeyError(bucket_name, '' if prefix is None else prefix)

    def list_keys(self, bucket_name, prefix=None):
        """
        Return a list of keys for the given prefix.
        :param prefix: Prefix to filter object names.
        :return: List of keys in bucket that match the given prefix.
        :rtype: list of str
        """
        try:
            keys = [key for key in self.blob_client.list_blob_names(bucket_name, prefix).items]
        except Exception:
            StorageNoSuchKeyError(bucket_name, '' if prefix is None else prefix)
        return keys