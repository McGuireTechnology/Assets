<script setup lang="ts">
import { computed, onMounted, reactive, ref, type Component } from 'vue';
import {
  Blocks,
  Cable,
  Columns3,
  Database,
  EthernetPort,
  Globe,
  Hash,
  Layers,
  LayoutGrid,
  ListTodo,
  ListTree,
  MapPin,
  Network,
  PanelLeftClose,
  PanelLeftOpen,
  Pencil,
  Plus,
  Route,
  RefreshCw,
  Server,
  Table2,
  Tags,
  Trash2,
  X,
} from '@lucide/vue';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { NativeSelect } from '@/components/ui/native-select';
import { Sheet } from '@/components/ui/sheet';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Tooltip } from '@/components/ui/tooltip';

type AnyRecord = Record<string, boolean | string | number | null>;

type FieldConfig = {
  key: string;
  label: string;
  type?: 'boolean' | 'number' | 'text';
  options?: () => Array<{ label: string; value: number | null }>;
};

type ResourceConfig = {
  key: string;
  label: string;
  navLabel?: string;
  navTooltip?: string;
  icon: Component;
  group: string;
  endpoint: string;
  idField?: string;
  fields: FieldConfig[];
  columns: Array<{ key: string; label: string; resolve?: (record: AnyRecord) => string }>;
};

type HealthResponse = {
  status: string;
  service: string;
  database: string;
};

type ViewMode = 'table' | 'cards' | 'queue';

const apiBaseUrl =
  import.meta.env.VITE_API_BASE_URL ?? `${window.location.protocol}//${window.location.hostname}:8000`;

const health = ref<HealthResponse | null>(null);
const records = reactive<Record<string, AnyRecord[]>>({});
const selectedResourceKey = ref('ip-addresses');
const selectedRecordId = ref<number | null>(null);
const inspectorMode = ref<'read' | 'edit' | 'create'>('read');
const inspectorOpen = ref(false);
const navCollapsed = ref(false);
const viewMode = ref<ViewMode>('table');
const form = reactive<AnyRecord>({});
const error = ref('');
const saving = ref(false);

const selectedResource = computed(() => {
  return resources.find((resource) => resource.key === selectedResourceKey.value) ?? resources[0];
});

const resourceGroups = computed(() => {
  return resources.reduce<Array<{ label: string; resources: ResourceConfig[] }>>((groups, resource) => {
    const group = groups.find((item) => item.label === resource.group);

    if (group) {
      group.resources.push(resource);
    } else {
      groups.push({ label: resource.group, resources: [resource] });
    }

    return groups;
  }, []);
});

const selectedRecords = computed(() => records[selectedResource.value.key] ?? []);

const selectedRecord = computed(() => {
  if (selectedRecordId.value === null) return null;
  return (
    selectedRecords.value.find((record) => Number(record.id) === selectedRecordId.value) ?? null
  );
});

const inspectorTitle = computed(() => {
  if (inspectorMode.value === 'create') return `Create ${selectedResource.value.label}`;
  if (inspectorMode.value === 'edit') return `Edit ${selectedResource.value.label}`;
  return `Inspect ${selectedResource.value.label}`;
});

const healthyLabel = computed(() => {
  if (error.value) return 'API unavailable';
  if (!health.value) return 'Checking API';
  return `${health.value.service} ${health.value.status} on ${health.value.database}`;
});

const ipamObjectCount = computed(() => {
  return resources
    .filter((resource) => resource.key !== 'configuration-items')
    .reduce((total, resource) => total + (records[resource.key]?.length ?? 0), 0);
});

const configurationItems = computed(() => records['configuration-items'] ?? []);
const l2Roles = computed(() => records['l2-roles'] ?? []);
const vlanRoles = computed(() =>
  l2Roles.value.filter((role) => role.available_to_vlans),
);
const macAddressRoles = computed(() =>
  l2Roles.value.filter((role) => role.available_to_mac_addresses),
);
const l3Roles = computed(() => records['l3-roles'] ?? []);
const ipAddressRoles = computed(() =>
  l3Roles.value.filter((role) => role.available_to_ip_addresses),
);
const ipRangeRoles = computed(() =>
  l3Roles.value.filter((role) => role.available_to_ip_ranges),
);
const vrfs = computed(() => records['virtual-routing-forwardings'] ?? []);
const sites = computed(() => records.sites ?? []);
const registries = computed(() => records['regional-internet-registries'] ?? []);
const vlans = computed(() => records.vlans ?? []);
const ieeeRegistries = computed(() => records['ieee-registries'] ?? []);
const macAddressBlocks = computed(() => records['mac-address-block-assignments'] ?? []);

