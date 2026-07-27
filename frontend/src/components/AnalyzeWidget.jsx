import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Shield, ShieldAlert, CheckCircle2, AlertTriangle, Loader2, Play } from 'lucide-react';
import { analyzePrompt } from '../services/securityApi';

const StatusBadge = ({ status }) => {
  const styles = {
    ALLOW: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
    WARN: "bg-amber-500/10 text-amber-400 border-amber-500/20",
    MODIFY: "bg-orange-500/10 text-orange-400 border-orange-500/20",
    BLOCK: "bg-red-500/10 text-red-400 border-red-500/20",
    Low: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
    Medium: "bg-amber-500/10 text-amber-400 border-amber-500/20",
    High: "bg-orange-500/10 text-orange-400 border-orange-500/20",
    Critical: "bg-red-500/10 text-red-400 border-red-500/20",
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
      const data = await analyzePrompt(prompt);
      if (data && data.status === 'SUCCESS' && data.result) {
        setResult(data.result);
      } else {
        setError(data?.message || 'Unable to connect to Security Agent.');
      }
    } catch (err) {
      setError('Unable to connect to Security Agent.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-gradient-to-br from-[#1a0c0e]/90 to-[#120809]/80 backdrop-blur-xl border border-[#2A0B12] rounded-2xl shadow-lg p-6 hover:border-[#DC143C]/20 transition-all duration-300">
      <div className="flex items-center gap-3 mb-4">
        <div className="p-2.5 rounded-xl bg-[#2A0B12] text-[#FF4D6D] border border-[#4B0F18] shadow-[0_0_10px_rgba(255,77,109,0.1)]">
          <Shield className="h-5 w-5" />
        </div>
        <h2 className="text-xl font-bold text-white tracking-tight">Security Agent Playground</h2>
      </div>
      
      <div className="mb-4">
        <textarea
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="Enter a prompt to analyze..."
          className="w-full h-24 bg-[#120809] border border-[#4B0F18] rounded-xl p-4 text-white placeholder:text-slate-500 focus:outline-none focus:border-[#DC143C] focus:ring-1 focus:ring-[#DC143C] transition-all resize-none"
        />
      </div>

      <div className="flex justify-between items-center mb-6">
        {error ? (
          <div className="text-sm text-red-400 flex items-center gap-2">
            <AlertTriangle className="h-4 w-4" /> {error}
          </div>
        ) : (
          <div className="text-xs text-slate-400">Test prompts against the IntelliGuard Security Engine</div>
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
          {/* Top Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-[#120809] border border-[#2A0B12] p-3 rounded-xl">
              <div className="text-xs text-slate-500 uppercase font-semibold mb-1">Risk Score</div>
              <div className={`text-2xl font-bold ${result?.risk_score > 75 ? 'text-red-400' : result?.risk_score > 50 ? 'text-orange-400' : result?.risk_score > 25 ? 'text-amber-400' : 'text-emerald-400'}`}>
                {result?.risk_score}
              </div>
            </div>
            <div className="bg-[#120809] border border-[#2A0B12] p-3 rounded-xl flex flex-col justify-center items-start">
              <div className="text-xs text-slate-500 uppercase font-semibold mb-2">Severity</div>
              <StatusBadge status={result?.severity} />
            </div>
            <div className="bg-[#120809] border border-[#2A0B12] p-3 rounded-xl flex flex-col justify-center items-start">
              <div className="text-xs text-slate-500 uppercase font-semibold mb-2">Decision</div>
              <StatusBadge status={result?.decision} />
            </div>
            <div className="bg-[#120809] border border-[#2A0B12] p-3 rounded-xl">
              <div className="text-xs text-slate-500 uppercase font-semibold mb-1">Confidence</div>
              <div className="text-2xl font-bold text-white">{((result?.confidence || 0) * 100).toFixed(0)}%</div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <div>
                <h4 className="text-xs text-slate-500 uppercase tracking-wider font-semibold mb-1">Risk Category</h4>
                <p className="text-sm text-white font-medium">{result?.risk_category || 'None'}</p>
              </div>
              <div>
                <h4 className="text-xs text-slate-500 uppercase tracking-wider font-semibold mb-1">Explanation</h4>
                <p className="text-sm text-slate-300">{result?.explanation}</p>
              </div>
              <div>
                <h4 className="text-xs text-slate-500 uppercase tracking-wider font-semibold mb-1">Recommended Action</h4>
                <p className="text-sm text-slate-300">{result?.recommended_action}</p>
              </div>
            </div>

            <div className="space-y-4">
              {result?.safe_prompt && result?.safe_prompt !== prompt && (
                <div>
                  <h4 className="text-xs text-[#FF4D6D] uppercase tracking-wider font-semibold mb-1 flex items-center gap-1">
                    <CheckCircle2 className="h-3 w-3" /> Safe Prompt
                  </h4>
                  <div className="bg-[#2A0B12]/50 border border-[#4B0F18] rounded-lg p-3 text-sm text-white font-mono whitespace-pre-wrap">
                    {result.safe_prompt}
                  </div>
                </div>
              )}

              {result?.remediation && (
                <div>
                  <h4 className="text-xs text-emerald-400 uppercase tracking-wider font-semibold mb-1">Remediation Action</h4>
                  <div className="bg-emerald-500/5 border border-emerald-500/20 rounded-lg p-3 text-sm text-slate-300 space-y-2">
                    {result.remediation.applied === false ? (
                      <div className="text-slate-400">
                        <span className="font-semibold text-slate-300">Not Applied: </span>
                        {result.remediation.reason}
                      </div>
                    ) : (
                      <>
                        {result.remediation.changes && result.remediation.changes.length > 0 && (
                          <div>
                            <span className="font-semibold text-emerald-400">Changes: </span>
                            <ul className="list-disc list-inside ml-1">
                              {result.remediation.changes.map((change, idx) => <li key={idx}>{change}</li>)}
                            </ul>
                          </div>
                        )}
                        {result.remediation.safe_prompt && (
                          <div>
                            <span className="font-semibold text-emerald-400 block mb-1">Rewritten Prompt: </span>
                            <div className="bg-[#120809] border border-[#2A0B12] rounded p-2 text-white font-mono text-xs whitespace-pre-wrap">
                              {result.remediation.safe_prompt}
                            </div>
                          </div>
                        )}
                        <div className="text-xs text-slate-500">
                          Confidence: {((result.remediation.confidence || 0) * 100).toFixed(0)}%
                        </div>
                      </>
                    )}
                  </div>
                </div>
              )}

              {result?.attack_summary && Object.keys(result.attack_summary).length > 0 && (
                <div>
                  <h4 className="text-xs text-slate-500 uppercase tracking-wider font-semibold mb-1 flex items-center gap-1">
                    <ShieldAlert className="h-3 w-3 text-orange-400" /> Attack Summary
                  </h4>
                  <ul className="space-y-1 text-sm text-slate-300">
                    {Object.entries(result.attack_summary).map(([attack, data]) => (
                      <li key={attack} className="flex justify-between items-center bg-[#2A0B12]/20 p-2 rounded border border-[#4B0F18]/20">
                         <span>{attack.replace(/_/g, ' ')}</span>
                         <div className="flex items-center gap-3 text-xs">
                           <span className="text-slate-400">Conf: {((data.confidence || 0) * 100).toFixed(0)}%</span>
                           <span className="text-slate-400">Matches: {data.signatures_matched}</span>
                         </div>
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
                            {finding.detector}
                          </span>
                          <div className="flex gap-2">
                            <span className="text-slate-400">Severity: <StatusBadge status={finding.severity} /></span>
                            <span className="text-slate-400">Conf: {((finding.confidence || 0) * 100).toFixed(0)}%</span>
                          </div>
                        </div>
                        <div className="text-slate-400 mt-1">{finding.reason}</div>
                        {finding.matched_patterns && finding.matched_patterns.length > 0 && (
                           <div className="mt-1 text-[10px] font-mono bg-[#120809] p-1 rounded text-slate-500 break-all">
                             {finding.matched_patterns.join(", ")}
                           </div>
                        )}
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
