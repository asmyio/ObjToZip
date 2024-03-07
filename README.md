# ObjToZip

This is an AWS Lambda function that gets triggered by an AWS S3 Bucket event; when new objects are being uploaded, the function gets triggered where it compresses the uploaded object into zip file, and deletes the original object to save space in the AWS S3 Bucket.

## Table of Contents
- [ObjToZip](#objtozip)
  - [Table of Contents](#table-of-contents)
  - [Requirements](#requirements)
  - [Installation](#installation)
    - [Step 1: Create an IAM especially for AWS SAM](#step-1-create-an-iam-especially-for-aws-sam)
    - [Step 2: Configure AWS](#step-2-configure-aws)
    - [Step 3: Configure AWS SAM](#step-3-configure-aws-sam)
  - [Usage](#usage)
    - [AWS Console](#aws-console)
  - [Uninstall](#uninstall)
  - [Architecture](#architecture)
    - [AWS Lambda \& S3 Bucket](#aws-lambda--s3-bucket)
    - [AWS SAM \& Cloudformation](#aws-sam--cloudformation)
      - [samconfig.toml](#samconfigtoml)
      - [template.yaml](#templateyaml)
  - [Development](#development)
    - [Setting Up Virtual Environment](#setting-up-virtual-environment)
      - [A) Mac](#a-mac)
      - [B) Windows](#b-windows)
    - [Virtual Environment](#virtual-environment)
      - [Checking your Virtual Environment](#checking-your-virtual-environment)
    - [Requirement File](#requirement-file)
    - [Running The Tests...](#running-the-tests)
    - [Deactivating Virtual Environment](#deactivating-virtual-environment)
  - [Discussion](#discussion)
    - [Cost Analysis](#cost-analysis)
      - [AWS Lambda](#aws-lambda)
      - [AWS S3 Bucket](#aws-s3-bucket)
      - [AWS CloudWatch Logs](#aws-cloudwatch-logs)
      - [Total Cost](#total-cost)
      - [Cost saving suggestions](#cost-saving-suggestions)
    - [Concerns](#concerns)
      - [Scalable?](#scalable)
      - [Bottlenecks?](#bottlenecks)
  - [Author](#author)

## Requirements

These are what is required in your local machine to create, deploy and connect the AWS Lambda with the AWS S3 Bucket:

- [AWS CLI](https://aws.amazon.com/cli/)
- [AWS SAM](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html)

## Installation

### Step 1: Create an IAM especially for AWS SAM

This step may be skipped if an AWS user role has been created for deployment to AWS

1. Create user
   a) go to the IAM and create user
   b) for the permission select add user to the group, we'll attach the permissions later
   c) review and create
2. Create user group
  a) still in IAM, create group
  b) add the created user to the group
  c) attach these permissions to the user group then review and create:
  ```
  AmazonS3FullAccess
  AWSCloudFormationFullAccess
  AWSLambda_FullAccess
  IAMFullAccess
  ```

### Step 2: Configure AWS

In your local machine

1. Run ```aws config``` in the terminal
2. Enter AWS ID and AWS key from the created IAM based on this: based on this: https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html
3. Now that AWS CLI has been configured, time to configure the AWS SAM

### Step 3: Configure AWS SAM

In your local machine 

1. run ```sam build``` in the terminal 
2. run ```sam deploy --capabilities CAPABILITY_NAMED_IAM```

## Usage

### AWS Console

Through your AWS Console, go to the AWS S3 Bucket, the bucket name should be 'respondio-test-bucket` and just upload the files. The file uploaded should be compressed to .zip file automatically since the lambda function will be triggered once the file is uploaded.


## Uninstall 

Once you're done, delete all files in the S3 Bucket and then run this in your local machine:

```sam delete```

that should delete everything that was created for this project

## Architecture

### AWS Lambda & S3 Bucket

The AWS Lambda function that's written in Python is designed to monitor an S3 bucket for new file uploads. When a new file is uploaded, it downloads the file, compresses it into a ZIP archive, uploads the compressed file back to the same S3 bucket, and finally deletes the original file.

In the main.py file contains the lambda_handler function, where it iterates over records in the event, which represent S3 bucket events. For each record, it extracts the bucket name and object key. It then attempts to download the object from S3, compresses it into a ZIP file, and uploads the compressed file back to S3. After successful upload and compression, it deletes the original file from the S3 bucket.

There are several functions defined in the lambda script:
- download_from_s3: Downloads an object from S3 to a temporary directory.
- compress_object_to_zip: Compresses a file into a ZIP archive.
- upload_to_s3: Uploads a file to an S3 bucket.
- delete_from_s3: Deletes an object from an S3 bucket.

Error handling is implemented to handle various exceptions that may occur during execution.

Overall, this lambda function automates the process of compressing files uploaded to an S3 bucket and managing the original files, making it suitable for tasks like reducing storage costs or optimizing data transfer.

### AWS SAM & Cloudformation

There's 2 important files in here, ```samconfig.toml``` and ```template.yaml``` are both related to the AWS Serverless Application Model (SAM), which is an open-source framework for building serverless applications on AWS.

#### samconfig.toml

This is configuration file written in TOML format, likely used in the context of deploying an AWS Serverless Application Model (SAM) application.

- version = 0.1: Specifies the version of the configuration file format. In this case, it's version 0.1.
[default.deploy.parameters]: This section specifies default deployment parameters for SAM deployments.
- stack_name = "respondio-test": Sets the name of the CloudFormation stack that will be created during deployment to "respondio-test".
- resolve_s3 = true: Indicates whether SAM should resolve S3 URLs for nested templates during deployment.
- s3_prefix = "respondio-test": Sets the prefix used for objects uploaded to S3 during deployment to "respondio-test".
- region = "ap-southeast-1": Specifies the AWS region where the CloudFormation stack will be deployed, in this case, "ap-southeast-1".
- confirm_changeset = true: Determines whether to confirm changesets before deployment. When set to true, it asks for confirmation before applying any changes.
- capabilities = "CAPABILITY_NAMED_IAM": Specifies the IAM capabilities required for the CloudFormation stack. In this case, it allows the creation of IAM resources with custom names.
- disable_rollback = true: Indicates whether CloudFormation should disable rollback on stack creation failures. When set to true, it prevents CloudFormation from rolling back the changes in case of a failure.
- image_repositories = []: This appears to be an empty array for defining image repositories. It might be used to specify Docker image repositories for containerized applications.

#### template.yaml

AWS CloudFormation template written in YAML format. It describes the infrastructure required to deploy an AWS Lambda function (ObjToZipLambdaFunction) triggered by an S3 bucket event.

There's 3 parts:

1. An AWS Lambda function (ObjToZipLambdaFunction) triggered by S3 bucket events.
2. An S3 bucket (ObjToZipS3Bucket) named "respondio-test-bucket".
3. An IAM role (ObjToZipLambdaExecutionRole) for the Lambda function to access S3 and write logs to CloudWatch.

Where basically this CloudFormation template creates three resources:

1. **ObjToZipLambdaFunction**:
    - Type: AWS::Serverless::Function
    - Properties:
        - Handler: Specifies the entry point for the Lambda function code.
        - Runtime: Specifies the runtime environment for the Lambda function (Python 3.9).
        - Timeout: Sets the maximum execution time for the Lambda function to 15 seconds.
        - CodeUri: Specifies the location of the Lambda function code.
        - Events: Defines the event source that triggers the Lambda function. In this case, it's an S3 bucket event.
        - Role: References the IAM role (`ObjToZipLambdaExecutionRole`) for the Lambda function to execute.

2. **ObjToZipS3Bucket**:
    - Type: AWS::S3::Bucket
    - Properties:
        - BucketName: Specifies the name of the S3 bucket ("respondio-test-bucket").
        - NotificationConfiguration: Configures notifications for the S3 bucket.
            - LambdaConfigurations: Specifies Lambda function configurations for S3 bucket events.
                - Event: Specifies the S3 event that triggers the Lambda function.
                - Function: References the `ObjToZipLambdaFunction` Lambda function.

3. **ObjToZipLambdaExecutionRole**:
    - Type: AWS::IAM::Role
    - Properties:
        - RoleName: Specifies the name of the IAM role ("ObjToZipLambdaExecutionRole").
        - AssumeRolePolicyDocument: Defines the trust policy that grants permission to assume the role.
        - Policies: Defines the policies attached to the IAM role. There are two policies:
            - `S3CloudWatchLogsPolicy`: Grants permissions to write CloudWatch Logs.
            - `S3ReadWritePolicy`: Grants permissions to read from and write to the specified S3 bucket ("respondio-test-bucket").

## Development

### Setting Up Virtual Environment

Inside the project, run this to generate a couple of files:

```
python -m venv env
```
Explanation:
```
python<version> -m venv <virtual-environment-name>
```

then, from the root of your project, based on your OS:

#### A) Mac
```
source env/bin/activate
```
#### B) Windows

CMD:
```
 env/Scripts/activate.bat
 ```
 Powershell:
 ```
 env/Scripts/Activate.ps1
 ```

### Virtual Environment

this activates the environment as you can see at the left of your terminal with (env).

REMINDER: DON'T FORGET TO PUT YOUR ENV DIRECTORY IN .gitignore file

just open up .gitignore file and add 

```
env/
```

that is it! It can be easily replicated in any new environment anyway ¯\_(ツ)_/¯

#### Checking your Virtual Environment

```
pip list
```

You'll see the list of packages that are installed within the virtual environment, if something's missing (as it is supposed to be*), then you'd better move on to the next step, requirement file

*we're in a virtual environment, of course the previous libraries you've already have is not a part of them

### Requirement File



```
pip3 install -r requirements_dev.txt
```

### Running The Tests...

Remember! Be sure that you have pytest (Python testing framework) installed, with:

```
pip3 install pytest
```

Then just run this in the terminal from the project root path for example:

```pytest -v -l -r f --tb=long```

### Deactivating Virtual Environment

Simply run this in your terminal

```
deactivate
```

and... done, you're back. Can see that (env) is finally gone!

## Discussion

Let's say a company is processing 1,000,000 files per hour with an average of 10MB per file. The monthly cost after addition of this feature would be explained in the cost analysis section.

### Cost Analysis

AWS Services used are: AWS Lambda, AWS S3 and Amazon CloudWatch Logs. Using https://calculator.aws 

Region: Singapore (ap-southeast-1)

#### AWS Lambda

- Number of requests: 1000000 per hour * (730 hours in a month) = 730000000 per month
- Duration for each requests per hour:  3600 seconds / 1 million requests ≈ 0.0036 seconds ≈ 3.6 milliseconds
- Amount of memory allocated: 128 MB x 0.0009765625 GB in a MB = 0.125 GB
- Amount of ephemeral storage allocated: 512 MB x 0.0009765625 GB in a MB = 0.5 GB

Since the function does gets triggered again when the .zip file gets uploaded in the same bucket, we'll double the number of requests to 1,460,000,000

**Pricing calculations**

- 1,460,000,000 requests x 2 ms x 0.001 ms to sec conversion factor = 2,920,000.00 total compute (seconds)
- 0.125 GB x 2,920,000.00 seconds = 365,000.00 total compute (GB-s)
- 365,000.00 GB-s x 0.0000166667 USD = 6.08 USD (monthly compute charges)
- 1,460,000,000 requests x 0.0000002 USD = 292.00 USD (monthly request charges)
- 0.50 GB - 0.5 GB (no additional charge) = 0.00 GB billable ephemeral storage per function
- 6.08 USD + 292.00 USD = 298.08 USD

***Lambda costs - Without Free Tier (monthly): 298.08 USD***

#### AWS S3 Bucket

Tiered price for: 7 GB
- 7 GB x 0.025 USD = 0.18 USD
- Total tier cost = 0.175 USD (S3 Standard storage cost)
- 1,460,000,000 PUT requests for S3 Standard Storage x 0.000005 USD per request = 7,300.00 USD (S3 Standard PUT requests cost)
- 7 GB x 0.0009 USD = 0.0063 USD (S3 select returned cost)
- 7 GB x 0.0025 USD = 0.0175 USD (S3 select scanned cost)
- 0.175 USD + 7,300.00 USD + 0.0063 USD + 0.0175 USD = 7,300.20 USD (Total S3 Standard Storage, data requests, S3 select cost)

***S3 Standard cost (monthly): 7,300.20 USD***

#### AWS CloudWatch Logs

FREE. There is no additional charge for using AWS CloudFormation with extension types in the following namespaces: AWS::*, Alexa::*, and Custom:: says AWS.

#### Total Cost

7598.28 USD a month, so expensive.

#### Cost saving suggestions

- Change to cheaper region
- Optimize the code to run for less duration
- Change to arm architecture instead of x86
- Grab S3 Bucket by batch by setting it so the AWS Lambda function activates only when a certain max number has been uploaded to the S3 bucket, can save costs in terms of requests invocation.

### Concerns
#### Scalable?
Yep, we can run this in a paralel if requests keep growing: concurrency to enable more events concurrently.
Also, integrating a message queue with concurrency in your AWS Lambda solution can enhance scalability and efficiency.

#### Bottlenecks?

This solution assumes that the user will upload the file one by one to the S3 bucket. It will be better if we use Paralel Processing to upload the files to the S3 Bucket to improve performance. Time taken for each processes is a concern too since it does impact the cost. File processing logic may be optimized with using asynchronous processing.

## Author

[Ahmad Siraj MY](https://linkedin.com/in/asmyio)