function byId(collection: AnyRecord[], id: boolean | string | number | null, fallback = 'Unassigned') {
  if (typeof id === 'boolean' || id === null || id === '') return fallback;

  const match = collection.find((item) => item.id === Number(id));
  return String(match?.name ?? match?.abbreviation ?? fallback);
}

function optionList(collection: AnyRecord[], labelKey = 'name') {
  return [
    { label: 'Unassigned', value: null },
    ...collection.map((item) => ({
      label: String(item[labelKey] ?? item.name ?? item.id),
      value: Number(item.id),
    })),
  ];
}

function vlanLabel(id: boolean | string | number | null, fallback = 'Unassigned') {
  if (typeof id === 'boolean' || id === null || id === '') return fallback;

  const match = vlans.value.find((vlan) => vlan.id === Number(id));
  if (!match) return fallback;

  return `${match.vlan_id} - ${match.name}`;
}

function vlanOptionList() {
  return [
    { label: 'Unassigned', value: null },
    ...vlans.value.map((vlan) => ({
      label: `${vlan.vlan_id} - ${vlan.name}`,
      value: Number(vlan.id),
    })),
  ];
}

function macAddressBlockLabel(id: boolean | string | number | null, fallback = 'Unassigned') {
  if (typeof id === 'boolean' || id === null || id === '') return fallback;

  const match = macAddressBlocks.value.find((block) => block.id === Number(id));
  if (!match) return fallback;

  return `${match.assignment} - ${match.organization_name}`;
}

function macAddressBlockOptionList() {
  return [
    { label: 'Unassigned', value: null },
    ...macAddressBlocks.value.map((block) => ({
      label: `${block.assignment} - ${block.organization_name}`,
      value: Number(block.id),
    })),
  ];
}

function compactCount(value: number) {
  if (value < 10000) return String(value);

  return `${Math.floor(value / 1000)}k`;
}

function resourceTooltip(resource: ResourceConfig) {
  const title = resource.navTooltip ?? resource.label;
  return {
    count: records[resource.key]?.length ?? 0,
    title,
  };
}

