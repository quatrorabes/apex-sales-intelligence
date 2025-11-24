import React, { useEffect, useMemo, useState, useRef } from "react";
import {
  Search,
  Users,
  TrendingUp,
  Brain,
  Sparkles,
  Zap,
  RefreshCw,
  Clock,
  List,
  Grid,
  ArrowUpDown,
  CheckCircle2,
  Eye,
  Mail,
  Phone,
  MessageSquare,
  Building,
  Briefcase,
  X,
  Upload,
  FileText,
  Database,
  Download,
  Target
} from "lucide-react";
import ContactEnrichmentView from "./components/ContactEnrichmentView";
import ContactDetailModal from "./components/ContactDetailModal";
import CadenceDashboard from "./components/CadenceDashboard";
import RawDataViewer from "./components/RawDataViewer";
import { ApexIntelligenceDashboard } from "./components/ApexIntelligence";
import BatchProgress from "./components/BatchProgress";

export interface Contact {
  id: number;
  hubspot_id?: string;
  name: string;
  firstname?: string;
  lastname?: string;
  title: string | null;
  company: string | null;
  email: string | null;
  phone?: string | null;
  linkedin_url?: string | null;
  enrichment_status?: "pending" | "processing" | "complete" | "failed" | null;
  enrichment_data?: any;
  opportunity_score?: number;
  dashboard?: any;
  generated_scripts?: any;
  pain_points?: string[];
  talking_points?: string[];
  trigger_events?: string[];
  mdcp_score?: number;
  rss_score?: number;
  priority_score?: number;
  mdcp_tier?: string;
  rss_tier?: string;
  urgency_level?: string;
  recommended_action?: string;
  persona_tier?: string;
  persona_type?: string;
  last_scored?: string;
}

interface Analytics {
  total_contacts: number;
  enriched_contacts: number;
  pending_enrichment: number;
  avg_opportunity_score: number;
  contacts_last_30_days: number;
  high_priority_contacts: number;
  scored_contacts?: number;
  pending_scoring?: number;
}

