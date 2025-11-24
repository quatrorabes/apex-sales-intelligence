import React, { useState } from 'react';
import { Target, Building2, Users, TrendingUp, CheckCircle, X } from 'lucide-react';

interface OnboardingModalProps {
  onComplete: (preferences: any) => void;
  onClose: () => void;
}

export default function OnboardingModal({ onComplete, onClose }: OnboardingModalProps) {
  const [step, setStep] = useState(1);
  const [preferences, setPreferences] = useState({
    user_id: 'default_user',
    industry: '',
    target_verticals: [] as string[],
    ideal_titles: [] as string[],
    avoid_titles: [] as string[],
    min_company_size: 10,
    max_company_size: 5000,
    target_industries: [] as string[],
    seniority_levels: [] as string[],
    exclude_c_suite: false
  });

  const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

  const industries = [
    { value: 'CRE_MORTGAGE', label: 'Commercial Real Estate - Mortgage/Lending' },
    { value: 'CRE_BROKERAGE', label: 'Commercial Real Estate - Brokerage' },
    { value: 'COMMERCIAL_BANKING', label: 'Commercial Banking' },
    { value: 'INSURANCE', label: 'Insurance' },
    { value: 'TECHNOLOGY', label: 'Technology' },
    { value: 'HEALTHCARE', label: 'Healthcare' }
  ];

  const seniorityLevels = [
    'Principal/Owner',
    'C-Suite (CEO, CFO, etc.)',
    'EVP (Executive VP)',
    'SVP (Senior VP)',
    'VP (Vice President)',
    'Director',
    'Manager',
    'Senior/Lead',
    'Associate/Analyst'
  ];

  const commonTitles = {
    CRE_MORTGAGE: [
      'Broker',
      'Senior Broker',
      'Vice President',
      'Senior Vice President',
      'Director',
      'Principal',
      'Loan Officer',
      'Mortgage Banker'
    ],
    CRE_BROKERAGE: [
      'Broker',
      'Senior Broker',
      'Director',
      'Senior Director',
      'Vice President',
      'Senior Associate',
      'Investment Sales',
      'Leasing Specialist'
    ],
    COMMERCIAL_BANKING: [
      'Relationship Manager',
      'Vice President',
      'Senior Vice President',
      'Portfolio Manager',
      'Commercial Banker',
      'Loan Officer'
    ],
    INSURANCE: [],
    TECHNOLOGY: [],
    HEALTHCARE: []
  };

  const handleSubmit = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/user/onboarding`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(preferences)
      });

      const data = await response.json();
      
      if (data.success) {
        alert('Preferences saved successfully!');
        onComplete(preferences);
      } else {
        alert(`Error: ${data.error || data.message}`);
      }
    } catch (error) {
      console.error('Error saving preferences:', error);
      alert('Failed to save preferences');
    }
  };

  const toggleTitle = (title: string, isIdeal: boolean) => {
    const titleLower = title.toLowerCase();
    if (isIdeal) {
      setPreferences(prev => ({
        ...prev,
        ideal_titles: prev.ideal_titles.includes(titleLower)
          ? prev.ideal_titles.filter(t => t !== titleLower)
          : [...prev.ideal_titles, titleLower]
      }));
    } else {
      setPreferences(prev => ({
        ...prev,
        avoid_titles: prev.avoid_titles.includes(titleLower)
          ? prev.avoid_titles.filter(t => t !== titleLower)
          : [...prev.avoid_titles, titleLower]
      }));
    }
  };

  const toggleSeniority = (level: string) => {
    setPreferences(prev => ({
      ...prev,
      seniority_levels: prev.seniority_levels.includes(level)
        ? prev.seniority_levels.filter(l => l !== level)
        : [...prev.seniority_levels, level]
    }));
  };

  const toggleVertical = (vertical: string) => {
    setPreferences(prev => ({
      ...prev,
      target_verticals: prev.target_verticals.includes(vertical)
        ? prev.target_verticals.filter(v => v !== vertical)
        : [...prev.target_verticals, vertical]
    }));
  };

  const totalSteps = 5;

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-6 z-50">
      <div className="bg-slate-800 rounded-xl max-w-3xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6 border-b border-slate-700">
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-bold text-white">Configure Your Ideal Customer Profile</h2>
            <button onClick={onClose} className="text-slate-400 hover:text-white">
              <X className="w-6 h-6" />
            </button>
          </div>
          <div className="flex items-center gap-2 mt-4">
            {Array.from({length: totalSteps}, (_, i) => i + 1).map(i => (
              <div
                key={i}
                className={`flex-1 h-2 rounded ${
                  i <= step ? 'bg-blue-500' : 'bg-slate-700'
                }`}
              />
            ))}
          </div>
        </div>

        <div className="p-6">
          {step === 1 && (
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-medium text-white mb-4">What's your business?</h3>
                <div className="grid grid-cols-1 gap-3">
                  {industries.map(ind => (
                    <label
                      key={ind.value}
                      className={`flex items-center gap-3 p-4 rounded-lg border cursor-pointer transition-colors ${
                        preferences.industry === ind.value
                          ? 'border-blue-500 bg-blue-500/10'
                          : 'border-slate-700 hover:border-slate-600'
                      }`}
                    >
                      <input
                        type="radio"
                        name="industry"
                        value={ind.value}
                        checked={preferences.industry === ind.value}
                        onChange={(e) => setPreferences({...preferences, industry: e.target.value})}
                        className="text-blue-500"
                      />
                      <div>
                        <p className="text-white font-medium">{ind.label}</p>
                      </div>
                    </label>
                  ))}
                </div>
              </div>
            </div>
          )}

          {step === 2 && (
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-medium text-white mb-4">Who are your target customers?</h3>
                <p className="text-sm text-slate-400 mb-4">Select the types of professionals you want to reach</p>
                
                <div className="space-y-3">
                  <h4 className="text-sm font-medium text-cyan-400">Commercial Real Estate Professionals</h4>
                  {[
                    { value: 'cre_brokers', label: 'CRE Brokers (Investment Sales)' },
                    { value: 'cre_leasing', label: 'Commercial Leasing Brokers' },
                    { value: 'mortgage_brokers', label: 'Commercial Mortgage Brokers' },
                    { value: 'developers', label: 'Real Estate Developers' },
                    { value: 'property_managers', label: 'Property/Asset Managers' },
                    { value: 'cre_lenders', label: 'CRE Lenders (Banks)' },
                    { value: 'investors', label: 'Real Estate Investors/Funds' }
                  ].map(vertical => (
                    <label
                      key={vertical.value}
                      className="flex items-center gap-3 p-3 rounded-lg border border-slate-700 hover:border-slate-600 cursor-pointer"
                    >
                      <input
                        type="checkbox"
                        checked={preferences.target_verticals.includes(vertical.value)}
                        onChange={() => toggleVertical(vertical.value)}
                        className="text-blue-500"
                      />
                      <span className="text-white">{vertical.label}</span>
                    </label>
                  ))}
                </div>
              </div>
            </div>
          )}

          {step === 3 && (
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-medium text-white mb-4">What job titles do you target?</h3>
                {preferences.industry && commonTitles[preferences.industry as keyof typeof commonTitles] && (
                  <div>
                    <p className="text-sm text-slate-400 mb-3">Common titles in your industry (click to select):</p>
                    <div className="flex flex-wrap gap-2 mb-6">
                      {(commonTitles[preferences.industry as keyof typeof commonTitles] || []).map(title => (
                        <button
                          key={title}
                          onClick={() => toggleTitle(title, true)}
                          className={`px-3 py-1 rounded-full text-sm transition-colors ${
                            preferences.ideal_titles.includes(title.toLowerCase())
                              ? 'bg-green-600 text-white'
                              : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                          }`}
                        >
                          {title}
                        </button>
                      ))}
                    </div>
                  </div>
                )}

                <div>
                  <p className="text-sm text-slate-400 mb-3">Titles to AVOID (click to mark):</p>
                  <div className="flex flex-wrap gap-2">
                    {['HR', 'Marketing', 'IT', 'Legal', 'Admin', 'Assistant', 'Coordinator', 'Intern'].map(title => (
                      <button
                        key={title}
                        onClick={() => toggleTitle(title, false)}
                        className={`px-3 py-1 rounded-full text-sm transition-colors ${
                          preferences.avoid_titles.includes(title.toLowerCase())
                            ? 'bg-red-600 text-white'
                            : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                        }`}
                      >
                        {title}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}

          {step === 4 && (
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-medium text-white mb-4">What seniority levels do you target?</h3>
                <div className="space-y-2">
                  {seniorityLevels.map(level => (
                    <label
                      key={level}
                      className="flex items-center gap-3 p-3 rounded-lg border border-slate-700 hover:border-slate-600 cursor-pointer"
                    >
                      <input
                        type="checkbox"
                        checked={preferences.seniority_levels.includes(level)}
                        onChange={() => toggleSeniority(level)}
                        className="text-blue-500"
                      />
                      <span className="text-white">{level}</span>
                    </label>
                  ))}
                </div>

                <label className="flex items-center gap-3 p-4 mt-4 rounded-lg bg-red-900/20 border border-red-800">
                  <input
                    type="checkbox"
                    checked={preferences.exclude_c_suite}
                    onChange={(e) => setPreferences({...preferences, exclude_c_suite: e.target.checked})}
                    className="text-red-500"
                  />
                  <div>
                    <p className="text-white font-medium">Exclude Non-CRE C-Suite</p>
                    <p className="text-sm text-slate-400">Penalize CEOs/CFOs not in real estate</p>
                  </div>
                </label>
              </div>
            </div>
          )}

          {step === 5 && (
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-medium text-white mb-4">Company Size Preferences</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm text-slate-400 mb-2">Minimum Employees</label>
                    <input
                      type="number"
                      value={preferences.min_company_size}
                      onChange={(e) => setPreferences({...preferences, min_company_size: parseInt(e.target.value) || 0})}
                      className="w-full px-3 py-2 bg-slate-700 rounded-lg text-white"
                    />
                  </div>
                  <div>
                    <label className="block text-sm text-slate-400 mb-2">Maximum Employees</label>
                    <input
                      type="number"
                      value={preferences.max_company_size}
                      onChange={(e) => setPreferences({...preferences, max_company_size: parseInt(e.target.value) || 10000})}
                      className="w-full px-3 py-2 bg-slate-700 rounded-lg text-white"
                    />
                  </div>
                </div>
              </div>

              <div className="bg-slate-700/50 rounded-lg p-4">
                <h4 className="text-white font-medium mb-3">Your ICP Summary:</h4>
                <div className="space-y-2 text-sm text-slate-300">
                  <p>• Industry: {preferences.industry || 'Not selected'}</p>
                  <p>• Target Verticals: {preferences.target_verticals.join(', ') || 'None selected'}</p>
                  <p>• Target Titles: {preferences.ideal_titles.join(', ') || 'None selected'}</p>
                  <p>• Avoid Titles: {preferences.avoid_titles.join(', ') || 'None selected'}</p>
                  <p>• Company Size: {preferences.min_company_size} - {preferences.max_company_size} employees</p>
                  <p>• Exclude Non-CRE C-Suite: {preferences.exclude_c_suite ? 'Yes' : 'No'}</p>
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="p-6 border-t border-slate-700 flex justify-between">
          {step > 1 && (
            <button
              onClick={() => setStep(step - 1)}
              className="px-6 py-2 bg-slate-700 text-white rounded-lg hover:bg-slate-600"
            >
              Previous
            </button>
          )}
          {step < totalSteps ? (
            <button
              onClick={() => setStep(step + 1)}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 ml-auto"
              disabled={step === 1 && !preferences.industry}
            >
              Next
            </button>
          ) : (
            <button
              onClick={handleSubmit}
              className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 ml-auto flex items-center gap-2"
            >
              <CheckCircle className="w-5 h-5" />
              Complete Setup
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
