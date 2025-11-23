import React from 'react';
import { Sparkles, CheckCircle2, RefreshCw } from 'lucide-react';

interface Props {
  isProcessing: boolean;
  progress: number;
  current: number;
  total: number;
  currentContact?: string;
}

export default function BatchProgress({ 
  isProcessing, 
  progress, 
  current, 
  total, 
  currentContact 
}: Props) {
  
  if (!isProcessing) return null;

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center">
      <div className="bg-slate-800 rounded-2xl border border-slate-700 p-8 max-w-md w-full">
        <div className="text-center mb-6">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-purple-600/20 rounded-full mb-4">
            {progress === 100 ? (
              <CheckCircle2 className="w-8 h-8 text-green-400" />
            ) : (
              <RefreshCw className="w-8 h-8 text-purple-400 animate-spin" />
            )}
          </div>
          
          <h3 className="text-xl font-bold text-white mb-2">
            {progress === 100 ? 'Enrichment Complete!' : 'Enriching Contacts...'}
          </h3>
          
          <p className="text-slate-400">
            {current} of {total} contacts processed
          </p>
          
          {currentContact && (
            <p className="text-sm text-slate-500 mt-2">
              Currently processing: {currentContact}
            </p>
          )}
        </div>

        <div className="space-y-2">
          <div className="flex justify-between text-sm text-slate-400">
            <span>Progress</span>
            <span>{Math.round(progress)}%</span>
          </div>
          
          <div className="w-full bg-slate-700 rounded-full h-3 overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-purple-500 to-blue-500 transition-all duration-500"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>

        {progress === 100 && (
          <button
            onClick={() => window.location.reload()}
            className="w-full mt-6 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-all"
          >
            View Results
          </button>
        )}
      </div>
    </div>
  );
}
