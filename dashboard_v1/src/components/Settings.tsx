// =============================================================================
// Settings.tsx - Apex Sales Intelligence Dashboard v1
// =============================================================================
// Premium Settings page with Sales Playbook, Import, and API configuration
// This is the brain of Apex - powering scoring, outreach, and intelligence
// =============================================================================

import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import ImportWizard from './ImportWizard';
import {
  Settings as SettingsIcon, BookOpen, Upload, Key, Users, Building2,
  Target, Zap, Trophy, Shield, Plus, Trash2, Save, X,
  Sparkles, DollarSign, TrendingUp, AlertTriangle,
  Lightbulb, FileText, Link2, RefreshCw, CheckCircle2,
  ArrowLeft, Copy, Eye, EyeOff,
  MessageSquare, BarChart3, Globe, Package, Loader2
} from 'lucide-react';

// =============================================================================
// TYPES
// =============================================================================

interface Product {
  id: string;
  name: string;
  description: string;
  priceRange: string;
  targetAudience: string;
  keyFeatures: string[];
}

interface ValueProp {
  id: string;
  headline: string;
  description: string;
  proofPoint: string;
}

interface ICP {
  industries: string[];
  companySize: { min: number; max: number; label: string };
  titles: string[];
  regions: string[];
  techStack: string[];
  budgetRange: string;
  painPoints: string[];
}

interface PainPoint {
  id: string;
  problem: string;
  solution: string;
  impact: string;
}

interface ProofPoint {
  id: string;
  type: 'case_study' | 'metric' | 'testimonial' | 'logo';
  title: string;
  description: string;
  metric?: string;
  source?: string;
}

interface Competitor {
  id: string;
  name: string;
  weaknesses: string[];
  ourAdvantage: string;
}

interface PlaybookData {
  companyName: string;
  tagline: string;
  website: string;
  products: Product[];
  valueProps: ValueProp[];
  icp: ICP;
  painPoints: PainPoint[];
  proofPoints: ProofPoint[];
  competitors: Competitor[];
  lastUpdated: string;
}

interface APIKey {
  id: string;
  name: string;
  key: string;
  status: 'active' | 'invalid' | 'unconfigured';
  lastUsed?: string;
}

// =============================================================================
// DEFAULT DATA
// =============================================================================

const defaultPlaybook: PlaybookData = {
  companyName: '',
  tagline: '',
  website: '',
  products: [],
  valueProps: [],
  icp: {
    industries: [],
    companySize: { min: 50, max: 1000, label: 'Mid-Market' },
    titles: [],
    regions: [],
    techStack: [],
    budgetRange: '',
    painPoints: []
  },
  painPoints: [],
  proofPoints: [],
  competitors: [],
  lastUpdated: new Date().toISOString()
};

// =============================================================================
// UTILITY COMPONENTS
// =============================================================================

const TabButton: React.FC<{
  active: boolean;
  onClick: () => void;
  icon: React.ReactNode;
  label: string;
  badge?: number;
}> = ({ active, onClick, icon, label, badge }) => (
  <button
    onClick={onClick}
    className={`flex items-center gap-3 w-full px-4 py-3 rounded-lg text-left transition-all
      ${active 
        ? 'bg-gradient-to-r from-indigo-600/20 to-purple-600/20 text-white border border-indigo-500/30' 
        : 'text-[#8b919a] hover:bg-[#21262d] hover:text-white'}`}
  >
    <span className={active ? 'text-indigo-400' : ''}>{icon}</span>
    <span className="font-medium">{label}</span>
    {badge !== undefined && badge > 0 && (
      <span className="ml-auto bg-indigo-500/20 text-indigo-300 text-xs px-2 py-0.5 rounded-full">
        {badge}%
      </span>
    )}
  </button>
);

const SectionCard: React.FC<{
  title: string;
  description: string;
  icon: React.ReactNode;
  children: React.ReactNode;
  action?: React.ReactNode;
  gradient?: string;
}> = ({ title, description, icon, children, action, gradient = 'from-blue-500 to-indigo-500' }) => (
  <div className="bg-[#161b22] border border-[#30363d] rounded-xl overflow-hidden">
    <div className="px-6 py-4 border-b border-[#30363d] flex items-center justify-between">
      <div className="flex items-center gap-4">
        <div className={`w-10 h-10 rounded-lg bg-gradient-to-br ${gradient} flex items-center justify-center`}>
          {icon}
        </div>
        <div>
          <h3 className="text-white font-semibold">{title}</h3>
          <p className="text-[#8b919a] text-sm">{description}</p>
        </div>
      </div>
      {action}
    </div>
    <div className="p-6">{children}</div>
  </div>
);

const InputField: React.FC<{
  label: string;
  value: string;
  onChange: (v: string) => void;
  placeholder?: string;
  type?: string;
  icon?: React.ReactNode;
}> = ({ label, value, onChange, placeholder, type = 'text', icon }) => (
  <div>
    <label className="block text-sm text-[#8b919a] mb-2">{label}</label>
    <div className="relative">
      {icon && (
        <span className="absolute left-3 top-1/2 -translate-y-1/2 text-[#6e7681]">
          {icon}
        </span>
      )}
      <input
        type={type}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        className={`w-full bg-[#0d1117] border border-[#30363d] rounded-lg px-4 py-2.5 text-white 
          placeholder-[#6e7681] focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500
          ${icon ? 'pl-10' : ''}`}
      />
    </div>
  </div>
);

