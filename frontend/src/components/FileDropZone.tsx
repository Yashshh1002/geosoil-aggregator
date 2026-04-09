"use client";

import { useCallback } from "react";
import { useDropzone } from "react-dropzone";

interface Props {
  onFile: (file: File) => void;
  loading: boolean;
}

export default function FileDropZone({ onFile, loading }: Props) {
  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      if (acceptedFiles.length > 0) {
        onFile(acceptedFiles[0]);
      }
    },
    [onFile]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "application/vnd.google-earth.kmz": [".kmz"],
      "application/vnd.google-earth.kml+xml": [".kml"],
    },
    maxFiles: 1,
    disabled: loading,
  });

  return (
    <div className="space-y-2">
      <h2 className="text-lg font-semibold text-gray-800">
        Or Upload KMZ/KML
      </h2>
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-colors ${
          isDragActive
            ? "border-emerald-500 bg-emerald-50"
            : "border-gray-300 hover:border-emerald-400 hover:bg-gray-50"
        } ${loading ? "opacity-50 cursor-not-allowed" : ""}`}
      >
        <input {...getInputProps()} />
        <div className="text-gray-500">
          <svg
            className="mx-auto h-10 w-10 mb-2 text-gray-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={1.5}
              d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
            />
          </svg>
          {isDragActive ? (
            <p className="text-emerald-600 font-medium">Drop file here</p>
          ) : (
            <p className="text-sm">
              Drag & drop a <span className="font-medium">.kmz</span> or{" "}
              <span className="font-medium">.kml</span> file here, or click to
              browse
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
