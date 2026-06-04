"""AWS Availability Zone mapping tool to map logical to physical zones."""
from datetime import datetime, timezone
import csv
import os
import json
import sys
import argparse
import boto3
import botocore

CSV_HEADER = ["AccountId", "Region", "LogicalAZ", "PhysicalAZ"]


def get_current_account_id():
    """Get the current AWS account ID from STS."""
    try:
        sts_client = boto3.client("sts")
        response = sts_client.get_caller_identity()
        return response["Account"]
    except botocore.exceptions.ClientError as error:
        print(f"Error retrieving account ID: {error}", file=sys.stderr)
        sys.exit(1)


def get_available_regions():
    """Fetch available AWS regions dynamically from EC2."""
    try:
        ec2_client = boto3.client("ec2", region_name="us-east-1")
        response = ec2_client.describe_regions(AllRegions=False)
        return sorted([region["RegionName"] for region in response["Regions"]])
    except botocore.exceptions.ClientError as error:
        print(f"Error fetching regions: {error}", file=sys.stderr)
        print(
            "WARNING: falling back to a hardcoded region list. It may be stale and "
            "may include regions this account cannot access; results could be "
            "incomplete.",
            file=sys.stderr,
        )
        return get_default_regions()


def get_default_regions():
    """Fallback list of common AWS regions."""
    return [
        "us-east-1",
        "us-east-2",
        "us-west-1",
        "us-west-2",
        "af-south-1",
        "ap-east-1",
        "ap-south-1",
        "ap-south-2",
        "ap-southeast-1",
        "ap-southeast-2",
        "ap-southeast-3",
        "ap-southeast-4",
        "ap-northeast-1",
        "ap-northeast-2",
        "ap-northeast-3",
        "ca-central-1",
        "eu-central-1",
        "eu-central-2",
        "eu-west-1",
        "eu-west-2",
        "eu-west-3",
        "eu-north-1",
        "eu-south-1",
        "eu-south-2",
        "me-south-1",
        "me-central-1",
        "sa-east-1",
    ]


def az_map_regions(regions, quiet=False):
    """Map the availability zones for the specified regions in current account."""
    account_id = get_current_account_id()

    zone_map = {
        "AccountId": account_id,
        "Zones": {}
    }

    if not quiet:
        print(f"Mapping availability zones for account: {account_id}", file=sys.stderr)

    for region in regions:
        if not quiet:
            print(f"  Processing region: {region}", file=sys.stderr)
        zone_map["Zones"][region] = {}

        try:
            ec2_client = boto3.client("ec2", region_name=region)
            # Filter to standard AZs only — excludes Local Zones and Wavelength Zones
            response = ec2_client.describe_availability_zones(
                Filters=[{"Name": "zone-type", "Values": ["availability-zone"]}]
            )

            for zone in response["AvailabilityZones"]:
                zone_map["Zones"][region][zone["ZoneName"]] = zone["ZoneId"]

            if not quiet:
                print(f"    Found {len(zone_map['Zones'][region])} availability zones",
                      file=sys.stderr)

        except botocore.exceptions.ClientError as error:
            print(f"    Error retrieving availability zones for {region}: {error}",
                  file=sys.stderr)
            zone_map["Zones"][region] = {}

    return zone_map


def _csv_rows(map_data):
    """Yield CSV data rows (no header) as lists for the mapping data."""
    account_id = map_data["AccountId"]
    for region, zones in map_data["Zones"].items():
        for logical_az, physical_az in zones.items():
            yield [account_id, region, logical_az, physical_az]


def create_output_file(map_data, output_dir="output", format_type="json"):
    """Generate output files containing the mapping data."""
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    account_id = map_data["AccountId"]

    os.makedirs(output_dir, exist_ok=True)

    if format_type == "json":
        filename = f"{output_dir}/aws-az-map-{account_id}-{timestamp}.json"
        with open(filename, "w", encoding="utf8") as file:
            json.dump(map_data, file, indent=2)
    elif format_type == "csv":
        filename = f"{output_dir}/aws-az-map-{account_id}-{timestamp}.csv"
        with open(filename, "w", encoding="utf8", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(CSV_HEADER)
            writer.writerows(_csv_rows(map_data))

    return filename


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Map AWS logical availability zones to physical zones for the current account"
    )

    parser.add_argument(
        "--regions",
        "-r",
        nargs="+",
        help=("Specific regions to map (e.g., us-east-1 us-west-2). "
              "If not specified, maps all available regions.")
    )

    parser.add_argument(
        "--output-dir",
        "-o",
        default="output",
        help="Output directory for the mapping file (default: output)"
    )

    parser.add_argument(
        "--format",
        "-f",
        choices=["json", "csv"],
        default="json",
        help="Output format: json or csv (default: json)"
    )

    parser.add_argument(
        "--list-regions",
        action="store_true",
        help="List all available AWS regions and exit"
    )

    parser.add_argument(
        "--stdout",
        action="store_true",
        help="Output to stdout instead of saving to a file"
    )

    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Suppress informational output on stderr"
    )

    return parser.parse_args()


def output_to_stdout(map_data, format_type="json"):
    """Output mapping data to stdout."""
    if format_type == "json":
        print(json.dumps(map_data, indent=2))
    elif format_type == "csv":
        writer = csv.writer(sys.stdout)
        writer.writerow(CSV_HEADER)
        writer.writerows(_csv_rows(map_data))


def main():
    """Primary function execution point."""
    args = parse_arguments()

    if args.list_regions:
        if not args.quiet:
            print("Fetching available AWS regions...", file=sys.stderr)
        regions = get_available_regions()
        if not args.quiet:
            print(f"\nAvailable regions ({len(regions)}):", file=sys.stderr)
        for region in regions:
            print(f"  - {region}")
        sys.exit(0)

    if args.regions:
        regions_to_map = args.regions
        if not args.quiet:
            print(f"Mapping specified regions: {', '.join(regions_to_map)}", file=sys.stderr)
    else:
        if not args.quiet:
            print("No regions specified, fetching all available regions...", file=sys.stderr)
        regions_to_map = get_available_regions()
        if not args.quiet:
            print(f"Will map {len(regions_to_map)} regions", file=sys.stderr)

    if not args.quiet:
        print("\nStarting availability zone mapping...", file=sys.stderr)
    zone_map = az_map_regions(regions_to_map, quiet=args.quiet)

    if args.stdout:
        output_to_stdout(zone_map, args.format)
    else:
        if not args.quiet:
            print(f"\nGenerating {args.format.upper()} output file...", file=sys.stderr)
        output_file = create_output_file(zone_map, args.output_dir, args.format)
        if not args.quiet:
            print(f"Mapping saved to: {output_file}", file=sys.stderr)

        total_azs = sum(len(zones) for zones in zone_map["Zones"].values())
        if not args.quiet:
            print("\nSummary:", file=sys.stderr)
            print(f"  Account ID: {zone_map['AccountId']}", file=sys.stderr)
            print(f"  Regions mapped: {len(zone_map['Zones'])}", file=sys.stderr)
            print(f"  Total AZs found: {total_azs}", file=sys.stderr)


if __name__ == "__main__":
    main()
