import { useEffect, useState } from "react";
import {
  Badge,
  Button,
  Card,
  Group,
  Modal,
  Paper,
  Select,
  SimpleGrid,
  Stack,
  Table,
  Text,
  TextInput,
  Textarea,
  Title,
} from "@mantine/core";
import { useDisclosure } from "@mantine/hooks";
import { notifications } from "@mantine/notifications";
import {
  IconCheck,
  IconPlus,
  IconReportAnalytics,
  IconSearch,
  IconUpload,
  IconUserExclamation,
} from "@tabler/icons-react";

import { api, type ActionItem } from "../api/client";

const ACTION_ICONS: Record<string, React.ReactNode> = {
  investigate: <IconSearch size={16} />,
  escalate: <IconUserExclamation size={16} />,
  update_data: <IconUpload size={16} />,
  generate_report: <IconReportAnalytics size={16} />,
};

const STATUS_BADGE: Record<string, string> = {
  Pending: "gray",
  "In Progress": "blue",
  Completed: "green",
  Cancelled: "red",
};

export default function Actions() {
  const [actions, setActions] = useState<ActionItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [opened, { open, close }] = useDisclosure(false);
  const [form, setForm] = useState({
    action_type: "",
    title: "",
    description: "",
    assigned_to: "",
  });
  const [submitting, setSubmitting] = useState(false);

  const load = () => {
    setLoading(true);
    api.actions.list()
      .then(setActions)
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    load();
  }, []);

  const handleCreate = async () => {
    if (!form.action_type || !form.title) {
      notifications.show({
        title: "Validation",
        message: "Action type and title are required.",
        color: "yellow",
      });
      return;
    }
    setSubmitting(true);
    try {
      await api.actions.create({
        action_type: form.action_type,
        title: form.title,
        description: form.description || undefined,
        assigned_to: form.assigned_to || undefined,
      });
      notifications.show({
        title: "Created",
        message: "Action created successfully.",
        color: "green",
      });
      close();
      setForm({ action_type: "", title: "", description: "", assigned_to: "" });
      load();
    } catch {
      notifications.show({ title: "Error", message: "Failed to create action.", color: "red" });
    } finally {
      setSubmitting(false);
    }
  };

  const handleComplete = async (id: string) => {
    try {
      await api.actions.complete(id);
      notifications.show({ title: "Completed", message: "Action marked as completed.", color: "green" });
      load();
    } catch {
      notifications.show({ title: "Error", message: "Failed to complete action.", color: "red" });
    }
  };

  return (
    <Stack gap="lg">
      <Group justify="space-between">
        <Title order={3}>Actions &amp; Insights</Title>
        <Button leftSection={<IconPlus size={18} />} onClick={open}>
          New Action
        </Button>
      </Group>

      <SimpleGrid cols={{ base: 1, sm: 3 }}>
        <Card withBorder padding="lg">
          <Group>
            <IconSearch size={28} color="var(--mantine-color-blue-6)" />
            <div>
              <Text size="xs" c="dimmed">Investigate</Text>
              <Text size="xl" fw={700}>
                {actions.filter((a) => a.action_type === "investigate" && a.status !== "Completed").length}
              </Text>
            </div>
          </Group>
        </Card>
        <Card withBorder padding="lg">
          <Group>
            <IconUserExclamation size={28} color="var(--mantine-color-red-6)" />
            <div>
              <Text size="xs" c="dimmed">Escalate</Text>
              <Text size="xl" fw={700}>
                {actions.filter((a) => a.action_type === "escalate" && a.status !== "Completed").length}
              </Text>
            </div>
          </Group>
        </Card>
        <Card withBorder padding="lg">
          <Group>
            <IconUpload size={28} color="var(--mantine-color-violet-6)" />
            <div>
              <Text size="xs" c="dimmed">Update Data / Reports</Text>
              <Text size="xl" fw={700}>
                {actions.filter((a) => a.action_type === "update_data" || a.action_type === "generate_report" && a.status !== "Completed").length}
              </Text>
            </div>
          </Group>
        </Card>
      </SimpleGrid>

      <Paper>
        <Table striped highlightOnHover>
          <Table.Thead>
            <Table.Tr>
              <Table.Th>Type</Table.Th>
              <Table.Th>Title</Table.Th>
              <Table.Th>Assigned To</Table.Th>
              <Table.Th>Status</Table.Th>
              <Table.Th>Created</Table.Th>
              <Table.Th>Action</Table.Th>
            </Table.Tr>
          </Table.Thead>
          <Table.Tbody>
            {actions.map((a) => (
              <Table.Tr key={a.id}>
                <Table.Td>
                  <Badge
                    variant="light"
                    leftSection={ACTION_ICONS[a.action_type] || null}
                  >
                    {a.action_type.replace("_", " ")}
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
                <Table.Td>{a.assigned_to || "—"}</Table.Td>
                <Table.Td>
                  <Badge color={STATUS_BADGE[a.status] || "gray"} variant="dot">
                    {a.status}
                  </Badge>
                </Table.Td>
                <Table.Td>
                  <Text size="sm">
                    {new Date(a.created_at).toLocaleDateString()}
                  </Text>
                </Table.Td>
                <Table.Td>
                  {a.status !== "Completed" && (
                    <Button
                      size="xs"
                      variant="light"
                      color="green"
                      leftSection={<IconCheck size={14} />}
                      onClick={() => handleComplete(a.id)}
                    >
                      Complete
                    </Button>
                  )}
                </Table.Td>
              </Table.Tr>
            ))}
            {actions.length === 0 && (
              <Table.Tr>
                <Table.Td colSpan={6}>
                  <Text ta="center" py="xl" c="dimmed">
                    No actions yet. Create one to start tracking remediation work.
                  </Text>
                </Table.Td>
              </Table.Tr>
            )}
          </Table.Tbody>
        </Table>
      </Paper>

      <Modal opened={opened} onClose={close} title="Create Action" size="md">
        <Stack>
          <Select
            label="Action Type"
            placeholder="Select type"
            data={[
              { value: "investigate", label: "Investigate" },
              { value: "escalate", label: "Escalate" },
              { value: "update_data", label: "Update Training Data" },
              { value: "generate_report", label: "Generate Compliance Report" },
            ]}
            value={form.action_type}
            onChange={(v) => setForm((f) => ({ ...f, action_type: v || "" }))}
            required
          />
          <TextInput
            label="Title"
            placeholder="Brief title for the action"
            value={form.title}
            onChange={(e) => setForm((f) => ({ ...f, title: e.currentTarget.value }))}
            required
          />
          <Textarea
            label="Description"
            placeholder="Detailed description of the action needed"
            value={form.description}
            onChange={(e) => setForm((f) => ({ ...f, description: e.currentTarget.value }))}
            minRows={3}
          />
          <TextInput
            label="Assigned To"
            placeholder="Person or team responsible"
            value={form.assigned_to}
            onChange={(e) => setForm((f) => ({ ...f, assigned_to: e.currentTarget.value }))}
          />
          <Group justify="flex-end" mt="md">
            <Button variant="default" onClick={close}>
              Cancel
            </Button>
            <Button onClick={handleCreate} loading={submitting}>
              Create
            </Button>
          </Group>
        </Stack>
      </Modal>
    </Stack>
  );
}