const TagInput: React.FC<{
  label: string;
  tags: string[];
  onChange: (tags: string[]) => void;
  placeholder?: string;
  suggestions?: string[];
}> = ({ label, tags, onChange, placeholder, suggestions = [] }) => {
  const [input, setInput] = useState('');
  const [showSuggestions, setShowSuggestions] = useState(false);

  const addTag = (tag: string) => {
    const trimmed = tag.trim();
    if (trimmed && !tags.includes(trimmed)) {
      onChange([...tags, trimmed]);
    }
    setInput('');
    setShowSuggestions(false);
  };

  const removeTag = (index: number) => {
    onChange(tags.filter((_, i) => i !== index));
  };

  const filteredSuggestions = suggestions.filter(
    s => s.toLowerCase().includes(input.toLowerCase()) && !tags.includes(s)
  );

  return (
    <div>
      <label className="block text-sm text-[#8b919a] mb-2">{label}</label>
      <div className="bg-[#0d1117] border border-[#30363d] rounded-lg p-2 focus-within:border-indigo-500">
        <div className="flex flex-wrap gap-2 mb-2">
          {tags.map((tag, i) => (
            <span
              key={i}
              className="bg-indigo-500/20 text-indigo-300 px-2.5 py-1 rounded-md text-sm flex items-center gap-1.5"
            >
              {tag}
              <button onClick={() => removeTag(i)} className="hover:text-white">
                <X size={12} />
              </button>
            </span>
          ))}
        </div>
        <div className="relative">
          <input
            type="text"
            value={input}
            onChange={(e) => {
              setInput(e.target.value);
              setShowSuggestions(true);
            }}
            onKeyDown={(e) => {
              if (e.key === 'Enter' || e.key === ',') {
                e.preventDefault();
                addTag(input);
              }
            }}
            onFocus={() => setShowSuggestions(true)}
            onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
            placeholder={placeholder}
            className="w-full bg-transparent text-white placeholder-[#6e7681] focus:outline-none text-sm"
          />
          {showSuggestions && filteredSuggestions.length > 0 && (
            <div className="absolute top-full left-0 right-0 mt-1 bg-[#1e2128] border border-[#30363d] rounded-lg shadow-xl z-10 max-h-40 overflow-y-auto">
              {filteredSuggestions.map((s, i) => (
                <button
                  key={i}
                  onMouseDown={() => addTag(s)}
                  className="w-full px-3 py-2 text-left text-sm text-[#b8bcc4] hover:bg-[#21262d] hover:text-white"
                >
                  {s}
                </button>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

const EmptyState: React.FC<{
  icon: React.ReactNode;
  title: string;
  description: string;
  action?: { label: string; onClick: () => void };
}> = ({ icon, title, description, action }) => (
  <div className="text-center py-8">
    <div className="w-12 h-12 rounded-full bg-[#21262d] flex items-center justify-center mx-auto mb-3">
      {icon}
    </div>
    <p className="text-white font-medium mb-1">{title}</p>
    <p className="text-[#8b919a] text-sm mb-4">{description}</p>
    {action && (
      <button
        onClick={action.onClick}
        className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 rounded-lg text-sm font-medium inline-flex items-center gap-2"
      >
        <Plus size={16} /> {action.label}
      </button>
    )}
  </div>
);

// =============================================================================
// MAIN COMPONENT
// =============================================================================

export default function Settings() {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<'playbook' | 'import' | 'api' | 'team'>('playbook');
  const [playbookSection, setPlaybookSection] = useState<'overview' | 'products' | 'value' | 'icp' | 'pain' | 'proof' | 'competitors'>('overview');
  const [playbook, setPlaybook] = useState<PlaybookData>(defaultPlaybook);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [importOpen, setImportOpen] = useState(false);
  const [syncingHubspot, setSyncingHubspot] = useState(false);
  const [hubspotResult, setHubspotResult] = useState<{imported: number, skipped: number} | null>(null);
  
  

  // API Keys State
  const [apiKeys, setApiKeys] = useState<APIKey[]>([
    { id: '1', name: 'Perplexity', key: '', status: 'unconfigured' },
    { id: '2', name: 'OpenAI', key: '', status: 'unconfigured' },
    { id: '3', name: 'Anthropic', key: '', status: 'unconfigured' },
  ]);
  const [showKeys, setShowKeys] = useState<Record<string, boolean>>({});

  // ---------------------------------------------------------------------------
  // LOAD DATA ON MOUNT
  // ---------------------------------------------------------------------------
  useEffect(() => {
    loadPlaybook();
    loadApiKeys();
  }, []);

  const loadPlaybook = async () => {
    try {
      // Try backend first
      const res = await fetch('https://apex-backend-i7b0.onrender.com/api/playbook');
      if (res.ok) {
        const data = await res.json();
        if (data && Object.keys(data).length > 0) {
          setPlaybook({ ...defaultPlaybook, ...data });
          setLoading(false);
          return;
        }
      }
    } catch (e) {
      console.log('Backend not available, trying localStorage');
    }

    // Fallback to localStorage
    const saved = localStorage.getItem('apex_playbook');
    if (saved) {
      try {
        setPlaybook({ ...defaultPlaybook, ...JSON.parse(saved) });
      } catch (e) {
        console.error('Failed to load playbook:', e);
      }
    }
    setLoading(false);
  };

  const loadApiKeys = () => {
    const savedKeys = localStorage.getItem('apex_api_keys');
    if (savedKeys) {
      try {
        setApiKeys(JSON.parse(savedKeys));
      } catch (e) {
        console.error('Failed to load API keys:', e);
      }
    }
  };

  // ---------------------------------------------------------------------------
  // SAVE PLAYBOOK
  // ---------------------------------------------------------------------------
  const savePlaybook = async () => {
    console.log('🔄 Saving playbook...', {
      companyName: playbook.companyName,
      productsCount: playbook.products.length,
      icpIndustries: playbook.icp.industries.length
    });
    
    try {
      // Save to localStorage first (immediate feedback)
      localStorage.setItem('salesPlaybook', JSON.stringify(playbook));
      console.log('✅ Saved to localStorage');
      
      // Attempt backend sync for multi-device persistence
      const response = await fetch(`${API_BASE_URL}/api/playbook`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(playbook)
      });
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error('❌ Backend save failed:', {
          status: response.status,
          statusText: response.statusText,
          body: errorText
        });
        throw new Error(`Backend returned ${response.status}: ${errorText}`);
      }
      
      const result = await response.json();
      console.log('✅ Backend sync successful:', result);
      
      alert('✅ Sales Playbook saved and synced across all devices!');
      
    } catch (error) {
      console.error('⚠️ Backend sync failed, saved locally only:', error);
      
      // User-facing message with context
      const errorMsg = error instanceof Error ? error.message : 'Unknown error';
      alert(
        `⚠️ Playbook saved locally but could not sync to server.\n\n` +
        `Error: ${errorMsg}\n\n` +
        `Your changes are saved on this device only. ` +
        `Check your internet connection or contact support if this persists.`
      );
    }
  };
  
  // Save API keys
  const saveApiKeys = () => {
    localStorage.setItem('apex_api_keys', JSON.stringify(apiKeys));
  };

  // Generate unique ID
  const genId = () => Math.random().toString(36).substr(2, 9);

  const syncHubspot = async () => {
    setSyncingHubspot(true);
    setHubspotResult(null);
    try {
      const res = await fetch('https://apex-backend-i7b0.onrender.com/api/v2/contacts/sync/hubspot/filtered', { method: 'POST' });      const data = await res.json();
      if (data.success) {
        setHubspotResult({ imported: data.imported, skipped: data.skipped });
      } else {
        alert('Sync failed: ' + (data.error || 'Unknown error'));
      }
    } catch (e) {
      alert('Sync failed');
    } finally {
      setSyncingHubspot(false);
    }
  };
  
  // =============================================================================
  // CRUD OPERATIONS
  // =============================================================================

  // Products
  const addProduct = () => {
    setPlaybook(prev => ({
      ...prev,
      products: [...prev.products, {
        id: genId(),
        name: '',
        description: '',
        priceRange: '',
        targetAudience: '',
        keyFeatures: []
      }]
    }));
  };

  const updateProduct = (id: string, updates: Partial<Product>) => {
    setPlaybook(prev => ({
      ...prev,
      products: prev.products.map(p => p.id === id ? { ...p, ...updates } : p)
    }));
  };

  const removeProduct = (id: string) => {
    setPlaybook(prev => ({
      ...prev,
      products: prev.products.filter(p => p.id !== id)
    }));
  };

  // Value Props
  const addValueProp = () => {
    setPlaybook(prev => ({
      ...prev,
      valueProps: [...prev.valueProps, {
        id: genId(),
        headline: '',
        description: '',
        proofPoint: ''
      }]
    }));
  };

  const updateValueProp = (id: string, updates: Partial<ValueProp>) => {
    setPlaybook(prev => ({
      ...prev,
      valueProps: prev.valueProps.map(v => v.id === id ? { ...v, ...updates } : v)
    }));
  };

  const removeValueProp = (id: string) => {
    setPlaybook(prev => ({
      ...prev,
      valueProps: prev.valueProps.filter(v => v.id !== id)
    }));
  };

  // Pain Points
  const addPainPoint = () => {
    setPlaybook(prev => ({
      ...prev,
      painPoints: [...prev.painPoints, {
        id: genId(),
        problem: '',
        solution: '',
        impact: ''
      }]
    }));
  };

  const updatePainPoint = (id: string, updates: Partial<PainPoint>) => {
    setPlaybook(prev => ({
      ...prev,
      painPoints: prev.painPoints.map(p => p.id === id ? { ...p, ...updates } : p)
    }));
  };

  const removePainPoint = (id: string) => {
    setPlaybook(prev => ({
      ...prev,
      painPoints: prev.painPoints.filter(p => p.id !== id)
    }));
  };

  // Proof Points
  const addProofPoint = (type: ProofPoint['type']) => {
    setPlaybook(prev => ({
      ...prev,
      proofPoints: [...prev.proofPoints, {
        id: genId(),
        type,
        title: '',
        description: '',
        metric: '',
        source: ''
      }]
    }));
  };

  const updateProofPoint = (id: string, updates: Partial<ProofPoint>) => {
    setPlaybook(prev => ({
      ...prev,
      proofPoints: prev.proofPoints.map(p => p.id === id ? { ...p, ...updates } : p)
    }));
  };

  const removeProofPoint = (id: string) => {
    setPlaybook(prev => ({
      ...prev,
      proofPoints: prev.proofPoints.filter(p => p.id !== id)
    }));
  };

  // Competitors
  const addCompetitor = () => {
    setPlaybook(prev => ({
      ...prev,
      competitors: [...prev.competitors, {
        id: genId(),
        name: '',
        weaknesses: [],
        ourAdvantage: ''
      }]
    }));
  };

  const updateCompetitor = (id: string, updates: Partial<Competitor>) => {
    setPlaybook(prev => ({
      ...prev,
      competitors: prev.competitors.map(c => c.id === id ? { ...c, ...updates } : c)
    }));
  };

  const removeCompetitor = (id: string) => {
    setPlaybook(prev => ({
      ...prev,
      competitors: prev.competitors.filter(c => c.id !== id)
    }));
  };

  // =============================================================================
  // COMPLETENESS SCORE
  // =============================================================================

  const calculateCompleteness = (): number => {
    let score = 0;

    // Company basics (20%)
    if (playbook.companyName) score += 7;
    if (playbook.tagline) score += 7;
    if (playbook.website) score += 6;

    // Products (20%)
    if (playbook.products.length > 0) score += 10;
    if (playbook.products.length >= 2) score += 5;
    if (playbook.products.some(p => p.keyFeatures.length > 0)) score += 5;

    // Value Props (15%)
    if (playbook.valueProps.length > 0) score += 8;
    if (playbook.valueProps.length >= 3) score += 7;

    // ICP (20%)
    if (playbook.icp.industries.length > 0) score += 5;
    if (playbook.icp.titles.length > 0) score += 5;
    if (playbook.icp.painPoints.length > 0) score += 5;
    if (playbook.icp.budgetRange) score += 5;

    // Pain Points (10%)
    if (playbook.painPoints.length > 0) score += 5;
    if (playbook.painPoints.length >= 3) score += 5;

    // Proof Points (10%)
    if (playbook.proofPoints.length > 0) score += 5;
    if (playbook.proofPoints.length >= 3) score += 5;

    // Competitors (5%)
    if (playbook.competitors.length > 0) score += 5;

    return Math.min(score, 100);
  };

  const completeness = calculateCompleteness();

  // =============================================================================
  // LOADING STATE
  // =============================================================================

  if (loading) {
    return (
      <div className="min-h-screen bg-[#0d1117] flex items-center justify-center">
        <div className="text-center">
          <Loader2 size={32} className="animate-spin text-indigo-500 mx-auto mb-4" />
          <p className="text-[#8b919a]">Loading playbook...</p>
        </div>
      </div>
    );
  }

  // =============================================================================
  // RENDER
  // =============================================================================

  return (
    <div className="min-h-screen bg-[#0d1117] text-white">
      {/* Header */}
      <div className="bg-[#161b22] border-b border-[#30363d] px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={() => navigate('/contacts')}
              className="p-2 hover:bg-[#21262d] rounded-lg transition-colors"
            >
              <ArrowLeft size={20} />
            </button>
            <div>
              <h1 className="text-xl font-bold flex items-center gap-2">
                <SettingsIcon size={24} className="text-indigo-400" />
                Settings
              </h1>
              <p className="text-[#8b919a] text-sm">Configure your Sales Playbook and integrations</p>
            </div>
          </div>

          <button
            onClick={savePlaybook}
            disabled={saving}
            className={`px-5 py-2.5 rounded-lg text-sm font-medium flex items-center gap-2 transition-all
              ${saved 
                ? 'bg-emerald-600 text-white' 
                : 'bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white'}`}
          >
            {saving ? (
              <RefreshCw size={16} className="animate-spin" />
            ) : saved ? (
              <CheckCircle2 size={16} />
            ) : (
              <Save size={16} />
            )}
            {saving ? 'Saving...' : saved ? 'Saved!' : 'Save Changes'}
          </button>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-6">
        <div className="flex gap-6">
          {/* Sidebar */}
          <div className="w-64 flex-shrink-0">
            <div className="bg-[#161b22] border border-[#30363d] rounded-xl p-4 sticky top-6">
              <nav className="space-y-2">
                <TabButton
                  active={activeTab === 'playbook'}
                  onClick={() => setActiveTab('playbook')}
                  icon={<BookOpen size={18} />}
                  label="Sales Playbook"
                  badge={completeness}
                />
                <TabButton
                  active={activeTab === 'import'}
                  onClick={() => setActiveTab('import')}
                  icon={<Upload size={18} />}
                  label="Import Data"
                />
                <TabButton
                  active={activeTab === 'api'}
                  onClick={() => setActiveTab('api')}
                  icon={<Key size={18} />}
                  label="API Keys"
                />
                <TabButton
                  active={activeTab === 'team'}
                  onClick={() => setActiveTab('team')}
                  icon={<Users size={18} />}
                  label="Team"
                />
              </nav>

              {/* Playbook Completeness */}
              {activeTab === 'playbook' && (
                <div className="mt-6 pt-6 border-t border-[#30363d]">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm text-[#8b919a]">Completeness</span>
                    <span className={`text-sm font-medium ${
                      completeness >= 80 ? 'text-emerald-400' :
                      completeness >= 50 ? 'text-yellow-400' : 'text-red-400'
                    }`}>{completeness}%</span>
                  </div>
                  <div className="h-2 bg-[#21262d] rounded-full overflow-hidden">
                    <div
                      className={`h-full transition-all duration-500 ${
                        completeness >= 80 ? 'bg-gradient-to-r from-emerald-500 to-green-500' :
                        completeness >= 50 ? 'bg-gradient-to-r from-yellow-500 to-orange-500' :
                        'bg-gradient-to-r from-red-500 to-pink-500'
                      }`}
                      style={{ width: `${completeness}%` }}
                    />
                  </div>
                                <p className="text-xs text-[#6e7681] mt-2">
                                  {completeness >= 100
                                    ? '✅ Excellent! Your playbook is complete'
                                    : completeness >= 80
                                    ? '🎯 Almost there! See what\'s missing below'
                                    : completeness >= 50
                                    ? 'Good progress! Keep adding details'
                                    : 'Add more details to improve scoring accuracy'}
                                </p>
                                {completeness < 100 && (
                                  <div className="mt-3 p-3 bg-[#161b22] rounded-lg border border-[#30363d]">
                                    <p className="text-xs font-medium text-[#8b919a] mb-2">To reach 100%:</p>
                                    <ul className="text-xs text-[#6e7681] space-y-1">
                                      {playbook.valueProps.length < 3 && (
                                        <li className="flex items-center gap-2">
                                          <span className="text-yellow-500">○</span>
                                          Add {3 - playbook.valueProps.length} more Value Prop{3 - playbook.valueProps.length > 1 ? 's' : ''} (+7 pts)
                                        </li>
                                      )}
                                      {playbook.painPoints.length < 3 && (
                                        <li className="flex items-center gap-2">
                                          <span className="text-yellow-500">○</span>
                                          Add {3 - playbook.painPoints.length} more Pain Point{3 - playbook.painPoints.length > 1 ? 's' : ''} (+5 pts)
                                        </li>
                                      )}
                                      {playbook.proofPoints.length < 3 && (
                                        <li className="flex items-center gap-2">
                                          <span className="text-yellow-500">○</span>
                                          Add {3 - playbook.proofPoints.length} more Proof Point{3 - playbook.proofPoints.length > 1 ? 's' : ''} (+5 pts)
                                        </li>
                                      )}
                                      {!playbook.companyName && <li className="flex items-center gap-2"><span className="text-yellow-500">○</span> Add Company Name (+7 pts)</li>}
                                      {!playbook.tagline && <li className="flex items-center gap-2"><span className="text-yellow-500">○</span> Add Tagline (+7 pts)</li>}
                                      {!playbook.website && <li className="flex items-center gap-2"><span className="text-yellow-500">○</span> Add Website (+6 pts)</li>}
                                      {playbook.products.length < 2 && <li className="flex items-center gap-2"><span className="text-yellow-500">○</span> Add {2 - playbook.products.length} more Product{2 - playbook.products.length > 1 ? 's' : ''} (+{playbook.products.length === 0 ? '15' : '5'} pts)</li>}
                                      {playbook.competitors.length === 0 && <li className="flex items-center gap-2"><span className="text-yellow-500">○</span> Add a Competitor (+5 pts)</li>}
                                    </ul>
                                  </div>
                                )}
                </div>
              )}
            </div>
          </div>

          {/* Main Content */}
          <div className="flex-1 min-w-0">
            {/* =============================================================== */}
            {/* SALES PLAYBOOK TAB */}
            {/* =============================================================== */}
            {activeTab === 'playbook' && (
              <div className="space-y-6">
                {/* Playbook Sub-navigation */}
                <div className="flex gap-2 overflow-x-auto pb-2">
                  {[
                    { id: 'overview', label: 'Overview', icon: <Building2 size={14} /> },
                    { id: 'products', label: 'Products', icon: <Package size={14} />, count: playbook.products.length },
                    { id: 'value', label: 'Value Props', icon: <Sparkles size={14} />, count: playbook.valueProps.length },
                    { id: 'icp', label: 'ICP', icon: <Target size={14} /> },
                    { id: 'pain', label: 'Pain Points', icon: <AlertTriangle size={14} />, count: playbook.painPoints.length },
                    { id: 'proof', label: 'Proof Points', icon: <Trophy size={14} />, count: playbook.proofPoints.length },
                    { id: 'competitors', label: 'Competitors', icon: <BarChart3 size={14} />, count: playbook.competitors.length },
                  ].map(item => (
                    <button
                      key={item.id}
                      onClick={() => setPlaybookSection(item.id as typeof playbookSection)}
                      className={`px-4 py-2 rounded-lg text-sm font-medium flex items-center gap-2 whitespace-nowrap transition-all
                        ${playbookSection === item.id
                          ? 'bg-indigo-600 text-white'
                          : 'bg-[#21262d] text-[#8b919a] hover:text-white'}`}
                    >
                      {item.icon}
                      {item.label}
                      {item.count !== undefined && item.count > 0 && (
                        <span className={`text-xs px-1.5 rounded ${
                          playbookSection === item.id ? 'bg-white/20' : 'bg-[#30363d]'
                        }`}>{item.count}</span>
                      )}
                    </button>
                  ))}
                </div>

                {/* Overview Section */}
                {playbookSection === 'overview' && (
                  <SectionCard
                    title="Company Overview"
                    description="Basic information about your company"
                    icon={<Building2 size={20} className="text-white" />}
                    gradient="from-blue-500 to-indigo-500"
                  >
                    <div className="grid md:grid-cols-2 gap-6">
                      <InputField
                        label="Company Name"
                        value={playbook.companyName}
                        onChange={(v) => setPlaybook(p => ({ ...p, companyName: v }))}
                        placeholder="Acme Corporation"
                        icon={<Building2 size={16} />}
                      />
                      <InputField
                        label="Website"
                        value={playbook.website}
                        onChange={(v) => setPlaybook(p => ({ ...p, website: v }))}
                        placeholder="https://acme.com"
                        icon={<Globe size={16} />}
                      />
                      <div className="md:col-span-2">
                        <InputField
                          label="Tagline / Elevator Pitch"
                          value={playbook.tagline}
                          onChange={(v) => setPlaybook(p => ({ ...p, tagline: v }))}
                          placeholder="We help companies do X to achieve Y"
                          icon={<MessageSquare size={16} />}
                        />
                      </div>
                    </div>
                  </SectionCard>
                )}

                {/* Products Section */}
                {playbookSection === 'products' && (
                  <SectionCard
                    title="Products & Services"
                    description="What you sell and who it's for"
                    icon={<Package size={20} className="text-white" />}
                    gradient="from-purple-500 to-pink-500"
                    action={
                      <button
                        onClick={addProduct}
                        className="px-3 py-1.5 bg-purple-600 hover:bg-purple-500 rounded-lg text-sm font-medium flex items-center gap-1"
                      >
                        <Plus size={14} /> Add Product
                      </button>
                    }
                  >
                    {playbook.products.length === 0 ? (
                      <EmptyState
                        icon={<Package size={24} className="text-[#6e7681]" />}
                        title="No products yet"
                        description="Add your products and services to power intelligent outreach"
                        action={{ label: 'Add Product', onClick: addProduct }}
                      />
                    ) : (
                      <div className="space-y-4">
                        {playbook.products.map((product, i) => (
                          <div key={product.id} className="bg-[#0d1117] border border-[#30363d] rounded-lg p-4">
                            <div className="flex items-start justify-between mb-4">
                              <span className="text-xs text-[#6e7681] bg-[#21262d] px-2 py-1 rounded">
                                Product {i + 1}
                              </span>
                              <button onClick={() => removeProduct(product.id)} className="text-[#6e7681] hover:text-red-400">
                                <Trash2 size={16} />
                              </button>
                            </div>
                            <div className="grid md:grid-cols-2 gap-4">
                              <InputField
                                label="Product Name"
                                value={product.name}
                                onChange={(v) => updateProduct(product.id, { name: v })}
                                placeholder="Enterprise Suite"
                              />
                              <InputField
                                label="Price Range"
                                value={product.priceRange}
                                onChange={(v) => updateProduct(product.id, { priceRange: v })}
                                placeholder="$10K - $50K/year"
                              />
                              <div className="md:col-span-2">
                                <label className="block text-sm text-[#8b919a] mb-2">Description</label>
                                <textarea
                                  value={product.description}
                                  onChange={(e) => updateProduct(product.id, { description: e.target.value })}
                                  placeholder="Brief description of what this product does..."
                                  className="w-full bg-[#0d1117] border border-[#30363d] rounded-lg px-4 py-2.5 text-white placeholder-[#6e7681] focus:outline-none focus:border-indigo-500 resize-none"
                                  rows={2}
                                />
                              </div>
                              <InputField
                                label="Target Audience"
                                value={product.targetAudience}
                                onChange={(v) => updateProduct(product.id, { targetAudience: v })}
                                placeholder="CTOs at mid-market SaaS companies"
                              />
                              <TagInput
                                label="Key Features"
                                tags={product.keyFeatures}
                                onChange={(tags) => updateProduct(product.id, { keyFeatures: tags })}
                                placeholder="Type and press Enter"
                              />
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </SectionCard>
                )}

                {/* Value Props Section */}
                {playbookSection === 'value' && (
                  <SectionCard
                    title="Value Propositions"
                    description="Why customers choose you"
                    icon={<Sparkles size={20} className="text-white" />}
                    gradient="from-amber-500 to-orange-500"
                    action={
                      <button onClick={addValueProp} className="px-3 py-1.5 bg-amber-600 hover:bg-amber-500 rounded-lg text-sm font-medium flex items-center gap-1">
                        <Plus size={14} /> Add Value Prop
                      </button>
                    }
                  >
                    {playbook.valueProps.length === 0 ? (
                      <EmptyState
                        icon={<Sparkles size={24} className="text-[#6e7681]" />}
                        title="No value propositions yet"
                        description="Define why customers choose you over alternatives"
                        action={{ label: 'Add Value Prop', onClick: addValueProp }}
                      />
                    ) : (
                      <div className="space-y-4">
                        {playbook.valueProps.map((vp, i) => (
                          <div key={vp.id} className="bg-[#0d1117] border border-[#30363d] rounded-lg p-4">
                            <div className="flex items-start justify-between mb-4">
                              <span className="text-xs text-[#6e7681] bg-[#21262d] px-2 py-1 rounded">Value Prop {i + 1}</span>
                              <button onClick={() => removeValueProp(vp.id)} className="text-[#6e7681] hover:text-red-400"><Trash2 size={16} /></button>
                            </div>
                            <div className="space-y-4">
                              <InputField label="Headline" value={vp.headline} onChange={(v) => updateValueProp(vp.id, { headline: v })} placeholder="10x faster time-to-value" />
                              <div>
                                <label className="block text-sm text-[#8b919a] mb-2">Description</label>
                                <textarea value={vp.description} onChange={(e) => updateValueProp(vp.id, { description: e.target.value })} placeholder="Explain the value and how you deliver it..." className="w-full bg-[#0d1117] border border-[#30363d] rounded-lg px-4 py-2.5 text-white placeholder-[#6e7681] focus:outline-none focus:border-indigo-500 resize-none" rows={2} />
                              </div>
                              <InputField label="Proof Point" value={vp.proofPoint} onChange={(v) => updateValueProp(vp.id, { proofPoint: v })} placeholder="Acme Corp reduced onboarding time by 80%" />
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </SectionCard>
                )}

                {/* ICP Section */}
                {playbookSection === 'icp' && (
                  <SectionCard
                    title="Ideal Customer Profile"
                    description="Define your perfect customer for better targeting"
                    icon={<Target size={20} className="text-white" />}
                    gradient="from-emerald-500 to-teal-500"
                  >
                    <div className="space-y-6">
                      <TagInput
                        label="Target Industries"
                        tags={playbook.icp.industries}
                        onChange={(tags) => setPlaybook(p => ({ ...p, icp: { ...p.icp, industries: tags } }))}
                        placeholder="Type industry and press Enter"
                        suggestions={['SaaS', 'FinTech', 'Healthcare', 'E-commerce', 'Manufacturing', 'Professional Services', 'Real Estate', 'Education', 'Financial Services', 'Insurance']}
                      />
                      <div className="grid md:grid-cols-2 gap-6">
                        <div>
                          <label className="block text-sm text-[#8b919a] mb-2">Company Size</label>
                          <select
                            value={playbook.icp.companySize.label}
                            onChange={(e) => {
                              const sizes: Record<string, { min: number; max: number; label: string }> = {
                                'Startup': { min: 1, max: 50, label: 'Startup' },
                                'SMB': { min: 50, max: 200, label: 'SMB' },
                                'Mid-Market': { min: 200, max: 1000, label: 'Mid-Market' },
                                'Enterprise': { min: 1000, max: 10000, label: 'Enterprise' },
                                'Large Enterprise': { min: 10000, max: 100000, label: 'Large Enterprise' }
                              };
                              setPlaybook(p => ({ ...p, icp: { ...p.icp, companySize: sizes[e.target.value] || sizes['Mid-Market'] } }));
                            }}
                            className="w-full bg-[#0d1117] border border-[#30363d] rounded-lg px-4 py-2.5 text-white focus:outline-none focus:border-indigo-500"
                          >
                            <option value="Startup">Startup (1-50)</option>
                            <option value="SMB">SMB (50-200)</option>
                            <option value="Mid-Market">Mid-Market (200-1,000)</option>
                            <option value="Enterprise">Enterprise (1,000-10,000)</option>
                            <option value="Large Enterprise">Large Enterprise (10,000+)</option>
                          </select>
                        </div>
                        <InputField label="Budget Range" value={playbook.icp.budgetRange} onChange={(v) => setPlaybook(p => ({ ...p, icp: { ...p.icp, budgetRange: v } }))} placeholder="$50K - $500K annually" icon={<DollarSign size={16} />} />
                      </div>
                      <TagInput label="Target Job Titles" tags={playbook.icp.titles} onChange={(tags) => setPlaybook(p => ({ ...p, icp: { ...p.icp, titles: tags } }))} placeholder="Type title and press Enter" suggestions={['CEO', 'CTO', 'CFO', 'VP Sales', 'VP Marketing', 'Director of Operations', 'Head of Engineering', 'Product Manager', 'Managing Director', 'Partner']} />
                      <TagInput label="Target Regions" tags={playbook.icp.regions} onChange={(tags) => setPlaybook(p => ({ ...p, icp: { ...p.icp, regions: tags } }))} placeholder="Type region and press Enter" suggestions={['United States', 'Canada', 'UK', 'EMEA', 'APAC', 'California', 'New York', 'Texas', 'Los Angeles', 'San Francisco']} />
                      <TagInput label="Tech Stack / Tools They Use" tags={playbook.icp.techStack} onChange={(tags) => setPlaybook(p => ({ ...p, icp: { ...p.icp, techStack: tags } }))} placeholder="Type technology and press Enter" suggestions={['Salesforce', 'HubSpot', 'Slack', 'AWS', 'Google Workspace', 'Microsoft 365', 'Zendesk', 'Jira']} />
                      <TagInput label="Pain Points They Have" tags={playbook.icp.painPoints} onChange={(tags) => setPlaybook(p => ({ ...p, icp: { ...p.icp, painPoints: tags } }))} placeholder="Type pain point and press Enter" suggestions={['Slow sales cycle', 'High churn', 'Manual processes', 'Data silos', 'Compliance issues', 'Scaling challenges', 'Capital access', 'Loan processing']} />
                    </div>
                  </SectionCard>
                )}

                {/* Pain Points Section */}
                {playbookSection === 'pain' && (
                  <SectionCard
                    title="Pain Points You Solve"
                    description="Problems → Solutions → Impact"
                    icon={<AlertTriangle size={20} className="text-white" />}
                    gradient="from-red-500 to-rose-500"
                    action={<button onClick={addPainPoint} className="px-3 py-1.5 bg-red-600 hover:bg-red-500 rounded-lg text-sm font-medium flex items-center gap-1"><Plus size={14} /> Add Pain Point</button>}
                  >
                    {playbook.painPoints.length === 0 ? (
                      <EmptyState icon={<AlertTriangle size={24} className="text-[#6e7681]" />} title="No pain points defined" description="Document the problems you solve for customers" action={{ label: 'Add Pain Point', onClick: addPainPoint }} />
                    ) : (
                      <div className="space-y-4">
                        {playbook.painPoints.map((pp, i) => (
                          <div key={pp.id} className="bg-[#0d1117] border border-[#30363d] rounded-lg p-4">
                            <div className="flex items-start justify-between mb-4">
                              <span className="text-xs text-[#6e7681] bg-[#21262d] px-2 py-1 rounded">Pain Point {i + 1}</span>
                              <button onClick={() => removePainPoint(pp.id)} className="text-[#6e7681] hover:text-red-400"><Trash2 size={16} /></button>
                            </div>
                            <div className="grid md:grid-cols-3 gap-4">
                              <div>
                                <label className="block text-sm text-red-400 mb-2 flex items-center gap-1"><AlertTriangle size={12} /> Problem</label>
                                <textarea value={pp.problem} onChange={(e) => updatePainPoint(pp.id, { problem: e.target.value })} placeholder="Sales reps spend 50% of time on admin..." className="w-full bg-[#0d1117] border border-[#30363d] rounded-lg px-4 py-2.5 text-white placeholder-[#6e7681] focus:outline-none focus:border-red-500 resize-none" rows={3} />
                              </div>
                              <div>
                                <label className="block text-sm text-emerald-400 mb-2 flex items-center gap-1"><Lightbulb size={12} /> Solution</label>
                                <textarea value={pp.solution} onChange={(e) => updatePainPoint(pp.id, { solution: e.target.value })} placeholder="We automate data entry and follow-ups..." className="w-full bg-[#0d1117] border border-[#30363d] rounded-lg px-4 py-2.5 text-white placeholder-[#6e7681] focus:outline-none focus:border-emerald-500 resize-none" rows={3} />
                              </div>
                              <div>
                                <label className="block text-sm text-blue-400 mb-2 flex items-center gap-1"><TrendingUp size={12} /> Impact</label>
                                <textarea value={pp.impact} onChange={(e) => updatePainPoint(pp.id, { impact: e.target.value })} placeholder="Reps close 40% more deals per quarter..." className="w-full bg-[#0d1117] border border-[#30363d] rounded-lg px-4 py-2.5 text-white placeholder-[#6e7681] focus:outline-none focus:border-blue-500 resize-none" rows={3} />
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </SectionCard>
                )}

                {/* Proof Points Section */}
                {playbookSection === 'proof' && (
                  <SectionCard
                    title="Proof Points"
                    description="Case studies, metrics, testimonials, and logos"
                    icon={<Trophy size={20} className="text-white" />}
                    gradient="from-yellow-500 to-amber-500"
                    action={
                      <div className="flex gap-2">
                        {[{ type: 'case_study', label: 'Case Study', icon: <FileText size={14} /> }, { type: 'metric', label: 'Metric', icon: <BarChart3 size={14} /> }, { type: 'testimonial', label: 'Quote', icon: <MessageSquare size={14} /> }].map(item => (
                          <button key={item.type} onClick={() => addProofPoint(item.type as ProofPoint['type'])} className="px-2.5 py-1.5 bg-[#21262d] hover:bg-[#30363d] rounded-lg text-xs font-medium flex items-center gap-1">{item.icon} {item.label}</button>
                        ))}
                      </div>
                    }
                  >
                    {playbook.proofPoints.length === 0 ? (
                      <EmptyState icon={<Trophy size={24} className="text-[#6e7681]" />} title="No proof points yet" description="Add case studies, metrics, and testimonials to build credibility" action={{ label: 'Add Case Study', onClick: () => addProofPoint('case_study') }} />
                    ) : (
                      <div className="grid md:grid-cols-2 gap-4">
                        {playbook.proofPoints.map((pp) => (
                          <div key={pp.id} className="bg-[#0d1117] border border-[#30363d] rounded-lg p-4">
                            <div className="flex items-start justify-between mb-3">
                              <span className={`text-xs px-2 py-1 rounded flex items-center gap-1 ${pp.type === 'case_study' ? 'bg-blue-500/20 text-blue-300' : pp.type === 'metric' ? 'bg-emerald-500/20 text-emerald-300' : 'bg-purple-500/20 text-purple-300'}`}>
                                {pp.type === 'case_study' && <FileText size={12} />}
                                {pp.type === 'metric' && <BarChart3 size={12} />}
                                {pp.type === 'testimonial' && <MessageSquare size={12} />}
                                {pp.type.replace('_', ' ')}
                              </span>
                              <button onClick={() => removeProofPoint(pp.id)} className="text-[#6e7681] hover:text-red-400"><Trash2 size={14} /></button>
                            </div>
                            <div className="space-y-3">
                              <InputField label="Title" value={pp.title} onChange={(v) => updateProofPoint(pp.id, { title: v })} placeholder={pp.type === 'metric' ? '40% increase in conversion' : 'Customer Success Story'} />
                              <div>
                                <label className="block text-sm text-[#8b919a] mb-2">Description</label>
                                <textarea value={pp.description} onChange={(e) => updateProofPoint(pp.id, { description: e.target.value })} placeholder="Details about the result..." className="w-full bg-[#0d1117] border border-[#30363d] rounded-lg px-4 py-2.5 text-white placeholder-[#6e7681] focus:outline-none focus:border-indigo-500 resize-none" rows={2} />
                              </div>
                              {pp.type === 'testimonial' && <InputField label="Source / Attribution" value={pp.source || ''} onChange={(v) => updateProofPoint(pp.id, { source: v })} placeholder="John Smith, CEO at Acme Corp" />}
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </SectionCard>
                )}

                {/* Competitors Section */}
                {playbookSection === 'competitors' && (
                  <SectionCard
                    title="Competitive Intelligence"
                    description="Know your competition and your advantages"
                    icon={<BarChart3 size={20} className="text-white" />}
                    gradient="from-slate-500 to-zinc-500"
                    action={<button onClick={addCompetitor} className="px-3 py-1.5 bg-slate-600 hover:bg-slate-500 rounded-lg text-sm font-medium flex items-center gap-1"><Plus size={14} /> Add Competitor</button>}
                  >
                    {playbook.competitors.length === 0 ? (
                      <EmptyState icon={<BarChart3 size={24} className="text-[#6e7681]" />} title="No competitors added" description="Track competitors to differentiate in sales conversations" action={{ label: 'Add Competitor', onClick: addCompetitor }} />
                    ) : (
                      <div className="space-y-4">
                        {playbook.competitors.map((comp) => (
                          <div key={comp.id} className="bg-[#0d1117] border border-[#30363d] rounded-lg p-4">
                            <div className="flex items-start justify-between mb-4">
                              <InputField label="Competitor Name" value={comp.name} onChange={(v) => updateCompetitor(comp.id, { name: v })} placeholder="Competitor Inc." />
                              <button onClick={() => removeCompetitor(comp.id)} className="text-[#6e7681] hover:text-red-400 mt-6"><Trash2 size={16} /></button>
                            </div>
                            <div className="grid md:grid-cols-2 gap-4">
                              <TagInput label="Their Weaknesses" tags={comp.weaknesses} onChange={(tags) => updateCompetitor(comp.id, { weaknesses: tags })} placeholder="Type weakness and press Enter" />
                              <div>
                                <label className="block text-sm text-[#8b919a] mb-2">Our Advantage</label>
                                <textarea value={comp.ourAdvantage} onChange={(e) => updateCompetitor(comp.id, { ourAdvantage: e.target.value })} placeholder="Why we win against them..." className="w-full bg-[#0d1117] border border-[#30363d] rounded-lg px-4 py-2.5 text-white placeholder-[#6e7681] focus:outline-none focus:border-indigo-500 resize-none" rows={3} />
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </SectionCard>
                )}
              </div>
            )}

            {/* =============================================================== */}
            {/* IMPORT TAB */}
            {/* =============================================================== */}
            {activeTab === 'import' && (
              <div className="space-y-6">
                <SectionCard title="Import Contacts" description="Bring your contacts into Apex" icon={<Upload size={20} className="text-white" />} gradient="from-cyan-500 to-blue-500">
                  <div className="grid md:grid-cols-2 gap-4">
                    <div className="bg-[#0d1117] border-2 border-dashed border-[#30363d] rounded-xl p-6 text-center hover:border-indigo-500/50 transition-colors cursor-pointer">
                      <div className="w-12 h-12 rounded-full bg-indigo-500/20 flex items-center justify-center mx-auto mb-3"><FileText size={24} className="text-indigo-400" /></div>
                      <p className="text-white font-medium mb-1">CSV / Excel Upload</p>
                      <p className="text-[#8b919a] text-sm mb-4">Drag & drop or click to browse</p>
                      <button className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 rounded-lg text-sm font-medium">Choose File</button>
                  </div>
                    <div className="bg-[#0d1117] border-2 border-dashed border-[#30363d] rounded-xl p-6 text-center hover:border-emerald-500/50 transition-colors cursor-pointer">
                      <div className="w-12 h-12 rounded-full bg-emerald-500/20 flex items-center justify-center mx-auto mb-3"><Copy size={24} className="text-emerald-400" /></div>
                      <p className="text-white font-medium mb-1">Copy & Paste</p>
                      <p className="text-[#8b919a] text-sm mb-4">Paste from spreadsheet or CRM</p>
                      <button className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 rounded-lg text-sm font-medium">Open Paste Mode</button>
                    </div>
                  </div>
                </SectionCard>
                <SectionCard title="CRM Integrations" description="Connect your CRM for automatic sync" icon={<Link2 size={20} className="text-white" />} gradient="from-orange-500 to-red-500">
                  <div className="grid md:grid-cols-3 gap-4">
                    {/* Salesforce */}
                    <div className="bg-[#0d1117] border border-[#30363d] rounded-xl p-4 opacity-50">
                      <div className="flex items-center gap-3 mb-3"><span className="text-2xl">☁️</span><span className="text-white font-medium">Salesforce</span></div>
                      <button disabled className="w-full px-4 py-2 rounded-lg text-sm font-medium bg-[#21262d] text-[#6e7681] cursor-not-allowed">Coming Soon</button>
                    </div>
              
                    {/* HubSpot */}
                    <div className="bg-[#0d1117] border border-[#30363d] rounded-xl p-4 hover:border-orange-500/50 transition-colors">
                      <div className="flex items-center gap-3 mb-3"><span className="text-2xl">🧡</span><span className="text-white font-medium">HubSpot</span></div>
                      <button 
                        onClick={syncHubspot} 
                        disabled={syncingHubspot}
                        className="w-full px-4 py-2 rounded-lg text-sm font-medium bg-orange-600 hover:bg-orange-500 text-white disabled:opacity-50"
                      >
                        {syncingHubspot ? 'Syncing...' : 'Sync Contacts'}
                      </button>
                      {hubspotResult && (
                        <p className="text-xs text-emerald-400 mt-2">✓ Imported {hubspotResult.imported}, skipped {hubspotResult.skipped}</p>
                      )}
                    </div>
              
                    {/* Pipedrive */}
                    <div className="bg-[#0d1117] border border-[#30363d] rounded-xl p-4 opacity-50">
                      <div className="flex items-center gap-3 mb-3"><span className="text-2xl">🎯</span><span className="text-white font-medium">Pipedrive</span></div>
                      <button disabled className="w-full px-4 py-2 rounded-lg text-sm font-medium bg-[#21262d] text-[#6e7681] cursor-not-allowed">Coming Soon</button>
                    </div>
                  </div>
                </SectionCard>
              </div>
            )}

            {/* =============================================================== */}
            {/* API KEYS TAB */}
            {/* =============================================================== */}
            {activeTab === 'api' && (
              <div className="space-y-6">
                <SectionCard title="API Configuration" description="Manage your API keys for AI enrichment" icon={<Key size={20} className="text-white" />} gradient="from-violet-500 to-purple-500">
                  <div className="space-y-4">
                    {apiKeys.map(api => (
                      <div key={api.id} className="bg-[#0d1117] border border-[#30363d] rounded-lg p-4">
                        <div className="flex items-center justify-between mb-3">
                          <div className="flex items-center gap-3">
                            <span className="text-white font-medium">{api.name}</span>
                            <span className={`text-xs px-2 py-0.5 rounded ${api.status === 'active' ? 'bg-emerald-500/20 text-emerald-300' : api.status === 'invalid' ? 'bg-red-500/20 text-red-300' : 'bg-gray-500/20 text-gray-300'}`}>{api.status}</span>
                          </div>
                        </div>
                        <div className="flex gap-2">
                          <div className="relative flex-1">
                            <input
                              type={showKeys[api.id] ? 'text' : 'password'}
                              value={api.key}
                              onChange={(e) => setApiKeys(keys => keys.map(k => k.id === api.id ? { ...k, key: e.target.value, status: e.target.value ? 'active' : 'unconfigured' } : k))}
                              onBlur={saveApiKeys}
                              placeholder={`Enter your ${api.name} API key`}
                              className="w-full bg-[#161b22] border border-[#30363d] rounded-lg px-4 py-2.5 text-white placeholder-[#6e7681] focus:outline-none focus:border-indigo-500 pr-10 font-mono text-sm"
                            />
                            <button onClick={() => setShowKeys(s => ({ ...s, [api.id]: !s[api.id] }))} className="absolute right-3 top-1/2 -translate-y-1/2 text-[#6e7681] hover:text-white">
                              {showKeys[api.id] ? <EyeOff size={16} /> : <Eye size={16} />}
                            </button>
                          </div>
                          <button className="px-4 py-2 bg-[#21262d] hover:bg-[#30363d] rounded-lg text-sm">Test</button>
                        </div>
                      </div>
                    ))}
                  </div>
                  <div className="mt-6 p-4 bg-blue-500/10 border border-blue-500/20 rounded-lg">
                    <div className="flex items-start gap-3">
                      <Shield size={20} className="text-blue-400 mt-0.5" />
                      <div>
                        <p className="text-white font-medium text-sm">Security Note</p>
                        <p className="text-[#8b919a] text-sm">API keys are stored locally and used only for enrichment calls.</p>
                      </div>
                    </div>
                  </div>
                </SectionCard>
                <ImportWizard isOpen={importOpen} onClose={() => setImportOpen(false)} onComplete={() => setImportOpen(false)} />
              </div>
            )}

            {/* =============================================================== */}
            {/* TEAM TAB */}
            {/* =============================================================== */}
            {activeTab === 'team' && (
              <SectionCard title="Team Management" description="Manage team members and permissions" icon={<Users size={20} className="text-white" />} gradient="from-pink-500 to-rose-500">
                <div className="text-center py-12">
                  <div className="w-16 h-16 rounded-full bg-gradient-to-br from-pink-500/20 to-rose-500/20 flex items-center justify-center mx-auto mb-4"><Users size={32} className="text-pink-400" /></div>
                  <p className="text-white font-medium text-lg mb-2">Team Features Coming Soon</p>
                  <p className="text-[#8b919a] max-w-md mx-auto">Invite team members, share playbooks, and collaborate on prospects. Available in Apex Pro.</p>
                  <button className="mt-6 px-6 py-2.5 bg-gradient-to-r from-pink-600 to-rose-600 hover:from-pink-500 hover:to-rose-500 rounded-lg text-sm font-medium inline-flex items-center gap-2"><Sparkles size={16} /> Join Waitlist</button>
                </div>
              </SectionCard>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
