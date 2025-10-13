# AWS Availability Zone Mapper

Maps AWS logical availability zones to physical zone IDs for the currently authenticated account.

## Code status

![pylint status](https://github.com/jbarnes/az-mapper/actions/workflows/pylint.yml/badge.svg)

## Overview

AWS uses logical AZ names (like `us-east-1a`) that map to different physical datacenters across accounts. This tool discovers the mapping for your account, which is useful for:

* Optimizing data transfer costs during AWS DMS migrations
* Ensuring resources are in the same physical datacenter across accounts
* Planning multi-account architectures with latency requirements

## Prerequisites

* Python 3.8 or higher
* AWS CLI configured with credentials
* IAM permissions required:
  * `ec2:DescribeAvailabilityZones`
  * `ec2:DescribeRegions`
  * `sts:GetCallerIdentity`

## Installation

```bash
make deps
```

Or manually:
```bash
pip install -r requirements.txt
```

## Usage

### Basic usage - Map all regions

```bash
python3 az_mapper.py
```

This will map all available AWS regions for your current account.

### Map specific regions

```bash
python3 az_mapper.py --regions us-east-1 us-west-2
```

### Output as CSV instead of JSON

```bash
python3 az_mapper.py --format csv
```

### Specify output directory

```bash
python3 az_mapper.py --output-dir /path/to/output
```

### List available regions

```bash
python3 az_mapper.py --list-regions
```

### Combined example

```bash
python3 az_mapper.py --regions us-east-1 eu-west-1 --format csv --output-dir ./mappings
```

## Output

The tool generates timestamped files in the specified output directory (default: `output/`):

* JSON format: `aws-az-map-{account-id}-{timestamp}.json`
* CSV format: `aws-az-map-{account-id}-{timestamp}.csv`

### Example JSON output

```json
{
  "AccountId": "123456789012",
  "Zones": {
    "us-east-1": {
      "us-east-1a": "use1-az1",
      "us-east-1b": "use1-az2",
      "us-east-1c": "use1-az4",
      "us-east-1d": "use1-az6",
      "us-east-1e": "use1-az3",
      "us-east-1f": "use1-az5"
    },
    "us-west-2": {
      "us-west-2a": "usw2-az2",
      "us-west-2b": "usw2-az1",
      "us-west-2c": "usw2-az3",
      "us-west-2d": "usw2-az4"
    }
  }
}
```

### Example CSV output

```csv
AccountId,Region,LogicalAZ,PhysicalAZ
123456789012,us-east-1,us-east-1a,use1-az1
123456789012,us-east-1,us-east-1b,use1-az2
123456789012,us-east-1,us-east-1c,use1-az4
123456789012,us-west-2,us-west-2a,usw2-az2
123456789012,us-west-2,us-west-2b,usw2-az1
```

## Feedback, improvements, issues

Please feel free to raise Pull Requests, Issues with identified problems or feedback.

Thank you.