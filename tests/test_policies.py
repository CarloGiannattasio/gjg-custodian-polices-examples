"""Validate and dry-run Cloud Custodian policies against Moto (no real AWS account)."""

import subprocess

import boto3
import pytest
from moto import mock_aws

from c7n import policy as policy_mod
from c7n.config import Config

from conftest import MOTO_DRYRUN_SKIP, REPO_ROOT, policy_yml_files

MOTO_DRYRUN_FILES = [p for p in policy_yml_files() if p not in MOTO_DRYRUN_SKIP]


def _policy_id(path):
    return str(path.relative_to(REPO_ROOT))


def test_validate_all_policy_files():
    for path in policy_yml_files():
        result = subprocess.run(
            ["custodian", "validate", str(path)],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, (
            f"custodian validate failed for {path}:\n{result.stdout}\n{result.stderr}"
        )


def test_service_quota_skipped_for_moto_dryrun():
    path = REPO_ROOT / "policies" / "aws" / "service-quota-usage.yml"
    assert path in MOTO_DRYRUN_SKIP


@pytest.mark.parametrize("policy_path", MOTO_DRYRUN_FILES, ids=_policy_id)
def test_moto_dryrun_policy(policy_path):
    @mock_aws
    def _run():
        ec2 = boto3.client("ec2", region_name="us-east-1")
        vpc = ec2.create_vpc(CidrBlock="10.0.0.0/16")["Vpc"]["VpcId"]
        subnet = ec2.create_subnet(VpcId=vpc, CidrBlock="10.0.0.0/24")["Subnet"]["SubnetId"]
        ec2.run_instances(
            ImageId="ami-0123456789abcdef0",
            MinCount=1,
            MaxCount=1,
            SubnetId=subnet,
        )
        iam = boto3.client("iam", region_name="us-east-1")
        iam.create_role(
            RoleName="moto-smoke-role",
            AssumeRolePolicyDocument='{"Version":"2012-10-17","Statement":[]}',
        )

        options = Config.empty(
            regions=["us-east-1"],
            dryrun=True,
            output_dir=str(REPO_ROOT / "tmp" / "c7n-moto-out"),
            account_id="123456789012",
        )
        collection = policy_mod.load(options, str(policy_path))
        for policy in collection:
            policy.run()

    _run()
