import React from 'react';

interface EnrichmentWarningProps {
  hasLinkedIn: boolean;
  onProceed?: () => void;
  onCancel?: () => void;
}

export const EnrichmentWarning: React.FC<EnrichmentWarningProps> = ({ 
  hasLinkedIn, 
  onProceed,
  onCancel 
}) => {
  if (hasLinkedIn) return null;

  return (
    <div className="bg-amber-50 border-l-4 border-amber-400 p-4 rounded">
      <div className="flex items-start">
        <div className="flex-shrink-0">
          <svg className="h-5 w-5 text-amber-400" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
          </svg>
        </div>
        <div className="ml-3 flex-1">
          <p className="text-sm text-amber-700 font-semibold">LinkedIn URL Missing</p>
          <p className="text-sm text-amber-600 mt-1">
            Enrichment works best with a LinkedIn profile URL. Profile quality may be limited without it.
          </p>
          {(onProceed || onCancel) && (
            <div className="mt-3 flex gap-2">
              {onProceed && (
                <button onClick={onProceed} className="px-3 py-1.5 bg-amber-600 text-white text-sm rounded hover:bg-amber-700 transition">
                  Proceed Anyway
                </button>
              )}
              {onCancel && (
                <button onClick={onCancel} className="px-3 py-1.5 bg-white text-amber-700 text-sm rounded border border-amber-300 hover:bg-amber-50 transition">
                  Cancel
                </button>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
