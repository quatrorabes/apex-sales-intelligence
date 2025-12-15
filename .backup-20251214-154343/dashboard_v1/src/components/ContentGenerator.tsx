import React, { useState } from 'react';
import { Wand2, Mail, Phone, Linkedin, Copy, Check, Loader } from 'lucide-react';
import { getContact, getContacts, enrichContact, getStats } from '@/config/api';

interface ContentGeneratorProps {
  contactId: number;
  contactName: string;
}

export const ContentGenerator: React.FC<ContentGeneratorProps> = ({ contactId, contactName }) => {
  const [activeTab, setActiveTab] = useState<'email' | 'linkedin' | 'call'>('email');
  const [generatedContent, setGeneratedContent] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [copied, setCopied] = useState(false);

  const handleGenerate = async () => {
    setIsGenerating(true);
    try {
      let content = '';
      
      switch (activeTab) {
        case 'email':
          // TODO: Email generation endpoint - not yet implemented in v2 API
          // // TODO: Email generation endpoint - not yet implemented in v2 API
          // const emailResult = await apiClient.generateEmail(contactId, {});
          content = emailResult.content || emailResult.email || 'Email generated successfully';
          break;
        case 'linkedin':
          // TODO: LinkedIn generation endpoint - not yet implemented in v2 API
          // // TODO: LinkedIn generation endpoint - not yet implemented in v2 API
          // const linkedInResult = await apiClient.generateLinkedInMessage(contactId, {});
          content = linkedInResult.content || linkedInResult.message || 'LinkedIn message generated';
          break;
        case 'call':
          // TODO: Call script generation endpoint - not yet implemented in v2 API
          // // TODO: Call script generation endpoint - not yet implemented in v2 API
          // const callResult = await apiClient.generateCallScript(contactId, {});
          content = callResult.content || callResult.script || 'Call script generated';
          break;
      }
      
      setGeneratedContent(content);
    } catch (error) {
      console.error('Generation failed:', error);
      setGeneratedContent('Failed to generate content. Please try again.');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(generatedContent);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const tabs = [
    { id: 'email', label: 'Email', icon: Mail },
    { id: 'linkedin', label: 'LinkedIn', icon: Linkedin },
    { id: 'call', label: 'Call Script', icon: Phone },
  ];

  return (
    <div className="bg-white rounded-lg border">
      <div className="border-b px-4 py-3">
        <h3 className="font-semibold text-gray-900">AI Content Generator</h3>
        <p className="text-sm text-gray-600 mt-1">Generate personalized outreach for {contactName}</p>
      </div>

      {/* Tabs */}
      <div className="flex border-b">
        {tabs.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            onClick={() => setActiveTab(id as any)}
            className={`flex items-center gap-2 px-4 py-3 text-sm font-medium transition ${
              activeTab === id
                ? 'text-blue-600 border-b-2 border-blue-600 bg-blue-50'
                : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
            }`}
          >
            <Icon className="h-4 w-4" />
            {label}
          </button>
        ))}
      </div>

      <div className="p-4 space-y-4">
        {/* Generate Button */}
        <button
          onClick={handleGenerate}
          disabled={isGenerating}
          className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg hover:from-purple-700 hover:to-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition font-medium"
        >
          {isGenerating ? (
            <>
              <Loader className="h-5 w-5 animate-spin" />
              Generating...
            </>
          ) : (
            <>
              <Wand2 className="h-5 w-5" />
              Generate {tabs.find(t => t.id === activeTab)?.label}
            </>
          )}
        </button>

        {/* Generated Content */}
        {generatedContent && (
          <div className="relative">
            <div className="bg-gray-50 rounded-lg p-4 border min-h-[200px] whitespace-pre-wrap font-mono text-sm">
              {generatedContent}
            </div>
            <button
              onClick={handleCopy}
              className="absolute top-2 right-2 p-2 bg-white border rounded-lg hover:bg-gray-50 transition"
              title="Copy to clipboard"
            >
              {copied ? (
                <Check className="h-4 w-4 text-green-600" />
              ) : (
                <Copy className="h-4 w-4 text-gray-600" />
              )}
            </button>
          </div>
        )}
      </div>
    </div>
  );
};
