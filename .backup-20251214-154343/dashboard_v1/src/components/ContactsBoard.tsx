import React, { useState, useEffect } from 'react';
import { Search, RefreshCw, Filter, Download, TrendingUp } from 'lucide-react';
import { getContact, getContacts, enrichContact, getStats } from '@/config/api';
import { Contact } from '../types';
import ContactDetailModal from './ContactDetailModal';
import { useTheme } from '../theme/ThemeProvider';

export const ContactsBoard: React.FC = () => {
  const { theme } = useTheme();
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedContactId, setSelectedContactId] = useState<number | null>(null);

  useEffect(() => {
    loadContacts();
  }, []);

  const loadContacts = async () => {
    setLoading(true);
    try {
      const data = await getContacts(100); const response = { contacts: data.contacts, total: data.total };
      setContacts(response.contacts || []);
    } catch (error) {
      console.error('Failed to load contacts:', error);
    } finally {
      setLoading(false);
    }
  };

  const filteredContacts = contacts.filter(c => {
    const q = searchQuery.toLowerCase();
    return c.name?.toLowerCase().includes(q) || c.company?.toLowerCase().includes(q);
  });

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-[#050816]">
        <TrendingUp className="text-[#22D3EE] animate-pulse" size={48} />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#050816] p-6">
      {/* Header */}
      <div className="bg-[#0B1120] backdrop-blur-sm border border-[#94A3B8]/35 shadow-[0_18px_45px_rgba(15,23,42,0.6)] rounded-xl p-5 mb-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-xl font-semibold text-[#F9FAFB]">All Contacts</h1>
            <p className="text-sm text-[#64748B] mt-1">{filteredContacts.length} prospects</p>
          </div>
          <div className="flex gap-2">
            <button onClick={loadContacts} className="border border-[#22D3EE] text-[#22D3EE] bg-transparent hover:bg-[#22D3EE]/10 rounded-lg px-3 py-2 transition-all">
              <RefreshCw size={16} />
            </button>
          </div>
        </div>

        {/* Search */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-[#64748B]" size={18} />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search prospects..."
            className="w-full pl-10 pr-4 py-2.5 rounded-lg border bg-[#0B1120] border-[#94A3B8]/35 text-[#F9FAFB] placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-[#22D3EE] text-sm"
          />
        </div>
      </div>

      {/* Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredContacts.map((contact) => (
          <div
            key={contact.id}
            onClick={() => setSelectedContactId(contact.id)}
            className="bg-[#0B1120] backdrop-blur-sm border border-[#94A3B8]/35 shadow-[0_18px_45px_rgba(15,23,42,0.6)] hover:shadow-[0_20px_50px_rgba(15,23,42,0.7)] hover:border-[#94A3B8]/50 rounded-xl p-4 cursor-pointer transition-all duration-200"
          >
            {/* Avatar & Info */}
            <div className="flex items-start gap-3 mb-3">
              <div className="w-11 h-11 rounded-lg bg-[#22D3EE] flex items-center justify-center text-[#050816] font-bold text-lg">
                {contact.name?.charAt(0) || '?'}
              </div>
              <div className="flex-1 min-w-0">
                <h3 className="font-medium text-[#F9FAFB] truncate text-sm">{contact.name}</h3>
                <p className="text-xs text-[#CBD5E1] truncate">{contact.title}</p>
                <p className="text-xs text-[#64748B] truncate">{contact.company}</p>
              </div>
            </div>

            {/* Scores */}
            <div className="flex gap-2">
              <div className="flex-1 bg-[#1E293B] rounded-lg p-2.5">
                <p className="text-xs text-[#22D3EE] font-medium mb-1">MDCP</p>
                <p className="text-lg font-bold text-[#F9FAFB]">{contact.mdcp_score || 0}</p>
              </div>
              <div className="flex-1 bg-[#1E293B] rounded-lg p-2.5">
                <p className="text-xs text-[#6366F1] font-medium mb-1">Priority</p>
                <p className="text-lg font-bold text-[#F9FAFB]">{contact.priority_score || 0}</p>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Modal */}
      {selectedContactId && (
        <ContactDetailModal
          contactId={selectedContactId}
          onClose={() => setSelectedContactId(null)}
        />
      )}
    </div>
  );
};

export default ContactsBoard;
