import { useEffect, useState } from "react";
import {
  Badge,
  Card,
  Group,
  SimpleGrid,
  Table,
  Text,
  TextInput,
  Title,
} from "@mantine/core";
import {
  IconFileReport,
  IconSearch,
  IconShieldCheck,
} from "@tabler/icons-react";
import type { AuditLog, SLABadge } from "../api/client";
import { api } from "../api/client";
import { SLABadgeCard } from "../components/SLABadge";

export function Governance() {
  const [badges, setBadges] = useState<SLABadge[]>([]);
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [b, l] = await Promise.all([
          api.governance.slaBadges(),
          api.governance.auditLogs(168),
        ]);
        setBadges(b);
        setLogs(l);
      } catch (err) {
        console.error("Failed to fetch governance data:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
    const interval = setInterval(fetchData, 15000);
    return () => clearInterval(interval);
  }, []);

  const filteredLogs = logs.filter(
    (log) =>
      log.action.toLowerCase().includes(search.toLowerCase()) ||
      log.actor.toLowerCase().includes(search.toLowerCase()) ||
      (log.details && log.details.toLowerCase().includes(search.toLowerCase())),
  );

  const slaCount = badges.length;
  const metCount = badges.filter((b) => b.status === "met").length;

  return (
    <div>
      <Group justify="space-between" mb="lg">
        <div>
          <Title order={3}>Governance & Compliance</Title>
          <Text size="sm" c="dimmed">SLA adherence monitoring and regulatory compliance</Text>
        </div>
        <Badge
          size="xl"
          variant="light"
          color={metCount === slaCount ? "green" : "orange"}
          leftSection={<IconShieldCheck size={18} />}
        >
          {metCount}/{slaCount} SLAs Met
        </Badge>
      </Group>

      <SimpleGrid cols={{ base: 1, sm: 2 }} mb="xl">
        {badges.map((badge) => (
          <SLABadgeCard
            key={badge.id}
            name={badge.name}
            description={badge.description}
            status={badge.status}
            currentValue={badge.current_value}
            threshold={badge.threshold}
            unit={badge.unit}
          />
        ))}
      </SimpleGrid>

      <Card shadow="sm" padding="lg" radius="md" withBorder>
        <Group justify="space-between" mb="md">
          <Title order={5}>
            <Group gap="xs">
              <IconFileReport size={20} />
              Compliance Audit Log
            </Group>
          </Title>
          <TextInput
            placeholder="Search logs..."
            leftSection={<IconSearch size={16} />}
            value={search}
            onChange={(e) => setSearch(e.currentTarget.value)}
            w={260}
          />
        </Group>
        <Table striped highlightOnHover>
          <Table.Thead>
            <Table.Tr>
              <Table.Th>Timestamp</Table.Th>
              <Table.Th>Action</Table.Th>
              <Table.Th>Actor</Table.Th>
              <Table.Th>Pipeline</Table.Th>
              <Table.Th>Details</Table.Th>
            </Table.Tr>
          </Table.Thead>
          <Table.Tbody>
            {filteredLogs.length === 0 ? (
              <Table.Tr>
                <Table.Td colSpan={5}>
                  <Text c="dimmed" ta="center" py="xl">No audit log entries found.</Text>
                </Table.Td>
              </Table.Tr>
            ) : (
              filteredLogs.map((log) => (
                <Table.Tr key={log.id}>
                  <Table.Td>
                    <Text size="xs" style={{ whiteSpace: "nowrap" }}>
                      {new Date(log.timestamp).toLocaleString()}
                    </Text>
                  </Table.Td>
                  <Table.Td>
                    <Badge
                      size="sm"
                      variant="light"
                      color={
                        log.action.includes("FAILOVER")
                          ? "red"
                          : log.action.includes("DRIFT")
                            ? "orange"
                            : log.action.includes("SLA")
                              ? "green"
                              : "blue"
                      }
                    >
                      {log.action}
                    </Badge>
                  </Table.Td>
                  <Table.Td>
                    <Text size="sm">{log.actor}</Text>
                  </Table.Td>
                  <Table.Td>
                    <Text size="sm">{log.pipeline || "—"}</Text>
                  </Table.Td>
                  <Table.Td>
                    <Text size="sm">{log.details}</Text>
                  </Table.Td>
                </Table.Tr>
              ))
            )}
          </Table.Tbody>
        </Table>
      </Card>
    </div>
  );
}
