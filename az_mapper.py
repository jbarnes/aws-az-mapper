"""AWS Availability Zone mapping tool to map logical to physical zones."""
from datetime import datetime
import os
import json
import sys
import boto3
import questionary as qst
import botocore


def aws_accounts_prompt():
    """Prompt the executing user to select which AWS accounts to map."""
    init_accounts_list = ["all"]
    print("Retrieving a list of AWS accounts...")
    org_account_list = aws_org_accounts()

    for account in org_account_list:
        init_accounts_list.append(account["Id"])

    account_selection = qst.checkbox(
        "Which AWS accounts do you want to map?",
        choices=init_accounts_list,
    ).ask()

    if "all" in account_selection:
        init_accounts_list.remove("all")
        return init_accounts_list

    if not account_selection:
        print("No accounts were selected, exiting.")
        sys.exit()

    return account_selection


def aws_org_accounts():
    """Get a list of all AWS accounts associated with the AWS organisation."""
    client = boto3.client("organizations")

    raw_account_list = []

    response = client.list_accounts(MaxResults=20)
    raw_account_list.extend(response["Accounts"])
    while "NextToken" in response:
        response = client.list_accounts(
            MaxResults=20,
            NextToken=response["NextToken"],
        )
        raw_account_list.extend(response["Accounts"])

    return raw_account_list


def aws_region_list():
    """Simple function to return a list of regions."""
    regions = [
        "us-east-1",
        "us-east-2",
        "us-west-1",
        "us-west-2",
        "af-south-1",
        "ap-east-1",
        "ap-south-1",
        "ap-northeast-1",
        "ap-northeast-2",
        "ap-northeast-3",
        "ap-southeast-1",
        "ap-southeast-2",
        "ca-central-1",
        "cn-north-1",
        "cn-northwest-1",
        "eu-central-1",
        "eu-west-1",
        "eu-west-2",
        "eu-west-3",
        "eu-north-1",
        "eu-south-1",
        "me-south-1",
        "sa-east-1",
        "us-gov-west-1",
        "us-gov-east-1",
    ]

    return regions


def aws_regions_prompt():
    """Prompts the executing user to select which AWS regions they wish to map."""
    regions = aws_region_list()

    region_selection = qst.checkbox(
        "Which AWS regions do you want to map?",
        choices=regions,
    ).ask()

    if not region_selection:
        print("You have failed to select a region, exiting.")
        sys.exit()

    return region_selection


def assume_role(account_id, role_name):
    """
    Assume a role with adequate permissions
    """

    role_arn = "arn:aws:iam::{}:role/{}".format(account_id, role_name)

    try:
        sts_client = boto3.client("sts")
        response = sts_client.assume_role(
            RoleArn=role_arn,
            RoleSessionName="AZMapperTool",
        )

        print(
            "Successfully assumed role: {} for AWS account: {}".format(
                role_name, account_id
            )
        )
    except botocore.exceptions.ClientError as error:
        print(
            "An error occurred when trying to assume role: {} for this account".format(
                role_name
            )
        )
        raise error

    sts_session = boto3.Session(
        aws_access_key_id=response["Credentials"]["AccessKeyId"],
        aws_secret_access_key=response["Credentials"]["SecretAccessKey"],
        aws_session_token=response["Credentials"]["SessionToken"],
    )

    return sts_session


def role_assertion_prompt():
    """Prompt executing user to provide the role to use for role assertion."""
    role_name = qst.text(
        "Please provide the AWS IAM role NAME az-mapper must use for role assertion:"
    ).ask()

    return role_name


def az_map_account(account_id, iam_role, regions):
    """Map the availability zones for the provided account and regions."""
    zone_map = {}
    zone_map["AccountId"] = account_id
    zone_map["Zones"] = {}

    session = assume_role(account_id, iam_role)

    for region in regions:
        zone_map["Zones"][region] = []
        zone_dict = {}

        client = session.client("ec2", region_name=region)

        try:
            response = client.describe_availability_zones()[
                "AvailabilityZones"
            ]
        except botocore.exceptions.ClientError as error:
            print(
                "An error occurred attempting to retrieve availability zones. Error: {}".format(
                    error
                )
            )

        for zone in response:
            zone_dict[zone["ZoneName"]] = zone["ZoneId"]

        zone_map["Zones"][region].append(zone_dict)

    return zone_map


def create_output_file(map_data):
    """Generate output files containing the mapping data."""
    timestamp = datetime.now()

    filename = "output/aws-az-map-{}.json".format(timestamp)
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    with open(filename, "w") as file:
        json.dump(map_data, file)

    return filename


def main():
    """Primary function execution point."""

    # Get basic mapping info from user
    accounts_map = aws_accounts_prompt()
    region_map = aws_regions_prompt()
    role_to_assume = role_assertion_prompt()

    complete_map = {}
    complete_map["Accounts"] = []

    for account in accounts_map:
        print("Beginning mapping for AWS account id: {}...".format(account))

        account_map = az_map_account(account, role_to_assume, region_map)
        complete_map["Accounts"].append(account_map)
        print("Successfully mapped AWS account id: {}".format(account))

    print("Generating final output file...")
    file = create_output_file(complete_map)
    print("File: {} has been created with the mapping data.".format(file))

    print("Availability Zone Mapper has completed, exiting.")


if __name__ == "__main__":
    main()
