import "@mantine/core/styles.css";
import "@mantine/charts/styles.css";
import "@mantine/notifications/styles.css";

import { MantineProvider } from "@mantine/core";
import { Notifications } from "@mantine/notifications";
import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";

import App from "./App";
import { theme } from "./theme";

import "./global.css";

const origOnError = window.onerror;
window.onerror = (msg, url, line, col, err) => {
  if (typeof msg === "string" && msg.includes("ResizeObserver")) return true;
  return origOnError?.call(window, msg, url, line, col, err);
};

ReactDOM.createRoot(document.getElementById("root")!).render(
  <MantineProvider theme={theme} defaultColorScheme="light">
    <Notifications position="top-right" />
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </MantineProvider>
);
