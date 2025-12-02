// ContactDetailPage.tsx - Sleeker design with colored actions
import React from 'react';
import { Phone, Mail, Linkedin, Globe, MessageSquare, Calendar, Target, TrendingUp } from 'lucide-react';

export function ContactDetailPage({ contact }: { contact: any }) {
  return (
    <div className="max-w-6xl mx-auto p-6">
      {/* Header with Visual Score */}
      <div className="bg-gradient-to-r from-slate-900 to-slate-800 rounded-xl p-6 mb-6">
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-3xl font-bold text-white">{contact.name}</h1>
            <p className="text-lg text-slate-400 mt-1">{contact.title} at {contact.company}</p>
            
            {/* Score Pills */}
            <div className="flex gap-3 mt-4">
              <ScorePill 
                label="Priority" 
                score={contact.priority_score ?? 0} 
                color={getScoreColor(contact.priority_score)}
                icon={<Target className="w-4 h-4" />}
              />
              <ScorePill 
                label="Role Fit" 
                score={contact.rss_score ?? 0} 
                color="blue"
                icon={<User className="w-4 h-4" />}
              />
              <ScorePill 
                label="Data" 
                score={contact.mdcp_score ?? 0} 
                color="green"
                icon={<TrendingUp className="w-4 h-4" />}
              />
              {contact.cold_score && (
                <ScorePill 
                  label="Cold" 
                  score={contact.cold_score} 
                  color="cyan"
                  icon={<Phone className="w-4 h-4" />}
                />
              )}
            </div>
          </div>

          {/* Visual Score Ring */}
          <div className="relative">
            <svg className="w-32 h-32 transform -rotate-90">
              <circle
                cx="64"
                cy="64"
                r="56"
                stroke="currentColor"
                strokeWidth="12"
                fill="none"
                className="text-slate-700"
              />
              <circle
                cx="64"
                cy="64"
                r="56"
                stroke="currentColor"
                strokeWidth="12"
                fill="none"
                strokeDasharray={`${2 * Math.PI * 56}`}
                strokeDashoffset={`${2 * Math.PI * 56 * (1 - (contact.priority_score ?? 0) / 100)}`}
                className={`${getScoreGradient(contact.priority_score)} transition-all duration-500`}
              />
            </svg>
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="text-center">
                <div className="text-3xl font-bold text-white">{contact.priority_score}</div>
                <div className="text-xs text-slate-400">Priority</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Action Bar with Colored Icons */}
      <div className="bg-slate-900 rounded-xl p-4 mb-6">
        <div className="flex gap-2 overflow-x-auto">
          <ActionButton 
            icon={<Phone />} 
            label="Call" 
            onClick={() => {}} 
            color="bg-green-600 hover:bg-green-700"
            subtext={contact.phone}
          />
          <ActionButton 
            icon={<Mail />} 
            label="Email" 
            onClick={() => {}} 
            color="bg-blue-600 hover:bg-blue-700"
            subtext="Send sequence"
          />
          <ActionButton 
            icon={<Linkedin />} 
            label="LinkedIn" 
            onClick={() => {}} 
            color="bg-blue-500 hover:bg-blue-600"
            subtext="View profile"
          />
          <ActionButton 
            icon={<MessageSquare />} 
            label="SMS" 
            onClick={() => {}} 
            color="bg-purple-600 hover:bg-purple-700"
            subtext="Text message"
          />
          <ActionButton 
            icon={<Calendar />} 
            label="Schedule" 
            onClick={() => {}} 
            color="bg-orange-600 hover:bg-orange-700"
            subtext="Book meeting"
          />
        </div>
      </div>

      {/* Cold Calling Section (if applicable) */}
      {contact.cold_score && (
        <div className="bg-gradient-to-r from-cyan-900/20 to-blue-900/20 rounded-xl p-6 border border-cyan-800/50">
          <h3 className="text-lg font-bold text-white mb-3 flex items-center gap-2">
            <Phone className="w-5 h-5 text-cyan-400" />
            Cold Outreach Strategy
          </h3>
          <div className="grid grid-cols-3 gap-4">
            <div className="bg-slate-900/50 rounded-lg p-3">
              <div className="text-2xl font-bold text-cyan-400">{contact.cold_score}</div>
              <div className="text-sm text-slate-400">Cold Score</div>
            </div>
            <div className="bg-slate-900/50 rounded-lg p-3">
              <div className="text-sm font-medium text-white">{contact.best_time_to_call || "Tue/Thu 10-11am"}</div>
              <div className="text-sm text-slate-400">Best Time</div>
            </div>
            <div className="bg-slate-900/50 rounded-lg p-3">
              <div className="text-sm font-medium text-white">{contact.recommended_approach}</div>
              <div className="text-sm text-slate-400">Approach</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// Helper Components
function ScorePill({ label, score, color, icon }: any) {
  const colors = {
    blue: 'bg-blue-900/30 text-blue-400 border-blue-800',
    green: 'bg-green-900/30 text-green-400 border-green-800',
    cyan: 'bg-cyan-900/30 text-cyan-400 border-cyan-800',
    orange: 'bg-orange-900/30 text-orange-400 border-orange-800',
    red: 'bg-red-900/30 text-red-400 border-red-800'
  };

  return (
    <div className={`px-3 py-2 rounded-lg border ${colors[color as keyof typeof colors]}`}>
      <div className="flex items-center gap-2">
        {icon}
        <div>
          <div className="text-xl font-bold">{score}</div>
          <div className="text-xs opacity-80">{label}</div>
        </div>
      </div>
    </div>
  );
}

function ActionButton({ icon, label, onClick, color, subtext }: any) {
  return (
    <button
      onClick={onClick}
      className={`${color} text-white rounded-lg px-4 py-3 transition-colors min-w-[120px]`}
    >
      <div className="flex flex-col items-center gap-1">
        <div className="w-6 h-6">{icon}</div>
        <div className="text-sm font-medium">{label}</div>
        {subtext && <div className="text-xs opacity-80">{subtext}</div>}
      </div>
    </button>
  );
}
