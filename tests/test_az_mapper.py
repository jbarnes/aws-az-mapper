"""Basic smoke tests for az_mapper.py"""
import json
import os
import tempfile
from unittest.mock import patch, MagicMock
import pytest
from botocore.exceptions import ClientError
import az_mapper


class TestBasicFunctionality:
    """Essential smoke tests for core functionality."""

    def test_get_default_regions_returns_list(self):
        """Test that default regions returns a valid list."""
        regions = az_mapper.get_default_regions()

        assert isinstance(regions, list)
        assert len(regions) > 0
        assert 'us-east-1' in regions

    @patch('az_mapper.boto3.client')
    def test_get_available_regions_success(self, mock_client):
        """Test successful region fetching."""
        mock_ec2 = MagicMock()
        mock_ec2.describe_regions.return_value = {
            'Regions': [
                {'RegionName': 'us-east-1'},
                {'RegionName': 'us-west-2'}
            ]
        }
        mock_client.return_value = mock_ec2

        regions = az_mapper.get_available_regions()

        assert 'us-east-1' in regions
        assert 'us-west-2' in regions

    @patch('az_mapper.boto3.client')
    def test_get_available_regions_fallback(self, mock_client):
        """Test fallback to default regions on API error."""
        mock_ec2 = MagicMock()
        mock_ec2.describe_regions.side_effect = ClientError(
            {'Error': {'Code': 'UnauthorizedOperation', 'Message': 'Not authorized'}},
            'DescribeRegions'
        )
        mock_client.return_value = mock_ec2

        regions = az_mapper.get_available_regions()

        assert isinstance(regions, list)
        assert len(regions) > 0

    @patch('az_mapper.boto3.client')
    def test_get_current_account_id(self, mock_client):
        """Test account ID retrieval."""
        mock_sts = MagicMock()
        mock_sts.get_caller_identity.return_value = {'Account': '123456789012'}
        mock_client.return_value = mock_sts

        account_id = az_mapper.get_current_account_id()

        assert account_id == '123456789012'

    @patch('az_mapper.get_current_account_id')
    @patch('az_mapper.boto3.client')
    def test_az_map_regions(self, mock_client, mock_account_id):
        """Test basic AZ mapping functionality."""
        mock_account_id.return_value = '123456789012'
        mock_ec2 = MagicMock()
        mock_ec2.describe_availability_zones.return_value = {
            'AvailabilityZones': [
                {'ZoneName': 'us-east-1a', 'ZoneId': 'use1-az1'},
                {'ZoneName': 'us-east-1b', 'ZoneId': 'use1-az2'}
            ]
        }
        mock_client.return_value = mock_ec2

        result = az_mapper.az_map_regions(['us-east-1'])

        assert result['AccountId'] == '123456789012'
        assert 'us-east-1' in result['Zones']
        assert result['Zones']['us-east-1']['us-east-1a'] == 'use1-az1'
        mock_ec2.describe_availability_zones.assert_called_with(
            Filters=[{'Name': 'zone-type', 'Values': ['availability-zone']}]
        )


class TestFileOutput:
    """Tests for file output functionality."""

    def test_json_output(self):
        """Test JSON file creation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            map_data = {
                'AccountId': '123456789012',
                'Zones': {'us-east-1': {'us-east-1a': 'use1-az1'}}
            }

            filename = az_mapper.create_output_file(map_data, tmpdir, 'json')

            assert os.path.exists(filename)
            assert filename.endswith('.json')

            with open(filename, 'r', encoding='utf8') as f:
                loaded_data = json.load(f)

            assert loaded_data['AccountId'] == '123456789012'

    def test_csv_output(self):
        """Test CSV file creation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            map_data = {
                'AccountId': '123456789012',
                'Zones': {'us-east-1': {'us-east-1a': 'use1-az1'}}
            }

            filename = az_mapper.create_output_file(map_data, tmpdir, 'csv')

            assert os.path.exists(filename)
            assert filename.endswith('.csv')

            with open(filename, 'r', encoding='utf8') as f:
                content = f.read()

            assert 'AccountId,Region,LogicalAZ,PhysicalAZ' in content
            assert '123456789012' in content


class TestCLIArguments:
    """Tests for CLI argument parsing."""

    def test_default_arguments(self, monkeypatch):
        """Test default argument values."""
        monkeypatch.setattr('sys.argv', ['az_mapper.py'])

        args = az_mapper.parse_arguments()

        assert args.regions is None
        assert args.output_dir == 'output'
        assert args.format == 'json'

    def test_custom_arguments(self, monkeypatch):
        """Test custom argument parsing."""
        monkeypatch.setattr(
            'sys.argv',
            ['az_mapper.py', '-r', 'us-east-1', '-f', 'csv']
        )

        args = az_mapper.parse_arguments()

        assert args.regions == ['us-east-1']
        assert args.format == 'csv'

    def test_stdout_flag(self, monkeypatch):
        """Test --stdout flag."""
        monkeypatch.setattr('sys.argv', ['az_mapper.py', '--stdout'])

        args = az_mapper.parse_arguments()

        assert args.stdout is True

    def test_quiet_flag(self, monkeypatch):
        """Test --quiet flag."""
        monkeypatch.setattr('sys.argv', ['az_mapper.py', '-q'])

        args = az_mapper.parse_arguments()

        assert args.quiet is True


class TestStdoutOutput:
    """Tests for stdout output functionality."""

    def test_json_stdout(self, capsys):
        """Test JSON output to stdout."""
        map_data = {
            'AccountId': '123456789012',
            'Zones': {'us-east-1': {'us-east-1a': 'use1-az1'}}
        }

        az_mapper.output_to_stdout(map_data, 'json')

        captured = capsys.readouterr()
        assert '123456789012' in captured.out
        assert 'us-east-1a' in captured.out

    def test_csv_stdout(self, capsys):
        """Test CSV output to stdout."""
        map_data = {
            'AccountId': '123456789012',
            'Zones': {'us-east-1': {'us-east-1a': 'use1-az1'}}
        }

        az_mapper.output_to_stdout(map_data, 'csv')

        captured = capsys.readouterr()
        assert 'AccountId,Region,LogicalAZ,PhysicalAZ' in captured.out
        assert '123456789012,us-east-1,us-east-1a,use1-az1' in captured.out
