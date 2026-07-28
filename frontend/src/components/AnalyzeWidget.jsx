import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Shield, ShieldAlert, CheckCircle2, AlertTriangle, Loader2, Play, Eye } from 'lucide-react';
import { analyzePrivacy } from '../services/privacyApi';

const StatusBadge = ({ status }) => {
  const styles = {
    low: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
    medium: "bg-amber-500/10 text-amber-400 border-amber-500/20",
    high: "bg-orange-500/10 text-orange-400 border-orange-500/20",
    critical: "bg-red-500/10 text-red-400 border-red-500/20",
    LOW: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
    MEDIUM: "bg-amber-500/10 text-amber-400 border-amber-500/20",
    HIGH: "bg-orange-500/10 text-orange-400 border-orange-500/20",
    CRITICAL: "bg-red-500/10 text-red-400 border-red-500/20",
    ALLOW: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
    WARN: "bg-amber-500/10 text-amber-400 border-amber-500/20",
    MODIFY: "bg-orange-500/10 text-orange-400 border-orange-500/20",
    BLOCK: "bg-red-500/10 text-red-400 border-red-500/20",
  };
  return (
    <span className={`px-2.5 py-0.5 rounded-full text-xs font-semibold border uppercase tracking-wider ${styles[status] || "bg-slate-500/10 text-slate-400 border-slate-500/20"}`}>
      {status}
    </span>
  );
};