const resources: ResourceConfig[] = [
  {
    key: 'configuration-items',
    label: 'Configuration Items',
    icon: Database,
    group: 'Core',
    endpoint: '/api/configuration-items',
    fields: [
      { key: 'name', label: 'Name' },
      { key: 'type', label: 'Type' },
      { key: 'owner', label: 'Owner' },
      { key: 'status', label: 'Status' },
    ],
    columns: [
      { key: 'name', label: 'Name' },
      { key: 'type', label: 'Type' },
      { key: 'owner', label: 'Owner' },
      { key: 'status', label: 'Status' },
    ],
  },
  {
    key: 'l2-roles',
    label: 'L2 Roles',
    icon: Tags,
    group: 'L2 Address Management',
    endpoint: '/api/l2/roles',
    fields: [
      { key: 'name', label: 'Name' },
      { key: 'available_to_vlans', label: 'Available to VLANs', type: 'boolean' },
      { key: 'available_to_mac_addresses', label: 'Available to MAC Addresses', type: 'boolean' },
      { key: 'description', label: 'Description' },
    ],
    columns: [
      { key: 'name', label: 'Name' },
      { key: 'availability', label: 'Available To', resolve: (record) => l2RoleAvailability(record) },
      { key: 'description', label: 'Description' },
    ],
  },
  {
    key: 'ieee-registries',
    label: 'IEEE Registries',
    icon: Globe,
    group: 'L2 Address Management',
    endpoint: '/api/l2/ieee-registries',
    fields: [
      { key: 'name', label: 'Name' },
      { key: 'abbreviation', label: 'Abbreviation' },
      { key: 'scope', label: 'Scope' },
      { key: 'description', label: 'Description' },
    ],
    columns: [
      { key: 'abbreviation', label: 'Registry' },
      { key: 'name', label: 'Name' },
      { key: 'scope', label: 'Scope' },
    ],
  },
  {
    key: 'mac-address-block-assignments',
    label: 'MAC Address Block Assignments',
    navLabel: 'MAC Blocks',
    navTooltip: 'MAC Address Block Assignments',
    icon: Blocks,
    group: 'L2 Address Management',
    endpoint: '/api/l2/mac-address-block-assignments',
    fields: [
      { key: 'registry', label: 'Registry' },
      { key: 'assignment', label: 'Assignment' },
      { key: 'organization_name', label: 'Organization Name' },
      { key: 'organization_address', label: 'Organization Address' },
    ],
    columns: [
      { key: 'registry', label: 'Registry' },
      { key: 'assignment', label: 'Assignment' },
      { key: 'organization_name', label: 'Organization Name' },
      { key: 'organization_address', label: 'Organization Address' },
    ],
  },
  {
    key: 'vlans',
    label: 'VLANs',
    icon: Cable,
    group: 'L2 Address Management',
    endpoint: '/api/l2/vlans',
    fields: [
      { key: 'vlan_id', label: 'VLAN ID', type: 'number' },
      { key: 'name', label: 'Name' },
      { key: 'role_id', label: 'Role', type: 'number', options: () => optionList(vlanRoles.value) },
      { key: 'site_id', label: 'Site', type: 'number', options: () => optionList(sites.value) },
      { key: 'status', label: 'Status' },
      { key: 'description', label: 'Description' },
    ],
    columns: [
      { key: 'vlan_id', label: 'VLAN' },
      { key: 'name', label: 'Name' },
      { key: 'role_id', label: 'Role', resolve: (record) => byId(l2Roles.value, record.role_id) },
      { key: 'site_id', label: 'Site', resolve: (record) => byId(sites.value, record.site_id) },
      { key: 'status', label: 'Status' },
    ],
  },
  {
    key: 'mac-addresses',
    label: 'MAC Addresses',
    icon: EthernetPort,
    group: 'L2 Address Management',
    endpoint: '/api/l2/mac-addresses',
    fields: [
      { key: 'address', label: 'MAC Address' },
      { key: 'vlan_id', label: 'VLAN', type: 'number', options: () => vlanOptionList() },
      { key: 'role_id', label: 'Role', type: 'number', options: () => optionList(macAddressRoles.value) },
      {
        key: 'block_assignment_id',
        label: 'MAC Block',
        type: 'number',
        options: () => macAddressBlockOptionList(),
      },
      {
        key: 'configuration_item_id',
        label: 'Configuration Item',
        type: 'number',
        options: () => optionList(configurationItems.value),
      },
      { key: 'status', label: 'Status' },
      { key: 'description', label: 'Description' },
    ],
    columns: [
      { key: 'address', label: 'MAC Address' },
      { key: 'vlan_id', label: 'VLAN', resolve: (record) => vlanLabel(record.vlan_id) },
      { key: 'role_id', label: 'Role', resolve: (record) => byId(l2Roles.value, record.role_id) },
      {
        key: 'block_assignment_id',
        label: 'MAC Block',
        resolve: (record) => macAddressBlockLabel(record.block_assignment_id),
      },
      {
        key: 'configuration_item_id',
        label: 'Assigned To',
        resolve: (record) => byId(configurationItems.value, record.configuration_item_id),
      },
      { key: 'status', label: 'Status' },
    ],
  },
  {
    key: 'ip-addresses',
    label: 'IP Addresses',
    icon: Server,
    group: 'L3 Address Management',
    endpoint: '/api/ipam/ip-addresses',
    fields: [
      { key: 'address', label: 'Address' },
      { key: 'role_id', label: 'Role', type: 'number', options: () => optionList(ipAddressRoles.value) },
      {
        key: 'configuration_item_id',
        label: 'Configuration Item',
        type: 'number',
        options: () => optionList(configurationItems.value),
      },
      { key: 'status', label: 'Status' },
      { key: 'description', label: 'Description' },
    ],
    columns: [
      { key: 'address', label: 'Address' },
      { key: 'role_id', label: 'Role', resolve: (record) => byId(l3Roles.value, record.role_id) },
      {
        key: 'configuration_item_id',
        label: 'Assigned To',
        resolve: (record) => byId(configurationItems.value, record.configuration_item_id),
      },
      { key: 'status', label: 'Status' },
    ],
  },
  {
    key: 'ip-prefixes',
    label: 'IP Prefixes',
    icon: Network,
    group: 'L3 Address Management',
    endpoint: '/api/ipam/ip-prefixes',
    fields: [
      { key: 'prefix', label: 'Prefix' },
      { key: 'vrf_id', label: 'VRF', type: 'number', options: () => optionList(vrfs.value) },
      { key: 'site_id', label: 'Site', type: 'number', options: () => optionList(sites.value) },
      { key: 'status', label: 'Status' },
      { key: 'description', label: 'Description' },
    ],
    columns: [
      { key: 'prefix', label: 'Prefix' },
      { key: 'vrf_id', label: 'VRF', resolve: (record) => byId(vrfs.value, record.vrf_id) },
      { key: 'site_id', label: 'Site', resolve: (record) => byId(sites.value, record.site_id) },
      { key: 'status', label: 'Status' },
    ],
  },
  {
    key: 'ip-aggregates',
    label: 'IP Aggregates',
    icon: Layers,
    group: 'L3 Address Management',
    endpoint: '/api/ipam/ip-aggregates',
    fields: [
      { key: 'aggregate', label: 'Aggregate' },
      {
        key: 'rir_id',
        label: 'Registry',
        type: 'number',
        options: () => optionList(registries.value, 'abbreviation'),
      },
      { key: 'status', label: 'Status' },
      { key: 'description', label: 'Description' },
    ],
    columns: [
      { key: 'aggregate', label: 'Aggregate' },
      {
        key: 'rir_id',
        label: 'Registry',
        resolve: (record) => byId(registries.value, record.rir_id),
      },
      { key: 'status', label: 'Status' },
    ],
  },
  {
    key: 'ip-ranges',
    label: 'IP Ranges',
    icon: ListTree,
    group: 'L3 Address Management',
    endpoint: '/api/ipam/ip-ranges',
    fields: [
      { key: 'start_address', label: 'Start Address' },
      { key: 'end_address', label: 'End Address' },
      { key: 'role_id', label: 'Role', type: 'number', options: () => optionList(ipRangeRoles.value) },
      { key: 'status', label: 'Status' },
      { key: 'description', label: 'Description' },
    ],
    columns: [
      { key: 'start_address', label: 'Start' },
      { key: 'end_address', label: 'End' },
      { key: 'role_id', label: 'Role', resolve: (record) => byId(l3Roles.value, record.role_id) },
      { key: 'status', label: 'Status' },
    ],
  },
  {
    key: 'autonomous-systems',
    label: 'AS Numbers',
    navTooltip: 'Autonomous System Numbers',
    icon: Hash,
    group: 'L3 Address Management',
    endpoint: '/api/ipam/autonomous-systems',
    fields: [
      { key: 'asn', label: 'ASN', type: 'number' },
      { key: 'name', label: 'Name' },
      {
        key: 'rir_id',
        label: 'Registry',
        type: 'number',
        options: () => optionList(registries.value, 'abbreviation'),
      },
      { key: 'status', label: 'Status' },
      { key: 'description', label: 'Description' },
    ],
    columns: [
      { key: 'asn', label: 'ASN' },
      { key: 'name', label: 'Name' },
      {
        key: 'rir_id',
        label: 'Registry',
        resolve: (record) => byId(registries.value, record.rir_id),
      },
      { key: 'status', label: 'Status' },
    ],
  },
  {
    key: 'l3-roles',
    label: 'L3 Roles',
    icon: Tags,
    group: 'L3 Address Management',
    endpoint: '/api/l3/roles',
    fields: [
      { key: 'name', label: 'Name' },
      { key: 'available_to_ip_addresses', label: 'Available to IP Addresses', type: 'boolean' },
      { key: 'available_to_ip_ranges', label: 'Available to IP Ranges', type: 'boolean' },
      { key: 'available_to_ip_prefixes', label: 'Available to IP Prefixes', type: 'boolean' },
      { key: 'available_to_ip_aggregates', label: 'Available to IP Aggregates', type: 'boolean' },
      { key: 'available_to_vrfs', label: 'Available to VRFs', type: 'boolean' },
      { key: 'description', label: 'Description' },
    ],
    columns: [
      { key: 'name', label: 'Name' },
      { key: 'availability', label: 'Available To', resolve: (record) => l3RoleAvailability(record) },
      { key: 'description', label: 'Description' },
    ],
  },
  {
    key: 'virtual-routing-forwardings',
    label: 'VRFs',
    navTooltip: 'Virtual Routing and Forwarding',
    icon: Route,
    group: 'L3 Address Management',
    endpoint: '/api/ipam/virtual-routing-forwardings',
    fields: [
      { key: 'name', label: 'Name' },
      { key: 'route_distinguisher', label: 'Route Distinguisher' },
      { key: 'description', label: 'Description' },
    ],
    columns: [
      { key: 'name', label: 'Name' },
      { key: 'route_distinguisher', label: 'RD' },
      { key: 'description', label: 'Description' },
    ],
  },
  {
    key: 'sites',
    label: 'Sites',
    icon: MapPin,
    group: 'Organization',
    endpoint: '/api/ipam/sites',
    fields: [
      { key: 'name', label: 'Name' },
      { key: 'status', label: 'Status' },
      { key: 'description', label: 'Description' },
    ],
    columns: [
      { key: 'name', label: 'Name' },
      { key: 'status', label: 'Status' },
      { key: 'description', label: 'Description' },
    ],
  },
  {
    key: 'regional-internet-registries',
    label: 'Regional Internet Registries',
    navLabel: 'RIRs',
    navTooltip: 'Regional Internet Registries',
    icon: Globe,
    group: 'L3 Address Management',
    endpoint: '/api/ipam/regional-internet-registries',
    fields: [
      { key: 'name', label: 'Name' },
      { key: 'abbreviation', label: 'Abbreviation' },
      { key: 'region', label: 'Region' },
      { key: 'description', label: 'Description' },
    ],
    columns: [
      { key: 'abbreviation', label: 'Registry' },
      { key: 'name', label: 'Name' },
      { key: 'region', label: 'Region' },
    ],
  },
];

