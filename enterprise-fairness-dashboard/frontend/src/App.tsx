import {
  AppShell,
  Group,
  NavLink,
  Text,
  Title,
  useMantineColorScheme,
} from "@mantine/core";
import {
  IconChartBar,
  IconAlertTriangle,
  IconShieldCheck,
  IconPlayerPlay,
  IconMoon,
  IconSun,
} from "@tabler/icons-react";
import { Route, Routes, useLocation, useNavigate } from "react-router-dom";

import ErrorBoundary from "./components/ErrorBoundary";
import Actions from "./pages/Actions";
import Alerts from "./pages/Alerts";
import Compliance from "./pages/Compliance";
import Dashboard from "./pages/Dashboard";

const NAV_ITEMS = [
  { label: "Dashboard", icon: IconChartBar, path: "/" },
  { label: "Bias Alerts", icon: IconAlertTriangle, path: "/alerts" },
  { label: "Compliance", icon: IconShieldCheck, path: "/compliance" },
  { label: "Actions", icon: IconPlayerPlay, path: "/actions" },
];

export default function App() {
  const location = useLocation();
  const navigate = useNavigate();
  const { colorScheme, toggleColorScheme } = useMantineColorScheme();
  const dark = colorScheme === "dark";

  return (
    <AppShell
      navbar={{ width: 240, breakpoint: 0 }}
      header={{ height: 56 }}
      padding="lg"
    >
      <AppShell.Header>
        <Group h="100%" px="lg" justify="space-between">
          <Group>
            <IconShieldCheck size={24} color="var(--mantine-color-blue-6)" />
            <Title order={4}>Fairness &amp; Bias Dashboard</Title>
          </Group>
          <IconAlertTriangle
            size={20}
            style={{ cursor: "pointer" }}
            onClick={() => toggleColorScheme()}
          >
            {dark ? <IconSun size={18} /> : <IconMoon size={18} />}
          </IconAlertTriangle>
        </Group>
      </AppShell.Header>

      <AppShell.Navbar p="xs">
        <AppShell.Section grow mt="md">
          {NAV_ITEMS.map((item) => (
            <NavLink
              key={item.path}
              label={item.label}
              leftSection={<item.icon size={20} />}
              active={location.pathname === item.path}
              onClick={() => navigate(item.path)}
              variant="light"
              mb={4}
            />
          ))}
        </AppShell.Section>
        <AppShell.Section>
          <Text size="xs" c="dimmed" ta="center" py="sm">
            Enterprise Fairness v1.0
          </Text>
        </AppShell.Section>
      </AppShell.Navbar>

      <AppShell.Main style={{ overflowY: "scroll", scrollbarGutter: "stable" }}>
        <ErrorBoundary>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/alerts" element={<Alerts />} />
            <Route path="/compliance" element={<Compliance />} />
            <Route path="/actions" element={<Actions />} />
          </Routes>
        </ErrorBoundary>
      </AppShell.Main>
    </AppShell>
  );
}
