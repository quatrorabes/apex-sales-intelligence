// src/components/Toolbar.tsx
import { useApi } from "../hooks/useApi";
import { useState } from "react";

export default function Toolbar({ selectedIds }: { selectedIds: number[] }) {
  const { post } = useApi();
  const [loading, setLoading] = useState(false);

  const handleEnrich = async () => {
    setLoading(true);
    await post("/api/apex/enrich", { contact_ids: selectedIds });
    setLoading(false);
  };

  const handleImport = async () => {
    setLoading(true);
    await post("/api/hubspot/import");
    setLoading(false);
  };

  return (
    <>
      <button disabled={loading} onClick={handleEnrich}>
        Enrich Selected
      </button>
      <button disabled={loading} onClick={handleImport}>
        Import from HubSpot
      </button>
    </>
  );
}
