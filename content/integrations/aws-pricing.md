# AWS Pricing

MTO supports AWS pricing model via the `integrationConfig.components.showbackOpts.cloudIntegrationSecretRef` field. Following 3 types of pricing are supported:

- [`AWS Standard Pricing`](#aws-standard-pricing)
- [`AWS Spot Instance Datafeed`](#aws-spot-instance-pricing)

## AWS Standard Pricing

OpenCost will automatically read the node information `node.spec.providerID` to determine the cloud service provider (CSP) in use. If it detects the CSP is AWS, it will attempt to pull the AWS on-demand pricing from the configured public API URL with no further configuration required.

OpenCost will request pricing data from the `us-east-1` region for your `node_region` using the template:

```url
https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonEC2/current/${node_region}/index.json
```

## AWS Spot Instance Pricing

To enable the AWS Spot Instance pricing, subscribe to AWS Spot Instance Data Feed with the following command

```sh
aws ec2 create-spot-datafeed-subscription \
    --bucket <BUCKET_NAME> \
    [--prefix <BUCKET_PREFIX>]
```

- `<BUCKET_NAME>` — Name of the bucket Amazon S3 bucket to store the data feed files
- `<BUCKET_PREFIX>` — Optional prefix directory in which data feed files will be stored

### Amazon S3 bucket requirements

When you subscribe to the data feed, you must specify an Amazon S3 bucket to store the data feed files.

Before you choose an Amazon S3 bucket for the data feed, consider the following:

- You must have `FULL_CONTROL` permission to the bucket. If you're the bucket owner, you have this permission by default. Otherwise, the bucket owner must grant your AWS account this permission.

- When you subscribe to a data feed, these permissions are used to update the bucket ACL to give the AWS data feed account `FULL_CONTROL` permission. The AWS data feed account writes data feed files to the bucket. If your account doesn't have the required permissions, the data feed files cannot be written to the bucket. For more information, see Logs sent to Amazon S3 in the Amazon CloudWatch Logs User Guide.

- If you update the ACL and remove the permissions for the AWS data feed account, the data feed files cannot be written to the bucket. You must resubscribe to the data feed to receive the data feed files.

- Each data feed file has its own ACL (separate from the ACL for the bucket). The bucket owner has `FULL_CONTROL` permission to the data files. The AWS data feed account has read and write permissions.

- If you delete your data feed subscription, Amazon EC2 doesn't remove the read and write permissions for the AWS data feed account on either the bucket or the data files. You must remove these permissions yourself.

- If you encrypt your Amazon S3 bucket using server-side encryption with an AWS KMS key stored in AWS Key Management Service (SSE-KMS), you must use a customer managed key. For more information, see Amazon S3 bucket server-side encryption in the Amazon CloudWatch Logs User Guide.

### Configure an IAM Policy

- Create a user or role for OpenCost with access to the spot feed bucket. Attach the policy below to the role/user and replace `<BUCKET_NAME>` with your spot bucket name

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Action": [
                "s3:ListAllMyBuckets",
                "s3:ListBucket",
                "s3:HeadBucket",
                "s3:HeadObject",
                "s3:List*",
                "s3:Get*"
            ],
            "Resource": [
                "arn:aws:s3:::<BUCKET_NAME>"
            ],
            "Effect": "Allow",
            "Sid": "SpotDataAccess"
        }
    ]
}
```

### Option 1: Service Keys

Generate Access Keys with following steps

1. Navigate to the AWS IAM Console.
1. Select Access Management > Users from the left navigation.
1. Find the OpenCost User and select Security credentials > Create access key.
1. Follow along to receive the Access Key ID and Secret Access Key (AWS will not provide you the Secret Access Key in the future, so make sure you save this value).

Create a `service-key.json` and replace the values with the user access keys

```json
{
  "aws_access_key_id": "<ACCESS_KEY_ID>",
  "aws_secret_access_key": "<SECRET_ACCESS_KEY>"
}
```

Create a Kubernetes secret with the following command

```sh
kubectl create secret generic <SECRET_NAME> --from-file=service-key.json --namespace multi-tenant-operator
```

!!! note
    When managing the service account key as a Kubernetes secret, the secret must reference the service account key JSON file, and that file must be named `service-key.json`.

The data feed will provide specific pricing information about any Spot instances in your account on an hourly basis. After setting this up, the bucket information can be provided through options in the IntegrationConfig via `integrationConfig.components.showbackOpts.custom` object.

- `awsSpotDataBucket` - The name of the S3 bucket Spot Instance Data Feed is publishing to.
- `awsSpotDataRegion` - The region configured for Spot Instance Data Feed
- `awsSpotDataPrefix` - The prefix (if any) configured for Spot Instance Data Feed
- `projectID` - The AWS Account ID
- `<SECRET_NAME>` - Name of the service key secret created in previous step

Example:

```yaml
components:
  showback: true # should be enabled
  showbackOpts:
    custom:
      provider: aws
      description: "AWS Provider Configuration. Provides default values used if instance type or spot information is not found."
      CPU: "0.031611"
      spotCPU: "0.006655"
      RAM: "0.004237"
      GPU: "0.95"
      spotRAM: "0.000892"
      storage: "0.000138888889"
      zoneNetworkEgress: "0.01"
      regionNetworkEgress: "0.01"
      internetNetworkEgress: "0.143"
      spotLabel: "kops.k8s.io/instancegroup"
      spotLabelValue: "spotinstance-nodes"
      awsSpotDataRegion: "us-east-2"
      awsSpotDataBucket: "my-spot-bucket"
      awsSpotDataPrefix: "spot_pricing_prefix"
      projectID: "012345678901"

    cloudPricingSecretRef:
      name: <SECRET_NAME>
      namespace: multi-tenant-operator
```

### Option 2: IRSA (IAM Roles for Service Accounts)

After creating the role and policy, attach the role ARN as an annotation to the opencost gateway account via following command

```sh
kubectl annotate serviceaccounts -n multi-tenant-operator tenant-operator-opencost-gateway eks.amazonaws.com/role-arn=<ROLE_ARN>
```

Apply the IntegrationConfig with current spot bucket data feed information

Example:

```yaml
components:
  showback: true # should be enabled
  showbackOpts:
    custom:
      provider: aws
      description: "AWS Provider Configuration. Provides default values used if instance type or spot information is not found."
      CPU: "0.031611"
      spotCPU: "0.006655"
      RAM: "0.004237"
      GPU: "0.95"
      spotRAM: "0.000892"
      storage: "0.000138888889"
      zoneNetworkEgress: "0.01"
      regionNetworkEgress: "0.01"
      internetNetworkEgress: "0.143"
      spotLabel: "kops.k8s.io/instancegroup"
      spotLabelValue: "spotinstance-nodes"
      awsSpotDataRegion: "us-east-2"
      awsSpotDataBucket: "my-spot-bucket"
      awsSpotDataPrefix: "spot_pricing_prefix"
      projectID: "012345678901"
```

## References

For more information, refer to the following resources

- [`OpenCost documentation`](https://www.opencost.io/docs/configuration/aws)
- [`Kubecost documentation`](https://docs.kubecost.com/install-and-configure/install/cloud-integration/aws-cloud-integrations)
- [`Assign IAM roles to Kubernetes service accounts`](https://docs.aws.amazon.com/eks/latest/userguide/associate-service-account-role.html)
- [`Track your Spot Instance costs using the Spot Instance data feed`](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/spot-data-feeds.html)
- [`Manage access keys from IAM users`](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html)
