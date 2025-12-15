import React from 'react';
import { Search, Filter, RefreshCw } from 'lucide-react';

interface ToolbarProps {
  onSearch?: (query: string) => void;
  onFilter?: () => void;
  onRefresh?: () => void;
}

export const Toolbar: React.FC<ToolbarProps> = ({ onSearch, onFilter, onRefresh }) => {
  return (
    <div className="flex items-center gap-2 p-2 bg-gray-50 border-b">
      <div className="flex-1 relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
        <input
          type="text"
          placeholder="Search contacts..."
          className="w-full pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
          onChange={(e) => onSearch?.(e.target.value)}
        />
      </div>
      {onFilter && (
        <button onClick={onFilter} className="p-2 hover:bg-gray-200 rounded">
          <Filter className="h-5 w-5" />
        </button>
      )}
      {onRefresh && (
        <button onClick={onRefresh} className="p-2 hover:bg-gray-200 rounded">
          <RefreshCw className="h-5 w-5" />
        </button>
      )}
    </div>
  );
};
