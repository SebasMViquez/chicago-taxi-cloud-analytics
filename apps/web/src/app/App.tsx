import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Navigate, RouterProvider, createBrowserRouter } from "react-router-dom";
import { AppLayout } from "../components/layout/AppLayout";
import { DashboardPage } from "../features/dashboard/DashboardPage";
import { DashboardShell } from "../features/dashboard/DashboardShell";
import { PaymentsPage } from "../features/dashboard/PaymentsPage";
import { QualityPage } from "../features/dashboard/QualityPage";
import { ZonesPage } from "../features/dashboard/ZonesPage";
import { LandingPage } from "../features/landing/LandingPage";

const queryClient = new QueryClient({
  defaultOptions: { queries: { staleTime: 60_000, retry: 1, refetchOnWindowFocus: false } },
});

const router = createBrowserRouter([
  {
    path: "/",
    element: <AppLayout />,
    children: [
      { index: true, element: <LandingPage /> },
      { path: "dashboard", element: <DashboardShell />, children: [
        { index: true, element: <Navigate to="resumen" replace /> },
        { path: "resumen", element: <DashboardPage /> },
        { path: "zonas", element: <ZonesPage /> },
        { path: "pagos", element: <PaymentsPage /> },
        { path: "calidad", element: <QualityPage /> },
      ] },
    ],
  },
]);

export function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <RouterProvider router={router} />
    </QueryClientProvider>
  );
}

