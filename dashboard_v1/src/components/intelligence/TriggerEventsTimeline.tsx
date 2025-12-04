interface TriggerEvent {
  text: string;
  category: 'urgent' | 'timing' | 'strategic' | 'other';
}

interface TriggerEventsTimelineProps {
  content: string;
}

export function TriggerEventsTimeline({ content }: TriggerEventsTimelineProps) {
  // Parse bullet points or numbered lists from content
  const events = content
    .split('\n')
    .filter(line => line.trim().match(/^[-•*\d.]/))
    .map(line => {
      const text = line.replace(/^[-•*\d.\s]+/, '').trim();
      
      // Categorize based on keywords
      let category: TriggerEvent['category'] = 'other';
      if (text.toLowerCase().includes('urgent') || text.toLowerCase().includes('immediate')) {
        category = 'urgent';
      } else if (text.toLowerCase().includes('budget') || text.toLowerCase().includes('timing')) {
        category = 'timing';
      } else if (text.toLowerCase().includes('strategic') || text.toLowerCase().includes('growth')) {
        category = 'strategic';
      }
      
      return { text, category };
    });

  const categoryColors = {
    urgent: 'bg-red-500/20 border-red-500 text-red-400',
    timing: 'bg-blue-500/20 border-blue text-blue',
    strategic: 'bg-gold/20 border-gold text-gold',
    other: 'bg-midnight-700 border-midnight-600 text-text-secondary',
  };

  const categoryIcons = {
    urgent: '🔥',
    timing: '⏰',
    strategic: '🎯',
    other: '💡',
  };

  if (events.length === 0) {
    return <p className="text-text-secondary">{content}</p>;
  }

  return (
    <div className="space-y-3">
      {events.map((event, index) => (
        <div
          key={index}
          className={`p-4 rounded-lg border ${categoryColors[event.category]} hover:shadow-lg transition-all`}
        >
          <div className="flex items-start gap-3">
            <span className="text-2xl flex-shrink-0">
              {categoryIcons[event.category]}
            </span>
            <p className="flex-1 leading-relaxed">{event.text}</p>
          </div>
        </div>
      ))}
    </div>
  );
}