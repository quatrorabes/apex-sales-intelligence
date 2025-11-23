
import React, { useState, useEffect } from 'react'

interface Contact {
  id: number
  name: string
  email: string
  company?: string
  title?: string
  phone?: string
  linkedin_url?: string
  enriched: boolean
  opportunity_score?: number
  persona_name?: string
  enrichment_data?: any
}

interface DashboardMetrics {
  total_contacts: number
  enriched: number
  open_rate: number
  sent: number
  errors: number
}

const App = () => {
  // State Management
  const [contacts, setContacts] = useState<Contact[]>([])
  const [selectedContact, setSelectedContact] = useState<Contact | null>(null)
  const [metrics, setMetrics] = useState<DashboardMetrics>({
    total_contacts: 0,
    enriched: 0,
    open_rate: 0,
    sent: 0,
    errors: 0
  })
  const [loading, setLoading] = useState(false)
  const [generatedContent, setGeneratedContent] = useState<any>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [activeTab, setActiveTab] = useState<'studio' | 'cadence' | 'activity'>('studio')

  // Load data on mount
  useEffect(() => {
    loadContacts()
  }, [])

  // Load contacts from backend
  const loadContacts = async () => {
    try {
      setLoading(true)
      const res = await fetch('http://localhost:3000/api/contacts')
      const data = await res.json()
      setContacts(data.contacts || [])
      
      // Calculate metrics
      const enrichedCount = (data.contacts || []).filter((c: Contact) => c.enriched).length
      setMetrics({
        total_contacts: data.contacts?.length || 0,
        enriched: enrichedCount,
        open_rate: enrichedCount > 0 ? (enrichedCount / (data.contacts?.length || 1)) * 100 : 0,
        sent: 0,
        errors: 0
      })
      
      setLoading(false)
    } catch (err) {
      console.error('Failed to load contacts:', err)
      setLoading(false)
    }
  }

  // Enrich contact with AI
  const handleEnrich = async (contactId: number) => {
    try {
      setLoading(true)
      const res = await fetch(`http://localhost:3000/api/contacts/${id}/deep-enrich`, {
      method: 'POST'
      })        headers: { 'Content-Type': 'application/json' }
      })
      const data = await res.json()
      alert(data.message || 'Enrichment started!')
      await loadContacts()
    } catch (err) {
      alert('Enrichment failed: ' + err)
    } finally {
      setLoading(false)
    }
  }

  // Generate call script
  const handleCallScript = async (contactId: number) => {
    try {
      setLoading(true)
      const res = await fetch(`http://localhost:3000/api/v1/outreach/contacts/${contactId}/call-scripts`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      })
      const data = await res.json()
      setGeneratedContent({ type: 'call_script', data })
    } catch (err) {
      alert('Failed to generate call script: ' + err)
    } finally {
      setLoading(false)
    }
  }

  // Generate email
  const handleEmail = async (contactId: number) => {
    try {
      setLoading(true)
      const res = await fetch(`http://localhost:3000/api/v1/outreach/contacts/${contactId}/emails`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      })
      const data = await res.json()
      setGeneratedContent({ type: 'email', data })
    } catch (err) {
      alert('Failed to generate email: ' + err)
    } finally {
      setLoading(false)
    }
  }

  // Filter contacts by search
  const filteredContacts = contacts.filter(c => 
    c.name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    c.email?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    c.company?.toLowerCase().includes(searchQuery.toLowerCase())
  )

  return (
    <div className="min-h-screen bg-slate-900 text-white">
      {/* Header */}
      <header className="bg-slate-800 border-b border-slate-700 px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-white">APEX Sales Intelligence</h1>
            <p className="text-sm text-slate-400 mt-1">AI-powered outreach platform | Backend: http://localhost:3000</p>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-sm text-slate-400">sales</span>
            <button className="p-2 hover:bg-slate-700 rounded">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 12h14M12 5l7 7-7 7" />
              </svg>
            </button>
          </div>
        </div>
      </header>

      {/* Metrics Cards */}
      <div className="grid grid-cols-5 gap-4 p-6">
        <div className="bg-slate-800 rounded-lg p-6 border-l-4 border-blue-500">
          <p className="text-slate-400 text-sm mb-2">Total Contacts</p>
          <p className="text-3xl font-bold">{metrics.total_contacts}</p>
        </div>
        <div className="bg-slate-800 rounded-lg p-6 border-l-4 border-green-500">
          <p className="text-slate-400 text-sm mb-2">Enriched</p>
          <p className="text-3xl font-bold">{metrics.enriched}</p>
        </div>
        <div className="bg-slate-800 rounded-lg p-6 border-l-4 border-yellow-500">
          <p className="text-slate-400 text-sm mb-2">Open Rate</p>
          <p className="text-3xl font-bold">{metrics.open_rate.toFixed(1)}%</p>
        </div>
        <div className="bg-slate-800 rounded-lg p-6 border-l-4 border-orange-500">
          <p className="text-slate-400 text-sm mb-2">Sent</p>
          <p className="text-3xl font-bold">{metrics.sent}</p>
        </div>
        <div className="bg-slate-800 rounded-lg p-6 border-l-4 border-red-500">
          <p className="text-slate-400 text-sm mb-2">Errors</p>
          <p className="text-3xl font-bold">{metrics.errors}</p>
        </div>
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-[400px_1fr] gap-6 p-6">
        {/* Contacts Sidebar */}
        <div className="bg-slate-800 rounded-lg overflow-hidden">
          <div className="p-4 border-b border-slate-700">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold">Contacts ({filteredContacts.length})</h2>
              <button className="text-slate-400 hover:text-white">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z" />
                </svg>
              </button>
            </div>
            <input
              type="text"
              placeholder="Search by name, email, company..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-slate-700 border border-slate-600 rounded px-3 py-2 text-sm text-white placeholder-slate-400 focus:outline-none focus:border-blue-500"
            />
          </div>

          <div className="overflow-y-auto max-h-[600px]">
            {filteredContacts.map(contact => (
              <div
                key={contact.id}
                onClick={() => setSelectedContact(contact)}
                className={`p-4 border-b border-slate-700 cursor-pointer transition-colors ${
                  selectedContact?.id === contact.id 
                    ? 'bg-slate-700 border-l-4 border-l-blue-500' 
                    : 'hover:bg-slate-750'
                }`}
              >
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-slate-600 flex items-center justify-center text-lg font-bold">
                    {contact.name?.charAt(0)?.toUpperCase() || '?'}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <h3 className="font-semibold truncate">{contact.name}</h3>
                      {contact.enriched ? (
                        <span className="text-xs bg-green-500/20 text-green-400 px-2 py-1 rounded">✓ Enriched</span>
                      ) : (
                        <span className="text-xs bg-slate-700 text-slate-400 px-2 py-1 rounded">Pending</span>
                      )}
                    </div>
                    <p className="text-sm text-slate-400 truncate">{contact.title || '—'}</p>
                    <p className="text-xs text-slate-500 truncate">{contact.company || 'No company'}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Detail Panel */}
        <div className="bg-slate-800 rounded-lg p-6">
          {selectedContact ? (
            <>
              {/* Contact Header */}
              <div className="flex items-start justify-between mb-6">
                <div>
                  <h2 className="text-2xl font-bold mb-2">{selectedContact.name}</h2>
                  <p className="text-slate-400">{selectedContact.title} · {selectedContact.company}</p>
                </div>
                {selectedContact.enriched && (
                  <span className="px-3 py-1 bg-green-500/20 text-green-400 rounded-full text-sm font-medium">
                    ✓ AI Enriched
                  </span>
                )}
              </div>

              {/* Gradient Divider */}
              <div className="h-1 bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 rounded-full mb-6"></div>

              {/* Contact Info Grid */}
              <div className="grid grid-cols-2 gap-4 mb-6 bg-slate-700/50 p-4 rounded-lg">
                <div>
                  <label className="text-xs text-slate-400 uppercase font-semibold">Email</label>
                  <p className="text-sm mt-1">{selectedContact.email || '—'}</p>
                </div>
                <div>
                  <label className="text-xs text-slate-400 uppercase font-semibold">Phone</label>
                  <p className="text-sm mt-1">{selectedContact.phone || '—'}</p>
                </div>
                <div>
                  <label className="text-xs text-slate-400 uppercase font-semibold">LinkedIn</label>
                  <p className="text-sm mt-1">
                    {selectedContact.linkedin_url ? (
                      <a href={selectedContact.linkedin_url} target="_blank" rel="noreferrer" className="text-blue-400 hover:underline">
                        View Profile →
                      </a>
                    ) : '—'}
                  </p>
                </div>
                <div>
                  <label className="text-xs text-slate-400 uppercase font-semibold">SQL</label>
                  <p className="text-sm mt-1">{selectedContact.persona_name || '—'}</p>
                </div>
              </div>

              {/* Tabs */}
              <div className="flex gap-4 mb-6 border-b border-slate-700">
                <button
                  onClick={() => setActiveTab('studio')}
                  className={`pb-3 px-2 font-medium transition-colors ${
                    activeTab === 'studio' 
                      ? 'text-white border-b-2 border-blue-500' 
                      : 'text-slate-400 hover:text-white'
                  }`}
                >
                  Outreach Studio
                </button>
                <button
                  onClick={() => setActiveTab('cadence')}
                  className={`pb-3 px-2 font-medium transition-colors ${
                    activeTab === 'cadence' 
                      ? 'text-white border-b-2 border-blue-500' 
                      : 'text-slate-400 hover:text-white'
                  }`}
                >
                  Cadence
                </button>
                <button
                  onClick={() => setActiveTab('activity')}
                  className={`pb-3 px-2 font-medium transition-colors ${
                    activeTab === 'activity' 
                      ? 'text-white border-b-2 border-blue-500' 
                      : 'text-slate-400 hover:text-white'
                  }`}
                >
                  Activity & Feedback
                </button>
              </div>

              {/* Tab Content */}
              {activeTab === 'studio' && (
                <>
                  <div className="mb-6">
                    <h3 className="text-sm font-semibold uppercase text-slate-400 mb-3">Generate Outreach Assets</h3>
                    <div className="flex flex-wrap gap-3">
                      {!selectedContact.enriched && (
                        <button
                          onClick={() => handleEnrich(selectedContact.id)}
                          disabled={loading}
                          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-600 rounded-lg font-medium transition-colors flex items-center gap-2"
                        >
                          <span>✨</span>
                          {loading ? 'Enriching...' : 'Enrich with AI'}
                        </button>
                      )}
                      <button
                        onClick={() => handleCallScript(selectedContact.id)}
                        disabled={loading}
                        className="px-4 py-2 bg-green-600 hover:bg-green-700 disabled:bg-slate-600 rounded-lg font-medium transition-colors flex items-center gap-2"
                      >
                        <span>📞</span>
                        Call Script
                      </button>
                      <button
                        onClick={() => handleEmail(selectedContact.id)}
                        disabled={loading}
                        className="px-4 py-2 bg-purple-600 hover:bg-purple-700 disabled:bg-slate-600 rounded-lg font-medium transition-colors flex items-center gap-2"
                      >
                        <span>✉️</span>
                        Email
                      </button>
                    </div>
                  </div>

                  {/* Generated Content */}
                  {generatedContent && (
                    <div className="bg-slate-700/50 rounded-lg p-4 mt-4">
                      <h4 className="font-semibold mb-3">Generated Content</h4>
                      <pre className="text-sm bg-slate-900 p-4 rounded overflow-x-auto">
                        {JSON.stringify(generatedContent.data, null, 2)}
                      </pre>
                    </div>
                  )}
                </>
              )}

              {activeTab === 'cadence' && (
                <div className="space-y-4">
                  <div className="flex gap-3 flex-wrap">
                    <button className="px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded-lg">Cold Emails</button>
                    <button className="px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded-lg">Warm Emails</button>
                    <button className="px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded-lg">Cold Coll Scripts</button>
                    <button className="px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded-lg">Warm Linkindin</button>
                  </div>
                  <p className="text-slate-400 text-sm">Configure automated outreach cadences for this contact</p>
                </div>
              )}

              {activeTab === 'activity' && (
                <div className="space-y-4">
                  <p className="text-slate-400">Capture what worked, what, or what you'd like future drafts to evolve...</p>
                  <textarea 
                    className="w-full bg-slate-700 border border-slate-600 rounded-lg p-3 text-white placeholder-slate-400 focus:outline-none focus:border-blue-500"
                    rows={4}
                    placeholder="Enter feedback..."
                  />
                  <button className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg font-medium">
                    Save feedback (hook into your backend)
                  </button>
                </div>
              )}
            </>
          ) : (
            <div className="flex items-center justify-center h-full text-slate-400">
              <p className="text-lg">👈 Select a contact to view details</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

