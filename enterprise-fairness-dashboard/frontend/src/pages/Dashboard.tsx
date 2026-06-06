import { useEffect, useState } from "react";
import {
  Badge,
  Card,
  Group,
  Paper,
  RingProgress,
  SimpleGrid,
  Stack,
  Text,
  Title,
} from "@mantine/core";
import { BarChart } from "@mantine/charts";
import {
  IconAlertTriangle,
  IconChecklist,
  IconScale,
  IconUsers,
} from "@tabler/icons-react";

import { api, type DashboardSummary, type DemographicParity } from "../api/client";

const DIMENSION_COLORS: Record<string, string> = {
  Gender: "blue",
  Region: "teal",
  Income: "yellow",
};

export default function Dashboard() {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [demographics, setDemographics] = useState<DemographicParity[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([api.fairness.summary(), api.fairness.demographics()])
      .then(([s, d]) => {
        setSummary(s);
        setDemographics(d);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <Text>Loading dashboard...</Text>;
  if (!summary) return <Text c="red">Failed to load dashboard data.</Text>;

  const grouped = groupBy(demographics, "dimension");
  const allGroups = demographics.map((d) => ({
    group: d.group_name,
    rate: Number(d.approval_rate),
  }));
  const tickFormatter = (v: number) => `${v}%`;

  return (
    <Stack gap="lg" pb="xl">
      <Title order={3}>Enterprise Fairness Overview</Title>

      <SimpleGrid cols={{ base: 1, sm: 2, md: 4 }}>
        <MetricCard icon={<IconScale size={28} />} label="Fairness Index" value={`${(summary.fairness_index * 100).toFixed(1)}%`} color={summary.fairness_index >= 0.8 ? "teal" : "red"} />
        <MetricCard icon={<IconUsers size={28} />} label="Disparate Impact" value={`${(summary.disparate_impact * 100).toFixed(1)}%`} color={summary.disparate_impact >= 0.8 ? "teal" : "orange"} />
        <MetricCard icon={<IconChecklist size={28} />} label="Equalized Odds" value={`${(summary.equalized_odds * 100).toFixed(1)}%`} color={summary.equalized_odds >= 0.75 ? "teal" : "orange"} />
        <MetricCard icon={<IconAlertTriangle size={28} />} label="Open Alerts" value={String(summary.open_alerts)} color={summary.open_alerts > 0 ? "red" : "teal"} />
      </SimpleGrid>

      <SimpleGrid cols={{ base: 1, md: 2 }} spacing="lg">
        <Paper>
          <Group mb="md">
            <IconUsers size={20} />
            <Text fw={600}>Demographic Parity — Approval Rate by Group</Text>
          </Group>
          <BarChart
            h={320}
            data={allGroups}
            dataKey="group"
            series={[{ name: "rate", color: "blue", label: "Approval Rate" }]}
            referenceLines={[{ y: 75, label: "Parity Threshold (75%)", color: "red" }]}
            valueFormatter={tickFormatter}
            withLegend
            withTooltip
            tickLine="y"
            gridAxis="y"
          />
        </Paper>

        <Paper>
          <Group mb="md">
            <IconScale size={20} />
            <Text fw={600}>Fairness Index Score</Text>
          </Group>
          <Stack align="center" gap="lg" py="xl">
            <RingProgress size={180} thickness={16} roundCaps
              sections={[{ value: summary.fairness_index * 100, color: summary.fairness_index >= 0.8 ? "teal" : "orange" }]}
              label={<Text ta="center" size="xl" fw={700}>{(summary.fairness_index * 100).toFixed(1)}%</Text>}
            />
            <Group gap="xs">
              <Badge color={summary.compliance_passed > 0 ? "green" : "gray"} size="lg">{summary.compliance_passed} Passed</Badge>
              <Badge color={summary.compliance_failed > 0 ? "red" : "gray"} size="lg">{summary.compliance_failed} Failed</Badge>
              <Badge color="blue" size="lg">{summary.groups_monitored} Groups</Badge>
            </Group>
          </Stack>
        </Paper>
      </SimpleGrid>

      {Object.entries(grouped).map(([dimension, items]) => (
        <Paper key={dimension}>
          <Group mb="md">
            <Text fw={600}>Parity by {dimension}</Text>
            <Badge color={getDimensionColor(dimension)} variant="light">{items.length} groups</Badge>
          </Group>
          <BarChart
            h={260}
            data={items.map((d) => ({ group: d.group_name, rate: Number(d.approval_rate) }))}
            dataKey="group"
            series={[{ name: "rate", color: getDimensionColor(dimension), label: "Approval Rate" }]}
            referenceLines={[{ y: 75, label: "Parity Threshold (75%)", color: "red" }]}
            valueFormatter={tickFormatter}
            withLegend
            withTooltip
            tickLine="y"
            gridAxis="y"
          />
        </Paper>
      ))}
    </Stack>
  );
}

function MetricCard({ icon, label, value, color }: { icon: React.ReactNode; label: string; value: string; color: string }) {
  return (
    <Card padding="lg" radius="md" withBorder>
      <Group>
        <div style={{ color: `var(--mantine-color-${color}-6)` }}>{icon}</div>
        <div>
          <Text size="xs" tt="uppercase" c="dimmed" fw={500}>{label}</Text>
          <Text size="xl" fw={700}>{value}</Text>
        </div>
      </Group>
    </Card>
  );
}

function groupBy<T extends Record<string, unknown>>(arr: T[], key: keyof T): Record<string, T[]> {
  return arr.reduce((acc, item) => {
    const k = String(item[key]);
    if (!acc[k]) acc[k] = [];
    acc[k].push(item);
    return acc;
  }, {} as Record<string, T[]>);
}

function getDimensionColor(dimension: string): string {
  return DIMENSION_COLORS[dimension] || "gray";
}
