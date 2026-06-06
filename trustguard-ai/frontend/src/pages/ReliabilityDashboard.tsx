import { useEffect, useState } from "react";
import {
  Card,
  Grid,
  Group,
  Paper,
  RingProgress,
  SimpleGrid,
  Text,
  Title,
} from "@mantine/core";
import { AreaChart, BarChart, LineChart } from "@mantine/charts";
import {
  IconActivity,
  IconClock,
  IconCurrencyDollar,
  IconPercentage,
  IconShieldCheck,
  IconX,
} from "@tabler/icons-react";
import { api } from "../api/client";
import type { ReliabilityMetric, ReliabilitySummary } from "../api/client";
import { ChartContainer } from "../components/ChartContainer";
import { MetricCard } from "../components/MetricCard";

export function ReliabilityDashboard() {
  const [summary, setSummary] = useState<ReliabilitySummary | null>(null);
  const [metrics, setMetrics] = useState<ReliabilityMetric[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [s, m] = await Promise.all([
          api.reliability.summary(),
          api.reliability.metrics(24),
        ]);
        setSummary(s);
        setMetrics(m);
      } catch (err) {
        console.error("Failed to fetch reliability data:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
    const interval = setInterval(fetchData, 10000);
    return () => clearInterval(interval);
  }, []);

  const chartData = metrics.map((m) => ({
    time: new Date(m.timestamp).toLocaleTimeString(),
    uptime: m.uptime_percent,
    latency: m.avg_latency_ms,
    p50: m.p50_latency_ms,
    p95: m.p95_latency_ms,
    p99: m.p99_latency_ms,
    falsePositives: m.false_positives,
    falseNegatives: m.false_negatives,
    precision: +(m.precision * 100).toFixed(1),
    recall: +(m.recall * 100).toFixed(1),
    f1: +(m.f1_score * 100).toFixed(1),
    totalTransactions: m.total_transactions,
  }));

  return (
    <div>
      <Group justify="space-between" mb="lg">
        <div>
          <Title order={3}>Reliability Dashboard</Title>
          <Text size="sm" c="dimmed">Real-time fraud detection reliability metrics</Text>
        </div>
        <RingProgress
          size={80}
          thickness={8}
          sections={[
            {
              value: summary?.current_uptime ?? 100,
              color: (summary?.current_uptime ?? 100) >= 99.9 ? "green" : "red",
            },
          ]}
          label={
            <Text size="xs" ta="center" fw={700}>
              {(summary?.current_uptime ?? 100).toFixed(2)}%
            </Text>
          }
        />
      </Group>

      <SimpleGrid cols={{ base: 1, sm: 2, lg: 4 }} mb="xl">
        <MetricCard
          title="Uptime"
          value={`${(summary?.current_uptime ?? 100).toFixed(3)}%`}
          subtitle="99.99% target"
          icon={<IconShieldCheck size={28} />}
          color="var(--mantine-color-green-6)"
          trend="up"
        />
        <MetricCard
          title="Avg Latency"
          value={`${summary?.avg_latency_ms ?? 0} ms`}
          subtitle="P99: ~42ms"
          icon={<IconClock size={28} />}
          color="var(--mantine-color-trust-6)"
          trend={(summary?.avg_latency_ms ?? 50) < 50 ? "up" : "down"}
        />
        <MetricCard
          title="F1 Score"
          value={(summary?.avg_f1_score ?? 0).toFixed(3)}
          subtitle={`Precision: ${((summary?.precision ?? 0) * 100).toFixed(1)}%`}
          icon={<IconPercentage size={28} />}
          color="var(--mantine-color-compliance-6)"
          trend="up"
        />
        <MetricCard
          title="Total Transactions"
          value={(summary?.total_transactions ?? 0).toLocaleString()}
          subtitle={`FP: ${summary?.total_false_positives ?? 0} | FN: ${summary?.total_false_negatives ?? 0}`}
          icon={<IconActivity size={28} />}
          color="var(--mantine-color-warning-6)"
          trend="neutral"
        />
      </SimpleGrid>

      <Grid mb="xl">
        <Grid.Col span={{ base: 12, md: 8 }}>
          <Card shadow="sm" padding="lg" radius="md" withBorder>
            <Title order={5} mb="md">FP / FN Trend (Last 24h)</Title>
            <ChartContainer>
              {(width) => (
                <AreaChart
                  h={300}
                  w={width}
                  data={chartData}
                  dataKey="time"
                  series={[
                    { name: "falsePositives", label: "False Positives", color: "orange.6" },
                    { name: "falseNegatives", label: "False Negatives", color: "red.6" },
                  ]}
                  areaChartProps={{ syncId: "reliability" }}
                  tickLine="y"
                  gridAxis="y"
                />
              )}
            </ChartContainer>
          </Card>
        </Grid.Col>
        <Grid.Col span={{ base: 12, md: 4 }}>
          <Card shadow="sm" padding="lg" radius="md" withBorder>
            <Title order={5} mb="md">Precision / Recall / F1</Title>
            <ChartContainer>
              {(width) => (
                <LineChart
                  h={300}
                  w={width}
                  data={chartData.slice(-60)}
                  dataKey="time"
                  series={[
                    { name: "precision", label: "Precision", color: "trust.6" },
                    { name: "recall", label: "Recall", color: "green.6" },
                    { name: "f1", label: "F1", color: "violet.6" },
                  ]}
                  withDots={false}
                  tickLine="y"
                  gridAxis="y"
                />
              )}
            </ChartContainer>
          </Card>
        </Grid.Col>
      </Grid>

      <Grid>
        <Grid.Col span={{ base: 12, md: 6 }}>
          <Card shadow="sm" padding="lg" radius="md" withBorder>
            <Title order={5} mb="md">Latency Percentiles (P50 / P95 / P99)</Title>
            <ChartContainer>
              {(width) => (
                <LineChart
                  h={300}
                  w={width}
                  data={chartData.slice(-120)}
                  dataKey="time"
                  series={[
                    { name: "p50", label: "P50", color: "trust.6" },
                    { name: "p95", label: "P95", color: "orange.6" },
                    { name: "p99", label: "P99", color: "red.6" },
                  ]}
                  withDots={false}
                  tickLine="y"
                  gridAxis="y"
                />
              )}
            </ChartContainer>
          </Card>
        </Grid.Col>
        <Grid.Col span={{ base: 12, md: 6 }}>
          <Card shadow="sm" padding="lg" radius="md" withBorder>
            <Title order={5} mb="md">Transaction Volume</Title>
            <ChartContainer>
              {(width) => (
                <BarChart
                  h={300}
                  w={width}
                  data={chartData.slice(-48)}
                  dataKey="time"
                  series={[{ name: "totalTransactions", label: "Transactions", color: "trust.6" }]}
                  tickLine="y"
                  gridAxis="y"
                />
              )}
            </ChartContainer>
          </Card>
        </Grid.Col>
      </Grid>
    </div>
  );
}
