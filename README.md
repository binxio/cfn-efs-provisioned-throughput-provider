# AWS EFS Provisioned throughput Provider
A CloudFormation custom resource provider for enabling provisioned throughput for EFS through CloudFormation.

On [July the 12th, 2018] Amazon announced the [availability of Provisioned throughput for EFS volumes](https://aws.amazon.com/about-aws/whats-new/2018/07/amazon-efs-now-supports-provisioned-throughput/). This was a long awaited and valuable feature for anybody using EFS>

Unfortunately, this can only be enable through the Console or the API, not via CloudFormation. As we use only allow changes through code, we need the
CloudFormation interface over the Console.  The Console is nice for playing around, not for engineering solutions on AWS.

So, I created this temporary custom provider in less than 15 minutes. However it is still a waste: I have to create it, customers will have to install the 
custom provider and add it to their CloudFormation template. When  AWS finally adds native support to CloudFormation, all work has to be undone.

To prevent all this waste, I would like to offer AWS my services to ensure all the CloudFormation is always on-par with the API. any time.

## How do I add provisioned throughput?
It is quite easy: you specify a CloudFormation resource of the type Custom::EfsProvisionedThroughput, as fllows

```yaml
    EfsProvisionedThroughput:
      Type: Custom::EfsProvisionedThroughput
      Properties: 
        FileSystemId: !Ref EFS
        ThroughputMode: provisioned
        ProvisionedThroughputInMibs: 1024.0
        ServiceToken: !Sub 'arn:aws:lambda:${AWS::Region}:${AWS::AccountId}:function:binxio-cfn-efs-provisioned-throughput-provider'
```
After the deployment, the EFS has the provisioned throughput. When the resource is deleted, the throughput mode is restored to 'bursting'

## Installation
To install these custom resources, type:

```sh
aws cloudformation create-stack \
	--capabilities CAPABILITY_IAM \
	--stack-name cfn-efs-provisioned-throughput-provider \
	--template-body file://cloudformation/cfn-resource-provider.yaml

aws cloudformation wait stack-create-complete  --stack-name cfn-efs-provisioned-throughput-provider
```

This CloudFormation template will use our pre-packaged provider from `s3://binxio-public/lambdas/cfn-efs-provisioned-throughput-provider-1.0.0.zip`.


