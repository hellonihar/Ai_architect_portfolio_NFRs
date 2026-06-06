import { useEffect, useState } from "react";
import {
  Badge,
  Card,
  Group,
  Paper,
  SimpleGrid,
  Stack,
  Table,
  Text,
  Timeline,
  Title,
} from "@mantine/core";
import {
  IconCertificate,
  IconChecks,
  IconClock,
  IconExclamationCircle,
  IconRefresh,
} from "@tabler/icons-react";

import { api, type ComplianceStatusItem } from "../api/client";

const STATUS_BADGE: Record<string, { color: string; icon: React.ReactNode }> = {
  Passed: { color: "green", icon: <IconChecks size={14} /> },
  Failed: { color: "red", icon: <IconExclamationCircle size={14} /> },
  Pending: { color: "gray", icon: <IconClock size={14} /> },
  "In Progress": { color: "blue", icon: <IconRefresh size={14} /> },
};

export default function Compliance() {
  const [items, setItems] = useState<ComplianceStatusItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.compliance.list()
      .then(setItems)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const passed = items.filter((i) => i.status === "Passed").length;
  const failed = items.filter((i) => i.status === "Failed").length;
  const inProgress = items.filter(
    (i) => i.status === "In Progress" || i.status === "Pending"
  ).length;

  if (loading) return <Text>Loading compliance data...</Text>;

  return (
    <Stack gap="lg">
      <Title order={3}>Compliance Status</Title>

      <SimpleGrid cols={{ base: 1, sm: 3 }}>
        <Card withBorder padding="lg" bg="green.0">
          <Group>
            <IconChecks size={28} color="var(--mantine-color-green-6)" />
            <div>
              <Text size="xs" c="dimmed">Passed</Text>
              <Text size="xl" fw={700}>{passed}</Text>
            </div>
          </Group>
        </Card>
        <Card withBorder padding="lg" bg="red.0">
          <Group>
            <IconExclamationCircle size={28} color="var(--mantine-color-red-6)" />
            <div>
              <Text size="xs" c="dimmed">Failed / Needs Attention</Text>
              <Text size="xl" fw={700}>{failed}</Text>
            </div>
          </Group>
        </Card>
        <Card withBorder padding="lg" bg="blue.0">
          <Group>
            <IconRefresh size={28} color="var(--mantine-color-blue-6)" />
            <div>
              <Text size="xs" c="dimmed">In Progress</Text>
              <Text size="xl" fw={700}>{inProgress}</Text>
            </div>
          </Group>
        </Card>
      </SimpleGrid>

      <Paper>
        <Table striped highlightOnHover>
          <Table.Thead>
            <Table.Tr>
              <Table.Th>Badge</Table.Th>
              <Table.Th>Status</Table.Th>
              <Table.Th>Description</Table.Th>
              <Table.Th>Last Audit</Table.Th>
              <Table.Th>Next Audit</Table.Th>
              <Table.Th>Retraining</Table.Th>
            </Table.Tr>
          </Table.Thead>
          <Table.Tbody>
            {items.map((item) => {
              const sb = STATUS_BADGE[item.status] || STATUS_BADGE.Pending;
              return (
                <Table.Tr key={item.id}>
                  <Table.Td>
                    <Group gap="xs">
                      <IconCertificate size={18} />
                      <Text fw={500} size="sm">
                        {item.badge_name}
                      </Text>
                    </Group>
                  </Table.Td>
                  <Table.Td>
                    <Badge color={sb.color} leftSection={sb.icon} variant="light">
                      {item.status}
                    </Badge>
                  </Table.Td>
                  <Table.Td>
                    <Text size="sm" lineClamp={2}>
                      {item.description}
                    </Text>
                  </Table.Td>
                  <Table.Td>
                    {item.last_audit_date
                      ? new Date(item.last_audit_date).toLocaleDateString()
                      : "—"}
                  </Table.Td>
                  <Table.Td>
                    {item.next_audit_date
                      ? new Date(item.next_audit_date).toLocaleDateString()
                      : "—"}
                  </Table.Td>
                  <Table.Td>
                    {item.requires_retraining ? (
                      <Badge color="red" variant="filled">
                        Required
                      </Badge>
                    ) : (
                      <Badge color="green" variant="light">
                        Up-to-date
                      </Badge>
                    )}
                  </Table.Td>
                </Table.Tr>
              );
            })}
          </Table.Tbody>
        </Table>
      </Paper>

      {items.some((i) => i.requires_retraining) && (
        <Paper>
          <Text fw={600} mb="md">
            <Group gap="xs">
              <IconRefresh size={18} />
              Retraining Requirements
            </Group>
          </Text>
          <Timeline active={0} bulletSize={24} lineWidth={2}>
            {items
              .filter((i) => i.requires_retraining)
              .map((item) => (
                <Timeline.Item
                  key={item.id}
                  title={item.badge_name}
                  bullet={<IconExclamationCircle size={12} />}
                >
                  <Text size="sm" c="dimmed">
                    {item.retraining_reason || "No reason provided."}
                  </Text>
                  <Text size="xs" mt={4}>
                    Status: <Badge color="red" variant="dot">{item.status}</Badge>
                  </Text>
                </Timeline.Item>
              ))}
          </Timeline>
        </Paper>
      )}
    </Stack>
  );
}
