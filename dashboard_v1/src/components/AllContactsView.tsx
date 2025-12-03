import { useState, useEffect } from 'react';
import { Search, RefreshCw, Mail, Phone, Linkedin, Filter, Download } from 'lucide-react';
import ContactDetailModal from './ContactDetailModal';

interface Contact {
  id: number;
  name: string;
  email: string;
  company: string;
  title: string;
  phone?: string;
  linkedin_url?: string;
  mdcp_score?: number;
  priority_score?: number;
  enrichment_status?: string;
  mdcp_tier?: string;
}

export default function AllContactsView() {
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [filteredContacts, setFilteredContacts] = useState<Contact[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedContactId, setSelectedContactId] = useState<number | null>(null);
  const [sortBy, setSortBy] = useState<'mdcp_score' | 'name' | 'company'>('mdcp_score');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchContacts();
  }, []);

  useEffect(() => {
    filterAndSortContacts();
  }, [contacts, searchQuery, sortBy, sortOrder]);

  const fetchContacts = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:8000/api/contacts?limit=200');
      const data = await response.json();
      setContacts(data.contacts || []);
    } catch (error) {
      console.error('Failed to fetch contacts:', error);
    } finally {
      setLoading(false);
    }
  };

  const filterAndSortContacts = () => {
    let filtered = contacts;

    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(c =>
        c.name?.toLowerCase().includes(query) ||
        c.company?.toLowerCase().includes(query) ||
        c.email?.toLowerCase().includes(query)
      );
    }

    filtered = [...filtered].sort((a, b) => {
      let aVal: string | number = sortBy === 'name' ? (a.name || '') : 
                                  sortBy === 'company' ? (a.company || '') : 
                                  (a.mdcp_score || 0);
      let bVal: string | number = sortBy === 'name' ? (b.name || '') : 
                                  sortBy === 'company' ? (b.company || '') : 
                                  (b.mdcp_score || 0);

      if (typeof aVal === 'string') {
        return sortOrder === 'asc' 
          ? aVal.localeCompare(bVal as string)
          : (bVal as string).localeCompare(aVal);
      }
      return sortOrder === 'asc' ? (aVal as number) - (bVal as number) : (bVal as number) - (aVal as number);
    });

    setFilteredContacts(filtered);
  };

  const handleCardClick = (contactId: number) => {
    console.log('Card clicked, contact ID:', contactId);
    setSelectedContactId(contactId);
  };

  const getAvatarColor = (name: string) => {
    const colors = [
      'from-blue-500 to-blue-600',
      'from-purple-500 to-purple-600',
      'from-green-500 to-green-600',
      'from-orange-500 to-orange-600',
      'from-pink-500 to-pink-600',
      'from-indigo-500 to-indigo-600',
    ];
    const index = name?.charCodeAt(0) % colors.length || 0;
    return colors[index];
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading contacts...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-900">All Contacts</h1>
        <div className="flex gap-2">
          <button 
            onClick={fetchContacts}
            className="p-2 hover:bg-gray-100 rounded-lg transition"
            title="Refresh"
          >
            <RefreshCw size={20} className="text-gray-600" />
          </button>
          <button className="p-2 hover:bg-gray-100 rounded-lg transition" title="Filter">
            <Filter size={20} className="text-gray-600" />
          </button>
          <button className="p-2 hover:bg-gray-100 rounded-lg transition" title="Export">
            <Download size={20} className="text-gray-600" />
          </button>
        </div>
      </div>

      {/* Search */}
      <div className="relative mb-4">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
        <input
          type="text"
          placeholder="Search contacts by name, company, or email..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full pl-10 pr-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent bg-gray-50"
        />
      </div>

      {/* Sort Controls */}
      <div className="flex items-center gap-4 mb-6">
        <span className="text-sm text-gray-600">Sort by:</span>
        <select
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value as 'mdcp_score' | 'name' | 'company')}
          className="px-3 py-1.5 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-indigo-500"
        >
          <option value="mdcp_score">MDCP Score</option>
          <option value="name">Name</option>
          <option value="company">Company</option>
        </select>
        <button
          onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
          className="text-indigo-600 text-sm font-medium hover:text-indigo-800"
        >
          {sortOrder === 'desc' ? '↓ Descending' : '↑ Ascending'}
        </button>
        <span className="ml-auto text-sm text-gray-500">{filteredContacts.length} contacts</span>
      </div>

      {/* Contact Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredContacts.map(contact => (
          <div
            key={contact.id}
            onClick={() => handleCardClick(contact.id)}
            className="bg-white rounded-xl border border-gray-200 p-5 hover:shadow-lg hover:border-indigo-300 transition-all cursor-pointer group"
          >
            {/* Avatar and Name */}
            <div className="flex items-start gap-4 mb-4">
              <div className={`w-12 h-12 rounded-full bg-gradient-to-br ${getAvatarColor(contact.name)} flex items-center justify-center text-white font-bold text-lg shadow-md`}>
                {contact.name?.charAt(0) || '?'}
              </div>
              <div className="flex-1 min-w-0">
                <h3 className="font-semibold text-gray-900 truncate group-hover:text-indigo-600 transition">
                  {contact.name}
                </h3>
                <p className="text-sm text-gray-600 truncate">{contact.title}</p>
                <p className="text-sm text-gray-500 truncate">{contact.company}</p>
              </div>
            </div>

            {/* Scores */}
            <div className="flex gap-3 mb-4">
              <div className="flex-1 bg-gray-50 rounded-lg p-3">
                <p className="text-xs font-medium text-indigo-600 mb-1">MDCP</p>
                <p className="text-xl font-bold text-gray-900">{contact.mdcp_score || 0}</p>
              </div>
              <div className="flex-1 bg-gray-50 rounded-lg p-3">
                <p className="text-xs font-medium text-purple-600 mb-1">Priority</p>
                <p className="text-xl font-bold text-gray-900">{contact.priority_score || 0}</p>
              </div>
            </div>

            {/* Action Icons */}
            <div className="flex gap-2 pt-2 border-t border-gray-100">
              {contact.email && (
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    window.location.href = `mailto:${contact.email}`;
                  }}
                  className="p-2 text-gray-500 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg transition"
                  title={contact.email}
                >
                  <Mail size={18} />
                </button>
              )}
              {contact.phone && (
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    window.location.href = `tel:${contact.phone}`;
                  }}
                  className="p-2 text-gray-500 hover:text-green-600 hover:bg-green-50 rounded-lg transition"
                  title={contact.phone}
                >
                  <Phone size={18} />
                </button>
              )}
              {contact.linkedin_url && (
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    window.open(contact.linkedin_url, '_blank');
                  }}
                  className="p-2 text-gray-500 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition"
                  title="View LinkedIn"
                >
                  <Linkedin size={18} />
                </button>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Empty State */}
      {filteredContacts.length === 0 && !loading && (
        <div className="text-center py-12 bg-gray-50 rounded-xl">
          <p className="text-gray-500 text-lg">No contacts found</p>
          <p className="text-gray-400 text-sm mt-2">Try adjusting your search</p>
        </div>
      )}

      {/* MODAL - This is the key part! */}
      {selectedContactId && (
        <ContactDetailModal
          contactId={selectedContactId}
          onClose={() => setSelectedContactId(null)}
        />
      )}
    </div>
  );
}
