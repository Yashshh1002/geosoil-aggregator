"use client";

import { useState } from "react";
import { querySoil, uploadKmz } from "@/lib/api";
import { SoilQueryResponse } from "@/lib/types";

export function useSoilQuery() {
  const [results, setResults] = useState<SoilQueryResponse[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function queryByCoordinates(lat: number, lon: number) {
    setLoading(true);
    setError(null);
    try {
      const data = await querySoil(lat, lon);
      setResults([data]);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  }

  async function queryByFile(file: File) {
    setLoading(true);
    setError(null);
    try {
      const data = await uploadKmz(file);
      setResults(data);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  }

  return { results, loading, error, queryByCoordinates, queryByFile };
}