function displayValue(record: AnyRecord, column: ResourceConfig['columns'][number]) {
  if (column.resolve) return column.resolve(record);
  return String(record[column.key] ?? 'None');
}

function primaryColumn() {
  return selectedResource.value.columns[0];
}

function secondaryColumns() {
  return selectedResource.value.columns.slice(1, 4);
}

function primaryValue(record: AnyRecord) {
  return displayValue(record, primaryColumn());
}

function l2RoleAvailability(record: AnyRecord) {
  const availability = [
    ['VLANs', record.available_to_vlans],
    ['MAC Addresses', record.available_to_mac_addresses],
  ]
    .filter(([, enabled]) => enabled)
    .map(([label]) => label);

  return availability.length > 0 ? availability.join(', ') : 'None';
}

function l3RoleAvailability(record: AnyRecord) {
  const availability = [
    ['Addresses', record.available_to_ip_addresses],
    ['Ranges', record.available_to_ip_ranges],
    ['Prefixes', record.available_to_ip_prefixes],
    ['Aggregates', record.available_to_ip_aggregates],
    ['VRFs', record.available_to_vrfs],
  ]
    .filter(([, enabled]) => enabled)
    .map(([label]) => label);

  return availability.length > 0 ? availability.join(', ') : 'None';
}

function displayFieldValue(record: AnyRecord, field: FieldConfig) {
  const value = record[field.key];

  if (field.type === 'boolean') return value ? 'Yes' : 'No';

  if (value === null || value === '') return 'Unassigned';

  if (field.options) {
    const option = field.options().find((item) => item.value === Number(value));
    return option?.label ?? 'Unassigned';
  }

  return String(value ?? 'None');
}

