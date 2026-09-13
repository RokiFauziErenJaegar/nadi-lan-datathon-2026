import React from "react";
import ReactDOM from "react-dom/client";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter } from "react-router-dom";
import App from "./App";
import { PenyediaAuth } from "./lib/auth";
import { TemaProvider } from "./lib/tema";
import "./styles/index.css";
import "leaflet/dist/leaflet.css";

const klien = new QueryClient({
  defaultOptions: {
    queries: {
      // Data pada sistem ini berubah lewat proses berkala, bukan setiap detik.
      // Menahan hasil selama lima menit menghindarkan permintaan berulang saat
      // pengguna berpindah-pindah layar.
      staleTime: 5 * 60 * 1000,
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <TemaProvider>
      <QueryClientProvider client={klien}>
        <BrowserRouter>
          <PenyediaAuth>
            <App />
          </PenyediaAuth>
        </BrowserRouter>
      </QueryClientProvider>
    </TemaProvider>
  </React.StrictMode>,
);
