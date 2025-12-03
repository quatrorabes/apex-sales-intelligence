import React from 'react';

interface BatchProgressProps {
  current: number;
  total: number;
  operation: string;
}

export const BatchProgress: React.FC<BatchProgressProps> = ({ current, total, operation }) => {
  const percentage = Math.round((current / total) * 100);

  return (
    <div className="fixed bottom-4 right-4 bg-white rounded-lg shadow-lg p-4 min-w-[300px] border">
      <div className="flex items-center justify-between mb-2">
        <span className="font-semibold text-gray-900">{operation}</span>
        <span className="text-sm text-gray-600">{current}/{total}</span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2">
        <div 
          className="bg-blue-600 h-2 rounded-full transition-all duration-300"
          style={{ width: `${percentage}%` }}
        />
      </div>
      <p className="text-xs text-gray-500 mt-2">{percentage}% complete</p>
    </div>
  );
};