export default function AnalyzeWidget() {
  const [prompt, setPrompt] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState(null);

  const handleAnalyze = async () => {
    if (!prompt.trim()) return;

    setLoading(true);
    setError('');
    setResult(null);

    try {
      const data = await analyzePrivacy(prompt);
      if (data && data.status) {
        setResult(data);
      } else {
        setError('Unable to retrieve results from Privacy Agent.');
      }
    } catch (err) {
      setError(err.message || 'Unable to connect to Privacy Agent.');
    } finally {
      setLoading(false);
    }
  };

  const entityCount = result?.findings?.reduce((sum, f) => sum + (f.entity_count || 0), 0) || 0;

  return (
    <div className="bg-gradient-to-br from-[#1a0c0e]/90 to-[#120809]/80 backdrop-blur-xl border border-[#2A0B12] rounded-2xl shadow-lg p-6 hover:border-[#DC143C]/20 transition-all duration-300">
      <div className="flex items-center gap-3 mb-4">
        <div className="p-2.5 rounded-xl bg-[#2A0B12] text-[#FF4D6D] border border-[#4B0F18] shadow-[0_0_10px_rgba(255,77,109,0.1)]">
          <Eye className="h-5 w-5" />
        </div>
        <h2 className="text-xl font-bold text-white tracking-tight">Privacy Agent Playground</h2>
      </div>

      <div className="mb-4">
        <textarea
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="Enter text to scan for PII..."
          className="w-full h-24 bg-[#120809] border border-[#4B0F18] rounded-xl p-4 text-white placeholder:text-slate-500 focus:outline-none focus:border-[#DC143C] focus:ring-1 focus:ring-[#DC143C] transition-all resize-none"
        />
      </div>

      <div className="flex justify-between items-center mb-6">
        {error ? (
          <div className="text-sm text-red-400 flex items-center gap-2">
            <AlertTriangle className="h-4 w-4" /> {error}
          </div>
        ) : (
          <div className="text-xs text-slate-400">Scan text for PII and privacy risks</div>
        )}
        <button
          onClick={handleAnalyze}
          disabled={loading || !prompt.trim()}
          className="flex items-center gap-2 bg-[#DC143C] hover:bg-[#FF4D6D] disabled:opacity-50 disabled:hover:bg-[#DC143C] text-white px-6 py-2 rounded-lg font-medium text-sm transition-all shadow-[0_0_15px_rgba(220,20,60,0.4)]"
        >
          {loading ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" /> Analyzing...
            </>
          ) : (
            <>
              <Play className="h-4 w-4 fill-current" /> Analyze
            </>
          )}
        </button>
      </div>

      {result && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="border-t border-[#2A0B12] pt-6 mt-4 space-y-6"
        >
          {result.errors && result.errors.length > 0 && (
            <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-3 text-sm text-red-400 flex items-center gap-2">
              <AlertTriangle className="h-4 w-4" />
              {result.errors.join(' ')}
            </div>
          )}

          {/* Top Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-[#120809] border border-[#2A0B12] p-3 rounded-xl">
              <div className="text-xs text-slate-500 uppercase font-semibold mb-1">Risk Score</div>
              <div className={`text-2xl font-bold ${result?.risk_score >= 75 ? 'text-red-400' : result?.risk_score >= 50 ? 'text-orange-400' : result?.risk_score >= 25 ? 'text-amber-400' : 'text-emerald-400'}`}>
                {result?.risk_score}
              </div>
            </div>
            <div className="bg-[#120809] border border-[#2A0B12] p-3 rounded-xl flex flex-col justify-center items-start">
              <div className="text-xs text-slate-500 uppercase font-semibold mb-2">Risk Level</div>
              <StatusBadge status={result?.risk_level} />
            </div>
            <div className="bg-[#120809] border border-[#2A0B12] p-3 rounded-xl flex flex-col justify-center items-start">
              <div className="text-xs text-slate-500 uppercase font-semibold mb-2">Agent</div>
              <span className="text-sm font-medium text-white">{result?.agent}</span>
            </div>
            <div className="bg-[#120809] border border-[#2A0B12] p-3 rounded-xl">
              <div className="text-xs text-slate-500 uppercase font-semibold mb-1">Entities Found</div>
              <div className="text-2xl font-bold text-white">{entityCount}</div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <div>
                <h4 className="text-xs text-slate-500 uppercase tracking-wider font-semibold mb-1">Agent</h4>
                <p className="text-sm text-white font-medium">{result?.agent}</p>
              </div>
              <div>
                <h4 className="text-xs text-slate-500 uppercase tracking-wider font-semibold mb-1">Request ID</h4>
                <p className="text-sm text-slate-300 font-mono">{result?.request_id}</p>
              </div>
              <div>
                <h4 className="text-xs text-slate-500 uppercase tracking-wider font-semibold mb-1">Status</h4>
                <StatusBadge status={result?.status} />
              </div>
            </div>

            <div className="space-y-4">
              {result?.recommendations && result.recommendations.length > 0 && (
                <div>
                  <h4 className="text-xs text-emerald-400 uppercase tracking-wider font-semibold mb-1">Recommendations</h4>
                  <ul className="space-y-1 text-sm text-slate-300">
                    {result.recommendations.map((rec, idx) => (
                      <li key={idx} className="flex items-start gap-2 text-xs bg-[#2A0B12]/30 p-2 rounded border border-[#4B0F18]/30">
                        <CheckCircle2 className="h-3 w-3 text-emerald-400 mt-0.5 shrink-0" />
                        {rec}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {result?.findings && result.findings.length > 0 && (
                <div>
                  <h4 className="text-xs text-slate-500 uppercase tracking-wider font-semibold mb-1">Findings</h4>
                  <ul className="space-y-2">
                    {result.findings.map((finding, idx) => (
                      <li key={idx} className="flex flex-col gap-1 text-xs text-slate-300 bg-[#2A0B12]/30 p-3 rounded border border-[#4B0F18]/30">
                        <div className="flex justify-between">
                          <span className="font-semibold text-white flex items-center gap-1">
                            <AlertTriangle className="h-3 w-3 text-orange-400 mt-0.5 shrink-0" />
                            {finding.category}
                          </span>
                          <div className="flex gap-2">
                            <span className="text-slate-400">Severity: <StatusBadge status={finding.severity} /></span>
                          </div>
                        </div>
                        <div className="text-slate-400 mt-1">{finding.description}</div>
                        <div className="text-slate-400 mt-1">
                          <span className="font-semibold text-slate-300">Entity Count: </span>
                          {finding.entity_count}
                        </div>
                        <div className="text-slate-400 mt-1">
                          <span className="font-semibold text-slate-300">Remediation: </span>
                          {finding.remediation}
                        </div>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        </motion.div>
      )}
    </div>
  );
}
