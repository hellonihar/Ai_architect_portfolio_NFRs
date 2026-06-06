import { Card, Group, Text } from "@mantine/core";
import { type ReactNode } from "react";

interface MetricCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon?: ReactNode;
  color?: string;
  trend?: "up" | "down" | "neutral";
}

export function MetricCard({ title, value, subtitle, icon, color, trend }: MetricCardProps) {
  const trendColor =
    trend === "up"
      ? "var(--mantine-color-green-6)"
      : trend === "down"
        ? "var(--mantine-color-red-6)"
        : "var(--mantine-color-gray-6)";

  return (
    <Card shadow="sm" padding="lg" radius="md" withBorder>
      <Group justify="space-between" align="flex-start">
        <div>
          <Text size="xs" tt="uppercase" fw={700} c="dimmed">
            {title}
          </Text>
          <Text
            size="xl"
            fw={700}
            c={color ?? undefined}
            style={{ lineHeight: 1.2, marginTop: 4 }}
          >
            {value}
          </Text>
          {subtitle && (
            <Text size="xs" c={trendColor} mt={4}>
              {subtitle}
            </Text>
          )}
        </div>
        {icon && (
          <div style={{ color: color ?? "var(--mantine-color-trust-6)", opacity: 0.7 }}>
            {icon}
          </div>
        )}
      </Group>
    </Card>
  );
}
