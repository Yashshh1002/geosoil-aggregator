export interface Location {
  lat: number;
  lon: number;
  name?: string | null;
}

export interface SoilType {
  primary: string | null;
  probability: number | null;
  alternatives: [string, number][] | null;
  property_based_suggestions: string[] | null;
  confidence_note: string | null;
}

export interface DepthValues {
  value: number | null;
  unit: string;
  depths: Record<string, number | null> | null;
}

export interface AngleOfFriction {
  value: number | null;
  unit: string;
  method: string;
}

export interface Texture {
  sand_pct: number | null;
  silt_pct: number | null;
  clay_pct: number | null;
  classification: string | null;
  depths: Record<string, Record<string, number | null>> | null;
}

export interface Elevation {
  value: number | null;
  unit: string;
}

export interface SoilQueryResponse {
  location: Location;
  soil_type: SoilType | null;
  bulk_density: DepthValues | null;
  ph_level: DepthValues | null;
  angle_of_friction: AngleOfFriction | null;
  texture: Texture | null;
  topography_elevation: Elevation | null;
  general_description: string | null;
  sources: string[];
  warnings: string[];
  queried_at: string;
}
