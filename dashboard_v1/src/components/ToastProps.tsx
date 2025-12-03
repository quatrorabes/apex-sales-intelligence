import React, { useEffect } from 'react';
import { CheckCircle2, AlertCircle, XCircle, X } from 'lucide-react';

export interface Toast {
  id: string;
  type: 'success' | 'error' | 'info' | 'warning';
  title: string;
  message: string;
}

interface ToastProps {
  toast: Toast;
  onClose: (id: string) => void;
}

export const ToastComponent: React.FC<ToastProps> = ({ toast, onClose }) => {
  useEffect(() => {
    const timer = setTimeout(() => onClose(toast.id), 5000);
    return () => clearTimeout(timer);
  }, [toast.id, onClose]);

  const icons = {
    success: <CheckCircle2 className="h-5 w-5 text-green-500" />,
    error: <XCircle className="h-5 w-5 text-red-500" />,
    warning: <AlertCircle className="h-5 w-5 text-amber-500" />,
    info: <AlertCircle className="h-5 w-5 text-blue-500" />,
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-4 min-w-[300px] border flex gap-3">
      {icons[toast.type]}
      <div className="flex-1">
        <p className="font-semibold text-gray-900">{toast.title}</p>
        <p className="text-sm text-gray-600 mt-1">{toast.message}</p>
      </div>
      <button onClick={() => onClose(toast.id)} className="text-gray-400 hover:text-gray-600">
        <X className="h-4 w-4" />
      </button>
    </div>
  );
};