function App() {
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [analytics, setAnalytics] = useState<Analytics>({
    total_contacts: 0,
    enriched_contacts: 0,
    pending_enrichment: 0,
    avg_opportunity_score: 0,
    contacts_last_30_days: 0,
    high_priority_contacts: 0,
    scored_contacts: 0,
    pending_scoring: 0
  });
  const [searchTerm, setSearchTerm] = useState("");
  const [filterStatus, setFilterStatus] = useState("all");
  const [selectedContact, setSelectedContact] = useState<Contact | null>(null);
  const [showEnrichmentView, setShowEnrichmentView] = useState(false);
  const [selectedContacts, setSelectedContacts] = useState<Set<number>>(new Set());
  const [isLoading, setIsLoading] = useState(false);
  const [activeTab, setActiveTab] = useState("contacts");
  const [viewMode, setViewMode] = useState<"list" | "card">("list");
  const [showBatchProgress, setShowBatchProgress] = useState(false);
  const [sortConfig, setSortConfig] = useState<{
    key: keyof Contact;
    direction: "asc" | "desc";
  }>({ key: "name", direction: "asc" });
  const [showRawData, setShowRawData] = useState(false);
  const [selectedRawData, setSelectedRawData] = useState<any>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";
  
  const fetchContacts = async () => {
    try {
      const response = await fetch(API_BASE + "/api/contacts");
      if (!response.ok) {
        throw new Error(`Failed to fetch contacts: ${response.statusText}`);
      }
      const data = await response.json();
      setContacts(data);
    } catch (error) {
      console.error("Error fetching contacts:", error);
      setContacts([]);
    }
  };

  const fetchAnalytics = async () => {
    try {
      // Calculate analytics from contacts since there's no dedicated endpoint
      const enriched = contacts.filter(c => c.enrichment_status === 'complete').length;
      const pending = contacts.filter(c => !c.enrichment_status || c.enrichment_status === 'pending').length;
      const scored = contacts.filter(c => c.priority_score).length;
      const avgScore = contacts.reduce((sum, c) => sum + (c.priority_score || 0), 0) / (scored || 1);
      
      setAnalytics({
        total_contacts: contacts.length,
        enriched_contacts: enriched,
        pending_enrichment: pending,
        avg_opportunity_score: avgScore,
        contacts_last_30_days: contacts.length,
        high_priority_contacts: contacts.filter(c => (c.priority_score || 0) >= 80).length,
        scored_contacts: scored,
        pending_scoring: contacts.length - scored
      });
    } catch (error) {
      console.error("Error calculating analytics:", error);
    }
  };

  useEffect(() => {
    fetchContacts();
  }, []);

  useEffect(() => {
    if (contacts.length > 0) {
      fetchAnalytics();
    }
  }, [contacts]);

  const handleImportFromHubSpot = async () => {
    if (!confirm("Import up to 100 new contacts from HubSpot?")) return;
    
    setIsLoading(true);
    try {
      const response = await fetch(API_BASE + "/api/hubspot/import", {
        method: "POST",
      });
      const data = await response.json();
      
      if (data.success) {
        alert(
          `Successfully imported ${data.imported} new contacts!\n` +
          `Skipped ${data.existing} existing contacts\n` +
          `Filtered out ${data.filtered} contacts\n` +
          `Total in HubSpot: ${data.total_in_hubspot}`
        );
        fetchContacts();
      } else {
        alert(`Import failed: ${data.message || data.error}`);
      }
    } catch (error) {
      console.error("Error importing from HubSpot:", error);
      alert("Failed to import contacts from HubSpot");
    } finally {
      setIsLoading(false);
    }
  };

  const handleScoreContact = async (contactId: number) => {
    setIsLoading(true);
    try {
      const response = await fetch(API_BASE + `/api/contacts/${contactId}/score`, {
        method: "POST",
      });
      const data = await response.json();
      
      if (data.success) {
        alert(
          `Contact scored successfully!\n\n` +
          `Priority Score: ${Math.round(data.scores.priority_score)}\n` +
          `MDCP Score: ${Math.round(data.scores.mdcp_score)}\n` +
          `RSS Score: ${Math.round(data.scores.rss_score)}\n` +
          `Urgency: ${data.tiers?.urgency_level || 'N/A'}`
        );
        fetchContacts();
      } else {
        alert(`Scoring failed: ${data.error}`);
      }
    } catch (error) {
      console.error("Error scoring contact:", error);
      alert("Failed to score contact");
    } finally {
      setIsLoading(false);
    }
  };

  const handleScoreBatch = async () => {
    if (!confirm("Score up to 50 unscored contacts?")) return;
    
    setIsLoading(true);
    setShowBatchProgress(true);
    try {
      const response = await fetch(API_BASE + "/api/contacts/score-batch", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ limit: 50 }),
      });
      const data = await response.json();
      
      if (data.success) {
        alert(
          `Batch scoring complete!\n` +
          `Scored: ${data.scored}\n` +
          `Failed: ${data.failed}\n` +
          `Total: ${data.total}`
        );
        fetchContacts();
      } else {
        alert(`Batch scoring failed: ${data.error}`);
      }
    } catch (error) {
      console.error("Error in batch scoring:", error);
      alert("Failed to score contacts");
    } finally {
      setIsLoading(false);
      setShowBatchProgress(false);
    }
  };

  const handleEnrichSelected = async () => {
    if (selectedContacts.size === 0) {
      alert("Please select contacts to enrich");
      return;
    }
  
    if (!confirm(`Enrich ${selectedContacts.size} selected contact(s)?`)) {
      return;
    }
  
    setIsLoading(true);
    setShowBatchProgress(true);
  
    try {
      const contactIds = Array.from(selectedContacts);
      let successCount = 0;
      let failCount = 0;
      
      for (const contactId of contactIds) {
        try {
          const response = await fetch(API_BASE + `/api/contacts/${contactId}/enrich`, {
            method: "POST",
          });
          
          if (response.ok) {
            successCount++;
          } else {
            failCount++;
          }
        } catch (err) {
          failCount++;
        }
      }
  
      alert(
        `Enrichment complete!\n` +
        `Success: ${successCount}\n` +
        `Failed: ${failCount}`
      );
      
      fetchContacts();
      setSelectedContacts(new Set()); // Clear selection after enrichment
    } catch (error) {
      console.error("Error enriching contacts:", error);
      alert("Failed to enrich contacts");
    } finally {
      setIsLoading(false);
      setShowBatchProgress(false);
    }
  };


  const handleSort = (key: keyof Contact) => {
    setSortConfig((prev) => ({
      key,
      direction: prev.key === key && prev.direction === "asc" ? "desc" : "asc",
    }));
  };

  const filteredContacts = useMemo(() => {
    let filtered = contacts.filter((contact) => {
      const matchesSearch =
        contact.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        contact.email?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        contact.company?.toLowerCase().includes(searchTerm.toLowerCase());

      const matchesStatus =
        filterStatus === "all" ||
        contact.enrichment_status === filterStatus;

      return matchesSearch && matchesStatus;
    });

    filtered.sort((a, b) => {
      const aValue = a[sortConfig.key];
      const bValue = b[sortConfig.key];

      if (aValue == null) return 1;
      if (bValue == null) return -1;

      if (typeof aValue === "string" && typeof bValue === "string") {
        return sortConfig.direction === "asc"
          ? aValue.localeCompare(bValue)
          : bValue.localeCompare(aValue);
      }

      if (typeof aValue === "number" && typeof bValue === "number") {
        return sortConfig.direction === "asc"
          ? aValue - bValue
          : bValue - aValue;
      }

      return 0;
    });

    return filtered;
  }, [contacts, searchTerm, filterStatus, sortConfig]);

  const toggleContactSelection = (contactId: number) => {
    setSelectedContacts((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(contactId)) {
        newSet.delete(contactId);
      } else {
        newSet.add(contactId);
      }
      return newSet;
    });
  };

  const getScoreTierClass = (score?: number): string => {
    if (!score) return "bg-gray-600 text-gray-300";
    if (score >= 80) return "bg-red-600 text-white";
    if (score >= 65) return "bg-orange-500 text-white";
    if (score >= 50) return "bg-blue-500 text-white";
    return "bg-gray-500 text-gray-300";
  };

  const getUrgencyBadgeClass = (urgency?: string): string => {
    if (!urgency) return "";
    const level = urgency.toLowerCase();
    if (level === "immediate") return "bg-red-600 text-white";
    if (level === "high") return "bg-orange-500 text-white";
    if (level === "medium") return "bg-blue-500 text-white";
    return "bg-gray-500 text-gray-300";
  };

  const handleViewEnrichment = (contact: Contact) => {
    setSelectedContact(contact);
    setShowEnrichmentView(true);
  };

  const handleViewRawData = (contact: Contact) => {
    setSelectedRawData(contact);
    setShowRawData(true);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <header className="border-b border-slate-800 bg-slate-900/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg">
                <Sparkles className="w-6 h-6" />
              </div>
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
                  APEX Sales Intelligence
                </h1>
                <p className="text-sm text-slate-400">AI-Powered Contact Enrichment & Scoring</p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <button
                onClick={handleImportFromHubSpot}
                disabled={isLoading}
                className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Upload className="w-4 h-4" />
                Import from HubSpot
              </button>

              <button
                onClick={handleScoreBatch}
                disabled={isLoading}
                className="flex items-center gap-2 px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Target className="w-4 h-4" />
                Score Batch
              </button>

              {selectedContacts.size > 0 && (
                <button
                  onClick={handleEnrichSelected}
                  disabled={isLoading}
                  className="flex items-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-700 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <Brain className="w-4 h-4" />
                  Enrich Selected ({selectedContacts.size})
                </button>
              )}
            </div>
          </div>

          <div className="flex gap-4 mt-4">
            <button
              onClick={() => setActiveTab("contacts")}
              className={`px-4 py-2 rounded-lg transition-colors ${
                activeTab === "contacts"
                  ? "bg-blue-600 text-white"
                  : "bg-slate-800 text-slate-300 hover:bg-slate-700"
              }`}
            >
              <Users className="w-4 h-4 inline mr-2" />
              Contacts
            </button>
            <button
              onClick={() => setActiveTab("cadence")}
              className={`px-4 py-2 rounded-lg transition-colors ${
                activeTab === "cadence"
                  ? "bg-blue-600 text-white"
                  : "bg-slate-800 text-slate-300 hover:bg-slate-700"
              }`}
            >
              <MessageSquare className="w-4 h-4 inline mr-2" />
              Cadence
            </button>
            <button
              onClick={() => setActiveTab("intelligence")}
              className={`px-4 py-2 rounded-lg transition-colors ${
                activeTab === "intelligence"
                  ? "bg-blue-600 text-white"
                  : "bg-slate-800 text-slate-300 hover:bg-slate-700"
              }`}
            >
              <Brain className="w-4 h-4 inline mr-2" />
              Apex Intelligence
            </button>
          </div>
        </div>
      </header>

      {activeTab === "contacts" && (
        <div className="container mx-auto px-4 py-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            <div className="bg-slate-900 rounded-lg p-6 border border-slate-800">
              <div className="flex items-center justify-between mb-2">
                <Users className="w-5 h-5 text-blue-400" />
                <span className="text-sm text-slate-400">Total</span>
              </div>
              <div className="text-3xl font-bold">{analytics.total_contacts}</div>
              <div className="text-sm text-slate-400 mt-1">Contacts</div>
            </div>

            <div className="bg-slate-900 rounded-lg p-6 border border-slate-800">
              <div className="flex items-center justify-between mb-2">
                <Target className="w-5 h-5 text-purple-400" />
                <span className="text-sm text-slate-400">Scored</span>
              </div>
              <div className="text-3xl font-bold">{analytics.scored_contacts || 0}</div>
              <div className="text-sm text-slate-400 mt-1">
                {analytics.pending_scoring || 0} pending
              </div>
            </div>

            <div className="bg-slate-900 rounded-lg p-6 border border-slate-800">
              <div className="flex items-center justify-between mb-2">
                <Brain className="w-5 h-5 text-green-400" />
                <span className="text-sm text-slate-400">Enriched</span>
              </div>
              <div className="text-3xl font-bold">{analytics.enriched_contacts}</div>
              <div className="text-sm text-slate-400 mt-1">
                {analytics.pending_enrichment} pending
              </div>
            </div>

            <div className="bg-slate-900 rounded-lg p-6 border border-slate-800">
              <div className="flex items-center justify-between mb-2">
                <TrendingUp className="w-5 h-5 text-orange-400" />
                <span className="text-sm text-slate-400">Avg Score</span>
              </div>
              <div className="text-3xl font-bold">
                {analytics.avg_opportunity_score
                  ? analytics.avg_opportunity_score.toFixed(1)
                  : "—"}
              </div>
              <div className="text-sm text-slate-400 mt-1">Opportunity</div>
            </div>
          </div>

          <div className="flex flex-col md:flex-row gap-4 mb-6">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-slate-400" />
                <input
                  type="text"
                  placeholder="Search contacts..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 bg-slate-900 border border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>

            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Statuses</option>
              <option value="pending">Pending</option>
              <option value="processing">Processing</option>
              <option value="complete">Complete</option>
              <option value="failed">Failed</option>
            </select>

            <div className="flex gap-2">
              <button
                onClick={() => setViewMode("list")}
                className={`p-2 rounded-lg ${
                  viewMode === "list"
                    ? "bg-blue-600"
                    : "bg-slate-800 hover:bg-slate-700"
                }`}
              >
                <List className="w-5 h-5" />
              </button>
              <button
                onClick={() => setViewMode("card")}
                className={`p-2 rounded-lg ${
                  viewMode === "card"
                    ? "bg-blue-600"
                    : "bg-slate-800 hover:bg-slate-700"
                }`}
              >
                <Grid className="w-5 h-5" />
              </button>
            </div>
          </div>

          {viewMode === "list" ? (
            <div className="bg-slate-900 rounded-lg border border-slate-800 overflow-hidden">
              <table className="w-full">
                <thead className="bg-slate-800">
                  <tr>
                    <th className="px-4 py-3 text-left">
                      <input
                        type="checkbox"
                        checked={selectedContacts.size === contacts.length && contacts.length > 0}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setSelectedContacts(new Set(contacts.map((c) => c.id)));
                          } else {
                            setSelectedContacts(new Set());
                          }
                        }}
                        className="rounded border-slate-600"
                      />
                    </th>
                    <th
                      className="px-4 py-3 text-left cursor-pointer hover:bg-slate-700"
                      onClick={() => handleSort("name")}
                    >
                      <div className="flex items-center gap-2">
                        Name
                        <ArrowUpDown className="w-4 h-4" />
                      </div>
                    </th>
                    <th className="px-4 py-3 text-left">Company</th>
                    <th className="px-4 py-3 text-left">Title</th>
                    <th
                      className="px-4 py-3 text-left cursor-pointer hover:bg-slate-700"
                      onClick={() => handleSort("priority_score")}
                    >
                      <div className="flex items-center gap-2">
                        Score
                        <ArrowUpDown className="w-4 h-4" />
                      </div>
                    </th>
                    <th className="px-4 py-3 text-left">Status</th>
                    <th className="px-4 py-3 text-left">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredContacts.length === 0 ? (
                    <tr>
                      <td colSpan={7} className="px-4 py-8 text-center text-slate-400">
                        No contacts found. Import contacts to get started.
                      </td>
                    </tr>
                  ) : (
                    filteredContacts.map((contact) => (
                      <tr
                        key={contact.id}
                        className="border-t border-slate-800 hover:bg-slate-800/50"
                      >
                        <td className="px-4 py-3">
                          <input
                            type="checkbox"
                            checked={selectedContacts.has(contact.id)}
                            onChange={() => toggleContactSelection(contact.id)}
                            className="rounded border-slate-600"
                          />
                        </td>
                        <td className="px-4 py-3">
                          <div>
                            <div className="font-medium">{contact.name}</div>
                            <div className="text-sm text-slate-400">{contact.email}</div>
                          </div>
                        </td>
                        <td className="px-4 py-3">{contact.company || "—"}</td>
                        <td className="px-4 py-3">{contact.title || "—"}</td>
                        <td className="px-4 py-3">
                          {contact.priority_score ? (
                            <div className="flex flex-col gap-1">
                              <span
                                className={`inline-flex items-center justify-center px-3 py-1 rounded-full text-sm font-bold ${getScoreTierClass(
                                  contact.priority_score
                                )}`}
                              >
                                {Math.round(contact.priority_score)}
                              </span>
                              {contact.urgency_level && (
                                <span
                                  className={`text-xs px-2 py-0.5 rounded ${getUrgencyBadgeClass(
                                    contact.urgency_level
                                  )}`}
                                >
                                  {contact.urgency_level}
                                </span>
                              )}
                            </div>
                          ) : (
                            <span className="text-slate-500">—</span>
                          )}
                        </td>
                        <td className="px-4 py-3">
                          {contact.enrichment_status === "complete" ? (
                            <span className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-green-900/50 text-green-300">
                              <CheckCircle2 className="w-3 h-3 mr-1" />
                              Complete
                            </span>
                          ) : contact.enrichment_status === "processing" ? (
                            <span className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-blue-900/50 text-blue-300">
                              <RefreshCw className="w-3 h-3 mr-1 animate-spin" />
                              Processing
                            </span>
                          ) : (
                            <span className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-slate-800 text-slate-400">
                              <Clock className="w-3 h-3 mr-1" />
                              Pending
                            </span>
                          )}
                        </td>
                        <td className="px-4 py-3">
                          <div className="flex gap-2">
                            {!contact.priority_score && (
                              <button
                                onClick={() => handleScoreContact(contact.id)}
                                className="p-1.5 hover:bg-slate-700 rounded"
                                title="Score Contact"
                              >
                                <Target className="w-4 h-4" />
                              </button>
                            )}
                            {contact.enrichment_status === "complete" && (
                              <>
                                <button
                                  onClick={() => handleViewEnrichment(contact)}
                                  className="p-1.5 hover:bg-slate-700 rounded"
                                  title="View Intelligence"
                                >
                                  <Eye className="w-4 h-4" />
                                </button>
                                <button
                                  onClick={() => handleViewRawData(contact)}
                                  className="p-1.5 hover:bg-slate-700 rounded"
                                  title="View Raw Data"
                                >
                                  <Database className="w-4 h-4" />
                                </button>
                              </>
                            )}
                          </div>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {filteredContacts.map((contact) => (
                <div
                  key={contact.id}
                  className="bg-slate-900 rounded-lg border border-slate-800 p-4 hover:border-blue-500 transition-colors"
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <h3 className="font-semibold text-lg">{contact.name}</h3>
                      {contact.title && (
                        <p className="text-sm text-slate-400">{contact.title}</p>
                      )}
                      {contact.company && (
                        <p className="text-sm text-blue-400">{contact.company}</p>
                      )}
                    </div>
                    {contact.priority_score && (
                      <span
                        className={`px-3 py-1 rounded-full text-sm font-bold ${getScoreTierClass(
                          contact.priority_score
                        )}`}
                      >
                        {Math.round(contact.priority_score)}
                      </span>
                    )}
                  </div>

                  <div className="space-y-2 mb-4">
                    {contact.email && (
                      <div className="flex items-center gap-2 text-sm text-slate-300">
                        <Mail className="w-4 h-4 text-slate-500" />
                        {contact.email}
                      </div>
                    )}
                    {contact.phone && (
                      <div className="flex items-center gap-2 text-sm text-slate-300">
                        <Phone className="w-4 h-4 text-slate-500" />
                        {contact.phone}
                      </div>
                    )}
                  </div>

                  {contact.urgency_level && (
                    <div className="mb-3">
                      <span
                        className={`text-xs px-2 py-1 rounded ${getUrgencyBadgeClass(
                          contact.urgency_level
                        )}`}
                      >
                        {contact.urgency_level} Urgency
                      </span>
                    </div>
                  )}

                  <div className="flex gap-2">
                    {!contact.priority_score && (
                      <button
                        onClick={() => handleScoreContact(contact.id)}
                        className="flex-1 px-3 py-2 bg-purple-600 hover:bg-purple-700 rounded text-sm"
                      >
                        Score
                      </button>
                    )}
                    {contact.enrichment_status === "complete" && (
                      <button
                        onClick={() => handleViewEnrichment(contact)}
                        className="flex-1 px-3 py-2 bg-blue-600 hover:bg-blue-700 rounded text-sm"
                      >
                        View Intel
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {activeTab === "cadence" && <CadenceDashboard contacts={contacts} />}

      {activeTab === "intelligence" && <ApexIntelligenceDashboard contacts={contacts} />}

      {showEnrichmentView && selectedContact && (
        <ContactEnrichmentView 
          contactId={selectedContact.id}
          onClose={() => {
            setShowEnrichmentView(false);
            setSelectedContact(null);
          }}
        />
      )}


      {showRawData && selectedRawData && (
        <RawDataViewer
          data={selectedRawData}
          onClose={() => {
            setShowRawData(false);
            setSelectedRawData(null);
          }}
        />
      )}

      {showBatchProgress && <BatchProgress onClose={() => setShowBatchProgress(false)} />}

      {isLoading && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-slate-900 rounded-lg p-8 flex flex-col items-center gap-4">
            <RefreshCw className="w-12 h-12 animate-spin text-blue-500" />
            <p className="text-lg">Processing...</p>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
