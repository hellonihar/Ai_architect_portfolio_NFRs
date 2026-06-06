import { useEffect, useState } from "react";
import {
  Badge,
  Button,
  Card,
  Group,
  Paper,
  SimpleGrid,
  Stack,
  Table,
  Tabs,
  Text,
  Title,
} from "@mantine/core";
import { notifications } from "@mantine/notifications";
import {
  IconAlertTriangle,
  IconCheck,
  IconEye,
  IconFlag,
} from "@tabler/icons-react";

import { api, type BiasAlert } from "../api/client";

const SEVERITY_BADGE: Record<string, { color: string; icon: React.ReactNode }> =
  {
    Review: { color: "yellow", icon: <IconEye size={14} /> },
    Investigate: { color: "orange", icon: <IconFlag size={14} /> },
    Escalate: { color: "red", icon: <IconAlertTriangle size={14} /> },
  };

export default function Alerts() {
  const [alerts, setAlerts] = useState<BiasAlert[]>([]);
  const [stats, setStats] = useState({ total: 0, review: 0, investigate: 0, escalate: 0 });
  const [activeTab, setActiveTab] = useState<string | null>("all");
  const [loading, setLoading] = useState(true);

  const load = () => {
    setLoading(true);
    Promise.all([
      api.alerts.list(
        activeTab && activeTab !== "all" ? { severity: activeTab } : undefined
      ),
      api.alerts.stats(),
    ])
      .then(([a, s]) => {
        setAlerts(a);
        setStats(s);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    load();
  }, [activeTab]);

  const handleResolve = async (id: string) => {
    try {
      await api.alerts.resolve(id);
      notifications.show({
        title: "Resolved",
        message: "Alert has been marked as resolved.",
        color: "green",
      });
      load();
    } catch (e) {
      notifications.show({
        title: "Error",
        message: "Failed to resolve alert.",
        color: "red",
      });
    }
  };

  return (
    <Stack gap="lg">
      <Title order={3}>Bias Alerts</Title>

      <SimpleGrid cols={{ base: 1, sm: 3 }}>
        <Card withBorder padding="lg">
          <Group>
            <IconAlertTriangle size={28} color="var(--mantine-color-red-6)" />
            <div>
              <Text size="xs" c="dimmed">Escalate</Text>
              <Text size="xl" fw={700}>{stats.escalate}</Text>
            </div>
          </Group>
        </Card>
        <Card withBorder padding="lg">
          <Group>
            <IconFlag size={28} color="var(--mantine-color-orange-6)" />
            <div>
              <Text size="xs" c="dimmed">Investigate</Text>
              <Text size="xl" fw={700}>{stats.investigate}</Text>
            </div>
          </Group>
        </Card>
        <Card withBorder padding="lg">
          <Group>
            <IconEye size={28} color="var(--mantine-color-yellow-6)" />
            <div>
              <Text size="xs" c="dimmed">Review</Text>
              <Text size="xl" fw={700}>{stats.review}</Text>
            </div>
          </Group>
        </Card>
      </SimpleGrid>

      <Tabs value={activeTab} onChange={setActiveTab}>
        <Tabs.List>
          <Tabs.Tab value="all">All ({stats.total})</Tabs.Tab>
          <Tabs.Tab value="Escalate">Escalate ({stats.escalate})</Tabs.Tab>
          <Tabs.Tab value="Investigate">Investigate ({stats.investigate})</Tabs.Tab>
          <Tabs.Tab value="Review">Review ({stats.review})</Tabs.Tab>
        </Tabs.List>
      </Tabs>

      <Paper>
        <Table striped highlightOnHover>
          <Table.Thead>
            <Table.Tr>
              <Table.Th>Severity</Table.Th>
              <Table.Th>Title</Table.Th>
              <Table.Th>Dimension</Table.Th>
              <Table.Th>Affected Group</Table.Th>
              <Table.Th>Metric</Table.Th>
              <Table.Th>Status</Table.Th>
              <Table.Th>Actions</Table.Th>
            </Table.Tr>
          </Table.Thead>
          <Table.Tbody>
            {alerts.map((a) => {
              const sev = SEVERITY_BADGE[a.severity] || SEVERITY_BADGE.Review;
              return (
                <Table.Tr key={a.id}>
                  <Table.Td>
                    <Badge
                      color={sev.color}
                      leftSection={sev.icon}
                      variant="light"
                    >
                      {a.severity}
                    </Badge>
                  </Table.Td>
                  <Table.Td>
                    <Text size="sm" fw={500}>
                      {a.title}
                    </Text>
                    {a.description && (
                      <Text size="xs" c="dimmed" lineClamp={1}>
                        {a.description}
                      </Text>
                    )}
                  </Table.Td>
                  <Table.Td>{a.dimension}</Table.Td>
                  <Table.Td>{a.affected_group}</Table.Td>
                  <Table.Td>
                    {a.metric_name && (
                      <Text size="sm">
                        {a.metric_name}: {Number(a.metric_value ?? 0).toFixed(3)}
                      </Text>
                    )}
                  </Table.Td>
                  <Table.Td>
                    <Badge
                      color={a.status === "Open" ? "red" : "green"}
                      variant="dot"
                    >
                      {a.status}
                    </Badge>
                  </Table.Td>
                  <Table.Td>
                    {a.status === "Open" && (
                      <Button
                        size="xs"
                        variant="light"
                        color="green"
                        leftSection={<IconCheck size={14} />}
                        onClick={() => handleResolve(a.id)}
                      >
                        Resolve
                      </Button>
                    )}
                  </Table.Td>
                </Table.Tr>
              );
            })}
            {alerts.length === 0 && (
              <Table.Tr>
                <Table.Td colSpan={7}>
                  <Text ta="center" py="xl" c="dimmed">
                    No alerts found.
                  </Text>
                </Table.Td>
              </Table.Tr>
            )}
          </Table.Tbody>
        </Table>
      </Paper>
    </Stack>
  );
}
