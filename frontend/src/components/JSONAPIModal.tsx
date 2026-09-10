import React, { useState } from 'react';
import { Code2, X, Copy, Check } from 'lucide-react';
import { RiskAssessmentResponse } from '../types';

interface JSONAPIModalProps {
  isOpen: boolean;
  onClose: () => void;
  assessment: RiskAssessmentResponse | null;
}

export const JSONAPIModal: React.FC<JSONAPIModalProps> = ({ isOpen, onClose, assessment }) => {
  const [copied, setCopied] = useState(false);

  if (!isOpen) return null;

  const jsonString = JSON.stringify(assessment || { message: 'VARUNA Marine Intelligence API Response' }, null, 2);

  const handleCopy = () => {
    navigator.clipboard.writeText(jsonString);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-ocean-950/80 backdrop-blur-md">
      <div className="relative w-full max-w-3xl bg-ocean-900 border border-cyan-500/30 rounded-3xl p-6 space-y-4 text-slate-100 shadow-2xl overflow-hidden">
        <div className="flex items-center justify-between border-b border-slate-800 pb-3">
          <div className="flex items-center space-x-2">
            <Code2 className="w-5 h-5 text-cyan-400" />
            <h3 className="font-bold text-base text-slate-100 font-mono">VARUNA REST API Payload (/api/risk)</h3>
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={handleCopy}
              className="px-3 py-1.5 rounded-lg bg-cyan-950 text-cyan-300 border border-cyan-700/60 text-xs font-mono font-bold flex items-center space-x-1.5 hover:bg-cyan-900 transition-all"
            >
              {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
              <span>{copied ? 'Copied!' : 'Copy JSON'}</span>
            </button>
            <button onClick={onClose} className="text-slate-400 hover:text-slate-100">
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        <pre className="p-4 rounded-2xl bg-ocean-950 border border-slate-800 text-xs font-mono text-cyan-300 overflow-x-auto max-h-[500px] scrollbar-thin">
          {jsonString}
        </pre>
      </div>
    </div>
  );
};
