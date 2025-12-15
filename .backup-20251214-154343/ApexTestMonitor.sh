#!/bin/bash
# ApexTestMonitor.sh - Test api.py/app.tsx + btop (50/50 2x2, safe/local)
# Usage: Save to ~/projects/apex/, chmod +x, ./ApexTestMonitor.sh
# Detach: Ctrl-b d | Reattach/Kill: tmux a -t ApexTest | tmux kill-s ApexTest

SESSION="ApexTest"
cd ~/projects/apex  # Your root (api.py + dashboard_v1) [memory:42]

# Cleanup
tmux kill-session -t $SESSION 2>/dev/null
pkill -f "python.*api.py" 2>/dev/null  # Stop local api.py
pkill -f "npm.*dev.*dashboard" 2>/dev/null  # Stop local frontend

tmux new-session -d -s $SESSION 'echo "Top-Left: Railway Prod Logs (watch)"'
tmux split-window -h -p 50 'btop'  # Top-Right: CPU/Mem [memory:40]
tmux select-pane -t 0
tmux split-window -v -p 50 'echo "Bottom-Left: api.py Local Test\nsleep 2 && venv/bin/python api.py'  # Bottom-Left: api.py (assumes venv) [memory:43]
tmux select-pane -t 1
tmux split-window -v -p 50 'echo "Bottom-Right: Dashboard_v1 Dev\nsleep 2 && cd dashboard_v1 && npm run dev'  # Bottom-Right: app.tsx dev [memory:59][memory:60]

tmux select-layout tiled  # 50/50/50/50 even
tmux select-pane -t 0
tmux send-keys 'watch -n 5 "railway logs --service apex-intelligence-production | tail -20"' Enter  # Prod-safe logs
tmux set -g pane-border-style fg=green,bg=black
tmux set -g pane-active-border-style fg=yellow

tmux attach -t $SESSION
echo "✅ ApexTest live: Test api.py/app.tsx safely | Prod Apex untouched | Ctrl-b d to detach"
