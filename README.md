# AWS Availability Zone Mapper

Availability Zone Mapper - Maps physical availability zones to an AWS accounts logical availability zones

## Code status

![pylint status](https://github.com/jbarnes/az-mapper/actions/workflows/pylint.yml/badge.svg)

## Basic commands

* Run `make deps` to install Python dependencies
* Run `make map` to run the Availability Zone mapping tool

## Using this tool

There are a small amount of prerequisites that must be completed prior to execution.

This tool has only been tested in a unix environment, specifically a WSL based unix environment.

### Prerequisites

#### Local environment

* Python 3.x must be installed
* AWS CLI must be installed
* Run the command `make deps` to download the required Python dependencies that are not standard

#### AWS requirements

* You must have an AWS IAM Role set up prior in **every AWS account** you wish to map
* This role must also be created and accessible in your **AWS management account** (if you wish to map it)
* This role only requires the following permissions
```
ec2:DescribeAvailabilityZones
organizations:ListAccounts
sts:AssumeRole
```
* If you are using AWS Control Tower, you can nominate the `AWSControlTowerExecution` IAM role
  * **Note**: This role does not exist be default in the AWS management account.

### Generating a map file

* Via the AWS CLI/a terminal window - Login to your AWS **management account**
* Ensure you are in this repositories main directory
* Run the command `make map`
* You will be prompted to select **all** of your AWS accounts to be mapped or your selections
  * You must select at least one account or **all** otherwise the tool will exit
* You will then be prompted to select which AWS regions you wish to map for each account
  * You must select at least one region
  * **Note**: You cannot select regions on a per account basis, if you wish to generate specific map information per account, run the tool for those accounts only
* You will finally be prompted to provide the **role name** that the Availability Zone Mapper will assume into each account to gather the information

### Runtime and output

Upon beginning the map file generation, the following will occur;

* The tool will connect to an account and then map the logical availability zones to the physical availability zones for that region
* It will then continue to do this for each region selected earlier for the current AWS account
* Once this has completed it will continue onto the next AWS account until all AWS accounts have been processed
* Once all AWS accounts have been processed the tool will produce a timestamped JSON file located in a folder called `outputs`

### Example output

The following contains mapping for four (4) different AWS accounts for AWS regions `us-east-1` and `ap-southeast-2`.

```json
{
    "Accounts": [
        {
            "AccountId": "111111111111",
            "Zones": {
                "us-east-1": [
                    {
                        "us-east-1a": "use1-az1",
                        "us-east-1b": "use1-az2",
                        "us-east-1c": "use1-az4",
                        "us-east-1d": "use1-az6",
                        "us-east-1e": "use1-az3",
                        "us-east-1f": "use1-az5"
                    }
                ],
                "ap-southeast-2": [
                    {
                        "ap-southeast-2a": "apse2-az3",
                        "ap-southeast-2b": "apse2-az1",
                        "ap-southeast-2c": "apse2-az2"
                    }
                ]
            }
        },
        {
            "AccountId": "222222222222",
            "Zones": {
                "us-east-1": [
                    {
                        "us-east-1a": "use1-az4",
                        "us-east-1b": "use1-az6",
                        "us-east-1c": "use1-az1",
                        "us-east-1d": "use1-az2",
                        "us-east-1e": "use1-az3",
                        "us-east-1f": "use1-az5"
                    }
                ],
                "ap-southeast-2": [
                    {
                        "ap-southeast-2a": "apse2-az3",
                        "ap-southeast-2b": "apse2-az1",
                        "ap-southeast-2c": "apse2-az2"
                    }
                ]
            }
        },
        {
            "AccountId": "333333333333",
            "Zones": {
                "us-east-1": [
                    {
                        "us-east-1a": "use1-az4",
                        "us-east-1b": "use1-az6",
                        "us-east-1c": "use1-az1",
                        "us-east-1d": "use1-az2",
                        "us-east-1e": "use1-az3",
                        "us-east-1f": "use1-az5"
                    }
                ],
                "ap-southeast-2": [
                    {
                        "ap-southeast-2a": "apse2-az3",
                        "ap-southeast-2b": "apse2-az1",
                        "ap-southeast-2c": "apse2-az2"
                    }
                ]
            }
        },
        {
            "AccountId": "444444444444",
            "Zones": {
                "us-east-1": [
                    {
                        "us-east-1a": "use1-az4",
                        "us-east-1b": "use1-az6",
                        "us-east-1c": "use1-az1",
                        "us-east-1d": "use1-az2",
                        "us-east-1e": "use1-az3",
                        "us-east-1f": "use1-az5"
                    }
                ],
                "ap-southeast-2": [
                    {
                        "ap-southeast-2a": "apse2-az1",
                        "ap-southeast-2b": "apse2-az3",
                        "ap-southeast-2c": "apse2-az2"
                    }
                ]
            }
        }
    ]
}
```

## Feedback, improvements, issues

Please feel free to raise Pull Requests, Issues with identified problems or feedback.

Thank you.