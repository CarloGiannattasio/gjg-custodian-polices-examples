from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
POLICIES_DIR = REPO_ROOT / "policies" / "aws"


def policy_yml_files():
    paths = sorted(POLICIES_DIR.rglob("*.yml"))
    return [p for p in paths if p.name != "notify-vars.yml"]


# Moto does not implement service-quotas ListServices (custodian aws.service-quota).
MOTO_DRYRUN_SKIP = {
    POLICIES_DIR / "service-quota-usage.yml",
}


@pytest.fixture(scope="session")
def repo_root():
    return REPO_ROOT


@pytest.fixture(scope="session")
def all_policy_files():
    return policy_yml_files()


@pytest.fixture(scope="session")
def moto_dryrun_policy_files():
    return [p for p in policy_yml_files() if p not in MOTO_DRYRUN_SKIP]
