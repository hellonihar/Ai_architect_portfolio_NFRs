import { useEffect, useState } from "react";
import {
  Badge,
  Card,
  Group,
  Table,
  Text,
  Timeline,
  Title,
} from "@mantine/core";
import {
  IconArrowsShuffle,
  IconCloud,
  IconServer,
  IconServer2,
} from "@tabler/icons-react";
import type { FailoverEvent, Topology } from "../api/client";
import { api } from "../api/client";
import { FailoverDiagram } from "../components/FailoverDiagram";

const tierIcons: Record<string, typeof IconServer> = {
  primary: IconServer,
  secondary: IconServer2,
  backup: IconCloud,
};

const statusColors: Record<string, string> = {
  healthy: "green",
  degraded: "red",
};

export function PipelineStatus() {
  const [topology, setTopology] = useState<Topology | null>(null);
  const [failovers, setFailovers] = useState<FailoverEvent[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [t, f] = await Promise.all([
          api.pipelines.topology(),
          api.pipelines.failovers(168),
        ]);
        setTopology(t);
        setFailovers(f);
      } catch (err) {
        console.error("Failed to fetch pipeline data:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
    const interval = setInterval(fetchData, 10000);
    return () => clearInterval(interval);
  }, []);

  const allPipelines = topology
    ? [...(topology.tiers.primary || []), ...(topology.tiers.secondary || []), ...(topology.tiers.backup || [])]
    : [];

  return (
    <div>
      <Group justify="space-between" mb="lg">
        <div>
          <Title order={3}>Pipeline Status & Failover</Title>
          <Text size="sm" c="dimmed">Multi-region fraud detection pipeline topology</Text>
        </div>
      </Group>

      <Card shadow="sm" padding="lg" radius="md" withBorder mb="xl">
        <Title order={5} mb="md">Failover Topology</Title>
        <FailoverDiagram topology={topology} />
      </Card>

      <Card shadow="sm" padding="lg" radius="md" withBorder mb="xl">
        <Title order={5} mb="md">Pipeline Health</Title>
        <Table striped highlightOnHover>
          <Table.Thead>
            <Table.Tr>
              <Table.Th>Pipeline</Table.Th>
              <Table.Th>Tier</Table.Th>
              <Table.Th>Region</Table.Th>
              <Table.Th>Status</Table.Th>
              <Table.Th>Uptime</Table.Th>
              <Table.Th>Active Requests</Table.Th>
            </Table.Tr>
          </Table.Thead>
          <Table.Tbody>
            {allPipelines.map((p) => {
              const TierIcon = tierIcons[p.tier] || IconServer;
              return (
                <Table.Tr key={p.id}>
                  <Table.Td>
                    <Group gap="xs">
                      <TierIcon size={16} />
                      <Text size="sm" fw={500}>{p.name}</Text>
                    </Group>
                  </Table.Td>
                  <Table.Td>
                    <Badge
                      size="sm"
                      variant="light"
                      color={p.tier === "primary" ? "trust" : p.tier === "secondary" ? "orange" : "gray"}
                    >
                      {p.tier}
                    </Badge>
                  </Table.Td>
                  <Table.Td>
                    <Text size="sm">{p.region}</Text>
                  </Table.Td>
                  <Table.Td>
                    <Badge size="sm" color={statusColors[p.status] || "gray"} variant="light">
                      {p.status}
                    </Badge>
                  </Table.Td>
                  <Table.Td>
                    <Text size="sm" fw={600}>
                      {p.uptime_percent.toFixed(3)}%
                    </Text>
                  </Table.Td>
                  <Table.Td>
                    <Text size="sm">{p.active_requests}</Text>
                  </Table.Td>
                </Table.Tr>
              );
            })}
          </Table.Tbody>
        </Table>
      </Card>

      <Card shadow="sm" padding="lg" radius="md" withBorder>
        <Title order={5} mb="md">
          <Group gap="xs">
            <IconArrowsShuffle size={20} />
            Failover Event Timeline
          </Group>
        </Title>
        {failovers.length === 0 ? (
          <Text c="dimmed" py="xl" ta="center">No failover events recorded in the selected period.</Text>
        ) : (
          <Timeline active={failovers.length} bulletSize={24} lineWidth={2}>
            {failovers.map((event) => (
              <Timeline.Item
                key={event.id}
                title={`${event.from_pipeline} → ${event.to_pipeline}`}
                bullet={
                  <IconArrowsShuffle size={12} />
                }
              >
                <Text size="sm" c="dimmed" mt={4}>
                  {event.cause} — Downtime: {event.duration_seconds}s
                </Text>
                <Group gap="xs" mt={4}>
                  <Badge size="sm" color={event.recovered ? "green" : "red"} variant="light">
                    {event.recovered ? "Recovered" : "Unresolved"}
                  </Badge>
                  <Text size="xs" c="dimmed">
                    {new Date(event.timestamp).toLocaleString()}
                  </Text>
                </Group>
              </Timeline.Item>
            ))}
          </Timeline>
        )}
      </Card>
    </div>
  );
}