function emptyForm() {
  selectedResource.value.fields.forEach((field) => {
    form[field.key] = field.type === 'boolean' ? false : field.type === 'number' ? null : '';
  });
}

function loadForm(record: AnyRecord) {
  selectedResource.value.fields.forEach((field) => {
    form[field.key] =
      record[field.key] ?? (field.type === 'boolean' ? false : field.type === 'number' ? null : '');
  });
}

function selectResource(key: string) {
  selectedResourceKey.value = key;
  closeInspector();
}

function selectViewMode(mode: ViewMode) {
  viewMode.value = mode;
}

function openInspector(record: AnyRecord) {
  inspectorOpen.value = true;
  inspectorMode.value = 'read';
  selectedRecordId.value = Number(record.id);
  emptyForm();
}

function openCreateInspector() {
  inspectorOpen.value = true;
  inspectorMode.value = 'create';
  selectedRecordId.value = null;
  emptyForm();
}

function openEditInspector() {
  if (!selectedRecord.value) return;
  inspectorMode.value = 'edit';
  loadForm(selectedRecord.value);
}

function cancelInspectorForm() {
  if (inspectorMode.value === 'edit') {
    inspectorMode.value = 'read';
    emptyForm();
    return;
  }

  closeInspector();
}

function closeInspector() {
  inspectorOpen.value = false;
  inspectorMode.value = 'read';
  selectedRecordId.value = null;
  emptyForm();
}

