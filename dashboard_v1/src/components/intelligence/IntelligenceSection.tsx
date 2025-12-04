import { useState } from 'react';
import { ChevronDown, ChevronUp, Copy, Check } from 'lucide-react';

interface IntelligenceSectionProps {
  title: string;
  content: string;
  icon?: string;
  defaultOpen?: boolean;
  copyable?: boolean;
}

export function IntelligenceSection({ 
  title, 
  content, 
  icon = '📊', 
  defaultOpen = false,
  copyable = false 
}: IntelligenceSectionProps) {
  const [isOpen, setIsOpen] = useState(defaultOpen);
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="bg-midnight-900 border border-midnight-700 rounded-xl overflow-hidden hover:border-midnight-600 transition-all">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full px-6 py-4 flex items-center justify-between hover:bg-midnight-800 transition-all"
      >
        <div className="flex items-center gap-3">
          <span className="text-2xl">{icon}</span>
          <h3 className="text-lg font-semibold text-text-primary">{title}</h3>
        </div>
        <div className="flex items-center gap-2">
          {copyable && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                handleCopy();
              }}
              className="p-2 hover:bg-midnight-700 rounded-lg transition-all"
            >
              {copied ? (
                <Check className="w-4 h-4 text-green-400" />
              ) : (
                <Copy className="w-4 h-4 text-text-secondary" />
              )}
            </button>
          )}
          {isOpen ? (
            <ChevronUp className="w-5 h-5 text-text-secondary" />
          ) : (
            <ChevronDown className="w-5 h-5 text-text-secondary" />
          )}
        </div>
      </button>
      
      {isOpen && (
        <div className="px-6 py-4 border-t border-midnight-700 animate-fadeIn">
          <div className="prose prose-invert max-w-none">
            <p className="text-text-secondary leading-relaxed whitespace-pre-wrap">
              {content}
            </p>
          </div>
        </div>
      )}
    </div>
  );
}