import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import App from "./App.tsx";
import { Provider } from "@/components/ui/provider";
import { AgentProvider } from "./context/agent-ctx.tsx";

createRoot(document.getElementById("root")!).render(
    <StrictMode>
        <Provider>
            <AgentProvider>
                <App />
            </AgentProvider>
        </Provider>
    </StrictMode>
);
