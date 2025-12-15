import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { ChevronLeft, Loader2 } from "lucide-react";

const API_URL =
  (import.meta.env.VITE_API_URL as string) ||
  "https://apex-backend-i7b0.onrender.com";

export default function ContactDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [contact, setContact] = useState<any>(null);

  useEffect(() => {
    if (!id) return;

    let cancelled = false;

    (async () => {
      try {
        setLoading(true);
        setError(null);

        const res = await fetch(`${API_URL}/api/contacts/${id}`);
        if (!res.ok) {
          throw new Error(`Request failed: ${res.status}`);
        }

        const data = await res.json();
        if (!cancelled) setContact(data.contact ?? data);
      } catch (e: any) {
        if (!cancelled) setError(e?.message ?? "Failed to load contact");
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [id]);

  if (loading) {
    return (
      <div className="min-h-screen bg-[#0f1114] text-white flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-purple-400" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-[#0f1114] text-white p-6">
        <div className="max-w-3xl mx-auto">
          <button
            onClick={() => navigate(-1)}
            className="inline-flex items-center gap-2 text-gray-400 hover:text-white"
          >
            <ChevronLeft size={18} /> Back
          </button>
          <div className="mt-4 bg-[#1e2228] border border-gray-800 rounded-xl p-4">
            <p className="text-red-400 font-medium">Failed to load contact.</p>
            <p className="text-gray-400 text-sm mt-1">{error}</p>
          </div>
        </div>
      </div>
    );
  }

  if (!contact) {
    return (
      <div className="min-h-screen bg-[#0f1114] text-white p-6">
        <div className="max-w-3xl mx-auto">
          <button
            onClick={() => navigate(-1)}
            className="inline-flex items-center gap-2 text-gray-400 hover:text-white"
          >
            <ChevronLeft size={18} /> Back
          </button>
          <div className="mt-4 bg-[#1e2228] border border-gray-800 rounded-xl p-4">
            <p className="text-gray-400">Contact not found.</p>
          </div>
        </div>
      </div>
    );
  }

  const name =
    (contact.name as string | undefined) ||
    `${contact.firstname ?? ""} ${contact.lastname ?? ""}`.trim() ||
    "Contact";

  return (
    <div className="min-h-screen bg-[#0f1114] text-white p-6">
      <div className="max-w-4xl mx-auto">
        <button
          onClick={() => navigate(-1)}
          className="inline-flex items-center gap-2 text-gray-400 hover:text-white"
        >
          <ChevronLeft size={18} /> Back
        </button>

        <h1 className="mt-4 text-2xl font-bold">{name}</h1>
        <p className="text-gray-400 mt-1">
          {contact.title ? `${contact.title} · ` : ""}
          {contact.company ?? ""}
        </p>

        <div className="mt-6 bg-[#1e2228] border border-gray-800 rounded-xl p-4 overflow-auto">
          <pre className="text-xs text-gray-300 whitespace-pre-wrap">
            {JSON.stringify(contact, null, 2)}
          </pre>
        </div>
      </div>
    </div>
  );
}
