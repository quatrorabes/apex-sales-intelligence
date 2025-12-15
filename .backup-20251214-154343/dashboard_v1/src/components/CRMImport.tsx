import { useState, useEffect } from 'react';
import { 
    Upload, X, Loader2, Check, AlertCircle, ChevronRight,
    Database, Cloud, FileSpreadsheet, Link2, Key, RefreshCw,
    Building2, Users, Zap
} from 'lucide-react';

const API_URL = import.meta.env.VITE_API_URL || 'https://apex-backend-i7b0.onrender.com';

interface CRMStatus {
    configured: boolean;
    type: string;
}

interface ImportResult {
    source: string;
    fetched?: number;
    success: number;
    failed: number;
    duplicates?: number;
}

const CRM_INFO = {
    hubspot: {
        name: 'HubSpot',
        icon: '🟠',
        color: 'from-orange-500 to-red-500',
        description: 'Import contacts from HubSpot CRM',
        authType: 'API Key or OAuth',
        fields: [
            { key: 'api_key', label: 'API Key', type: 'password', placeholder: 'pat-na1-xxxxx' },
        ]
    },
    salesforce: {
        name: 'Salesforce',
        icon: '☁️',
        color: 'from-blue-500 to-cyan-500',
        description: 'Import contacts from Salesforce',
        authType: 'Username + Password + Token',
        fields: [
            { key: 'username', label: 'Username', type: 'text', placeholder: 'user@company.com' },
            { key: 'password', label: 'Password', type: 'password', placeholder: '••••••••' },
            { key: 'security_token', label: 'Security Token', type: 'password', placeholder: 'xxxxx' },
        ]
    },
    pipedrive: {
        name: 'Pipedrive',
        icon: '🟢',
        color: 'from-green-500 to-emerald-500',
        description: 'Import contacts from Pipedrive',
        authType: 'API Token',
        fields: [
            { key: 'api_token', label: 'API Token', type: 'password', placeholder: 'xxxxxxxx' },
        ]
    },
    csv: {
        name: 'CSV File',
        icon: '📄',
        color: 'from-purple-500 to-pink-500',
        description: 'Upload a CSV file with contacts',
        authType: 'File Upload',
        fields: []
    }
};

