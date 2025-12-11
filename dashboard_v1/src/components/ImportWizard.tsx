import { useState, useCallback } from 'react';
import { 
    Upload, FileText, Check, X, AlertCircle, Loader2,
    ChevronRight, Download, Users, Linkedin, Table
} from 'lucide-react';

const API_URL = 'https://apex-backend-i7b0.onrender.com';

interface ImportStep {
    id: number;
    title: string;
    completed: boolean;
}

interface ParsedContact {
    name?: string;
    first_name?: string;
    last_name?: string;
    email?: string;
    phone?: string;
    company?: string;
    title?: string;
    linkedin_url?: string;
    [key: string]: any;
}

export default function ImportWizard({ isOpen, onClose, onComplete }: { 
    isOpen: boolean; 
    onClose: () => void;
    onComplete: () => void;
}) {
    const [step, setStep] = useState(1);
    const [importType, setImportType] = useState<'csv' | 'linkedin' | 'paste'>('csv');
    const [file, setFile] = useState<File | null>(null);
    const [pasteData, setPasteData] = useState('');
    const [parsedContacts, setParsedContacts] = useState<ParsedContact[]>([]);
    const [fieldMapping, setFieldMapping] = useState<Record<string, string>>({});
    const [importing, setImporting] = useState(false);
    const [importResult, setImportResult] = useState<{ success: number; failed: number } | null>(null);
    const [error, setError] = useState<string | null>(null);

    const steps: ImportStep[] = [
        { id: 1, title: 'Select Source', completed: step > 1 },
        { id: 2, title: 'Upload Data', completed: step > 2 },
        { id: 3, title: 'Map Fields', completed: step > 3 },
        { id: 4, title: 'Import', completed: step > 4 },
    ];

    const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const f = e.target.files?.[0];
        if (!f) return;
        
        setFile(f);
        setError(null);
        
        try {
            const text = await f.text();
            const lines = text.split('\n').filter(l => l.trim());
            const headers = lines[0].split(',').map(h => h.trim().replace(/"/g, ''));
            
            const contacts: ParsedContact[] = lines.slice(1).map(line => {
                const values = line.split(',').map(v => v.trim().replace(/"/g, ''));
                const contact: ParsedContact = {};
                headers.forEach((h, i) => {
                    contact[h] = values[i] || '';
                });
                return contact;
            });
            
            setParsedContacts(contacts);
            
            // Auto-detect field mapping
            const mapping: Record<string, string> = {};
            headers.forEach(h => {
                const lower = h.toLowerCase();
                if (lower.includes('first') && lower.includes('name')) mapping[h] = 'first_name';
                else if (lower.includes('last') && lower.includes('name')) mapping[h] = 'last_name';
                else if (lower === 'name' || lower === 'full name') mapping[h] = 'name';
                else if (lower.includes('email')) mapping[h] = 'email';
                else if (lower.includes('phone') || lower.includes('mobile')) mapping[h] = 'phone';
                else if (lower.includes('company') || lower.includes('organization')) mapping[h] = 'company';
                else if (lower.includes('title') || lower.includes('position')) mapping[h] = 'title';
                else if (lower.includes('linkedin')) mapping[h] = 'linkedin_url';
            });
            setFieldMapping(mapping);
            
            setStep(3);
        } catch (e) {
            setError('Failed to parse CSV file');
        }
    };

    const handlePaste = () => {
        const lines = pasteData.split('\n').filter(l => l.trim());
        const contacts: ParsedContact[] = lines.map(line => {
            const parts = line.split('\t');
            return {
                name: parts[0] || '',
                email: parts[1] || '',
                company: parts[2] || '',
                title: parts[3] || '',
            };
        });
        setParsedContacts(contacts);
        setStep(3);
    };

    const handleImport = async () => {
        setImporting(true);
        setError(null);
        
        try {
            // Map fields to standard format
            const mappedContacts = parsedContacts.map(c => {
                const mapped: ParsedContact = {};
                Object.entries(fieldMapping).forEach(([from, to]) => {
                    if (c[from]) mapped[to] = c[from];
                });
                // Include unmapped fields too
                Object.entries(c).forEach(([k, v]) => {
                    if (!fieldMapping[k] && v) {
                        const lower = k.toLowerCase();
                        if (!mapped.name && (lower === 'name' || lower === 'full name')) mapped.name = v;
                    }
                });
                return mapped;
            });
            
            const res = await fetch(`${API_URL}/api/v2/contacts/import`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ contacts: mappedContacts })
            });
            
            const result = await res.json();
            setImportResult(result);
            setStep(5);
        } catch (e) {
            setError('Import failed. Please try again.');
        } finally {
            setImporting(false);
        }
    };

    const fieldOptions = [
        { value: '', label: '-- Skip --' },
        { value: 'name', label: 'Full Name' },
        { value: 'first_name', label: 'First Name' },
        { value: 'last_name', label: 'Last Name' },
        { value: 'email', label: 'Email' },
        { value: 'phone', label: 'Phone' },
        { value: 'company', label: 'Company' },
        { value: 'title', label: 'Title' },
        { value: 'linkedin_url', label: 'LinkedIn URL' },
    ];

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50" onClick={onClose}>
            <div 
                className="bg-[#1e2228] rounded-2xl border border-gray-700 w-full max-w-3xl mx-4 overflow-hidden"
                onClick={e => e.stopPropagation()}
            >
                {/* Header */}
                <div className="px-6 py-4 border-b border-gray-800 flex items-center justify-between">
                    <h2 className="text-lg font-semibold text-white flex items-center gap-2">
                        <Upload size={20} className="text-purple-400" />
                        Import Contacts
                    </h2>
                    <button onClick={onClose} className="text-gray-500 hover:text-white">
                        <X size={20} />
                    </button>
                </div>

                {/* Progress Steps */}
                <div className="px-6 py-4 border-b border-gray-800">
                    <div className="flex items-center justify-between">
                        {steps.map((s, i) => (
                            <div key={s.id} className="flex items-center">
                                <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                                    s.completed ? 'bg-green-500 text-white' :
                                    step === s.id ? 'bg-purple-600 text-white' :
                                    'bg-gray-800 text-gray-500'
                                }`}>
                                    {s.completed ? <Check size={16} /> : s.id}
                                </div>
                                <span className={`ml-2 text-sm ${step === s.id ? 'text-white' : 'text-gray-500'}`}>
                                    {s.title}
                                </span>
                                {i < steps.length - 1 && (
                                    <ChevronRight size={16} className="mx-4 text-gray-600" />
                                )}
                            </div>
                        ))}
                    </div>
                </div>

                {/* Content */}
                <div className="p-6 min-h-[300px]">
                    {error && (
                        <div className="mb-4 p-3 bg-red-500/20 border border-red-500/50 rounded-lg flex items-center gap-2 text-red-300">
                            <AlertCircle size={18} />
                            {error}
                        </div>
                    )}

                    {/* Step 1: Select Source */}
                    {step === 1 && (
                        <div className="grid grid-cols-3 gap-4">
                            {[
                                { id: 'csv', icon: <Table size={32} />, title: 'CSV File', desc: 'Upload a CSV file' },
                                { id: 'linkedin', icon: <Linkedin size={32} />, title: 'LinkedIn Export', desc: 'From LinkedIn export' },
                                { id: 'paste', icon: <FileText size={32} />, title: 'Paste Data', desc: 'Copy/paste from spreadsheet' },
                            ].map(source => (
                                <button
                                    key={source.id}
                                    onClick={() => { setImportType(source.id as any); setStep(2); }}
                                    className={`p-6 rounded-xl border-2 transition text-center hover:border-purple-500 ${
                                        importType === source.id ? 'border-purple-500 bg-purple-500/10' : 'border-gray-700'
                                    }`}
                                >
                                    <div className="text-purple-400 mb-3 flex justify-center">{source.icon}</div>
                                    <h3 className="font-medium text-white mb-1">{source.title}</h3>
                                    <p className="text-gray-500 text-sm">{source.desc}</p>
                                </button>
                            ))}
                        </div>
                    )}

                    {/* Step 2: Upload */}
                    {step === 2 && (
                        <div>
                            {(importType === 'csv' || importType === 'linkedin') && (
                                <div className="border-2 border-dashed border-gray-700 rounded-xl p-12 text-center">
                                    <Upload size={48} className="text-gray-600 mx-auto mb-4" />
                                    <p className="text-gray-400 mb-4">Drag & drop your file here, or click to browse</p>
                                    <input
                                        type="file"
                                        accept=".csv"
                                        onChange={handleFileUpload}
                                        className="hidden"
                                        id="file-upload"
                                    />
                                    <label
                                        htmlFor="file-upload"
                                        className="inline-flex items-center gap-2 px-6 py-3 bg-purple-600 hover:bg-purple-700 rounded-lg cursor-pointer"
                                    >
                                        <FileText size={18} />
                                        Select CSV File
                                    </label>
                                </div>
                            )}
                            
                            {importType === 'paste' && (
                                <div>
                                    <p className="text-gray-400 mb-3">Paste your data below (tab-separated: Name, Email, Company, Title)</p>
                                    <textarea
                                        value={pasteData}
                                        onChange={e => setPasteData(e.target.value)}
                                        placeholder="John Doe	john@company.com	Acme Corp	CEO"
                                        className="w-full h-48 bg-[#0f1114] border border-gray-700 rounded-lg p-4 text-white font-mono text-sm"
                                    />
                                    <button
                                        onClick={handlePaste}
                                        disabled={!pasteData.trim()}
                                        className="mt-4 px-6 py-2 bg-purple-600 hover:bg-purple-700 disabled:opacity-50 rounded-lg"
                                    >
                                        Continue
                                    </button>
                                </div>
                            )}
                        </div>
                    )}

                    {/* Step 3: Map Fields */}
                    {step === 3 && (
                        <div>
                            <p className="text-gray-400 mb-4">Map your columns to contact fields ({parsedContacts.length} contacts found)</p>
                            <div className="space-y-3 max-h-[300px] overflow-y-auto">
                                {Object.keys(parsedContacts[0] || {}).map(field => (
                                    <div key={field} className="flex items-center gap-4">
                                        <span className="w-40 text-gray-400 text-sm truncate">{field}</span>
                                        <ChevronRight size={16} className="text-gray-600" />
                                        <select
                                            value={fieldMapping[field] || ''}
                                            onChange={e => setFieldMapping(prev => ({ ...prev, [field]: e.target.value }))}
                                            className="flex-1 bg-[#0f1114] border border-gray-700 rounded-lg px-3 py-2 text-white"
                                        >
                                            {fieldOptions.map(opt => (
                                                <option key={opt.value} value={opt.value}>{opt.label}</option>
                                            ))}
                                        </select>
                                        <span className="text-gray-500 text-sm w-32 truncate">
                                            {parsedContacts[0]?.[field] || '-'}
                                        </span>
                                    </div>
                                ))}
                            </div>
                            <button
                                onClick={() => setStep(4)}
                                className="mt-6 px-6 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg"
                            >
                                Continue to Import
                            </button>
                        </div>
                    )}

                    {/* Step 4: Confirm & Import */}
                    {step === 4 && (
                        <div className="text-center">
                            <Users size={48} className="text-purple-400 mx-auto mb-4" />
                            <h3 className="text-xl font-semibold text-white mb-2">Ready to Import</h3>
                            <p className="text-gray-400 mb-6">{parsedContacts.length} contacts will be imported</p>
                            
                            <div className="bg-[#0f1114] rounded-lg p-4 mb-6 text-left max-h-[200px] overflow-y-auto">
                                {parsedContacts.slice(0, 5).map((c, i) => (
                                    <div key={i} className="flex items-center gap-3 py-2 border-b border-gray-800 last:border-0">
                                        <div className="w-8 h-8 bg-purple-500/20 rounded-full flex items-center justify-center text-purple-400 text-sm">
                                            {(c.name || c.first_name || '?')[0].toUpperCase()}
                                        </div>
                                        <div>
                                            <p className="text-white text-sm">{c.name || `${c.first_name} ${c.last_name}`}</p>
                                            <p className="text-gray-500 text-xs">{c.email} • {c.company}</p>
                                        </div>
                                    </div>
                                ))}
                                {parsedContacts.length > 5 && (
                                    <p className="text-gray-500 text-sm text-center py-2">+{parsedContacts.length - 5} more</p>
                                )}
                            </div>
                            
                            <button
                                onClick={handleImport}
                                disabled={importing}
                                className="px-8 py-3 bg-green-600 hover:bg-green-700 disabled:opacity-50 rounded-lg font-medium inline-flex items-center gap-2"
                            >
                                {importing ? (
                                    <><Loader2 size={20} className="animate-spin" /> Importing...</>
                                ) : (
                                    <><Upload size={20} /> Import {parsedContacts.length} Contacts</>
                                )}
                            </button>
                        </div>
                    )}

                    {/* Step 5: Results */}
                    {step === 5 && importResult && (
                        <div className="text-center">
                            <div className="w-16 h-16 bg-green-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
                                <Check size={32} className="text-green-400" />
                            </div>
                            <h3 className="text-xl font-semibold text-white mb-2">Import Complete!</h3>
                            <p className="text-gray-400 mb-6">
                                {importResult.success} contacts imported successfully
                                {importResult.failed > 0 && `, ${importResult.failed} failed`}
                            </p>
                            <button
                                onClick={() => { onComplete(); onClose(); }}
                                className="px-6 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg"
                            >
                                View Contacts
                            </button>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
