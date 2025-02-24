# AWS Pricing Model

MTO supports AWS pricing model via the `integrationConfig.components.showbackOpts.cloudIntegrationSecretRef` field. Following 3 types of pricing are supported:

- [Cost Allocation](https://opencost.io/docs/configuration/aws#cost-allocation)
- [AWS Cloud Costs](https://opencost.io/docs/configuration/aws#aws-cloud-costs)
- [AWS Spot Instance Datafeed](https://opencost.io/docs/configuration/aws#aws-spot-instance-data-feed)

## Cost Allocation

OpenCost will automatically read the node information `node.spec.providerID` to determine the cloud service provider (CSP) in use. If it detects the CSP is AWS, it will attempt to pull the AWS on-demand pricing from the configured public API URL with no further configuration required.

OpenCost will request pricing data from the `us-east-1` region for your `node_region` using the template:

```
https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonEC2/current/${node_region}/index.json
```

## AWS Cloud Costs

Following AWS services that are involved in the process of integration.

**Cost and Usage Report**: AWS report which tracks cloud spending and writes to an Amazon Simple Storage Service (Amazon S3) bucket for ingestion and long term historical data. The CUR is originally formatted as a CSV, but when integrated with Athena, is converted to Parquet format.

**Amazon Athena**: Analytics service which queries the CUR S3 bucket for your AWS cloud spending, then outputs data to a separate S3 bucket. Opencost uses Athena to query for the bill data to perform reconciliation. Athena is technically optional for AWS cloud integration, but as a result, Opencost will only provide unreconciled costs (on-demand public rates).

**S3 bucket**: Cloud object storage tool which both CURs and Athena output cost data to. Opencost needs access to these buckets in order to read that data.


### Step 1: Setting up a CUR

Follow the [AWS documentation](https://docs.aws.amazon.com/cur/latest/userguide/cur-create.html) to create a CUR export using the settings below.

- For time granularity, select Daily.
- Under 'Additional content', select the Enable resource IDs checkbox.
- Under 'Report data integration' select the Amazon Athena checkbox.
- Select the checkbox to enable the JSON IAM policy to be applied to your bucket.

AWS may take up to 24 hours to publish data. Wait until this is complete before continuing to the next step.

### Step 2: Setting up Athena

As part of the CUR creation process, Amazon also creates a CloudFormation template that is used to create the Athena integration. It is created in the CUR S3 bucket, listed in the Objects tab in the path `s3-path-prefix/cur-name` and typically has the filename `crawler-cfn.yml`. This `.yml` is your necessary CloudFormation template. You will need it in order to complete the CUR Athena integration. See the AWS doc [Setting up Athena using AWS CloudFormation templates](https://docs.aws.amazon.com/cur/latest/userguide/use-athena-cf.html) to complete your Athena setup.

Once Athena is set up with the CUR, you will need to create a new S3 bucket for Athena query results.

- Navigate to the S3 Management Console.
- Select Create bucket. The Create Bucket page opens.
- Use the same region used for the CUR bucket and pick a name that follows the format aws-athena-query-results-.
- Select Create bucket at the bottom of the page.
- Navigate to the Amazon Athena dashboard.
- Select Settings, then select Manage. The Manage settings window opens.
- Set Location of query result to the S3 bucket you just created, which will look like `s3://aws-athena-query-results...`, then select Save.

### Step 3: Setting up IAM permissions

Attach the following policy to the same role or user. Use a user if you intend to integrate via ServiceKey, and a role if via IAM annotation. The SpotDataAccess policy statement is optional if the Spot data feed is configured

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AthenaAccess",
      "Effect": "Allow",
      "Action": ["athena:*"],
      "Resource": ["*"]
    },
    {
      "Sid": "ReadAccessToAthenaCurDataViaGlue",
      "Effect": "Allow",
      "Action": [
        "glue:GetDatabase*",
        "glue:GetTable*",
        "glue:GetPartition*",
        "glue:GetUserDefinedFunction",
        "glue:BatchGetPartition"
      ],
      "Resource": [
        "arn:aws:glue:*:*:catalog",
        "arn:aws:glue:*:*:database/athenacurcfn*",
        "arn:aws:glue:*:*:table/athenacurcfn*/*"
      ]
    },
    {
      "Sid": "AthenaQueryResultsOutput",
      "Effect": "Allow",
      "Action": [
        "s3:GetBucketLocation",
        "s3:GetObject",
        "s3:ListBucket",
        "s3:ListBucketMultipartUploads",
        "s3:ListMultipartUploadParts",
        "s3:AbortMultipartUpload",
        "s3:CreateBucket",
        "s3:PutObject"
      ],
      "Resource": ["arn:aws:s3:::aws-athena-query-results-*"]
    },
    {
      "Sid": "S3ReadAccessToAwsBillingData",
      "Effect": "Allow",
      "Action": ["s3:Get*", "s3:List*"],
      "Resource": ["arn:aws:s3:::${AthenaCURBucket}*"]
    },
    {
      "Sid": "SpotDataAccess",
      "Effect": "Allow",
      "Action": [
        "s3:ListAllMyBuckets",
        "s3:ListBucket",
        "s3:HeadBucket",
        "s3:HeadObject",
        "s3:List*",
        "s3:Get*"
      ],
      "Resource": "arn:aws:s3:::${SpotDataFeedBucketName}*"
    }
  ]
}
```

### Step 4: Generate Access Keys

1. Navigate to the AWS IAM Console.
1. select Access Management > Users from the left navigation. 
1. Find the Kubecost User and select Security credentials > Create access key. 
1. Follow along to receive the Access Key ID and Secret Access Key (AWS will not provide you the Secret Access Key in the future, so make sure you save this value). 

### Step 5: Create cloud integration secret

Set these values into the AWS array in the `cloud-integration.json`:

- `<ACCESS_KEY_ID>` is the ID of the Access Key created in the previous step.
- `<ACCESS_KEY_SECRET>` is the secret of the Access Key created in the
- `<ATHENA_BUCKET_NAME>` is the S3 bucket storing Athena query results which OpenCost has permission to access. The name of the bucket should match `s3://aws-athena-query-results-*`, so the IAM roles defined above will automatically allow access to it. The bucket can have a canned ACL set to Private or other permissions as needed.
- `<ATHENA_REGION>` is the AWS region Athena is running in
- `<ATHENA_DATABASE>` is the name of the database created by the Athena setup. The Athena database name is available as the value (physical id) of `AWSCURDatabase` in the `CloudFormation` stack created in [step 2](#step-2-setting-up-athena).
- `<ATHENA_TABLE>` is the name of the table created by the Athena setup The table name is typically the database name with the leading `athenacurcfn_` removed (but is not available as a CloudFormation stack resource).
- `<ATHENA_WORKGROUP>` is the workgroup assigned to be used with Athena. Default value is Primary.
- `<ATHENA_PROJECT_ID>` is the AWS AccountID where the Athena CUR is. For example: 530337586277.
- `<MASTER_PAYER_ARN>` is an optional value which should be set if you are using a multi-account billing set-up and are not accessing Athena through the primary account. It should be set to the ARN of the role in the management (formerly master payer) account, for example: `arn:aws:iam::530337586275:role/OpenCostRole`.

```json
{
    "aws": [
        {
            "serviceKeyName": "<ACCESS_KEY_ID>",
            "serviceKeySecret":"<ACCESS_KEY_SECRET>",
            "athenaBucketName": "s3://ATHENA_RESULTS_BUCKET_NAME",
            "athenaRegion": "ATHENA_REGION",
            "athenaDatabase": "ATHENA_DATABASE",
            "athenaTable": "ATHENA_TABLE",
            "athenaWorkgroup": "ATHENA_WORKGROUP",
            "projectID": "ATHENA_PROJECT_ID",
            "masterPayerARN": "PAYER_ACCOUNT_ROLE_ARN"
        }
    ]
}
```

Create a Kubernetes secret using following command

```sh
kubectl create secret generic <SECRET_NAME> --from-file=cloud-integration.json -n multi-tenant-operator
```

### Step 5: Update the Integration Config

Provide the secret name MTO's Integration Config

```yaml
components:
  showback: true # should be enabled
  customPricingEnabled: false # should be set to false
  showbackOpts:
    cloudPricingSecretRef:
      name: <SECRET_NAME>
      namespace: multi-tenant-operator
```

## AWS Spot Instance Data Feed

First, to enable the AWS Spot data feed, follow AWS [Spot Instance Data Feed](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/spot-data-feeds.html) doc.

- Set up Spot Instance Data Feed.
- Create a user or role for OpenCost with access to the spot feed bucket. Attach the policy below to the role/user and replace CHANGE-ME with your spot bucket name

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
                "arn:aws:s3:::CHANGE-ME"
            ],
            "Effect": "Allow",
            "Sid": "SpotDataAccess"
        }
    ]
}
```

### Option 1: Service Keys

Create a `service-key.json` and replace the values with the keys created in [step 4](#step-4-generate-access-keys)

```json
{
  "aws_access_key_id": "<ACCESS_KEY_ID>",
  "aws_secret_access_key": "<SECRET_ACCESS_KEY>"
}
```

Create a Kubernetes secret

```sh
$ kubectl create secret generic <SECRET_NAME> --from-file=service-key.json --namespace multi-tenant-operator
```

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
    customPricingEnabled: true
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

After creating the role and policy, attach the role as an annotation on the service account via `integrationConfig.components.showbackOpts.opencostServiceRoleArn` field

Example:

```yaml
components:
  showback: true # should be enabled
  showbackOpts:
    customPricingEnabled: true
    # This role will be assigned tenant-operator-opencost-gateway service account
    opencostServiceRoleArn: arn:aws:iam::123456789012:role/S3Access
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

For more information, refer to the 
- [OpenCost documentation](https://www.opencost.io/docs/configuration/aws).
- [Kubecost documentation](https://docs.kubecost.com/install-and-configure/install/cloud-integration/aws-cloud-integrations)
- [Creating Cost and Usage Reports](https://docs.aws.amazon.com/cur/latest/userguide/creating-cur.html)
- [Setting up Athena using AWS CloudFormation templates](https://docs.aws.amazon.com/cur/latest/userguide/use-athena-cf.html)
- [Assign IAM roles to Kubernetes service accounts](https://docs.aws.amazon.com/eks/latest/userguide/associate-service-account-role.html)