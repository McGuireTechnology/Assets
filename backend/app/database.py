from collections.abc import Generator

from sqlmodel import Session, SQLModel, create_engine, select

from app.config import DATABASE_URL, DEFAULT_SQLITE_PATH
from app.models import (
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
    AutonomousSystem,
    ConfigurationItem,
    IeeeRegistry,
    IpAddress,
    IpAggregate,
    IpPrefix,
    IpRange,
    L2Role,
    L3Role,
    MacAddressBlockAssignment,
    MacAddress,
    RegionalInternetRegistry,
    Site,
    Vlan,
    VirtualRoutingForwarding,
)


connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, echo=False, connect_args=connect_args, pool_pre_ping=True)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


def init_db() -> None:
    if DATABASE_URL.startswith("sqlite"):
        DEFAULT_SQLITE_PATH.parent.mkdir(parents=True, exist_ok=True)

    SQLModel.metadata.create_all(engine)
    ensure_sqlite_schema()

    with Session(engine) as session:
        seed_table(session, ConfigurationItem, DEFAULT_CONFIGURATION_ITEMS)
        seed_table(session, L3Role, DEFAULT_L3_ROLES)
        seed_table(session, L2Role, DEFAULT_L2_ROLES)
        seed_table(session, VirtualRoutingForwarding, DEFAULT_VIRTUAL_ROUTING_FORWARDINGS)
        seed_table(session, Site, DEFAULT_SITES)
        seed_table(session, Vlan, DEFAULT_VLANS)
        seed_table(session, IeeeRegistry, DEFAULT_IEEE_REGISTRIES)
        seed_table(
            session,
            MacAddressBlockAssignment,
            DEFAULT_MAC_ADDRESS_BLOCK_ASSIGNMENTS,
        )
        sync_default_records_by_id(session, IeeeRegistry, DEFAULT_IEEE_REGISTRIES)
        sync_default_records_by_id(
            session,
            MacAddressBlockAssignment,
            DEFAULT_MAC_ADDRESS_BLOCK_ASSIGNMENTS,
            insert_missing=False,
        )
        seed_table(session, MacAddress, DEFAULT_MAC_ADDRESSES)
        seed_table(session, IpAddress, DEFAULT_IP_ADDRESSES)
        seed_table(session, IpPrefix, DEFAULT_IP_PREFIXES)
        seed_table(
            session,
            RegionalInternetRegistry,
            DEFAULT_REGIONAL_INTERNET_REGISTRIES,
        )
        seed_table(session, AutonomousSystem, DEFAULT_AUTONOMOUS_SYSTEMS)
        seed_table(session, IpAggregate, DEFAULT_IP_AGGREGATES)
        seed_table(session, IpRange, DEFAULT_IP_RANGES)
        assign_existing_aggregates_to_private_rir(session)
        assign_existing_l3_role_flags(session)
        assign_existing_mac_block_assignment_fields(session)
        assign_existing_ipam_references(session)
        assign_existing_l2_references(session)


def seed_table(session: Session, model: type[SQLModel], records: list[SQLModel]) -> None:
    existing_item = session.exec(select(model)).first()

    if existing_item is None:
        session.add_all(records)
        session.commit()


def sync_default_records_by_id(
    session: Session,
    model: type[SQLModel],
    records: list[SQLModel],
    insert_missing: bool = True,
) -> None:
    changed = False

    for default_record in records:
        if default_record.id is None:
            continue

        existing_record = session.get(model, default_record.id)
        if existing_record is None:
            if insert_missing:
                session.add(default_record)
                changed = True
            continue

        for key, value in default_record.model_dump(exclude={"id"}).items():
            if getattr(existing_record, key, None) != value:
                setattr(existing_record, key, value)
                changed = True
        session.add(existing_record)

    if changed:
        session.commit()


