import { getToken } from "@/lib/auth";
import type { components } from "@/lib/api-types";

type Schemas = components["schemas"];

export type User = Schemas["UserRead"];
export type UserPublic = Schemas["UserPublic"];
export type Institution = Schemas["InstitutionRead"];
export type DiseasePreset = Schemas["DiseasePresetRead"];
export type DiseasePresetInput = Schemas["DiseasePresetCreate"];
export type DiseasePresetPermissions = Schemas["DiseasePresetPermissions"];
export type DiseasePresetCloneInput = Schemas["DiseasePresetCloneRequest"];
export type PopulationDataset = Schemas["PopulationDatasetRead"];
export type PopulationDatasetSummary = Schemas["PopulationDatasetSummary"];
export type PopulationDatasetList = Schemas["PopulationDatasetList"];
export type PopulationGranularity = Schemas["Granularity"];
export type PopulationDatasetStatus = Schemas["DatasetStatus"];
export type RegisterInput = Schemas["UserCreate"];
export type LoginInput = Schemas["LoginRequest"];
export type ForgotPasswordInput = Schemas["ForgotPasswordRequest"];
export type ResetPasswordInput = Schemas["ResetPasswordRequest"];

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function apiFetch<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string> | undefined),
  };
  if (token) headers.Authorization = `Bearer ${token}`;

  const res = await fetch(`${API_URL}${path}`, { ...options, headers });

  if (!res.ok) {
    const body = await res.json().catch(() => null);
    const detail = body?.detail;
    const message = typeof detail === "string" ? detail : Array.isArray(detail) ? detail.map((d: { msg?: string }) => d.msg).join(", ") : res.statusText;
    throw new Error(message);
  }

  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

export async function login(email: string, password: string): Promise<{ access_token: string; token_type: string; role: string }> {
  const payload: LoginInput = { email, password };
  return apiFetch("/auth/login", { method: "POST", body: JSON.stringify(payload) });
}

export async function register(payload: RegisterInput): Promise<User> {
  return apiFetch("/auth/register", { method: "POST", body: JSON.stringify(payload) });
}

export async function forgotPassword(email: string): Promise<{ detail: string }> {
  const payload: ForgotPasswordInput = { email };
  return apiFetch("/auth/password/forgot", { method: "POST", body: JSON.stringify(payload) });
}

export async function resetPassword(token: string, password: string): Promise<{ detail: string }> {
  const payload: ResetPasswordInput = { token, password };
  return apiFetch("/auth/password/reset", { method: "POST", body: JSON.stringify(payload) });
}

export async function getMe(): Promise<User> {
  return apiFetch("/users/me");
}

export async function getUserPublic(id: string): Promise<UserPublic> {
  return apiFetch(`/users/${id}`);
}

export async function getInstitutions(): Promise<Institution[]> {
  return apiFetch("/institutions");
}

export async function getDiseasePresets(): Promise<DiseasePreset[]> {
  return apiFetch("/disease-presets");
}

export async function getDiseasePreset(id: string): Promise<DiseasePreset> {
  return apiFetch(`/disease-presets/${id}`);
}

export async function createDiseasePreset(payload: DiseasePresetInput): Promise<DiseasePreset> {
  return apiFetch("/disease-presets", { method: "POST", body: JSON.stringify(payload) });
}

export async function updateDiseasePreset(id: string, payload: DiseasePresetInput): Promise<DiseasePreset> {
  return apiFetch(`/disease-presets/${id}`, { method: "PUT", body: JSON.stringify(payload) });
}

export async function cloneDiseasePreset(id: string, name?: string): Promise<DiseasePreset> {
  const payload: DiseasePresetCloneInput = { name: name || null };
  return apiFetch(`/disease-presets/${id}/clone`, { method: "POST", body: JSON.stringify(payload) });
}

export async function deleteDiseasePreset(id: string): Promise<void> {
  return apiFetch(`/disease-presets/${id}`, { method: "DELETE" });
}

// --- Module 3: Population Data Management ---

export type PopulationDatasetFilters = {
  region_id?: string;
  year?: number;
  source?: string;
  status?: PopulationDatasetStatus;
  page?: number;
  page_size?: number;
};

export async function getPopulationDatasets(filters: PopulationDatasetFilters = {}): Promise<PopulationDatasetList> {
  const params = new URLSearchParams();
  Object.entries(filters).forEach(([key, value]) => {
    if (value !== undefined && value !== "") params.set(key, String(value));
  });
  const query = params.toString();
  return apiFetch(`/population-datasets${query ? `?${query}` : ""}`);
}

export async function getPopulationDataset(id: string): Promise<PopulationDatasetSummary> {
  return apiFetch(`/population-datasets/${id}`);
}

export async function getPopulationDatasetVersions(id: string): Promise<PopulationDataset[]> {
  return apiFetch(`/population-datasets/${id}/versions`);
}

export async function aggregatePopulationDataset(id: string): Promise<{ dataset_id: string; status: string; detail: string }> {
  return apiFetch(`/population-datasets/${id}/aggregate`, { method: "POST" });
}

export type PopulationImportInput = {
  name: string;
  region_id: string;
  year: number;
  source: string;
  granularity: PopulationGranularity;
  file: File;
};

export async function importPopulationDataset(input: PopulationImportInput): Promise<PopulationDataset> {
  const token = getToken();
  const form = new FormData();
  form.set("name", input.name);
  form.set("region_id", input.region_id);
  form.set("year", String(input.year));
  form.set("source", input.source);
  form.set("granularity", input.granularity);
  form.set("file", input.file);

  // Not apiFetch: multipart uploads must NOT carry a JSON Content-Type - the
  // browser sets the multipart boundary header itself.
  const res = await fetch(`${API_URL}/population-datasets/import`, {
    method: "POST",
    headers: token ? { Authorization: `Bearer ${token}` } : undefined,
    body: form,
  });
  if (!res.ok) {
    const body = await res.json().catch(() => null);
    const detail = body?.detail;
    throw new Error(typeof detail === "string" ? detail : res.statusText);
  }
  return res.json() as Promise<PopulationDataset>;
}
