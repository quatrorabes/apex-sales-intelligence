import React, { useState, useEffect } from 'react';
import { Target, Loader, AlertCircle } from 'lucide-react';
import { apiClient } from '../utils/api';

interface WhyMeTabProps {
  contactId: number;
}

export const WhyMeTab: React.FC<WhyMeTabProps> = ({ contactId }) => {
  const [whyMeData, setWhyMeData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadWhyMe();
  }, [contactId]);

  const loadWhyMe = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await apiClient.getWhyMe(contactId);
      setWhyMeData(data);
    } catch (err) {
      console.error('Failed to load Why Me:', err);
      setError('Failed to load Why Me analysis');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <Loader className="h-8 w-8 animate-spin text-blue-600" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center p-8 text-center">
        <AlertCircle className="h-12 w-12 text-red-500 mb-3" />
        <p className="text-red-600 font-medium">{error}</p>
        <button
          onClick={loadWhyMe}
          className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          Try Again
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3 mb-6">
        <Target className="h-6 w-6 text-purple-600" />
        <h2 className="text-xl font-bold text-gray-900">Why This Contact Matters</h2>
      </div>

      {whyMeData?.reasons && (
        <div className="space-y-4">
          {whyMeData.reasons.map((reason: any, index: number) => (
            <div key={index} className="bg-white border rounded-lg p-4">
              <h3 className="font-semibold text-gray-900 mb-2">{reason.title}</h3>
              <p className="text-gray-700">{reason.description}</p>
              {reason.evidence && (
                <ul className="mt-3 space-y-1">
                  {reason.evidence.map((item: string, i: number) => (
                    <li key={i} className="text-sm text-gray-600 flex items-start gap-2">
                      <span className="text-green-600 mt-0.5">✓</span>
                      <span>{item}</span>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          ))}
        </div>
      )}

      {whyMeData?.recommended_approach && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h3 className="font-semibold text-blue-900 mb-2">Recommended Approach</h3>
          <p className="text-blue-800">{whyMeData.recommended_approach}</p>
        </div>
      )}
    </div>
  );
};
