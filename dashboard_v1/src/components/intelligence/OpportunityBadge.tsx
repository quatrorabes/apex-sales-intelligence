interface OpportunityBadgeProps {
  level: 'HIGH' | 'MEDIUM' | 'LOW' | string;
  size?: 'sm' | 'md' | 'lg';
}

export function OpportunityBadge({ level, size = 'md' }: OpportunityBadgeProps) {
  const levelUpper = level?.toUpperCase();
  
  const colors = {
    HIGH: 'bg-gold/20 text-gold border-gold',
    MEDIUM: 'bg-blue/20 text-blue border-blue',
    LOW: 'bg-midnight-700 text-text-tertiary border-midnight-600',
  };

  const sizes = {
    sm: 'text-xs px-2 py-1',
    md: 'text-sm px-3 py-1.5',
    lg: 'text-base px-4 py-2',
  };

  const colorClass = colors[levelUpper as keyof typeof colors] || colors.LOW;
  const sizeClass = sizes[size];

  return (
    <span className={`inline-flex items-center gap-2 rounded-full border font-semibold ${colorClass} ${sizeClass}`}>
      {levelUpper === 'HIGH' && '🔥'}
      {levelUpper === 'MEDIUM' && '⚡'}
      {levelUpper === 'LOW' && '💤'}
      {level}
    </span>
  );
}