function payloadFromForm() {
  return selectedResource.value.fields.reduce<AnyRecord>((payload, field) => {
    const value = form[field.key];
    if (field.type === 'boolean') {
      payload[field.key] = Boolean(value);
    } else {
      payload[field.key] = field.type === 'number' && value !== null ? Number(value) : value || null;
    }
    return payload;
  }, {});
}

async function requestJson<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${apiBaseUrl}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });

  if (!response.ok) {
    throw new Error(await response.text());
  }

  return response.json();
}

async function loadDashboard() {
  error.value = '';

  try {
    health.value = await requestJson<HealthResponse>('/health');

    await Promise.all(
      resources.map(async (resource) => {
        records[resource.key] = await requestJson<AnyRecord[]>(resource.endpoint);
      }),
    );
  } catch (event) {
    error.value = event instanceof Error ? event.message : 'Unable to reach the API.';
  }
}

async function saveRecord() {
  saving.value = true;
  error.value = '';

  try {
    const endpoint =
      inspectorMode.value === 'create'
        ? selectedResource.value.endpoint
        : `${selectedResource.value.endpoint}/${selectedRecordId.value}`;
    const method = inspectorMode.value === 'create' ? 'POST' : 'PUT';

    const savedRecord = await requestJson<AnyRecord>(endpoint, {
      method,
      body: JSON.stringify(payloadFromForm()),
    });

    await loadDashboard();

    if (inspectorMode.value === 'create') {
      closeInspector();
    } else {
      selectedRecordId.value = Number(savedRecord.id);
      inspectorMode.value = 'read';
      emptyForm();
    }
  } catch (event) {
    error.value = event instanceof Error ? event.message : 'Unable to save record.';
  } finally {
    saving.value = false;
  }
}

async function deleteRecord(record: AnyRecord) {
  error.value = '';

  try {
    await fetch(`${apiBaseUrl}${selectedResource.value.endpoint}/${record.id}`, {
      method: 'DELETE',
    }).then((response) => {
      if (!response.ok) throw new Error('Unable to delete record.');
    });

    if (selectedRecordId.value === Number(record.id)) closeInspector();
    await loadDashboard();
  } catch (event) {
    error.value = event instanceof Error ? event.message : 'Unable to delete record.';
  }
}

onMounted(async () => {
  emptyForm();
  await loadDashboard();
});
</script>

