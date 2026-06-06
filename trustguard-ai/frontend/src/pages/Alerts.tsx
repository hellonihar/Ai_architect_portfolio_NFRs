import { useEffect, useState } from "react";
import {
  Badge,
  Card,
  Group,
  Paper,
  SimpleGrid,
  Table,
  Tabs,
  Text,
  Title,
} from "@mantine/core";
import {
  IconAlertTriangle,
  IconBug,
  IconExchange,
  IconRefresh,
} from "@tabler/icons-react";
import type { Alert, DriftEvent } from "../api/client";
import { api } from "../api/client";

const severityColors: Record<string, string> = {
  critical: "red",
  warning: "orange",
  info: "blue",
};

const typeIcons: Record<string, typeof IconBug> = {
  drift: IconRefresh,
  anomaly: IconBug,
  failover: IconExchange,
};

const severityOrder = ["critical", "warning", "info"];

export function Alerts() {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [driftEvents, setDriftEvents] = useState<DriftEvent[]>([]);
  const [activeTab, setActiveTab] = useState<string | null>("all");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [a, d] = await Promise.all([
          api.alerts.feed(72),
          api.alerts.drift(168),
        ]);
        setAlerts(a);
        setDriftEvents(d);
      } catch (err) {
        console.error("Failed to fetch alerts:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
    const interval = setInterval(fetchData, 10000);
    return () => clearInterval(interval);
  }, []);

  const filteredAlerts =
    activeTab === "all" ? alerts : alerts.filter((a) => a.type === activeTab);

  const criticalCount = alerts.filter((a) => a.severity === "critical").length;
  const warningCount = alerts.filter((a) => a.severity === "warning").length;
  const infoCount = alerts.filter((a) => a.severity === "info").length;

  return (
    <div>
      <Group justify="space-between" mb="lg">
        <div>
          <Title order={3}>Alerts & Anomalies</Title>
          <Text size="sm" c="dimmed">Real-time drift detection and system notifications</Text>
        </div>
      </Group>

      <SimpleGrid cols={{ base: 1, sm: 3 }} mb="xl">
        {[
          { label: "Critical", count: criticalCount, color: "red" },
          { label: "Warning", count: warningCount, color: "orange" },
          { label: "Info", count: infoCount, color: "blue" },
        ].map((item) => (
          <Paper
            key={item.label}
            withBorder
            p="lg"
            radius="md"
            style={{
              borderLeft: `4px solid var(--mantine-color-${item.color}-6)`,
            }}
          >
            <Group justify="space-between">
              <div>
                <Text size="xs" tt="uppercase" fw={700} c="dimmed">
                  {item.label}
                </Text>
                <Text size="xxxl" fw={700} c={`${item.color}.6`}>
                  {item.count}
                </Text>
              </div>
              <IconAlertTriangle
                size={32}
                color={`var(--mantine-color-${item.color}-6)`}
                opacity={0.4}
              />
            </Group>
          </Paper>
        ))}
      </SimpleGrid>

      <Card shadow="sm" padding="lg" radius="md" withBorder>
        <Tabs value={activeTab} onChange={setActiveTab}>
          <Tabs.List mb="md">
            <Tabs.Tab value="all" leftSection={<IconAlertTriangle size={16} />}>
              All ({alerts.length})
            </Tabs.Tab>
            <Tabs.Tab value="drift" leftSection={<IconRefresh size={16} />}>
              Drift ({alerts.filter((a) => a.type === "drift").length})
            </Tabs.Tab>
            <Tabs.Tab value="failover" leftSection={<IconExchange size={16} />}>
              Failover ({alerts.filter((a) => a.type === "failover").length})
            </Tabs.Tab>
          </Tabs.List>

          <Table striped highlightOnHover>
            <Table.Thead>
              <Table.Tr>
                <Table.Th>Time</Table.Th>
                <Table.Th>Severity</Table.Th>
                <Table.Th>Type</Table.Th>
                <Table.Th>Title</Table.Th>
                <Table.Th>Description</Table.Th>
                <Table.Th>Status</Table.Th>
              </Table.Tr>
            </Table.Thead>
            <Table.Tbody>
              {filteredAlerts.length === 0 ? (
                <Table.Tr>
                  <Table.Td colSpan={6}>
                    <Text c="dimmed" ta="center" py="xl">
                      No alerts found. The system is running smoothly.
                    </Text>
                  </Table.Td>
                </Table.Tr>
              ) : (
                filteredAlerts.map((alert) => {
                  const TypeIcon = typeIcons[alert.type] || IconBug;
                  return (
                    <Table.Tr key={alert.id}>
                      <Table.Td>
                        <Text size="xs" style={{ whiteSpace: "nowrap" }}>
                          {new Date(alert.timestamp).toLocaleString()}
                        </Text>
                      </Table.Td>
                      <Table.Td>
                        <Badge
                          size="sm"
                          color={severityColors[alert.severity] || "gray"}
                          variant="light"
                        >
                          {alert.severity}
                        </Badge>
                      </Table.Td>
                      <Table.Td>
                        <Group gap="xs">
                          <TypeIcon size={14} />
                          <Text size="sm" tt="capitalize">
                            {alert.type}
                          </Text>
                        </Group>
                      </Table.Td>
                      <Table.Td>
                        <Text size="sm" fw={500}>
                          {alert.title}
                        </Text>
                      </Table.Td>
                      <Table.Td>
                        <Text size="sm">{alert.description}</Text>
                      </Table.Td>
                      <Table.Td>
                        <Badge
                          size="sm"
                          color={alert.resolved ? "green" : "red"}
                          variant="light"
                        >
                          {alert.resolved ? "Resolved" : "Active"}
                        </Badge>
                      </Table.Td>
                    </Table.Tr>
                  );
                })
              )}
            </Table.Tbody>
          </Table>
        </Tabs>
      </Card>

      {driftEvents.length > 0 && (
        <Card shadow="sm" padding="lg" radius="md" withBorder mt="lg">
          <Title order={5} mb="md">Drift Detection History</Title>
          <Table striped highlightOnHover>
            <Table.Thead>
              <Table.Tr>
                <Table.Th>Time</Table.Th>
                <Table.Th>Feature</Table.Th>
                <Table.Th>Magnitude</Table.Th>
                <Table.Th>Severity</Table.Th>
                <Table.Th>Retrained</Table.Th>
                <Table.Th>Resolved</Table.Th>
              </Table.Tr>
            </Table.Thead>
            <Table.Tbody>
              {driftEvents.slice(0, 20).map((event) => (
                <Table.Tr key={event.id}>
                  <Table.Td>
                    <Text size="xs">
                      {new Date(event.timestamp).toLocaleString()}
                    </Text>
                  </Table.Td>
                  <Table.Td>
                    <Text size="sm" fw={500}>{event.feature}</Text>
                  </Table.Td>
                  <Table.Td>
                    <Text size="sm">{event.magnitude.toFixed(4)}</Text>
                  </Table.Td>
                  <Table.Td>
                    <Badge
                      size="sm"
                      color={severityColors[event.severity] || "gray"}
                      variant="light"
                    >
                      {event.severity}
                    </Badge>
                  </Table.Td>
                  <Table.Td>
                    <Badge
                      size="sm"
                      color={event.retraining_triggered ? "green" : "orange"}
                      variant="light"
                    >
                      {event.retraining_triggered ? "Yes" : "Pending"}
                    </Badge>
                  </Table.Td>
                  <Table.Td>
                    <Badge
                      size="sm"
                      color={event.resolved ? "green" : "orange"}
                      variant="light"
                    >
                      {event.resolved ? "Resolved" : "Active"}
                    </Badge>
                  </Table.Td>
                </Table.Tr>
              ))}
            </Table.Tbody>
          </Table>
        </Card>
      )}
    </div>
  );
}
