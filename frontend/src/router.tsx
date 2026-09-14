import { createBrowserRouter } from "react-router-dom";

import LandingPage from "@/pages/LandingPage";
import LoginPage from "@/pages/login/page";
import RegisterPage from "@/pages/register/page";
import ForgotPasswordPage from "@/pages/forgot-password/page";
import ResetPasswordPage from "@/pages/reset-password/page";

import AppLayout from "@/pages/AppLayout";
import DashboardPage from "@/pages/dashboard/page";
import ProfilePage from "@/pages/profile/page";
import SettingsPage from "@/pages/settings/page";

import AdminInstitutionsPage from "@/pages/admin/institutions/page";
import AdminLoginActivityPage from "@/pages/admin/login-activity/page";
import AdminUsersPage from "@/pages/admin/users/page";

import AnalysisReportsPage from "@/pages/analysis/reports/page";
import AnalysisScenarioComparisonPage from "@/pages/analysis/scenario-comparison/page";
import AnalysisVisualizationsPage from "@/pages/analysis/visualizations/page";

import HealthcareCapacityPage from "@/pages/data/healthcare-capacity/page";
import InterventionPackagesPage from "@/pages/data/interventions/page";
import InterventionPackageBuilderPage from "@/pages/data/interventions/[id]/page";
import NewInterventionPackagePage from "@/pages/data/interventions/new/page";
import InterventionTypesPage from "@/pages/data/interventions/types/page";
import NewInterventionTypePage from "@/pages/data/interventions/types/new/page";
import EditInterventionTypePage from "@/pages/data/interventions/types/[id]/edit/page";
import PopulationBrowserPage from "@/pages/data/population/page";
import PopulationDatasetDetailPage from "@/pages/data/population/[id]/page";
import PopulationImportPage from "@/pages/data/population/import/page";

import DiseasePresetsPage from "@/pages/disease-presets/page";
import NewDiseasePresetPage from "@/pages/disease-presets/new/page";
import EditDiseasePresetPage from "@/pages/disease-presets/[id]/edit/page";

import SimulationHistoryPage from "@/pages/simulations/history/page";
import NewSimulationPage from "@/pages/simulations/new/page";

export const router = createBrowserRouter([
  { path: "/", element: <LandingPage /> },
  { path: "/login", element: <LoginPage /> },
  { path: "/register", element: <RegisterPage /> },
  { path: "/forgot-password", element: <ForgotPasswordPage /> },
  { path: "/reset-password", element: <ResetPasswordPage /> },
  {
    element: <AppLayout />,
    children: [
      { path: "/dashboard", element: <DashboardPage /> },
      { path: "/profile", element: <ProfilePage /> },
      { path: "/settings", element: <SettingsPage /> },

      { path: "/admin/institutions", element: <AdminInstitutionsPage /> },
      { path: "/admin/login-activity", element: <AdminLoginActivityPage /> },
      { path: "/admin/users", element: <AdminUsersPage /> },

      { path: "/analysis/reports", element: <AnalysisReportsPage /> },
      { path: "/analysis/scenario-comparison", element: <AnalysisScenarioComparisonPage /> },
      { path: "/analysis/visualizations", element: <AnalysisVisualizationsPage /> },

      { path: "/data/healthcare-capacity", element: <HealthcareCapacityPage /> },
      { path: "/data/interventions", element: <InterventionPackagesPage /> },
      { path: "/data/interventions/new", element: <NewInterventionPackagePage /> },
      { path: "/data/interventions/:id", element: <InterventionPackageBuilderPage /> },
      { path: "/data/interventions/types", element: <InterventionTypesPage /> },
      { path: "/data/interventions/types/new", element: <NewInterventionTypePage /> },
      { path: "/data/interventions/types/:id/edit", element: <EditInterventionTypePage /> },
      { path: "/data/population", element: <PopulationBrowserPage /> },
      { path: "/data/population/import", element: <PopulationImportPage /> },
      { path: "/data/population/:id", element: <PopulationDatasetDetailPage /> },

      { path: "/disease-presets", element: <DiseasePresetsPage /> },
      { path: "/disease-presets/new", element: <NewDiseasePresetPage /> },
      { path: "/disease-presets/:id/edit", element: <EditDiseasePresetPage /> },

      { path: "/simulations/history", element: <SimulationHistoryPage /> },
      { path: "/simulations/new", element: <NewSimulationPage /> },
    ],
  },
]);
