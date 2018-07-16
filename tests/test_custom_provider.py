import boto3
import uuid
from time import sleep

from provider import handler

efs = boto3.client('efs')


def get_throughput_mode(file_system_id):
    available = False
    while not available:
        response = efs.describe_file_systems(FileSystemId=file_system_id)
        fs = response['FileSystems'][0]
        available = fs['LifeCycleState'] == 'available'
        if not available:
            sleep(10)

    return fs['ThroughputMode'], fs['ProvisionedThroughputInMibps'] if 'ProvisionedThroughputInMibps' in fs else None


def test_invalid_input():
    name = 'test-%s' % uuid.uuid4()

    request = Request('Create', 'fs-doesnotexist', 'provisioned', None)
    request['ResourceProperties']['ProvisionedThroughputInMibps'] = 1024.0

    response = handler(request, {})
    assert response['Status'] == 'FAILED', response['Reason']


def test_invalid_mibps():
    request = Request('Create', 'fs-doesnotexist', 'provisioned', 'badshit')
    response = handler(request, {})
    assert response['Status'] == 'FAILED', response['Reason']


def test_create():
    name = 'test-%s' % uuid.uuid4()
    fs = None

    try:
        fs_response = efs.create_file_system(CreationToken=name)
        fs = fs_response['FileSystemId']
        mode, mibs = get_throughput_mode(fs)
        assert mode == 'bursting'

        request = Request('Create', fs, 'provisioned', 756.0)
        response = handler(request, {})
        assert response['Status'] == 'SUCCESS', response['Reason']
        assert 'PhysicalResourceId' in response
        mode, mibs = get_throughput_mode(fs)
        assert mode == 'provisioned'
        assert mibs == 756.0

        sleep(10)
        physical_resource_id = response['PhysicalResourceId']
        request = Request('Update', fs, 'provisioned', 1024.0, physical_resource_id)
        response = handler(request, {})
        assert response['Status'] == 'SUCCESS', response['Reason']
        assert 'PhysicalResourceId' in response
        assert response['PhysicalResourceId'] == physical_resource_id
        mode, mibs = get_throughput_mode(fs)
        assert mode == 'provisioned'
        assert mibs == 1024.0

        # delete
        sleep(10)
        request['RequestType'] = 'Delete'
        response = handler(request, {})
        assert response['Status'] == 'SUCCESS', response['Reason']
        mode, mibs = get_throughput_mode(fs)
        assert mode == 'bursting'

    except:
        if fs is not None:
            efs.delete_file_system(FileSystemId=fs)
        raise


class Request(dict):

    def __init__(self, request_type, efs_id, mode, mibs=None, physical_resource_id=None):
        request_id = 'request-%s' % uuid.uuid4()
        self.update({
            'RequestType': request_type,
            'ResponseURL': 'https://httpbin.org/put',
            'StackId': 'arn:aws:cloudformation:us-west-2:EXAMPLE/stack-name/guid',
            'RequestId': request_id,
            'ResourceType': 'Custom::EfsProvisionedThroughput',
            'LogicalResourceId': 'EfsProvisionedThroughput',
            'ResourceProperties': {
                'FileSystemId': efs_id,
                'ThroughputMode': mode
            }})

        self['PhysicalResourceId'] = physical_resource_id if physical_resource_id is not None else 'initial-%s' % str(
            uuid.uuid4())

        if mibs is not None:
            self['ResourceProperties']['ProvisionedThroughputInMibps'] = mibs
