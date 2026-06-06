import { Component, type ReactNode, type ErrorInfo } from "react";
import { Text, Paper, Stack, Title } from "@mantine/core";

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export default class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false, error: null };

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error("ErrorBoundary caught:", error, info);
  }

  render() {
    if (this.state.hasError) {
      return (
        this.props.fallback || (
          <Paper p="xl" mt="lg">
            <Stack align="center" gap="sm">
              <Title order={4}>Something went wrong</Title>
              <Text size="sm" c="dimmed">
                {this.state.error?.message || "An unexpected error occurred"}
              </Text>
            </Stack>
          </Paper>
        )
      );
    }
    return this.props.children;
  }
}
