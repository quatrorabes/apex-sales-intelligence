import React, { useState, useEffect } from 'react';
import { Search, Filter, Download, RefreshCw, User, Mail, Phone, Linkedin, TrendingUp } from 'lucide-react';
import { apiClient } from '../utils/api';
import { Contact } from '../types';
import { PersonaBadge } from './PersonaBadge';
import ContactDetailModal from './ContactDetailModal';

export const ContactsBoard: React.FC = () => {
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [sortField, setSortField] = useState<'name' | 'mdcp_score' | 'priority_score'>('mdcp_score');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('desc');
  const [selectedContactId, setSelectedContactId] = useState<number | null>(null);

  useEffect(() => {
    loadContacts();
  }, []);

  const loadContacts = async () => {
    setLoading(true);
    try {
      const response = await apiClient.getContacts({ limit: 100 });
      setContacts(response.contacts || []);
    } catch (error) {
      console.error('Failed to load contacts:', error);
    } finally {
      setLoading(false);
    }
  };

  const filteredContacts = contacts
    .filter(contact => {
      const query = searchQuery.toLowerCase();
      return (
        contact.name?.toLowerCase().includes(query) ||
        contact.company?.toLowerCase().includes(query) ||
        contact.email?.toLowerCase().includes(query)
      );
    })
    .sort((a, b) => {
      const aVal = a[sortField] || 0;
      const bVal = b[sortField] || 0;
      if (sortField === 'name') {
        return sortDirection === 'asc'
          ? String(aVal).localeCompare(String(bVal))
          : String(bVal).localeCompare(String(aVal));
      }
      return sortDirection === 'asc' ? Number(aVal) - Number(bVal) : Number(bVal) - Number(aVal);
    });

  const getTierColor = (tier?: string) => {
    switch (tier?.toLowerCase()) {
      case 'hot': return 'bg-red-100 text-red-800 border-red-300';
      case 'warm': return 'bg-orange-100 text-orange-800 border-orange-300';
      case 'qualified': return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      case 'nurture': return 'bg-blue-100 text-blue-800 border-blue-300';
      case 'cold': return 'bg-gray-100 text-gray-800 border-gray-300';
      default: return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };

  const getAvatarColor = (name: string) => {
    const colors = [
      'bg-blue-500', 'bg-purple-500', 'bg-green-500',
      'bg-orange-500', 'bg-pink-500', 'bg-indigo-500'
    ];
    return colors[name?.charCodeAt(0) % colors.length || 0];
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  return (
    <div className="p-6">
      {/* Header & Search */}
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-900">All Contacts</h1>
        <div className="flex gap-2">
          <button onClick={loadContacts} className="p-2 hover:bg-gray-100 rounded-lg" title="Refresh">
            <RefreshCw size={20} className="text-gray-600" />
          </button>
          <button className="p-2 hover:bg-gray-100 rounded-lg" title="Filter">
            <Filter size={20} className="text-gray-600" />
          </button>
          <button className="p-2 hover:bg-gray-100 rounded-lg" title="Export">
            <Download size={20} className="text-gray-600" />
          </button>
        </div>
      </div>

      {/* Search */}
      <div className="relative mb-4">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Search contacts by name, company, or email..."
          className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
      </div>

      {/* Sort Controls */}
      <div className="flex items-center gap-4 mb-6">
        <span className="text-sm text-gray-600">Sort by:</span>
        <select
          value={sortField}
          onChange={(e) => setSortField(e.target.value as any)}
          className="text-sm border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
        >
          <option value="mdcp_score">MDCP Score</option>
          <option value="priority_score">Priority Score</option>
          <option value="name">Name</option>
        </select>
        <button
          onClick={() => setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc')}
          className="text-sm text-blue-600 hover:text-blue-800 font-medium"
        >
          {sortDirection === 'asc' ? '↑ Ascending' : '↓ Descending'}
        </button>
        <span className="ml-auto text-sm text-gray-500">{filteredContacts.length} contacts</span>
      </div>

      {/* Contacts Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredContacts.map((contact) => (
          <div
            key={contact.id}
            onClick={() => setSelectedContactId(contact.id)}
            className="border border-gray-200 rounded-lg p-4 hover:shadow-lg hover:border-blue-300 transition cursor-pointer bg-white"
          >
            {/* Contact Header */}
            <div className="flex items-start gap-3 mb-3">
              <div className={`w-10 h-10 rounded-full ${getAvatarColor(contact.name)} flex items-center justify-center text-white font-bold`}>
                {contact.name?.charAt(0)?.toUpperCase() || '?'}
              </div>
              <div className="flex-1 min-w-0">
                <h3 className="font-semibold text-gray-900 truncate">{contact.name}</h3>
                <p className="text-sm text-gray-600 truncate">{contact.title}</p>
                <p className="text-sm text-gray-500 truncate">{contact.company}</p>
              </div>
            </div>

            {/* Persona Badge */}
            {contact.persona && (
              <div className="mb-3">
                <PersonaBadge persona={contact.persona} confidence={contact.persona_confidence_score} size="sm" />
              </div>
            )}

            {/* Scores */}
            <div className="flex gap-3 mb-3">
              <div className="flex-1 bg-gray-50 rounded p-2">
                <p className="text-xs text-indigo-600 font-medium">MDCP</p>
                <p className="text-lg font-bold text-gray-900">{contact.mdcp_score || 0}</p>
                {contact.mdcp_tier && (
                  <span className={`text-xs px-1.5 py-0.5 rounded border ${getTierColor(contact.mdcp_tier)}`}>
                    {contact.mdcp_tier}
                  </span>
                )}
              </div>
              <div className="flex-1 bg-gray-50 rounded p-2">
                <p className="text-xs text-purple-600 font-medium">Priority</p>
                <p className="text-lg font-bold text-gray-900">{contact.priority_score || 0}</p>
                {contact.urgency_level && (
                  <span className="text-xs text-gray-500">{contact.urgency_level}</span>
                )}
              </div>
            </div>

            {/* Contact Methods */}
            <div className="flex gap-1 pt-2 border-t border-gray-100">
              {contact.email && (
                <a
                  href={`mailto:${contact.email}`}
                  onClick={(e) => e.stopPropagation()}
                  className="p-1.5 hover:bg-blue-50 rounded text-blue-600 transition"
                  title="Email"
                >
                  <Mail size={16} />
                </a>
              )}
              {contact.phone && (
                <a
                  href={`tel:${contact.phone}`}
                  onClick={(e) => e.stopPropagation()}
                  className="p-1.5 hover:bg-green-50 rounded text-green-600 transition"
                  title="Call"
                >
                  <Phone size={16} />
                </a>
              )}
              {contact.linkedin_url && (
                <a
                  href={contact.linkedin_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  onClick={(e) => e.stopPropagation()}
                  className="p-1.5 hover:bg-blue-50 rounded text-blue-600 transition"
                  title="LinkedIn"
                >
                  <Linkedin size={16} />
                </a>
              )}
            </div>
          </div>
        ))}
      </div>

      {filteredContacts.length === 0 && (
        <div className="text-center py-12 bg-gray-50 rounded-lg">
          <p className="text-gray-500">No contacts found</p>
        </div>
      )}

      {/* THE MODAL - THIS WAS MISSING! */}
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
