import { useState, useEffect } from 'react';
import { X, User, Briefcase, Target, Trophy, ChevronRight, ChevronLeft, Check, Loader2 } from 'lucide-react';

const API_URL = 'https://apex-backend-production-production.up.railway.app';

interface UserOnboardingProps {
    isOpen: boolean;
    onClose: () => void;
    onComplete: () => void;
}

export default function UserOnboarding({ isOpen, onClose, onComplete }: UserOnboardingProps) {
    const [step, setStep] = useState(1);
    const [saving, setSaving] = useState(false);
    
    const [profile, setProfile] = useState({
        full_name: '',
        role: '',
        company: '',
        years_experience: 0,
        primary_product: '',
        products_services: [] as string[],
        sweet_spot_min: 500000,
        sweet_spot_max: 10000000,
        asset_types: [] as string[],
        geographic_markets: [] as string[],
        differentiators: '',
        specialization: '',
        ideal_titles: [] as string[],
        ideal_company_types: [] as string[],
    });
    
    const [proofPoints, setProofPoints] = useState({
        deals_closed_12mo: 0,
        total_volume_12mo: 0,
        avg_close_days: 0,
        notable_deals: [] as { amount: string; type: string; timeline: string; highlight: string }[],
    });

    const roles = [
        { id: 'commercial_banker', label: 'Commercial Banker' },
        { id: 'sba_lender', label: 'SBA Lender' },
        { id: 'cre_broker', label: 'CRE Broker' },
        { id: 'mortgage_broker', label: 'Mortgage Broker' },
        { id: 'private_lender', label: 'Private Lender' },
        { id: 'investment_banker', label: 'Investment Banker' },
    ];

    const productOptions = [
        'Bridge Loans', 'Permanent Financing', 'Construction Loans', 'SBA 7(a)',
        'SBA 504', 'CMBS', 'Mezzanine', 'Preferred Equity', 'Hard Money',
    ];

    const assetOptions = [
        'Multifamily', 'Retail', 'Industrial', 'Office', 'Mixed-Use',
        'Hospitality', 'Self-Storage', 'Senior Housing', 'Medical Office',
    ];

    const titleOptions = [
        'CEO', 'President', 'Principal', 'Partner', 'Managing Director',
        'SVP', 'VP', 'Director', 'Senior Broker', 'Broker',
    ];

    const companyTypeOptions = [
        'CRE Brokerage', 'Developer', 'Investor/Fund', 'REIT', 'Family Office',
        'Private Equity', 'Syndicator', 'Owner/Operator', 'Property Manager',
    ];

    const handleMultiSelect = (field: string, value: string) => {
        setProfile(p => {
            const current = p[field as keyof typeof p] as string[];
            return {
                ...p,
                [field]: current.includes(value)
                    ? current.filter(v => v !== value)
                    : [...current, value]
            };
        });
    };

    const saveProfile = async () => {
        setSaving(true);
        try {
            await fetch(`${API_URL}/api/user/profile`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ ...profile, user_id: 'default' })
            });
            
            await fetch(`${API_URL}/api/user/proof-points`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ ...proofPoints, user_id: 'default' })
            });
            
            localStorage.setItem('apex_onboarded', 'true');
            onComplete();
        } catch (e) {
            console.error('Save error:', e);
        } finally {
            setSaving(false);
        }
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">
            <div className="bg-[#1a1d21] rounded-2xl w-full max-w-2xl max-h-[90vh] overflow-hidden flex flex-col">
                {/* Header */}
                <div className="bg-[#0f1114] px-6 py-4 border-b border-gray-800 flex items-center justify-between shrink-0">
                    <div>
                        <h2 className="text-xl font-bold text-white">Set Up Your Profile</h2>
                        <p className="text-gray-400 text-sm">Help Apex match contacts to YOUR strengths</p>
                    </div>
                    <button onClick={onClose} className="text-gray-500 hover:text-white">
                        <X size={24} />
                    </button>
                </div>

                {/* Progress */}
                <div className="px-6 py-3 bg-[#1e2228] border-b border-gray-800 shrink-0">
                    <div className="flex items-center justify-between">
                        {[
                            { num: 1, label: 'About You', icon: <User size={16} /> },
                            { num: 2, label: 'Products', icon: <Briefcase size={16} /> },
                            { num: 3, label: 'Ideal Client', icon: <Target size={16} /> },
                            { num: 4, label: 'Track Record', icon: <Trophy size={16} /> },
                        ].map((s, i) => (
                            <div key={s.num} className="flex items-center">
                                <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-sm ${
                                    step === s.num ? 'bg-purple-600 text-white' :
                                    step > s.num ? 'bg-green-600/20 text-green-400' :
                                    'bg-gray-800 text-gray-500'
                                }`}>
                                    {step > s.num ? <Check size={14} /> : s.icon}
                                    <span className="hidden sm:inline">{s.label}</span>
                                </div>
                                {i < 3 && <div className="w-8 h-px bg-gray-700 mx-2" />}
                            </div>
                        ))}
                    </div>
                </div>

                {/* Content */}
                <div className="p-6 overflow-y-auto flex-1">
                    {/* STEP 1 */}
                    {step === 1 && (
                        <div className="space-y-4">
                            <div>
                                <label className="block text-gray-400 text-sm mb-1">Your Name</label>
                                <input
                                    type="text"
                                    value={profile.full_name}
                                    onChange={e => setProfile(p => ({ ...p, full_name: e.target.value }))}
                                    className="w-full bg-[#0f1114] border border-gray-700 rounded-lg px-4 py-2 text-white focus:border-purple-500 outline-none"
                                    placeholder="John Smith"
                                />
                            </div>
                            <div>
                                <label className="block text-gray-400 text-sm mb-2">Your Role</label>
                                <div className="grid grid-cols-2 gap-2">
                                    {roles.map(r => (
                                        <button
                                            key={r.id}
                                            onClick={() => setProfile(p => ({ ...p, role: r.id }))}
                                            className={`px-4 py-2 rounded-lg text-sm font-medium transition ${
                                                profile.role === r.id
                                                    ? 'bg-purple-600 text-white'
                                                    : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
                                            }`}
                                        >
                                            {r.label}
                                        </button>
                                    ))}
                                </div>
                            </div>
                            <div>
                                <label className="block text-gray-400 text-sm mb-1">Company</label>
                                <input
                                    type="text"
                                    value={profile.company}
                                    onChange={e => setProfile(p => ({ ...p, company: e.target.value }))}
                                    className="w-full bg-[#0f1114] border border-gray-700 rounded-lg px-4 py-2 text-white focus:border-purple-500 outline-none"
                                    placeholder="ABC Capital"
                                />
                            </div>
                            <div>
                                <label className="block text-gray-400 text-sm mb-1">Years of Experience</label>
                                <input
                                    type="number"
                                    value={profile.years_experience || ''}
                                    onChange={e => setProfile(p => ({ ...p, years_experience: parseInt(e.target.value) || 0 }))}
                                    className="w-full bg-[#0f1114] border border-gray-700 rounded-lg px-4 py-2 text-white focus:border-purple-500 outline-none"
                                />
                            </div>
                        </div>
                    )}

                    {/* STEP 2 */}
                    {step === 2 && (
                        <div className="space-y-4">
                            <div>
                                <label className="block text-gray-400 text-sm mb-2">Products/Services You Offer</label>
                                <div className="flex flex-wrap gap-2">
                                    {productOptions.map(p => (
                                        <button
                                            key={p}
                                            onClick={() => handleMultiSelect('products_services', p)}
                                            className={`px-3 py-1.5 rounded-full text-sm transition ${
                                                profile.products_services.includes(p)
                                                    ? 'bg-purple-600 text-white'
                                                    : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
                                            }`}
                                        >
                                            {p}
                                        </button>
                                    ))}
                                </div>
                            </div>
                            <div>
                                <label className="block text-gray-400 text-sm mb-2">Asset Types You Focus On</label>
                                <div className="flex flex-wrap gap-2">
                                    {assetOptions.map(a => (
                                        <button
                                            key={a}
                                            onClick={() => handleMultiSelect('asset_types', a)}
                                            className={`px-3 py-1.5 rounded-full text-sm transition ${
                                                profile.asset_types.includes(a)
                                                    ? 'bg-purple-600 text-white'
                                                    : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
                                            }`}
                                        >
                                            {a}
                                        </button>
                                    ))}
                                </div>
                            </div>
                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-gray-400 text-sm mb-1">Deal Size Min ($)</label>
                                    <input
                                        type="number"
                                        value={profile.sweet_spot_min || ''}
                                        onChange={e => setProfile(p => ({ ...p, sweet_spot_min: parseInt(e.target.value) || 0 }))}
                                        className="w-full bg-[#0f1114] border border-gray-700 rounded-lg px-4 py-2 text-white focus:border-purple-500 outline-none"
                                    />
                                </div>
                                <div>
                                    <label className="block text-gray-400 text-sm mb-1">Deal Size Max ($)</label>
                                    <input
                                        type="number"
                                        value={profile.sweet_spot_max || ''}
                                        onChange={e => setProfile(p => ({ ...p, sweet_spot_max: parseInt(e.target.value) || 0 }))}
                                        className="w-full bg-[#0f1114] border border-gray-700 rounded-lg px-4 py-2 text-white focus:border-purple-500 outline-none"
                                    />
                                </div>
                            </div>
                            <div>
                                <label className="block text-gray-400 text-sm mb-1">What Makes You Different?</label>
                                <textarea
                                    value={profile.differentiators}
                                    onChange={e => setProfile(p => ({ ...p, differentiators: e.target.value }))}
                                    className="w-full bg-[#0f1114] border border-gray-700 rounded-lg px-4 py-2 text-white h-20 focus:border-purple-500 outline-none"
                                    placeholder="Fast closings, direct lender relationships, creative structures..."
                                />
                            </div>
                        </div>
                    )}

                    {/* STEP 3 */}
                    {step === 3 && (
                        <div className="space-y-4">
                            <div>
                                <label className="block text-gray-400 text-sm mb-2">Ideal Client Titles</label>
                                <div className="flex flex-wrap gap-2">
                                    {titleOptions.map(t => (
                                        <button
                                            key={t}
                                            onClick={() => handleMultiSelect('ideal_titles', t)}
                                            className={`px-3 py-1.5 rounded-full text-sm transition ${
                                                profile.ideal_titles.includes(t)
                                                    ? 'bg-purple-600 text-white'
                                                    : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
                                            }`}
                                        >
                                            {t}
                                        </button>
                                    ))}
                                </div>
                            </div>
                            <div>
                                <label className="block text-gray-400 text-sm mb-2">Ideal Company Types</label>
                                <div className="flex flex-wrap gap-2">
                                    {companyTypeOptions.map(c => (
                                        <button
                                            key={c}
                                            onClick={() => handleMultiSelect('ideal_company_types', c)}
                                            className={`px-3 py-1.5 rounded-full text-sm transition ${
                                                profile.ideal_company_types.includes(c)
                                                    ? 'bg-purple-600 text-white'
                                                    : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
                                            }`}
                                        >
                                            {c}
                                        </button>
                                    ))}
                                </div>
                            </div>
                            <div>
                                <label className="block text-gray-400 text-sm mb-1">Your Specialization</label>
                                <input
                                    type="text"
                                    value={profile.specialization}
                                    onChange={e => setProfile(p => ({ ...p, specialization: e.target.value }))}
                                    className="w-full bg-[#0f1114] border border-gray-700 rounded-lg px-4 py-2 text-white focus:border-purple-500 outline-none"
                                    placeholder="e.g., Value-add multifamily, ground-up construction"
                                />
                            </div>
                        </div>
                    )}

                    {/* STEP 4 */}
                    {step === 4 && (
                        <div className="space-y-4">
                            <div className="bg-purple-900/20 border border-purple-800/50 rounded-lg p-4 mb-4">
                                <p className="text-purple-300 text-sm">
                                    💡 These metrics power your personalized "Why Me" content for each contact.
                                </p>
                            </div>
                            <div className="grid grid-cols-3 gap-4">
                                <div>
                                    <label className="block text-gray-400 text-sm mb-1">Deals Closed (12mo)</label>
                                    <input
                                        type="number"
                                        value={proofPoints.deals_closed_12mo || ''}
                                        onChange={e => setProofPoints(p => ({ ...p, deals_closed_12mo: parseInt(e.target.value) || 0 }))}
                                        className="w-full bg-[#0f1114] border border-gray-700 rounded-lg px-4 py-2 text-white focus:border-purple-500 outline-none"
                                    />
                                </div>
                                <div>
                                    <label className="block text-gray-400 text-sm mb-1">Volume ($M)</label>
                                    <input
                                        type="number"
                                        value={proofPoints.total_volume_12mo || ''}
                                        onChange={e => setProofPoints(p => ({ ...p, total_volume_12mo: parseFloat(e.target.value) || 0 }))}
                                        className="w-full bg-[#0f1114] border border-gray-700 rounded-lg px-4 py-2 text-white focus:border-purple-500 outline-none"
                                    />
                                </div>
                                <div>
                                    <label className="block text-gray-400 text-sm mb-1">Avg Days to Close</label>
                                    <input
                                        type="number"
                                        value={proofPoints.avg_close_days || ''}
                                        onChange={e => setProofPoints(p => ({ ...p, avg_close_days: parseInt(e.target.value) || 0 }))}
                                        className="w-full bg-[#0f1114] border border-gray-700 rounded-lg px-4 py-2 text-white focus:border-purple-500 outline-none"
                                    />
                                </div>
                            </div>
                            <div className="bg-[#0f1114] rounded-lg p-4 border border-gray-800">
                                <p className="text-gray-400 text-sm mb-2">You can add notable deals and more proof points later in Settings.</p>
                            </div>
                        </div>
                    )}
                </div>

                {/* Footer */}
                <div className="px-6 py-4 bg-[#0f1114] border-t border-gray-800 flex justify-between shrink-0">
                    <button
                        onClick={() => setStep(s => Math.max(1, s - 1))}
                        disabled={step === 1}
                        className="px-4 py-2 text-gray-400 hover:text-white disabled:opacity-30 flex items-center gap-2"
                    >
                        <ChevronLeft size={18} /> Back
                    </button>
                    
                    {step < 4 ? (
                        <button
                            onClick={() => setStep(s => s + 1)}
                            className="bg-purple-600 hover:bg-purple-700 text-white px-6 py-2 rounded-lg font-medium flex items-center gap-2"
                        >
                            Next <ChevronRight size={18} />
                        </button>
                    ) : (
                        <button
                            onClick={saveProfile}
                            disabled={saving}
                            className="bg-green-600 hover:bg-green-700 disabled:opacity-50 text-white px-6 py-2 rounded-lg font-medium flex items-center gap-2"
                        >
                            {saving ? <Loader2 size={18} className="animate-spin" /> : <Check size={18} />}
                            {saving ? 'Saving...' : 'Complete Setup'}
                        </button>
                    )}
                </div>
            </div>
        </div>
    );
}
