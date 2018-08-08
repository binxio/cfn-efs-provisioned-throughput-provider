# AWS EFS Provisioned throughput Provider
A CloudFormation custom resource provider for enabling provisioned throughput for EFS through CloudFormation.

On [July the 12th, 2018] Amazon announced the [availability of Provisioned throughput for EFS volumes](https://aws.amazon.com/about-aws/whats-new/2018/07/amazon-efs-now-supports-provisioned-throughput/). This was a long awaited and valuable feature for anybody using EFS.

Unfortunately, this could only be enable through the Console or the API, not via CloudFormation. As we use only allow changes through code, we need the CloudFormation interface over the Console.  The Console is nice for playing around, not for engineering solutions on AWS.

On August the 8th, we discovered that Amazon added the properties `ThroughputMode` and `ProvisionedThroughputInMibs` on CloudFormation resources of type [AWS::EFS::FileSystem](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-efs-filesystem.html), making this provider obsolete!
