from sqlmodel import Field, SQLModel


class ConfigurationItem(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    type: str = Field(index=True)
    owner: str = Field(index=True)
    status: str = Field(index=True)


class L3Role(SQLModel, table=True):
    __tablename__ = "ip_roles"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    available_to_ip_addresses: bool = Field(default=False, index=True)
    available_to_ip_ranges: bool = Field(default=False, index=True)
    available_to_ip_prefixes: bool = Field(default=False, index=True)
    available_to_ip_aggregates: bool = Field(default=False, index=True)
    available_to_vrfs: bool = Field(default=False, index=True)
    description: str | None = None


class VirtualRoutingForwarding(SQLModel, table=True):
    __tablename__ = "virtual_routing_forwardings"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    route_distinguisher: str | None = Field(default=None, index=True)
    description: str | None = None


class Site(SQLModel, table=True):
    __tablename__ = "sites"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    status: str = Field(index=True)
    description: str | None = None


class Vlan(SQLModel, table=True):
    __tablename__ = "vlans"

    id: int | None = Field(default=None, primary_key=True)
    vlan_id: int = Field(index=True, unique=True)
    name: str = Field(index=True)
    role_id: int | None = Field(default=None, foreign_key="l2_roles.id", index=True)
    site_id: int | None = Field(default=None, foreign_key="sites.id", index=True)
    status: str = Field(index=True)
    description: str | None = None


class L2Role(SQLModel, table=True):
    __tablename__ = "l2_roles"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    available_to_vlans: bool = Field(default=False, index=True)
    available_to_mac_addresses: bool = Field(default=False, index=True)
    description: str | None = None


class IeeeRegistry(SQLModel, table=True):
    __tablename__ = "ieee_registries"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    abbreviation: str = Field(index=True, unique=True)
    scope: str = Field(index=True)
    description: str | None = None


class MacAddressBlockAssignment(SQLModel, table=True):
    __tablename__ = "mac_address_block_assignments"

    id: int | None = Field(default=None, primary_key=True)
    registry: str = Field(index=True)
    assignment: str = Field(index=True, unique=True)
    organization_name: str = Field(index=True)
    organization_address: str | None = None


class MacAddress(SQLModel, table=True):
    __tablename__ = "mac_addresses"

    id: int | None = Field(default=None, primary_key=True)
    address: str = Field(index=True, unique=True)
    vlan_id: int | None = Field(default=None, foreign_key="vlans.id", index=True)
    role_id: int | None = Field(default=None, foreign_key="l2_roles.id", index=True)
    block_assignment_id: int | None = Field(
        default=None,
        foreign_key="mac_address_block_assignments.id",
        index=True,
    )
    configuration_item_id: int | None = Field(
        default=None,
        foreign_key="configurationitem.id",
        index=True,
    )
    status: str = Field(index=True)
    description: str | None = None


class IpAddress(SQLModel, table=True):
    __tablename__ = "ip_addresses"

    id: int | None = Field(default=None, primary_key=True)
    address: str = Field(index=True, unique=True)
    status: str = Field(index=True)
    role_id: int | None = Field(default=None, foreign_key="ip_roles.id", index=True)
    configuration_item_id: int | None = Field(
        default=None,
        foreign_key="configurationitem.id",
        index=True,
    )
    description: str | None = None


class IpPrefix(SQLModel, table=True):
    __tablename__ = "ip_prefixes"

    id: int | None = Field(default=None, primary_key=True)
    prefix: str = Field(index=True, unique=True)
    vrf_id: int | None = Field(
        default=None,
        foreign_key="virtual_routing_forwardings.id",
        index=True,
    )
    status: str = Field(index=True)
    site_id: int | None = Field(default=None, foreign_key="sites.id", index=True)
    description: str | None = None


class RegionalInternetRegistry(SQLModel, table=True):
    __tablename__ = "regional_internet_registries"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    abbreviation: str = Field(index=True, unique=True)
    region: str = Field(index=True)
    description: str | None = None


class AutonomousSystem(SQLModel, table=True):
    __tablename__ = "autonomous_systems"

    id: int | None = Field(default=None, primary_key=True)
    asn: int = Field(index=True, unique=True)
    name: str = Field(index=True)
    rir_id: int | None = Field(
        default=None,
        foreign_key="regional_internet_registries.id",
        index=True,
    )
    status: str = Field(index=True)
    description: str | None = None


class IpAggregate(SQLModel, table=True):
    __tablename__ = "ip_aggregates"

    id: int | None = Field(default=None, primary_key=True)
    aggregate: str = Field(index=True, unique=True)
    rir_id: int | None = Field(
        default=None,
        foreign_key="regional_internet_registries.id",
        index=True,
    )
    status: str = Field(index=True)
    description: str | None = None


class IpRange(SQLModel, table=True):
    __tablename__ = "ip_ranges"

    id: int | None = Field(default=None, primary_key=True)
    start_address: str = Field(index=True)
    end_address: str = Field(index=True)
    status: str = Field(index=True)
    role_id: int | None = Field(default=None, foreign_key="ip_roles.id", index=True)
    description: str | None = None


DEFAULT_CONFIGURATION_ITEMS = [
    ConfigurationItem(
        name="Customer Portal",
        type="Application",
        owner="Platform",
        status="Operational",
    ),
    ConfigurationItem(
        name="Primary PostgreSQL",
        type="Database",
        owner="Data Services",
        status="Monitored",
    ),
    ConfigurationItem(
        name="Edge Router A",
        type="Network",
        owner="Infrastructure",
        status="Maintenance",
    ),
]

DEFAULT_L3_ROLES = [
    L3Role(
        id=1,
        name="Application",
        available_to_ip_addresses=True,
        available_to_ip_prefixes=True,
        description="Application service addressing",
    ),
    L3Role(
        id=2,
        name="Database",
        available_to_ip_addresses=True,
        available_to_ip_prefixes=True,
        description="Database service addressing",
    ),
    L3Role(
        id=3,
        name="Gateway",
        available_to_ip_addresses=True,
        available_to_ip_prefixes=True,
        description="Network gateway addressing",
    ),
    L3Role(
        id=4,
        name="DHCP",
        available_to_ip_ranges=True,
        description="Dynamic host assignment range",
    ),
    L3Role(
        id=5,
        name="Static",
        available_to_ip_addresses=True,
        available_to_ip_ranges=True,
        description="Static assignment range",
    ),
]

DEFAULT_IP_ROLES = DEFAULT_L3_ROLES

DEFAULT_VIRTUAL_ROUTING_FORWARDINGS = [
    VirtualRoutingForwarding(
        id=1,
        name="global",
        route_distinguisher=None,
        description="Default global routing table",
    ),
]

DEFAULT_SITES = [
    Site(
        id=1,
        name="HQ",
        status="Active",
        description="Headquarters site",
    ),
]

DEFAULT_VLANS = [
    Vlan(
        id=1,
        vlan_id=10,
        name="Application",
        role_id=1,
        site_id=1,
        status="Active",
        description="Application access VLAN",
    ),
    Vlan(
        id=2,
        vlan_id=20,
        name="Infrastructure",
        role_id=2,
        site_id=1,
        status="Active",
        description="Infrastructure access VLAN",
    ),
]

DEFAULT_L2_ROLES = [
    L2Role(
        id=1,
        name="Access",
        available_to_vlans=True,
        description="Layer 2 access segmentation",
    ),
    L2Role(
        id=2,
        name="Infrastructure",
        available_to_vlans=True,
        available_to_mac_addresses=True,
        description="Layer 2 infrastructure connectivity",
    ),
    L2Role(
        id=3,
        name="Endpoint",
        available_to_mac_addresses=True,
        description="Layer 2 endpoint identifier",
    ),
]

DEFAULT_IEEE_REGISTRIES = [
    IeeeRegistry(
        id=1,
        name="MAC Address Block - Large",
        abbreviation="MA-L",
        scope="Large MAC address block assignments",
        description="IEEE registry for large MAC address block assignments",
    ),
    IeeeRegistry(
        id=2,
        name="MAC Address Block - Medium",
        abbreviation="MA-M",
        scope="Medium MAC address block assignments",
        description="IEEE registry for medium MAC address block assignments",
    ),
    IeeeRegistry(
        id=3,
        name="MAC Address Block - Small",
        abbreviation="MA-S",
        scope="Small MAC address block assignments",
        description="IEEE registry for small MAC address block assignments",
    ),
    IeeeRegistry(
        id=4,
        name="Company ID",
        abbreviation="CID",
        scope="Company identifier assignments",
        description="IEEE registry for company identifiers",
    ),
]

DEFAULT_MAC_ADDRESS_BLOCK_ASSIGNMENTS = [
    MacAddressBlockAssignment(
        id=1,
        registry="MA-S",
        assignment="8C1F64AFA",
        organization_name="DATA ELECTRONIC DEVICES, INC",
        organization_address="32 NORTHWESTERN DR SALEM NH US 03079",
    ),
    MacAddressBlockAssignment(
        id=2,
        registry="MA-S",
        assignment="8C1F649B9",
        organization_name="QUERCUS TECHNOLOGIES, S.L.",
        organization_address="Av. Onze de Setembre 19 Reus Tarragona ES",
    ),
    MacAddressBlockAssignment(
        id=3,
        registry="MA-S",
        assignment="8C1F64D0F",
        organization_name="Mecco LLC",
        organization_address="290 Executive Drive Cranberry Township PA US",
    ),
]

DEFAULT_MAC_ADDRESSES = [
    MacAddress(
        address="00:11:22:33:44:55",
        vlan_id=1,
        role_id=3,
        block_assignment_id=1,
        configuration_item_id=1,
        status="Active",
        description="Customer Portal service interface",
    ),
    MacAddress(
        address="00:11:22:33:44:66",
        vlan_id=2,
        role_id=2,
        block_assignment_id=1,
        configuration_item_id=3,
        status="Active",
        description="Edge Router A uplink interface",
    ),
]

DEFAULT_IP_ADDRESSES = [
    IpAddress(
        address="10.10.1.10",
        status="Active",
        role_id=1,
        configuration_item_id=1,
        description="Frontend service endpoint",
    ),
    IpAddress(
        address="10.10.1.11",
        status="Reserved",
        role_id=2,
        configuration_item_id=2,
        description="Database listener",
    ),
    IpAddress(
        address="10.10.2.1",
        status="Active",
        role_id=3,
        configuration_item_id=3,
        description="Infrastructure gateway",
    ),
]

DEFAULT_IP_PREFIXES = [
    IpPrefix(
        prefix="10.10.1.0/24",
        vrf_id=1,
        status="Active",
        site_id=1,
        description="Application subnet",
    ),
    IpPrefix(
        prefix="10.10.2.0/24",
        vrf_id=1,
        status="Active",
        site_id=1,
        description="Infrastructure subnet",
    ),
]

DEFAULT_REGIONAL_INTERNET_REGISTRIES = [
    RegionalInternetRegistry(
        id=1,
        name="African Network Information Centre",
        abbreviation="AFRINIC",
        region="Africa",
        description="Regional Internet Registry for Africa",
    ),
    RegionalInternetRegistry(
        id=2,
        name="Asia-Pacific Network Information Centre",
        abbreviation="APNIC",
        region="Asia Pacific",
        description="Regional Internet Registry for the Asia Pacific region",
    ),
    RegionalInternetRegistry(
        id=3,
        name="American Registry for Internet Numbers",
        abbreviation="ARIN",
        region="North America",
        description="Regional Internet Registry for North America",
    ),
    RegionalInternetRegistry(
        id=4,
        name="Latin America and Caribbean Network Information Centre",
        abbreviation="LACNIC",
        region="Latin America and Caribbean",
        description="Regional Internet Registry for Latin America and the Caribbean",
    ),
    RegionalInternetRegistry(
        id=5,
        name="RIPE Network Coordination Centre",
        abbreviation="RIPE NCC",
        region="Europe, Middle East, and parts of Central Asia",
        description="Regional Internet Registry for Europe, the Middle East, and parts of Central Asia",
    ),
    RegionalInternetRegistry(
        id=6,
        name="Private Address Space",
        abbreviation="Private",
        region="Internal",
        description="Internal non-public address allocations",
    ),
]

DEFAULT_IP_AGGREGATES = [
    IpAggregate(
        aggregate="10.10.0.0/16",
        rir_id=6,
        status="Active",
        description="Internal RFC1918 allocation for Assets starter data",
    ),
]

DEFAULT_AUTONOMOUS_SYSTEMS = [
    AutonomousSystem(
        asn=64512,
        name="Assets Lab Transit",
        rir_id=6,
        status="Active",
        description="Private ASN for internal transit routing",
    ),
    AutonomousSystem(
        asn=64513,
        name="Assets Lab Edge",
        rir_id=6,
        status="Reserved",
        description="Private ASN reserved for edge routing",
    ),
]

DEFAULT_IP_RANGES = [
    IpRange(
        start_address="10.10.1.100",
        end_address="10.10.1.149",
        status="Active",
        role_id=4,
        description="Workstation DHCP pool",
    ),
    IpRange(
        start_address="10.10.1.200",
        end_address="10.10.1.220",
        status="Reserved",
        role_id=5,
        description="Reserved static assignment pool",
    ),
]
