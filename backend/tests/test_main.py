import os

from fastapi.testclient import TestClient

os.environ["ASSETS_SKIP_DB_INIT"] = "1"

from app.database import get_session  # noqa: E402
from app.main import app  # noqa: E402
from app.models import (  # noqa: E402
    DEFAULT_AUTONOMOUS_SYSTEMS,
    DEFAULT_CONFIGURATION_ITEMS,
    DEFAULT_IEEE_REGISTRIES,
    DEFAULT_IP_ADDRESSES,
    DEFAULT_IP_AGGREGATES,
    DEFAULT_IP_PREFIXES,
    DEFAULT_IP_RANGES,
    DEFAULT_L2_ROLES,
    DEFAULT_L3_ROLES,
    DEFAULT_MAC_ADDRESS_BLOCK_ASSIGNMENTS,
    DEFAULT_MAC_ADDRESSES,
    DEFAULT_REGIONAL_INTERNET_REGISTRIES,
    DEFAULT_SITES,
    DEFAULT_VLANS,
    DEFAULT_VIRTUAL_ROUTING_FORWARDINGS,
)


client = TestClient(app)


class FakeResult:
    def __init__(self, records):
        self.records = records

    def all(self):
        return self.records


class FakeSession:
    def __init__(self, records):
        self.records = records

    def exec(self, statement):
        return FakeResult(self.records)


def override_session(records):
    def fake_get_session():
        yield FakeSession(records)

    app.dependency_overrides[get_session] = fake_get_session


def test_health_check() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "assets-api",
        "database": "sqlite",
    }


def test_list_configuration_items() -> None:
    override_session(DEFAULT_CONFIGURATION_ITEMS)

    response = client.get("/api/configuration-items")

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()[0]["name"] == "Customer Portal"


def test_list_vlans() -> None:
    override_session(DEFAULT_VLANS)

    response = client.get("/api/l2/vlans")

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()[0]["vlan_id"] == 10
    assert response.json()[0]["role_id"] == 1
    assert response.json()[0]["site_id"] == 1


def test_list_l2_roles() -> None:
    override_session(DEFAULT_L2_ROLES)

    response = client.get("/api/l2/roles")

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()[0]["name"] == "Access"
    assert response.json()[0]["available_to_vlans"] is True
    assert response.json()[0]["available_to_mac_addresses"] is False


def test_list_ieee_registries() -> None:
    override_session(DEFAULT_IEEE_REGISTRIES)

    response = client.get("/api/l2/ieee-registries")

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()[0]["abbreviation"] == "MA-L"


def test_list_mac_address_block_assignments() -> None:
    override_session(DEFAULT_MAC_ADDRESS_BLOCK_ASSIGNMENTS)

    response = client.get("/api/l2/mac-address-block-assignments")

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()[0]["registry"] == "MA-S"
    assert response.json()[0]["assignment"] == "8C1F64AFA"
    assert response.json()[0]["organization_name"] == "DATA ELECTRONIC DEVICES, INC"


def test_list_mac_addresses() -> None:
    override_session(DEFAULT_MAC_ADDRESSES)

    response = client.get("/api/l2/mac-addresses")

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()[0]["address"] == "00:11:22:33:44:55"
    assert response.json()[0]["vlan_id"] == 1
    assert response.json()[0]["role_id"] == 3
    assert response.json()[0]["block_assignment_id"] == 1
    assert response.json()[0]["configuration_item_id"] == 1


def test_list_ip_addresses() -> None:
    override_session(DEFAULT_IP_ADDRESSES)

    response = client.get("/api/ipam/ip-addresses")

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()[0]["address"] == "10.10.1.10"
    assert response.json()[0]["role_id"] == 1
    assert response.json()[0]["configuration_item_id"] == 1


def test_list_ip_prefixes() -> None:
    override_session(DEFAULT_IP_PREFIXES)

    response = client.get("/api/ipam/ip-prefixes")

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()[0]["prefix"] == "10.10.1.0/24"
    assert response.json()[0]["vrf_id"] == 1
    assert response.json()[0]["site_id"] == 1


def test_list_l3_roles() -> None:
    override_session(DEFAULT_L3_ROLES)

    response = client.get("/api/l3/roles")

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()[0]["name"] == "Application"
    assert response.json()[0]["available_to_ip_addresses"] is True
    assert response.json()[0]["available_to_ip_prefixes"] is True
    assert response.json()[0]["available_to_ip_ranges"] is False


def test_list_virtual_routing_forwardings() -> None:
    override_session(DEFAULT_VIRTUAL_ROUTING_FORWARDINGS)

    response = client.get("/api/ipam/virtual-routing-forwardings")

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()[0]["name"] == "global"


def test_list_sites() -> None:
    override_session(DEFAULT_SITES)

    response = client.get("/api/ipam/sites")

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()[0]["name"] == "HQ"


def test_list_regional_internet_registries() -> None:
    override_session(DEFAULT_REGIONAL_INTERNET_REGISTRIES)

    response = client.get("/api/ipam/regional-internet-registries")

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()[0]["abbreviation"] == "AFRINIC"


def test_list_ip_aggregates() -> None:
    override_session(DEFAULT_IP_AGGREGATES)

    response = client.get("/api/ipam/ip-aggregates")

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()[0]["aggregate"] == "10.10.0.0/16"
    assert response.json()[0]["rir_id"] == 6


def test_list_autonomous_systems() -> None:
    override_session(DEFAULT_AUTONOMOUS_SYSTEMS)

    response = client.get("/api/ipam/autonomous-systems")

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()[0]["asn"] == 64512
    assert response.json()[0]["rir_id"] == 6


def test_list_ip_ranges() -> None:
    override_session(DEFAULT_IP_RANGES)

    response = client.get("/api/ipam/ip-ranges")

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()[0]["start_address"] == "10.10.1.100"
    assert response.json()[0]["role_id"] == 4
