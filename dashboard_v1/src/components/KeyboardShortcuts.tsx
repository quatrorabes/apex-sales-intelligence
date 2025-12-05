import { X, Command } from 'lucide-react';

const shortcuts = [
    { category: 'Navigation', items: [
        { keys: ['⌘', 'K'], description: 'Global search' },
        { keys: ['⌘', 'J'], description: 'AI Command Bar' },
        { keys: ['G', 'H'], description: 'Go to Home' },
        { keys: ['G', 'C'], description: 'Go to Contacts' },
        { keys: ['G', 'A'], description: 'Go to Analytics' },
        { keys: ['G', 'Q'], description: 'Go to Cold Call Queue' },
    ]},
    { category: 'Actions', items: [
        { keys: ['E'], description: 'Enrich selected contact' },
        { keys: ['S'], description: 'Score selected contact' },
        { keys: ['N'], description: 'New contact' },
        { keys: ['⌘', 'Enter'], description: 'Execute action' },
    ]},
    { category: 'Views', items: [
        { keys: ['1'], description: 'Table view' },
        { keys: ['2'], description: 'Card view' },
        { keys: ['3'], description: 'Kanban view' },
        { keys: ['4'], description: 'Compact view' },
    ]},
    { category: 'General', items: [
        { keys: ['?'], description: 'Show shortcuts' },
        { keys: ['Esc'], description: 'Close modal' },
        { keys: ['↑', '↓'], description: 'Navigate list' },
        { keys: ['Enter'], description: 'Select/Open' },
    ]},
];

export default function KeyboardShortcuts({ isOpen, onClose }: { isOpen: boolean; onClose: () => void }) {
    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50" onClick={onClose}>
            <div 
                className="bg-[#1e2228] rounded-2xl border border-gray-700 w-full max-w-2xl mx-4 overflow-hidden"
                onClick={e => e.stopPropagation()}
            >
                <div className="px-6 py-4 border-b border-gray-800 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <Command size={20} className="text-purple-400" />
                        <h2 className="text-lg font-semibold text-white">Keyboard Shortcuts</h2>
                    </div>
                    <button onClick={onClose} className="text-gray-500 hover:text-white">
                        <X size={20} />
                    </button>
                </div>
                
                <div className="p-6 grid md:grid-cols-2 gap-6 max-h-[60vh] overflow-y-auto">
                    {shortcuts.map(section => (
                        <div key={section.category}>
                            <h3 className="text-sm font-medium text-gray-400 mb-3">{section.category}</h3>
                            <div className="space-y-2">
                                {section.items.map((item, i) => (
                                    <div key={i} className="flex items-center justify-between">
                                        <span className="text-gray-300 text-sm">{item.description}</span>
                                        <div className="flex items-center gap-1">
                                            {item.keys.map((key, j) => (
                                                <kbd 
                                                    key={j}
                                                    className="px-2 py-1 bg-[#0f1114] border border-gray-700 rounded text-xs text-gray-400 min-w-[24px] text-center"
                                                >
                                                    {key}
                                                </kbd>
                                            ))}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    ))}
                </div>
                
                <div className="px-6 py-3 bg-[#0f1114] border-t border-gray-800 text-center text-sm text-gray-500">
                    Press <kbd className="px-1.5 py-0.5 bg-gray-800 rounded text-xs">?</kbd> anytime to show this panel
                </div>
            </div>
        </div>
    );
}
