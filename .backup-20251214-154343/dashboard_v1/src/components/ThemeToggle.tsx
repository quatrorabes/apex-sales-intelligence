import { useState, useEffect } from 'react';
import { Sun, Moon, Monitor } from 'lucide-react';

type Theme = 'dark' | 'light' | 'system';

export default function ThemeToggle() {
    const [theme, setTheme] = useState<Theme>(() => {
        return (localStorage.getItem('apex-theme') as Theme) || 'dark';
    });

    useEffect(() => {
        const root = document.documentElement;
        
        if (theme === 'system') {
            const isDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
            root.classList.toggle('light-mode', !isDark);
        } else {
            root.classList.toggle('light-mode', theme === 'light');
        }
        
        localStorage.setItem('apex-theme', theme);
    }, [theme]);

    const themes: { id: Theme; icon: React.ReactNode; label: string }[] = [
        { id: 'dark', icon: <Moon size={16} />, label: 'Dark' },
        { id: 'light', icon: <Sun size={16} />, label: 'Light' },
        { id: 'system', icon: <Monitor size={16} />, label: 'System' },
    ];

    return (
        <div className="flex items-center gap-1 bg-[#0f1114] rounded-lg p-1">
            {themes.map(t => (
                <button
                    key={t.id}
                    onClick={() => setTheme(t.id)}
                    className={`p-2 rounded-md transition ${
                        theme === t.id 
                            ? 'bg-purple-600 text-white' 
                            : 'text-gray-400 hover:text-white'
                    }`}
                    title={t.label}
                >
                    {t.icon}
                </button>
            ))}
        </div>
    );
}
