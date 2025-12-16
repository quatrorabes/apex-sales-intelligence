import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { apiClient } from '../config/api';
import { Phone, User, Building, TrendingUp, AlertCircle, CheckCircle } from 'lucide-react';

interface CallAssistantData {
  contact_id: string;
  name: string;
  firstname: string;
  lastname: string;
  company: string;
  title: string;
  phone: string;
  score: number;
  tier: string;
  profile_context: string;
  call_script_1: string | null;
  call_script_2: string | null;
  call_script_3: string | null;
  has_scripts: boolean;
}

export default function CallAssistantPage() {
  const { id } = useParams<{ id: string }>();
  const [data, setData] = useState<CallAssistantData | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeScript, setActiveScript] = useState(1);
  const [callStarted, setCallStarted] = useState(false);
  const [callNotes, setCallNotes] = useState('');

  useEffect(() => {
    loadCallAssistantData();
  }, [id]);

  const loadCallAssistantData = async () => {
    try {
      const response = await apiClient.get(`/api/contacts/${id}/call-assistant-data`);
      setData(response.data);
    } catch (err) {
      console.error('Error loading call assistant data:', err);
    } finally {
      setLoading(false);
    }
  };

  const startCall = () => {
    setCallStarted(true);
  };

  const endCall = () => {
    setCallStarted(false);
    // Save call notes logic here
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="flex items-center justify-center h-screen">
        <AlertCircle className="h-12 w-12 text-red-500" />
        <p className="ml-3 text-lg text-gray-700">Failed to load call assistant data</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Top Bar */}
      <div className={`${callStarted ? 'bg-green-600' : 'bg-indigo-600'} text-white p-4`}>
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <div className="flex items-center space-x-4">
            <Phone className={`h-6 w-6 ${callStarted ? 'animate-pulse' : ''}`} />
            <div>
              <h1 className="text-2xl font-bold">{data.name}</h1>
              <p className="text-sm opacity-90">{data.title} at {data.company}</p>
            </div>
          </div>
          
          <div className="flex items-center space-x-4">
            <div className="text-right">
              <div className="text-sm opacity-75">APEX Score</div>
              <div className="text-3xl font-bold">{data.score}</div>
            </div>
            
            {!callStarted ? (
              <button
                onClick={startCall}
                className="bg-white text-indigo-600 px-6 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors"
              >
                Start Call
              </button>
            ) : (
              <button
                onClick={endCall}
                className="bg-red-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-red-700 transition-colors"
              >
                End Call
              </button>
            )}
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto p-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left: Contact Intel */}
          <div className="lg:col-span-1 space-y-6">
            {/* Contact Card */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <User className="h-5 w-5 mr-2 text-indigo-600" />
                Contact Info
              </h2>
              <div className="space-y-3 text-sm">
                <div>
                  <span className="text-gray-500">Phone:</span>
                  <span className="ml-2 font-medium">{data.phone || 'Not available'}</span>
                </div>
                <div>
                  <span className="text-gray-500">Company:</span>
                  <span className="ml-2 font-medium">{data.company}</span>
                </div>
                <div>
                  <span className="text-gray-500">Tier:</span>
                  <span className={`ml-2 px-2 py-1 rounded text-xs font-medium ${
                    data.tier === 'HIGH' ? 'bg-green-100 text-green-800' :
                    data.tier === 'MEDIUM' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-gray-100 text-gray-800'
                  }`}>
                    {data.tier}
                  </span>
                </div>
              </div>
            </div>

            {/* Intelligence */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <TrendingUp className="h-5 w-5 mr-2 text-indigo-600" />
                Intelligence Brief
              </h2>
              <p className="text-sm text-gray-700 whitespace-pre-wrap">
                {data.profile_context || 'No enrichment data available'}
              </p>
            </div>

            {/* Call Notes */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Call Notes</h2>
              <textarea
                value={callNotes}
                onChange={(e) => setCallNotes(e.target.value)}
                className="w-full h-32 border rounded-lg p-3 text-sm focus:ring-2 focus:ring-indigo-500"
                placeholder="Take notes during the call..."
              />
            </div>
          </div>

          {/* Right: Call Scripts */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow">
              {/* Script Tabs */}
              <div className="border-b border-gray-200">
                <div className="flex space-x-1 p-2">
                  {[1, 2, 3].map((num) => (
                    <button
                      key={num}
                      onClick={() => setActiveScript(num)}
                      className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                        activeScript === num
                          ? 'bg-indigo-600 text-white'
                          : 'text-gray-600 hover:bg-gray-100'
                      }`}
                    >
                      Script {num}
                    </button>
                  ))}
                </div>
              </div>

              {/* Script Content */}
              <div className="p-6">
                {data.has_scripts ? (
                  <div className="prose max-w-none">
                    <pre className="whitespace-pre-wrap font-sans text-sm leading-relaxed">
                      {activeScript === 1 && data.call_script_1}
                      {activeScript === 2 && data.call_script_2}
                      {activeScript === 3 && data.call_script_3}
                    </pre>
                  </div>
                ) : (
                  <div className="text-center py-12">
                    <AlertCircle className="mx-auto h-12 w-12 text-gray-400 mb-3" />
                    <h3 className="text-lg font-medium text-gray-900 mb-2">No Call Scripts Generated</h3>
                    <p className="text-gray-500 mb-4">Generate call scripts from the contact detail page first.</p>
                    <button
                      onClick={() => window.history.back()}
                      className="text-indigo-600 hover:text-indigo-700 font-medium"
                    >
                      ← Back to Contact
                    </button>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