<template>
  <main class="console-shell" :class="{ 'nav-collapsed': navCollapsed }">
    <aside class="console-nav" aria-label="Resource navigation">
      <div class="brand-block">
        <div class="brand-copy">
          <p class="eyebrow">McGuire Technology, LLC</p>
          <h1>Assets</h1>
        </div>
        <Button
          type="button"
          class="nav-toggle"
          variant="secondary"
          size="icon"
          :title="navCollapsed ? 'Expand navigation' : 'Collapse navigation'"
          @click="navCollapsed = !navCollapsed"
        >
          <PanelLeftOpen v-if="navCollapsed" />
          <PanelLeftClose v-else />
        </Button>
      </div>

      <nav class="resource-nav">
        <section v-for="group in resourceGroups" :key="group.label" class="nav-group">
          <h2>{{ group.label }}</h2>
          <Tooltip
            v-for="resource in group.resources"
            :key="resource.key"
            :count="resourceTooltip(resource).count"
            :text="resourceTooltip(resource).title"
          >
            <Button
              type="button"
              variant="ghost"
              :aria-label="resource.label"
              :class="{ active: resource.key === selectedResource.key }"
              @click="selectResource(resource.key)"
            >
              <component :is="resource.icon" class="nav-icon" aria-hidden="true" />
              <span class="nav-label">{{ resource.navLabel ?? resource.label }}</span>
              <Badge
                class="nav-count"
                variant="secondary"
              >
                {{ compactCount(records[resource.key]?.length ?? 0) }}
              </Badge>
            </Button>
          </Tooltip>
        </section>
      </nav>

      <div class="nav-status">
        <span class="label">API Status</span>
        <strong>{{ healthyLabel }}</strong>
        <span class="label">Assets</span>
        <strong>{{ configurationItems.length }}</strong>
        <span class="label">Network Objects</span>
        <strong>{{ ipamObjectCount }}</strong>
      </div>
    </aside>

    <section class="primary-view" aria-label="Resource list">
      <header class="primary-header">
        <div>
          <p class="eyebrow">Resource Type</p>
          <h2>{{ selectedResource.label }}</h2>
        </div>
        <div class="primary-actions">
          <div class="view-switcher" aria-label="Resource view selector">
            <Button
              type="button"
              :variant="viewMode === 'table' ? 'default' : 'secondary'"
              size="sm"
              @click="selectViewMode('table')"
            >
              <Table2 />
              Table
            </Button>
            <Button
              type="button"
              :variant="viewMode === 'cards' ? 'default' : 'secondary'"
              size="sm"
              @click="selectViewMode('cards')"
            >
              <LayoutGrid />
              Cards
            </Button>
            <Button
              type="button"
              :variant="viewMode === 'queue' ? 'default' : 'secondary'"
              size="sm"
              @click="selectViewMode('queue')"
            >
              <ListTodo />
              Queue
            </Button>
          </div>
          <Button type="button" variant="secondary" @click="loadDashboard">
            <RefreshCw />
            Refresh
          </Button>
          <Button type="button" @click="openCreateInspector">
            <Plus />
            Create
          </Button>
        </div>
      </header>

      <p v-if="error" class="notice">{{ error }}</p>

      <section class="list-panel">
        <div v-if="viewMode === 'table'" class="table-wrap">
          <Table class="min-w-[680px]">
            <TableHeader>
              <TableRow>
                <TableHead v-for="column in selectedResource.columns" :key="column.key">
                  {{ column.label }}
                </TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              <TableRow
                v-for="record in selectedRecords"
                :key="String(record.id)"
                class="selectable-row"
                :class="{ selected: selectedRecordId === Number(record.id) && inspectorOpen }"
                @click="openInspector(record)"
              >
                <TableCell v-for="column in selectedResource.columns" :key="column.key">
                  {{ displayValue(record, column) }}
                </TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </div>

        <div v-else-if="viewMode === 'cards'" class="card-view">
          <article
            v-for="record in selectedRecords"
            :key="String(record.id)"
            class="resource-card"
            :class="{ selected: selectedRecordId === Number(record.id) && inspectorOpen }"
            @click="openInspector(record)"
          >
            <header>
              <div>
                <p class="eyebrow">{{ selectedResource.label }}</p>
                <h3>{{ primaryValue(record) }}</h3>
              </div>
              <Badge>{{ String(record.status ?? record.id ?? 'Open') }}</Badge>
            </header>
            <dl>
              <div v-for="column in secondaryColumns()" :key="column.key">
                <dt>{{ column.label }}</dt>
                <dd>{{ displayValue(record, column) }}</dd>
              </div>
            </dl>
          </article>
        </div>

        <div v-else class="queue-workspace">
          <div class="queue-view">
            <button
              v-for="(record, index) in selectedRecords"
              :key="String(record.id)"
              type="button"
              class="queue-item"
              :class="{ selected: selectedRecordId === Number(record.id) && inspectorOpen }"
              @click="openInspector(record)"
            >
              <span class="queue-rank">{{ index + 1 }}</span>
              <span class="queue-main">
                <strong>{{ primaryValue(record) }}</strong>
                <span>{{ secondaryColumns().map((column) => displayValue(record, column)).join(' / ') }}</span>
              </span>
              <Columns3 />
            </button>
          </div>

          <aside class="inspector inline-inspector" aria-label="Queue inspector">
            <template v-if="inspectorOpen">
              <header class="inspector-header">
                <div>
                  <p class="eyebrow">{{ inspectorMode === 'create' ? 'Create' : 'Inspector' }}</p>
                  <h2>{{ inspectorTitle }}</h2>
                </div>
                <Button
                  type="button"
                  class="icon-button"
                  variant="secondary"
                  size="icon"
                  title="Clear inspector"
                  @click="closeInspector"
                >
                  <X />
                </Button>
              </header>

              <section v-if="inspectorMode === 'read' && selectedRecord" class="inspector-form">
                <dl class="read-fields">
                  <div v-for="field in selectedResource.fields" :key="field.key" class="read-field">
                    <dt>{{ field.label }}</dt>
                    <dd>{{ displayFieldValue(selectedRecord, field) }}</dd>
                  </div>
                </dl>

                <div class="form-actions">
                  <Button type="button" @click="openEditInspector">
                    <Pencil />
                    Edit
                  </Button>
                  <Button
                    type="button"
                    variant="destructive"
                    @click="deleteRecord({ id: selectedRecordId })"
                  >
                    <Trash2 />
                    Delete
                  </Button>
                </div>
              </section>

              <form v-else class="editor inspector-form" @submit.prevent="saveRecord">
                <Label v-for="field in selectedResource.fields" :key="field.key">
                  <span v-if="field.type !== 'boolean'">{{ field.label }}</span>
                  <label v-if="field.type === 'boolean'" class="checkbox-field">
                    <input v-model="form[field.key]" type="checkbox" />
                    <span>{{ field.label }}</span>
                  </label>
                  <NativeSelect v-if="field.options" v-model="form[field.key]">
                    <option
                      v-for="option in field.options()"
                      :key="`${field.key}-${option.value ?? 'null'}`"
                      :value="option.value"
                    >
                      {{ option.label }}
                    </option>
                  </NativeSelect>
                  <Input
                    v-else-if="field.type !== 'boolean'"
                    v-model="form[field.key]"
                    :type="field.type ?? 'text'"
                  />
                </Label>

                <div class="form-actions">
                  <Button type="submit" :disabled="saving">
                    <Plus v-if="inspectorMode === 'create'" />
                    {{ inspectorMode === 'create' ? 'Create' : 'Update' }}
                  </Button>
                  <Button
                    type="button"
                    variant="secondary"
                    @click="cancelInspectorForm"
                  >
                    Cancel
                  </Button>
                  <Button
                    v-if="inspectorMode === 'edit'"
                    type="button"
                    variant="destructive"
                    @click="deleteRecord({ id: selectedRecordId })"
                  >
                    <Trash2 />
                    Delete
                  </Button>
                </div>
              </form>
            </template>

            <div v-else class="empty-inspector">
              <p class="eyebrow">Inspector</p>
              <h2>No Object Selected</h2>
            </div>
          </aside>
        </div>
      </section>
    </section>

    <Sheet v-if="viewMode !== 'queue'" v-model:open="inspectorOpen" :title="inspectorTitle">
      <aside class="inspector" aria-label="Object inspector">
      <template v-if="inspectorOpen">
        <header class="inspector-header">
          <div>
            <p class="eyebrow">{{ inspectorMode === 'create' ? 'Create' : 'Inspector' }}</p>
            <h2>{{ inspectorTitle }}</h2>
          </div>
          <Button
            type="button"
            class="icon-button"
            variant="secondary"
            size="icon"
            title="Close inspector"
            @click="closeInspector"
          >
            <X />
          </Button>
        </header>

        <section v-if="inspectorMode === 'read' && selectedRecord" class="inspector-form">
          <dl class="read-fields">
            <div v-for="field in selectedResource.fields" :key="field.key" class="read-field">
              <dt>{{ field.label }}</dt>
              <dd>{{ displayFieldValue(selectedRecord, field) }}</dd>
            </div>
          </dl>

          <div class="form-actions">
            <Button type="button" @click="openEditInspector">
              <Pencil />
              Edit
            </Button>
            <Button
              type="button"
              variant="destructive"
              @click="deleteRecord({ id: selectedRecordId })"
            >
              <Trash2 />
              Delete
            </Button>
          </div>
        </section>

        <form v-else class="editor inspector-form" @submit.prevent="saveRecord">
          <Label v-for="field in selectedResource.fields" :key="field.key">
            <span v-if="field.type !== 'boolean'">{{ field.label }}</span>
            <label v-if="field.type === 'boolean'" class="checkbox-field">
              <input v-model="form[field.key]" type="checkbox" />
              <span>{{ field.label }}</span>
            </label>
            <NativeSelect v-if="field.options" v-model="form[field.key]">
              <option
                v-for="option in field.options()"
                :key="`${field.key}-${option.value ?? 'null'}`"
                :value="option.value"
              >
                {{ option.label }}
              </option>
            </NativeSelect>
            <Input
              v-else-if="field.type !== 'boolean'"
              v-model="form[field.key]"
              :type="field.type ?? 'text'"
            />
          </Label>

          <div class="form-actions">
            <Button type="submit" :disabled="saving">
              <Plus v-if="inspectorMode === 'create'" />
              {{ inspectorMode === 'create' ? 'Create' : 'Update' }}
            </Button>
            <Button
              type="button"
              variant="secondary"
              @click="cancelInspectorForm"
            >
              Cancel
            </Button>
            <Button
              v-if="inspectorMode === 'edit'"
              type="button"
              variant="destructive"
              @click="deleteRecord({ id: selectedRecordId })"
            >
              <Trash2 />
              Delete
            </Button>
          </div>
        </form>
      </template>

      <div v-else class="empty-inspector">
        <p class="eyebrow">Inspector</p>
        <h2>No Object Selected</h2>
      </div>
      </aside>
    </Sheet>
  </main>
</template>
