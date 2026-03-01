import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { ProtectedRoute } from "@/components/ProtectedRoute";
import Index from "./pages/Index";
import AuthPage from "./pages/AuthPage";
import ClientDashboard from "./pages/ClientDashboard";
import NewJobPage from "./pages/NewJobPage";
import ClientJobDetail from "./pages/ClientJobDetail";
import ArtisanDashboard from "./pages/ArtisanDashboard";
import ArtisanJobDetail from "./pages/ArtisanJobDetail";
import ArtisanProfile from "./pages/ArtisanProfile";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Index />} />
          <Route path="/auth" element={<AuthPage />} />
          
          {/* Client routes */}
          <Route element={<ProtectedRoute allowedRole="client" />}>
            <Route path="/client/dashboard" element={<ClientDashboard />} />
            <Route path="/client/new-job" element={<NewJobPage />} />
            <Route path="/client/jobs/:id" element={<ClientJobDetail />} />
          </Route>

          {/* Artisan routes */}
          <Route element={<ProtectedRoute allowedRole="artisan" />}>
            <Route path="/artisan/dashboard" element={<ArtisanDashboard />} />
            <Route path="/artisan/jobs/:id" element={<ArtisanJobDetail />} />
            <Route path="/artisan/profile" element={<ArtisanProfile />} />
          </Route>

          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
