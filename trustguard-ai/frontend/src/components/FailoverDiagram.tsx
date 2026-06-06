import { Box, Group, Text, ThemeIcon, Tooltip } from "@mantine/core";
import {
  IconArrowRight,
  IconCircleCheck,
  IconCircleX,
  IconCloud,
  IconExclamationCircle,
  IconServer,
  IconServer2,
} from "@tabler/icons-react";
import type { PipelineHealth, Topology } from "../api/client";

interface FailoverDiagramProps {
  topology: Topology | null;
}

function PipelineNode({ pipeline, isActive }: { pipeline: PipelineHealth; isActive: boolean }) {
  const isHealthy = pipeline.status === "healthy";
  const IconComponent = pipeline.tier === "backup" ? IconCloud : pipeline.tier === "secondary" ? IconServer2 : IconServer;

  return (
    <Tooltip
      label={`${pipeline.name} (${pipeline.region}) - ${isHealthy ? "Healthy" : "Degraded"} - ${pipeline.uptime_percent.toFixed(3)}% uptime`}
    >
      <Box
        style={(theme) => ({
          border: `2px solid ${isActive ? theme.colors.trust[6] : theme.colors.gray[3]}`,
          borderRadius: theme.radius.md,
          padding: "12px 16px",
          backgroundColor: isActive
            ? isHealthy
              ? theme.colors.green[0]
              : theme.colors.red[0]
            : theme.colors.gray[0],
          opacity: isActive ? 1 : 0.5,
          transition: "all 0.3s ease",
          cursor: "pointer",
          minWidth: 140,
          textAlign: "center",
        })}
      >
        <Group justify="center" mb={4}>
          <ThemeIcon
            size="sm"
            variant="light"
            color={isHealthy ? "green" : "red"}
            radius="xl"
          >
            {isHealthy ? <IconCircleCheck size={14} /> : <IconCircleX size={14} />}
          </ThemeIcon>
          <IconComponent size={20} color={isActive ? "var(--mantine-color-trust-6)" : "gray"} />
          {isActive && !isHealthy && <IconExclamationCircle size={14} color="red" />}
        </Group>
        <Text size="sm" fw={600}>
          {pipeline.name}
        </Text>
        <Text size="xs" c="dimmed">
          {pipeline.region}
        </Text>
      </Box>
    </Tooltip>
  );
}

export function FailoverDiagram({ topology }: FailoverDiagramProps) {
  if (!topology) {
    return (
      <Box py="xl" ta="center">
        <Text c="dimmed">Loading pipeline topology...</Text>
      </Box>
    );
  }

  const activeTier = topology.active_tier;
  const tiers = topology.tiers;

  const renderTierRow = (tier: "primary" | "secondary" | "backup", label: string) => {
    const pipelines = tiers[tier] || [];
    const isActive = activeTier === tier;

    return (
      <Group justify="center" gap="xl" mb="lg" style={{ opacity: isActive ? 1 : 0.4 }}>
        {pipelines.map((p) => (
          <PipelineNode key={p.id} pipeline={p} isActive={isActive || !activeTier} />
        ))}
      </Group>
    );
  };

  const tierOrder: Array<{ key: "primary" | "secondary" | "backup"; label: string }> = [
    { key: "primary", label: "Primary Tier" },
    { key: "secondary", label: "Secondary Tier" },
    { key: "backup", label: "Backup Tier" },
  ];

  const activeIdx = tierOrder.findIndex((t) => t.key === activeTier);

  return (
    <Box py="md">
      <Text size="sm" c="dimmed" mb="lg" ta="center">
        Active Tier: <strong style={{ color: "var(--mantine-color-trust-6)", textTransform: "uppercase" }}>{activeTier || "none"}</strong>
      </Text>

      {tierOrder.map((tier, idx) => (
        <div key={tier.key}>
          <Group justify="center" gap="xs" mb={4}>
            <Text size="xs" tt="uppercase" fw={700} c="dimmed">
              {tier.label}
            </Text>
            {idx === activeIdx && (
              <Text size="xs" c="trust" fw={600}>
                ← Active
              </Text>
            )}
          </Group>
          {renderTierRow(tier.key, tier.label)}
          {idx < tierOrder.length - 1 && (
            <Group justify="center" gap={4} mb="md">
              <IconArrowRight
                size={16}
                color={idx < activeIdx ? "var(--mantine-color-green-6)" : "var(--mantine-color-gray-4)"}
              />
              <Text size="xs" c="dimmed">
                {idx < activeIdx ? "Failover path" : "Standby"}
              </Text>
            </Group>
          )}
        </div>
      ))}
    </Box>
  );
}