export default function CRMImport({ isOpen, onClose, onComplete }: {
    isOpen: boolean;
    onClose: () => void;
    onComplete: () => void;
}) {
    const [step, setStep] = useState<'select' | 'configure' | 'importing' | 'result'>('select');
    const [selectedCRM, setSelectedCRM] = useState<string | null>(null);
    const [crmStatus, setCrmStatus] = useState<Record<string, CRMStatus>>({});
    const [credentials, setCredentials] = useState<Record<string, string>>({});
    const [csvContent, setCsvContent] = useState('');
    const [csvFileName, setCsvFileName] = useState('');
    const [importing, setImporting] = useState(false);
    const [result, setResult] = useState<ImportResult | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [importLimit, setImportLimit] = useState(500);

    useEffect(() => {
        if (isOpen) {
            fetchStatus();
            setStep('select');
            setSelectedCRM(null);
            setCredentials({});
            setCsvContent('');
            setResult(null);
            setError(null);
        }
    }, [isOpen]);

    const fetchStatus = async () => {
        try {
            const res = await fetch(`${API_URL}/api/import/status`);
            const data = await res.json();
            setCrmStatus(data);
        } catch (e) {
            console.error('Failed to fetch CRM status');
        }
    };

    const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (!file) return;
        
        setCsvFileName(file.name);
        const reader = new FileReader();
        reader.onload = (event) => {
            setCsvContent(event.target?.result as string);
        };
        reader.readAsText(file);
    };

    const handleImport = async () => {
        if (!selectedCRM) return;
        
        setImporting(true);
        setError(null);
        setStep('importing');
        
        try {
            let endpoint = `/api/import/${selectedCRM}`;
            let body: any = { limit: importLimit };
            
            if (selectedCRM === 'csv') {
                body.csv_content = csvContent;
            } else {
                body = { ...body, ...credentials };
            }
            
            const res = await fetch(`${API_URL}${endpoint}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body)
            });
            
            const data = await res.json();
            
            if (!res.ok) {
                throw new Error(data.error || 'Import failed');
            }
            
            setResult(data);
            setStep('result');
            
        } catch (e: any) {
            setError(e.message || 'Import failed');
            setStep('configure');
        } finally {
            setImporting(false);
        }
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50" onClick={onClose}>
            <div 
                className="bg-[#1e2228] rounded-2xl border border-gray-700 w-full max-w-2xl mx-4 overflow-hidden"
                onClick={e => e.stopPropagation()}
            >
                {/* Header */}
                <div className="px-6 py-4 border-b border-gray-800 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <Database size={20} className="text-purple-400" />
                        <h2 className="text-lg font-semibold text-white">Import from CRM</h2>
                    </div>
                    <button onClick={onClose} className="text-gray-500 hover:text-white">
                        <X size={20} />
                    </button>
                </div>

                {/* Content */}
                <div className="p-6">
                    {error && (
                        <div className="mb-4 p-3 bg-red-500/20 border border-red-500/50 rounded-lg flex items-center gap-2 text-red-300">
                            <AlertCircle size={18} />
                            {error}
                        </div>
                    )}

                    {/* Step: Select CRM */}
                    {step === 'select' && (
                        <div className="grid grid-cols-2 gap-4">
                            {Object.entries(CRM_INFO).map(([key, crm]) => {
                                const status = crmStatus[key];
                                return (
                                    <button
                                        key={key}
                                        onClick={() => { setSelectedCRM(key); setStep('configure'); }}
                                        className="p-5 rounded-xl border-2 border-gray-700 hover:border-gray-600 transition text-left group relative overflow-hidden"
                                    >
                                        <div className={`absolute inset-0 bg-gradient-to-br ${crm.color} opacity-0 group-hover:opacity-10 transition`} />
                                        
                                        <div className="relative">
                                            <div className="flex items-center justify-between mb-3">
                                                <span className="text-3xl">{crm.icon}</span>
                                                {status?.configured && (
                                                    <span className="px-2 py-0.5 bg-green-500/20 text-green-400 text-xs rounded-full">
                                                        Connected
                                                    </span>
                                                )}
                                            </div>
                                            <h3 className="font-semibold text-white mb-1">{crm.name}</h3>
                                            <p className="text-gray-500 text-sm">{crm.description}</p>
                                        </div>
                                    </button>
                                );
                            })}
                        </div>
                    )}

                    {/* Step: Configure */}
                    {step === 'configure' && selectedCRM && (
                        <div className="space-y-6">
                            <div className="flex items-center gap-3 mb-6">
                                <button 
                                    onClick={() => setStep('select')}
                                    className="text-gray-500 hover:text-white"
                                >
                                    ← Back
                                </button>
                                <span className="text-2xl">{CRM_INFO[selectedCRM as keyof typeof CRM_INFO].icon}</span>
                                <h3 className="text-xl font-semibold text-white">
                                    {CRM_INFO[selectedCRM as keyof typeof CRM_INFO].name}
                                </h3>
                            </div>

                            {/* CSV Upload */}
                            {selectedCRM === 'csv' && (
                                <div className="space-y-4">
                                    <div className="border-2 border-dashed border-gray-700 rounded-xl p-8 text-center">
                                        <FileSpreadsheet size={40} className="text-gray-600 mx-auto mb-4" />
                                        <p className="text-gray-400 mb-4">Drop your CSV file here or click to browse</p>
                                        <input
                                            type="file"
                                            accept=".csv"
                                            onChange={handleFileUpload}
                                            className="hidden"
                                            id="csv-upload"
                                        />
                                        <label
                                            htmlFor="csv-upload"
                                            className="inline-flex items-center gap-2 px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg cursor-pointer"
                                        >
                                            <Upload size={18} />
                                            Select File
                                        </label>
                                    </div>
                                    
                                    {csvFileName && (
                                        <div className="flex items-center gap-3 p-3 bg-green-500/20 border border-green-500/50 rounded-lg text-green-300">
                                            <Check size={18} />
                                            {csvFileName} loaded
                                        </div>
                                    )}
                                </div>
                            )}

                            {/* API Credentials */}
                            {selectedCRM !== 'csv' && (
                                <div className="space-y-4">
                                    <p className="text-gray-400 text-sm flex items-center gap-2">
                                        <Key size={16} />
                                        {CRM_INFO[selectedCRM as keyof typeof CRM_INFO].authType}
                                    </p>
                                    
                                    {CRM_INFO[selectedCRM as keyof typeof CRM_INFO].fields.map(field => (
                                        <div key={field.key}>
                                            <label className="block text-sm text-gray-400 mb-1">{field.label}</label>
                                            <input
                                                type={field.type}
                                                placeholder={field.placeholder}
                                                value={credentials[field.key] || ''}
                                                onChange={e => setCredentials(prev => ({ ...prev, [field.key]: e.target.value }))}
                                                className="w-full bg-[#0f1114] border border-gray-700 rounded-lg px-4 py-2 text-white focus:border-purple-500 focus:ring-1 focus:ring-purple-500"
                                            />
                                        </div>
                                    ))}
                                    
                                    {crmStatus[selectedCRM]?.configured && (
                                        <div className="p-3 bg-blue-500/20 border border-blue-500/50 rounded-lg text-blue-300 text-sm">
                                            💡 Leave blank to use saved credentials from environment
                                        </div>
                                    )}
                                </div>
                            )}

                            {/* Import Limit */}
                            <div>
                                <label className="block text-sm text-gray-400 mb-1">Import Limit</label>
                                <select
                                    value={importLimit}
                                    onChange={e => setImportLimit(Number(e.target.value))}
                                    className="w-full bg-[#0f1114] border border-gray-700 rounded-lg px-4 py-2 text-white"
                                >
                                    <option value={100}>100 contacts</option>
                                    <option value={250}>250 contacts</option>
                                    <option value={500}>500 contacts</option>
                                    <option value={1000}>1,000 contacts</option>
                                    <option value={5000}>5,000 contacts</option>
                                </select>
                            </div>

                            <button
                                onClick={handleImport}
                                disabled={selectedCRM === 'csv' && !csvContent}
                                className="w-full py-3 bg-purple-600 hover:bg-purple-700 disabled:opacity-50 rounded-xl font-medium flex items-center justify-center gap-2"
                            >
                                <Zap size={20} />
                                Start Import
                            </button>
                        </div>
                    )}

                    {/* Step: Importing */}
                    {step === 'importing' && (
                        <div className="text-center py-12">
                            <Loader2 size={48} className="text-purple-400 animate-spin mx-auto mb-4" />
                            <h3 className="text-xl font-semibold text-white mb-2">Importing Contacts</h3>
                            <p className="text-gray-400">
                                Fetching from {CRM_INFO[selectedCRM as keyof typeof CRM_INFO]?.name}...
                            </p>
                        </div>
                    )}

                    {/* Step: Result */}
                    {step === 'result' && result && (
                        <div className="text-center py-8">
                            <div className="w-16 h-16 bg-green-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
                                <Check size={32} className="text-green-400" />
                            </div>
                            <h3 className="text-xl font-semibold text-white mb-2">Import Complete!</h3>
                            
                            <div className="grid grid-cols-3 gap-4 mt-6 mb-8">
                                <div className="bg-[#0f1114] rounded-lg p-4">
                                    <p className="text-3xl font-bold text-green-400">{result.success}</p>
                                    <p className="text-gray-500 text-sm">Imported</p>
                                </div>
                                <div className="bg-[#0f1114] rounded-lg p-4">
                                    <p className="text-3xl font-bold text-yellow-400">{result.duplicates || 0}</p>
                                    <p className="text-gray-500 text-sm">Duplicates</p>
                                </div>
                                <div className="bg-[#0f1114] rounded-lg p-4">
                                    <p className="text-3xl font-bold text-red-400">{result.failed}</p>
                                    <p className="text-gray-500 text-sm">Failed</p>
                                </div>
                            </div>
                            
                            <div className="flex gap-3 justify-center">
                                <button
                                    onClick={() => { onComplete(); onClose(); }}
                                    className="px-6 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg font-medium"
                                >
                                    View Contacts
                                </button>
                                <button
                                    onClick={() => { setStep('select'); setResult(null); }}
                                    className="px-6 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg"
                                >
                                    Import More
                                </button>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
