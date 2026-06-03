# API

The backend exposes a small starter API.

## Health

`GET /health`

Returns service status.

The response includes `database: sqlite` for the default local development database.

## Configuration Items

`GET /api/configuration-items`

Returns known configuration items with name, type, owner, and status fields.

## L2 Address Management

Each object endpoint supports standard CRUD operations:

- `GET /collection`
- `POST /collection`
- `GET /collection/{id}`
- `PUT /collection/{id}`
- `DELETE /collection/{id}`

`GET /api/l2/vlans`

Returns VLAN records. VLANs can reference L2 roles and sites by id.

`GET /api/l2/roles`

Returns L2 role records. Roles include boolean availability flags for VLANs and MAC addresses.

`GET /api/l2/ieee-registries`

Returns IEEE registry records for MAC and EUI assignment authorities.

`GET /api/l2/mac-address-block-assignments`

Returns MAC address block assignment records from IEEE registry files. The primary columns are `registry`, `assignment`, `organization_name`, and `organization_address`.

`GET /api/l2/mac-addresses`

Returns MAC address records. MAC addresses can reference VLANs, L2 roles, MAC address block assignments, and configuration items by id.

## L3 Address Management

Each object endpoint supports standard CRUD operations:

- `GET /collection`
- `POST /collection`
- `GET /collection/{id}`
- `PUT /collection/{id}`
- `DELETE /collection/{id}`

`GET /api/ipam/ip-addresses`

Returns IP address records. Addresses reference IP roles and configuration items by id.

`GET /api/ipam/ip-prefixes`

Returns IP prefix records. Prefixes reference VRFs and sites by id.

`GET /api/l3/roles`

Returns L3 role records. Roles include boolean availability flags for IP addresses, ranges, prefixes, aggregates, and VRFs.

`GET /api/ipam/virtual-routing-forwardings`

Returns virtual routing and forwarding records.

`GET /api/ipam/sites`

Returns site records.

`GET /api/ipam/regional-internet-registries`

Returns Regional Internet Registry records.

`GET /api/ipam/autonomous-systems`

Returns Autonomous System number records. Each AS number can reference a Regional Internet Registry by `rir_id`.

`GET /api/ipam/ip-aggregates`

Returns IP aggregate records. Each aggregate includes `rir_id`, assigning it to a Regional Internet Registry.

`GET /api/ipam/ip-ranges`

Returns IP range records. Ranges reference IP roles by id.
