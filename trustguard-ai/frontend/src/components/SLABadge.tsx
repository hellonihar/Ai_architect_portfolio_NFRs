import { Badge, Card, Group, RingProgress, Text, Tooltip } from "@mantine/core";

interface SLABadgeCardProps {
  name: string;
  description: string;
  status: string;
  currentValue: number;
  threshold: number;
  unit: string;
}

export function SLABadgeCard({
  name,
  description,
  status,
  currentValue,
  threshold,
  unit,
}: SLABadgeCardProps) {
  const isMet = status === "met";
  const progressValue = unit === "%" ? currentValue : (currentValue / threshold) * 100;
  const ringValue = Math.min(100, Math.max(0, unit === "ms" ? 100 - progressValue + 50 : progressValue));
  const ringColor = isMet ? "compliance" : "severity";

  return (
    <Card shadow="sm" padding="lg" radius="md" withBorder>
      <Group justify="space-between" align="flex-start">
        <div style={{ flex: 1 }}>
          <Group gap="xs" mb={4}>
            <Text size="sm" fw={600}>
              {name}
            </Text>
            <Badge
              color={isMet ? "green" : "red"}
              variant="light"
              size="sm"
            >
              {isMet ? "✓ Met" : "✗ Breached"}
            </Badge>
          </Group>
          <Text size="xs" c="dimmed" mb={8}>
            {description}
          </Text>
          <Group gap="xs">
            <Text size="lg" fw={700} c={isMet ? "green" : "red"}>
              {currentValue}
              {unit === "score" ? "" : unit === "%" ? "%" : " ms"}
            </Text>
            <Text size="xs" c="dimmed">
              / threshold {threshold}{unit === "score" ? "" : unit === "%" ? "%" : " ms"}
            </Text>
          </Group>
        </div>
        <Tooltip label={`${isMet ? "SLA Met" : "SLA Breached"}`}>
          <RingProgress
            size={70}
            thickness={6}
            sections={[{ value: ringValue, color: ringColor }]}
            label={
              <Text size="xs" ta="center" fw={700} c={ringColor}>
                {Math.round(ringValue)}%
              </Text>
            }
          />
        </Tooltip>
      </Group>
    </Card>
  );
}
