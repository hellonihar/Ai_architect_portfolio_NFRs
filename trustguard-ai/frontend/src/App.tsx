import {
  AppShell,
  Burger,
  Group,
  NavLink,
  Text,
  Title,
  useMantineColorScheme,
} from "@mantine/core";
import { useDisclosure } from "@mantine/hooks";
import {
  IconAlertTriangle,
  IconChartBar,
  IconShieldCheck,
  IconShieldHalf,
} from "@tabler/icons-react";
import { Route, Routes, useLocation, useNavigate } from "react-router-dom";
import { ErrorBoundary } from "./components/ErrorBoundary";
import { Alerts } from "./pages/Alerts";
import { Governance } from "./pages/Governance";
import { PipelineStatus } from "./pages/PipelineStatus";
import { ReliabilityDashboard } from "./pages/ReliabilityDashboard";

const navItems = [
  { label: "Reliability Dashboard", icon: IconChartBar, path: "/" },
  { label: "Pipeline Status", icon: IconShieldHalf, path: "/pipelines" },
  { label: "Governance", icon: IconShieldCheck, path: "/governance" },
  { label: "Alerts", icon: IconAlertTriangle, path: "/alerts" },
];

export default function App() {
  const [opened, { toggle }] = useDisclosure();
  const navigate = useNavigate();
  const location = useLocation();
  const { colorScheme, toggleColorScheme } = useMantineColorScheme();

  return (
    <AppShell
      header={{ height: 56 }}
      navbar={{ width: 260, breakpoint: "sm", collapsed: { mobile: !opened } }}
      padding="md"
    >
      <AppShell.Header>
        <Group h="100%" px="md" justify="space-between">
          <Group>
            <Burger opened={opened} onClick={toggle} hiddenFrom="sm" size="sm" />
            <IconShieldCheck size={28} color="var(--mantine-color-trust-6)" />
            <Title order={4}>TrustGuard AI</Title>
          </Group>
          <Text size="sm" c="dimmed">Enterprise Reliability Platform</Text>
        </Group>
      </AppShell.Header>

      <AppShell.Navbar p="xs">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            label={item.label}
            leftSection={<item.icon size={20} />}
            active={location.pathname === item.path}
            onClick={() => {
              navigate(item.path);
              toggle();
            }}
            variant="filled"
            mb={4}
          />
        ))}
      </AppShell.Navbar>

      <AppShell.Main>
        <ErrorBoundary>
          <Routes>
            <Route path="/" element={<ReliabilityDashboard />} />
            <Route path="/pipelines" element={<PipelineStatus />} />
            <Route path="/governance" element={<Governance />} />
            <Route path="/alerts" element={<Alerts />} />
          </Routes>
        </ErrorBoundary>
      </AppShell.Main>
    </AppShell>
  );
}