def ensure_sqlite_schema() -> None:
    if not DATABASE_URL.startswith("sqlite"):
        return

    with engine.begin() as connection:
        aggregate_columns = {
            row[1]
            for row in connection.exec_driver_sql("PRAGMA table_info(ip_aggregates)").all()
        }

        if aggregate_columns and "rir_id" not in aggregate_columns:
            connection.exec_driver_sql("ALTER TABLE ip_aggregates ADD COLUMN rir_id INTEGER")

        address_columns = {
            row[1]
            for row in connection.exec_driver_sql("PRAGMA table_info(ip_addresses)").all()
        }
        if address_columns and "role_id" not in address_columns:
            connection.exec_driver_sql("ALTER TABLE ip_addresses ADD COLUMN role_id INTEGER")
        if address_columns and "configuration_item_id" not in address_columns:
            connection.exec_driver_sql(
                "ALTER TABLE ip_addresses ADD COLUMN configuration_item_id INTEGER"
            )

        prefix_columns = {
            row[1]
            for row in connection.exec_driver_sql("PRAGMA table_info(ip_prefixes)").all()
        }
        if prefix_columns and "vrf_id" not in prefix_columns:
            connection.exec_driver_sql("ALTER TABLE ip_prefixes ADD COLUMN vrf_id INTEGER")
        if prefix_columns and "site_id" not in prefix_columns:
            connection.exec_driver_sql("ALTER TABLE ip_prefixes ADD COLUMN site_id INTEGER")

        range_columns = {
            row[1]
            for row in connection.exec_driver_sql("PRAGMA table_info(ip_ranges)").all()
        }
        if range_columns and "role_id" not in range_columns:
            connection.exec_driver_sql("ALTER TABLE ip_ranges ADD COLUMN role_id INTEGER")

        role_columns = {
            row[1]
            for row in connection.exec_driver_sql("PRAGMA table_info(ip_roles)").all()
        }
        role_flag_columns = [
            "available_to_ip_addresses",
            "available_to_ip_ranges",
            "available_to_ip_prefixes",
            "available_to_ip_aggregates",
            "available_to_vrfs",
        ]
        for column_name in role_flag_columns:
            if role_columns and column_name not in role_columns:
                connection.exec_driver_sql(
                    f"ALTER TABLE ip_roles ADD COLUMN {column_name} BOOLEAN DEFAULT 0"
                )

        vlan_columns = {
            row[1]
            for row in connection.exec_driver_sql("PRAGMA table_info(vlans)").all()
        }
        if vlan_columns and "role_id" not in vlan_columns:
            connection.exec_driver_sql("ALTER TABLE vlans ADD COLUMN role_id INTEGER")

        mac_address_columns = {
            row[1]
            for row in connection.exec_driver_sql("PRAGMA table_info(mac_addresses)").all()
        }
        if mac_address_columns and "role_id" not in mac_address_columns:
            connection.exec_driver_sql("ALTER TABLE mac_addresses ADD COLUMN role_id INTEGER")
        if mac_address_columns and "block_assignment_id" not in mac_address_columns:
            connection.exec_driver_sql(
                "ALTER TABLE mac_addresses ADD COLUMN block_assignment_id INTEGER"
            )

        mac_block_columns = {
            row[1]
            for row in connection.exec_driver_sql(
                "PRAGMA table_info(mac_address_block_assignments)"
            ).all()
        }
        mac_block_text_columns = [
            "registry",
            "assignment",
            "organization_name",
            "organization_address",
        ]
        for column_name in mac_block_text_columns:
            if mac_block_columns and column_name not in mac_block_columns:
                connection.exec_driver_sql(
                    f"ALTER TABLE mac_address_block_assignments ADD COLUMN {column_name} TEXT"
                )


def assign_existing_aggregates_to_private_rir(session: Session) -> None:
    private_rir = session.exec(
        select(RegionalInternetRegistry).where(
            RegionalInternetRegistry.abbreviation == "Private"
        )
    ).first()

    if private_rir is None or private_rir.id is None:
        return

    aggregates = session.exec(select(IpAggregate)).all()
    changed = False

    for aggregate in aggregates:
        if aggregate.rir_id is None:
            aggregate.rir_id = private_rir.id
            session.add(aggregate)
            changed = True

    if changed:
        session.commit()


def assign_existing_l3_role_flags(session: Session) -> None:
    defaults_by_name = {
        record.name: record
        for record in DEFAULT_L3_ROLES
    }
    changed = False

    for role in session.exec(select(L3Role)).all():
        role_default = defaults_by_name.get(role.name)
        if role_default is None:
            continue

        if (
            not role.available_to_ip_addresses
            and not role.available_to_ip_ranges
            and not role.available_to_ip_prefixes
            and not role.available_to_ip_aggregates
            and not role.available_to_vrfs
        ):
            role.available_to_ip_addresses = role_default.available_to_ip_addresses
            role.available_to_ip_ranges = role_default.available_to_ip_ranges
            role.available_to_ip_prefixes = role_default.available_to_ip_prefixes
            role.available_to_ip_aggregates = role_default.available_to_ip_aggregates
            role.available_to_vrfs = role_default.available_to_vrfs
            session.add(role)
            changed = True

    if changed:
        session.commit()


