import os
from uuid import uuid4
import boto3
import logging
from botocore.exceptions import ClientError
from cfn_resource_provider import ResourceProvider

logger = logging.getLogger()


#
# The request schema defining the Resource Properties
#
request_schema = {
    "type": "object",
    "required": ["FileSystemId", "ThroughputMode"],
    "properties": {
        "FileSystemId": {
            "type": "string",
            "description": "to set the throughput mode of"
        },
        "ThroughputMode": {
            "type": "string",
            "description": "to apply",
            "enum": ["provisioned", "bursting"]
        },
        "ProvisionedThroughputInMibps": {
            "type": "number",
            "description": "to provision"
        }
    }
}


class EfsProvisionedThroughputProvider(ResourceProvider):

    def __init__(self):
        super(ResourceProvider, self).__init__()
        self.request_schema = request_schema
        self.efs = boto3.client('efs')

    def convert_property_types(self):
        try:
            if 'ProvisionedThroughputInMibps' in self.properties:
                self.properties['ProvisionedThroughputInMibps'] = float(self.properties['ProvisionedThroughputInMibps'])
        except:
            logger.debug('ProvisionedThroughputInMibps is not a float')

    def is_valid_request(self):
        result = super(EfsProvisionedThroughputProvider, self).is_valid_request()
        if result and self.mode == 'provisioned' and 'ProvisionedThroughputInMibps' not in self.properties:
            self.fail('missing ProvisionedThroughputInMibps')
            return False

        return True

    @property
    def file_system_id(self):
        return self.get('FileSystemId')

    @property
    def provisioned_mibs(self):
        return self.get('ProvisionedThroughputInMibps', None)

    @property
    def mode(self):
        return self.get('ThroughputMode', None)

    def update_file_system(self):
        try:
            args = {'FileSystemId': self.file_system_id, 'ThroughputMode': self.mode}
            if self.mode == 'provisioned':
                args['ProvisionedThroughputInMibps'] = self.provisioned_mibs
            response = self.efs.update_file_system(**args)
        except ClientError as e:
            self.fail(e.response['Error']['Message'])

    def create(self):
        self.update_file_system()
        self.physical_resource_id = 'prd-{}'.format(uuid4()) if self.status == 'SUCCESS' else 'failed-to-create'
        print (self.response)

    def update(self):
        self.update_file_system()

    def delete(self):
        pass


provider = EfsProvisionedThroughputProvider()


def handler(request, context):
    return provider.handle(request, context)
