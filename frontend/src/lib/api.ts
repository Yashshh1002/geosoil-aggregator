import { SoilQueryResponse } from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function querySoil(
  lat: number,
  lon: number
): Promise<SoilQueryResponse> {
  const res = await fetch(
    `${API_URL}/api/v1/soil/query?lat=${lat}&lon=${lon}`
  );
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Failed to fetch soil data");
  }
  return res.json();
}

export async function uploadKmz(
  file: File
): Promise<SoilQueryResponse[]> {
  const formData = new FormData();
  formData.append("file", file);
  const res = await fetch(`${API_URL}/api/v1/soil/upload`, {
    method: "POST",
    body: formData,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Failed to process file");
  }
  return res.json();
}