def assign_existing_ipam_references(session: Session) -> None:
    role_by_name = {
        role.name: role.id
        for role in session.exec(select(L3Role)).all()
        if role.id is not None
    }
    configuration_item_by_name = {
        item.name: item.id
        for item in session.exec(select(ConfigurationItem)).all()
        if item.id is not None
    }
    vrf_by_name = {
        vrf.name: vrf.id
        for vrf in session.exec(select(VirtualRoutingForwarding)).all()
        if vrf.id is not None
    }
    site_by_name = {
        site.name: site.id
        for site in session.exec(select(Site)).all()
        if site.id is not None
    }

    address_defaults = {
        record.address: record
        for record in DEFAULT_IP_ADDRESSES
    }
    prefix_defaults = {
        record.prefix: record
        for record in DEFAULT_IP_PREFIXES
    }
    range_defaults = {
        (record.start_address, record.end_address): record
        for record in DEFAULT_IP_RANGES
    }

    changed = False

    for address in session.exec(select(IpAddress)).all():
        address_default = address_defaults.get(address.address)
        if address.role_id is None:
            address.role_id = role_by_name.get(legacy_value(address, "role"))
            if address.role_id is None and address_default is not None:
                address.role_id = address_default.role_id
            changed = True
        if address.configuration_item_id is None:
            address.configuration_item_id = configuration_item_by_name.get(
                legacy_value(address, "assigned_to")
            )
            if address.configuration_item_id is None and address_default is not None:
                address.configuration_item_id = address_default.configuration_item_id
            changed = True
        if changed:
            session.add(address)

    for prefix in session.exec(select(IpPrefix)).all():
        prefix_default = prefix_defaults.get(prefix.prefix)
        if prefix.vrf_id is None:
            prefix.vrf_id = vrf_by_name.get(legacy_value(prefix, "vrf"))
            if prefix.vrf_id is None and prefix_default is not None:
                prefix.vrf_id = prefix_default.vrf_id
            changed = True
        if prefix.site_id is None:
            prefix.site_id = site_by_name.get(legacy_value(prefix, "site"))
            if prefix.site_id is None and prefix_default is not None:
                prefix.site_id = prefix_default.site_id
            changed = True
        if changed:
            session.add(prefix)

    for address_range in session.exec(select(IpRange)).all():
        range_default = range_defaults.get(
            (address_range.start_address, address_range.end_address)
        )
        if address_range.role_id is None:
            address_range.role_id = role_by_name.get(legacy_value(address_range, "role"))
            if address_range.role_id is None and range_default is not None:
                address_range.role_id = range_default.role_id
            changed = True
        if changed:
            session.add(address_range)

    if changed:
        session.commit()


def assign_existing_mac_block_assignment_fields(session: Session) -> None:
    defaults_by_id = {
        record.id: record
        for record in DEFAULT_MAC_ADDRESS_BLOCK_ASSIGNMENTS
        if record.id is not None
    }
    changed = False

    for block_assignment in session.exec(select(MacAddressBlockAssignment)).all():
        block_default = defaults_by_id.get(block_assignment.id)
        if block_default is None:
            continue

        if block_assignment.registry is None:
            block_assignment.registry = block_default.registry
            changed = True
        if block_assignment.assignment is None:
            block_assignment.assignment = block_default.assignment
            changed = True
        if block_assignment.organization_name is None:
            block_assignment.organization_name = block_default.organization_name
            changed = True
        if block_assignment.organization_address is None:
            block_assignment.organization_address = block_default.organization_address
            changed = True

        if changed:
            session.add(block_assignment)

    if changed:
        session.commit()


def assign_existing_l2_references(session: Session) -> None:
    vlan_defaults = {
        record.vlan_id: record
        for record in DEFAULT_VLANS
    }
    mac_address_defaults = {
        record.address: record
        for record in DEFAULT_MAC_ADDRESSES
    }
    changed = False

    for vlan in session.exec(select(Vlan)).all():
        vlan_default = vlan_defaults.get(vlan.vlan_id)
        if vlan.role_id is None and vlan_default is not None:
            vlan.role_id = vlan_default.role_id
            session.add(vlan)
            changed = True

    for mac_address in session.exec(select(MacAddress)).all():
        mac_address_default = mac_address_defaults.get(mac_address.address)
        if mac_address.role_id is None and mac_address_default is not None:
            mac_address.role_id = mac_address_default.role_id
            session.add(mac_address)
            changed = True
        if mac_address.block_assignment_id is None and mac_address_default is not None:
            mac_address.block_assignment_id = mac_address_default.block_assignment_id
            session.add(mac_address)
            changed = True

    if changed:
        session.commit()


def legacy_value(model: SQLModel, field_name: str) -> str | None:
    return model.__dict__.get(field_name)
