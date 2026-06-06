import { createTheme, virtualColor } from "@mantine/core";

export const theme = createTheme({
  primaryColor: "fairness",
  colors: {
    fairness: virtualColor({
      name: "fairness",
      dark: "blue",
      light: "blue",
    }),
    severity: [
      "#fff0f0",
      "#ffd6d6",
      "#ffb3b3",
      "#ff8080",
      "#ff4d4d",
      "#e63946",
      "#b71c1c",
      "#8a1414",
      "#5e0e0e",
      "#3a0808",
    ],
    compliance: [
      "#e6f9ed",
      "#c2f0d4",
      "#85e2a8",
      "#47d47c",
      "#1db954",
      "#14a044",
      "#0d7d33",
      "#095d25",
      "#063e19",
      "#03210d",
    ],
  },
  fontFamily:
    "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
  defaultRadius: "md",
  components: {
    Paper: {
      defaultProps: {
        shadow: "sm",
        p: "lg",
        radius: "md",
      },
    },
  },
});
