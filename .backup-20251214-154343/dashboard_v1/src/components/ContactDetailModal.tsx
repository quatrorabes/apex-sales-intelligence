import { useState, useEffect } from 'react';
import { X, Sparkles } from 'lucide-react';

interface Contact {
  id: number;
  name: string;
  email: string;
  company: string;
  title: string;
  phone?: string;
  linkedin_url?: string;
  profile_content?: string;
  mdcp_score?: number;
  mdcp_tier?: string;
  priority_score?: number;
  enrichment_status?: string;
}

interface Props {
  contactId: number;
  onClose: () => void;
}

export default function ContactDetailModal({ contactId, onClose }: Props) {
  const [contact, setContact] = useState<Contact | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`https://apex-backend-i7b0.onrender.com/api/v2/contacts/${contactId}`)
      .then(r => r.json())
      .then(setContact)
      .finally(() => setLoading(false));
  }, [contactId]);

  const formatProfile = (content: string) => {
    if (!content) return null;
    return content.split(/###?\s+/).filter(s => s.trim()).map((section, i) => {
      const [heading, ...body] = section.trim().split('\n');
      const text = body.join('\n').trim();
      if (!text) return null;
      return (
        <div key={i} className="mb-6">
          <h3 className="text-lg font-semibold bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent mb-2 pb-1 border-b border-gray-800">
            {heading}
          </h3>
          <div className="text-gray-300 whitespace-pre-wrap leading-relaxed">
            {text}
          </div>
        </div>
      );
    });
  };

  if (loading) {
    return (
      <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50">
        <Sparkles size={48} className="text-cyan-400 animate-pulse" />
      </div>
    );
  }

  if (!contact) return null;

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-[#111928]/95 backdrop-blur-xl rounded-2xl shadow-2xl max-w-5xl w-full max-h-[90vh] flex flex-col border border-white/10 shadow-cyan-400/20">
        
        {/* Header with Gradient */}
        <div className="relative p-6 border-b border-white/10">
          <div className="absolute -top-20 -left-20 w-40 h-40 rounded-full blur-3xl opacity-30 bg-gradient-to-br from-cyan-400 to-purple-600"></div>
          
          <div className="relative flex justify-between items-start">
            <div className="flex items-start gap-4">
              <div className="relative">
                <div className="absolute inset-0 rounded-full blur-lg opacity-50 bg-gradient-to-br from-cyan-400 to-purple-600"></div>
                <div className="relative w-16 h-16 rounded-full bg-gradient-to-br from-cyan-400 to-purple-600 flex items-center justify-center text-white font-bold text-2xl shadow-lg shadow-cyan-400/30">
                  {contact.name?.charAt(0) || '?'}
                </div>
              </div>
              
              <div>
                <h2 className="text-2xl font-bold text-white mb-1">{contact.name}</h2>
                <p className="text-gray-400">{contact.title}</p>
                <p className="text-sm text-gray-500">{contact.company}</p>
              </div>
            </div>
            
            <button onClick={onClose} className="text-gray-400 hover:text-white p-2 rounded-full hover:bg-white/10 transition">
              <X size={24} />
            </button>
          </div>

          {/* Scores */}
          {(contact.mdcp_score || contact.priority_score) && (
            <div className="flex gap-6 mt-4 pt-4 border-t border-white/10">
              {contact.mdcp_score && (
                <div>
                  <span className="text-xs text-gray-500 uppercase">MDCP</span>
                  <div className="flex items-center gap-2 mt-1">
                    <span className="text-3xl font-bold text-cyan-400">{contact.mdcp_score}</span>
                    {contact.mdcp_tier && (
                      <span className="text-xs px-2 py-1 rounded-full bg-cyan-400/20 text-cyan-400 border border-cyan-400/30">
                        {contact.mdcp_tier}
                      </span>
                    )}
                  </div>
                </div>
              )}
              {contact.priority_score && (
                <div>
                  <span className="text-xs text-gray-500 uppercase">Priority</span>
                  <div className="text-3xl font-bold text-purple-400 mt-1">{contact.priority_score}</div>
                </div>
              )}
              {contact.enrichment_status === 'completed' && (
                <div className="ml-auto flex items-center gap-2 text-green-400">
                  <Sparkles size={16} />
                  <span className="text-sm font-semibold">ENRICHED</span>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {contact.profile_content ? (
            <div className="prose prose-invert max-w-none">
              {formatProfile(contact.profile_content)}
            </div>
          ) : (
            <div className="text-center py-12 bg-white/5 backdrop-blur-sm rounded-xl border border-white/10">
              <p className="text-gray-400 mb-2">No enrichment data yet</p>
              <p className="text-sm text-gray-500">Click "Enrich" to generate intelligence</p>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="border-t border-white/10 p-4 backdrop-blur-sm flex justify-end">
          <button onClick={onClose} className="px-6 py-2 bg-gradient-to-r from-cyan-400 to-purple-500 text-white font-semibold rounded-full hover:shadow-lg hover:shadow-cyan-400/50 transition-all">
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
