import React, { useState, useEffect } from 'react';
import { Loader, AlertCircle, CheckCircle2, Sparkles, Brain, RefreshCw, Download, Upload } from 'lucide-react';
import { Contact } from '../types';
import { getContact, getContacts, enrichContact, getStats } from '@/config/api';
import { PersonaBadge } from './PersonaBadge';
import { BatchProgress } from './BatchProgress';
import ContactDetailModal from './ContactDetailModal';

interface EnrichmentJob {
  id: string;
  contactId: number;
  contactName: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress?: number;
  error?: string;
  startTime: Date;
  endTime?: Date;
}

export const ContactEnrichmentView: React.FC = () => {
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [selectedContactId, setSelectedContactId] = useState<number | null>(null);
  const [selectedContacts, setSelectedContacts] = useState<Set<number>>(new Set());
  const [enrichmentJobs, setEnrichmentJobs] = useState<EnrichmentJob[]>([]);
  const [loading, setLoading] = useState(true);
  const [enriching, setEnriching] = useState(false);
  const [filter, setFilter] = useState<'all' | 'pending' | 'completed' | 'failed'>('all');

  useEffect(() => {
    loadContacts();
  }, []);

  const loadContacts = async () => {
    setLoading(true);
    try {
      const data = await getContacts(200); const response = { contacts: data.contacts, total: data.total };
      setContacts(response.contacts || []);
    } catch (error) {
      console.error('Failed to load contacts:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectContact = (contactId: number) => {
    const newSelected = new Set(selectedContacts);
    if (newSelected.has(contactId)) {
      newSelected.delete(contactId);
    } else {
      newSelected.add(contactId);
    }
    setSelectedContacts(newSelected);
  };

  const handleSelectAll = () => {
    if (selectedContacts.size === filteredContacts.length) {
      setSelectedContacts(new Set());
    } else {
      setSelectedContacts(new Set(filteredContacts.map(c => c.id)));
    }
  };

  const handleBatchEnrich = async () => {
    if (selectedContacts.size === 0) return;

    setEnriching(true);
    const contactsToEnrich = Array.from(selectedContacts);
    
    // Create jobs
    const jobs: EnrichmentJob[] = contactsToEnrich.map(id => {
      const contact = contacts.find(c => c.id === id);
      return {
        id: `job-${id}-${Date.now()}`,
        contactId: id,
        contactName: contact?.name || 'Unknown',
        status: 'pending',
        startTime: new Date(),
      };
    });
    
    setEnrichmentJobs(jobs);

    // Process sequentially
    for (let i = 0; i < jobs.length; i++) {
      const job = jobs[i];
      
      // Update to processing
      setEnrichmentJobs(prev => 
        prev.map(j => j.id === job.id ? { ...j, status: 'processing', progress: 0 } : j)
      );

      try {
        await enrichContact(job.contactId);
        
        // Update to completed
        setEnrichmentJobs(prev => 
          prev.map(j => j.id === job.id ? { 
            ...j, 
            status: 'completed', 
            progress: 100,
            endTime: new Date() 
          } : j)
        );
      } catch (error: any) {
        console.error(`Enrichment failed for contact ${job.contactId}:`, error);
        
        // Update to failed
        setEnrichmentJobs(prev => 
          prev.map(j => j.id === job.id ? { 
            ...j, 
            status: 'failed',
            error: error.message || 'Enrichment failed',
            endTime: new Date()
          } : j)
        );
      }
    }

    setEnriching(false);
    setSelectedContacts(new Set());
    await loadContacts();
  };

  const filteredContacts = contacts.filter(contact => {
    if (filter === 'all') return true;
    return contact.enrichment_status === filter;
  });

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle2 className="h-5 w-5 text-green-600" />;
      case 'processing':
        return <Loader className="h-5 w-5 animate-spin text-blue-600" />;
      case 'failed':
        return <AlertCircle className="h-5 w-5 text-red-600" />;
      default:
        return <div className="h-5 w-5 rounded-full border-2 border-gray-300" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'bg-green-100 text-green-800';
      case 'pending': return 'bg-yellow-100 text-yellow-800';
      case 'failed': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const stats = {
    total: contacts.length,
    completed: contacts.filter(c => c.enrichment_status === 'completed').length,
    pending: contacts.filter(c => c.enrichment_status === 'pending').length,
    failed: contacts.filter(c => c.enrichment_status === 'failed').length,
  };

  const activeJobs = enrichmentJobs.filter(j => j.status === 'processing');
  const completedJobsCount = enrichmentJobs.filter(j => j.status === 'completed').length;

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <Loader className="h-12 w-12 animate-spin text-blue-600" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-blue-600 rounded-lg p-6 text-white">
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <Sparkles className="h-8 w-8" />
              <h1 className="text-2xl font-bold">Contact Enrichment</h1>
            </div>
            <p className="text-purple-100">
              AI-powered profile enrichment and persona classification
            </p>
          </div>
          <button
            onClick={loadContacts}
            className="p-3 bg-white/20 hover:bg-white/30 rounded-lg transition"
          >
            <RefreshCw className="h-6 w-6" />
          </button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white border rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <Brain className="h-5 w-5 text-blue-600" />
            <span className="text-sm font-medium text-gray-600">Total Contacts</span>
          </div>
          <p className="text-2xl font-bold text-gray-900">{stats.total}</p>
        </div>
        <div className="bg-white border rounded-lg p-4 cursor-pointer hover:shadow-md transition" onClick={() => setFilter('completed')}>
          <div className="flex items-center gap-2 mb-2">
            <CheckCircle2 className="h-5 w-5 text-green-600" />
            <span className="text-sm font-medium text-gray-600">Enriched</span>
          </div>
          <p className="text-2xl font-bold text-gray-900">{stats.completed}</p>
          <p className="text-xs text-gray-500 mt-1">
            {Math.round((stats.completed / stats.total) * 100)}% complete
          </p>
        </div>
        <div className="bg-white border rounded-lg p-4 cursor-pointer hover:shadow-md transition" onClick={() => setFilter('pending')}>
          <div className="flex items-center gap-2 mb-2">
            <Loader className="h-5 w-5 text-yellow-600" />
            <span className="text-sm font-medium text-gray-600">Pending</span>
          </div>
          <p className="text-2xl font-bold text-gray-900">{stats.pending}</p>
        </div>
        <div className="bg-white border rounded-lg p-4 cursor-pointer hover:shadow-md transition" onClick={() => setFilter('failed')}>
          <div className="flex items-center gap-2 mb-2">
            <AlertCircle className="h-5 w-5 text-red-600" />
            <span className="text-sm font-medium text-gray-600">Failed</span>
          </div>
          <p className="text-2xl font-bold text-gray-900">{stats.failed}</p>
        </div>
      </div>

      {/* Filter & Actions */}
      <div className="bg-white border rounded-lg p-4">
        <div className="flex items-center justify-between flex-wrap gap-4">
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium text-gray-700">Filter:</span>
            <div className="flex gap-2">
              {(['all', 'pending', 'completed', 'failed'] as const).map(f => (
                <button
                  key={f}
                  onClick={() => setFilter(f)}
                  className={`px-3 py-1.5 rounded-lg text-sm font-medium transition ${
                    filter === f
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  {f.charAt(0).toUpperCase() + f.slice(1)}
                </button>
              ))}
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-600">
              {selectedContacts.size} selected
            </span>
            <button
              onClick={handleBatchEnrich}
              disabled={selectedContacts.size === 0 || enriching}
              className="flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition"
            >
              <Sparkles className="h-4 w-4" />
              Enrich Selected ({selectedContacts.size})
            </button>
          </div>
        </div>
      </div>

      {/* Enrichment Jobs Progress */}
      {enrichmentJobs.length > 0 && (
        <div className="bg-white border rounded-lg p-4">
          <h3 className="font-semibold text-gray-900 mb-4">
            Enrichment Progress ({completedJobsCount}/{enrichmentJobs.length})
          </h3>
          <div className="space-y-2 max-h-48 overflow-y-auto">
            {enrichmentJobs.map(job => (
              <div key={job.id} className="flex items-center gap-3 p-2 bg-gray-50 rounded">
                {getStatusIcon(job.status)}
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 truncate">
                    {job.contactName}
                  </p>
                  {job.error && (
                    <p className="text-xs text-red-600">{job.error}</p>
                  )}
                </div>
                <span className={`px-2 py-0.5 rounded text-xs font-semibold ${getStatusColor(job.status)}`}>
                  {job.status}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Contacts Table */}
      <div className="bg-white border rounded-lg overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 border-b">
              <tr>
                <th className="px-4 py-3 text-left">
                  <input
                    type="checkbox"
                    checked={selectedContacts.size === filteredContacts.length && filteredContacts.length > 0}
                    onChange={handleSelectAll}
                    className="rounded border-gray-300 text-blue-600 focus:ring-2 focus:ring-blue-500"
                  />
                </th>
                <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">Name</th>
                <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">Company</th>
                <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">Persona</th>
                <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">MDCP</th>
                <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">Status</th>
                <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">Last Enriched</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {filteredContacts.map(contact => (
                <tr key={contact.id} onClick={() => setSelectedContactId(contact.id)} className="cursor-pointer hover:bg-gray-50 transition">
                  <td className="px-4 py-3">
                    <input
                      type="checkbox"
                      checked={selectedContacts.has(contact.id)}
                      onChange={(e) => {
                        e.stopPropagation();
                        handleSelectContact(contact.id);
                      }}
                      onClick={(e) => e.stopPropagation()}
                      className="rounded border-gray-300 text-blue-600 focus:ring-2 focus:ring-blue-500"
                    />
                  </td>
                  <td className="px-4 py-3">
                    <div className="font-medium text-gray-900">{contact.name}</div>
                    <div className="text-sm text-gray-500">{contact.title}</div>
                  </td>
                  <td className="px-4 py-3 text-gray-900">{contact.company}</td>
                  <td className="px-4 py-3">
                    {contact.persona ? (
                      <PersonaBadge
                        persona={contact.persona}
                        confidence={contact.personaconfidence}
                        size="sm"
                      />
                    ) : (
                      <span className="text-sm text-gray-400">Not classified</span>
                    )}
                  </td>
                  <td className="px-4 py-3">
                    <span className="text-lg font-bold text-purple-600">
                      {contact.mdcp_score || 0}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <span className={`inline-flex items-center gap-1 px-2 py-1 rounded text-xs font-semibold ${getStatusColor(contact.enrichment_status)}`}>
                      {contact.enrichment_status === 'completed' && <CheckCircle2 className="h-3 w-3" />}
                      {contact.enrichment_status === 'failed' && <AlertCircle className="h-3 w-3" />}
                      {contact.enrichment_status}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-600">
                    {contact.enrichment_date
                      ? new Date(contact.enrichment_date).toLocaleDateString()
                      : 'Never'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {filteredContacts.length === 0 && (
          <div className="text-center py-12">
            <AlertCircle className="h-12 w-12 text-gray-400 mx-auto mb-3" />
            <p className="text-gray-500">No contacts found with current filter</p>
            <button
              onClick={() => setFilter('all')}
              className="mt-3 text-blue-600 hover:underline"
            >
              View all contacts
            </button>
          </div>
        )}
      </div>

      {/* Batch Progress Overlay */}
      {activeJobs.length > 0 && (
        <BatchProgress
          current={completedJobsCount}
          total={enrichmentJobs.length}
          operation="Enriching Contacts"
        />
      )}
    </div>
  );
};

export default ContactEnrichmentView;
