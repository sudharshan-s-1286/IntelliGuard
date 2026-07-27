import React, { useState } from 'react';
import { Search, Filter, Calendar, ChevronDown, ChevronUp, Download, Eye, ShieldAlert, CheckCircle2, ShieldOff } from 'lucide-react';
import PageHeader from '@/components/PageHeader';
import { motion, AnimatePresence } from 'framer-motion';

const mockAuditLogs = [
  {
    id: "LOG-9281A", timestamp: "2023-10-24 14:32:01", user: "j.doe@enterprise.com", tool: "Copilot", promptId: "PRM-192", 
    decision: "Blocked", riskScore: 94, agent: "Security", status: "Critical",
    details: "Detected potential SQL injection syntax in prompt. Blocked before execution.",
    timeline: [
      { time: "14:32:00", event: "Request received via API Gateway" },
      { time: "14:32:01", event: "Security Agent pattern matched malicious syntax" },
      { time: "14:32:01", event: "Decision Agent routed to block" },
    ]
  },
  {
    id: "LOG-9281B", timestamp: "2023-10-24 14:30:15", user: "m.smith@enterprise.com", tool: "ChatGPT", promptId: "PRM-191", 
    decision: "Masked", riskScore: 65, agent: "Privacy", status: "Warning",
    details: "Identified PII (Email Address) in outgoing request. Applied mask.",
    timeline: [
      { time: "14:30:14", event: "Request received via API Gateway" },
      { time: "14:30:15", event: "Privacy Agent identified PII" },
      { time: "14:30:15", event: "Remediation Agent masked data: m.s****@enterprise.com" },
    ]
  },
  {
    id: "LOG-9281C", timestamp: "2023-10-24 14:28:40", user: "system_batch", tool: "Internal CRM AI", promptId: "PRM-190", 
    decision: "Approved", riskScore: 12, agent: "Trust", status: "Safe",
    details: "Standard summary request. No anomalies detected.",
    timeline: [
      { time: "14:28:39", event: "Batch job initiated" },
      { time: "14:28:40", event: "Trust Agent verified source" },
      { time: "14:28:40", event: "Decision Agent approved" },
    ]
  },
  {
    id: "LOG-9281D", timestamp: "2023-10-24 14:15:22", user: "a.lee@enterprise.com", tool: "Copilot", promptId: "PRM-189", 
    decision: "Flagged", riskScore: 78, agent: "Compliance", status: "Warning",
    details: "Prompt discussed financial earnings prior to public release. Flagged for review.",
    timeline: [
      { time: "14:15:20", event: "Request received" },
      { time: "14:15:21", event: "Compliance Agent matched SEC policy rule" },
      { time: "14:15:22", event: "Flagged and added to review queue" },
    ]
  },
];

const StatusIcon = ({ status }) => {
  switch (status) {
    case "Critical": return <ShieldAlert className="h-4 w-4 text-red-400" />;
    case "Warning": return <ShieldAlert className="h-4 w-4 text-orange-400" />;
    case "Safe": return <CheckCircle2 className="h-4 w-4 text-emerald-400" />;
    default: return <ShieldOff className="h-4 w-4 text-slate-400" />;
  }
};

const AuditRow = ({ log }) => {
  const [expanded, setExpanded] = useState(false);

  return (
    <>
      <tr 
        onClick={() => setExpanded(!expanded)}
        className="border-b border-[#2A0B12] hover:bg-[#2A0B12]/50 transition-colors cursor-pointer group"
      >
        <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-300">
          <div className="flex items-center gap-2">
            {expanded ? <ChevronUp className="h-4 w-4 text-slate-500" /> : <ChevronDown className="h-4 w-4 text-slate-500 group-hover:text-[#FF4D6D]" />}
            {log.timestamp}
          </div>
        </td>
        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-white">{log.user}</td>
        <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-400">{log.tool}</td>
        <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-300">{log.promptId}</td>
        <td className="px-6 py-4 whitespace-nowrap text-sm">
          <span className={`px-2 py-1 rounded text-xs font-semibold ${
            log.decision === 'Blocked' ? 'bg-red-500/10 text-red-400 border border-red-500/20' :
            log.decision === 'Masked' ? 'bg-orange-500/10 text-orange-400 border border-orange-500/20' :
            log.decision === 'Flagged' ? 'bg-yellow-500/10 text-yellow-400 border border-yellow-500/20' :
            'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
          }`}>
            {log.decision}
          </span>
        </td>
        <td className="px-6 py-4 whitespace-nowrap text-sm font-bold text-white">{log.riskScore}</td>
        <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-400">{log.agent}</td>
        <td className="px-6 py-4 whitespace-nowrap text-sm flex items-center gap-2">
          <StatusIcon status={log.status} />
          <span className={
            log.status === 'Critical' ? 'text-red-400' :
            log.status === 'Warning' ? 'text-orange-400' : 'text-emerald-400'
          }>{log.status}</span>
        </td>
      </tr>
      <AnimatePresence>
        {expanded && (
          <tr>
            <td colSpan={8} className="bg-[#120809]/80 p-0">
              <motion.div 
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: 'auto', opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                className="overflow-hidden"
              >
                <div className="p-6 border-b border-[#2A0B12] grid grid-cols-1 lg:grid-cols-2 gap-8">
                  <div>
                    <h4 className="text-sm font-bold text-white mb-2 flex items-center gap-2">
                      <Eye className="h-4 w-4 text-[#FF4D6D]" /> Details
                    </h4>
                    <p className="text-sm text-slate-300 bg-[#2A0B12] p-4 rounded-lg border border-[#4B0F18]">
                      {log.details}
                    </p>
                    <div className="mt-4 flex gap-3">
                      <button className="text-xs bg-[#4B0F18] hover:bg-[#DC143C] text-white px-3 py-1.5 rounded transition-colors">View Full Prompt</button>
                      <button className="text-xs bg-[#2A0B12] hover:bg-[#4B0F18] text-slate-300 px-3 py-1.5 rounded transition-colors border border-[#4B0F18]">Export Trace</button>
                    </div>
                  </div>
                  <div>
                    <h4 className="text-sm font-bold text-white mb-2">Execution Timeline</h4>
                    <div className="space-y-3 relative before:absolute before:inset-0 before:ml-2 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-transparent before:via-[#4B0F18] before:to-transparent">
                      {log.timeline.map((step, idx) => (
                        <div key={idx} className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group is-active">
                          <div className="flex items-center justify-center w-4 h-4 rounded-full border-2 border-[#120809] bg-[#FF4D6D] shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2 shadow-[0_0_8px_#FF4D6D]" />
                          <div className="w-[calc(100%-2rem)] md:w-[calc(50%-1.5rem)] bg-[#2A0B12]/50 p-2 rounded border border-[#4B0F18]/50 text-xs">
                            <span className="text-[#DC143C] font-semibold mr-2">{step.time}</span>
                            <span className="text-slate-300">{step.event}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </motion.div>
            </td>
          </tr>
        )}
      </AnimatePresence>
    </>
  );
};

export default function Audit() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-[#120809] via-[#1A090D] to-[#2A0B12] text-slate-200 p-4 md:p-8 font-sans selection:bg-[#DC143C]/30 relative overflow-hidden z-0">
      <div className="fixed inset-0 pointer-events-none -z-10">
        <div className="absolute top-0 left-1/4 w-[800px] h-[600px] bg-[#4B0F18]/20 rounded-full blur-[120px] mix-blend-screen" />
        <div className="absolute bottom-0 right-1/4 w-[600px] h-[600px] bg-[#DC143C]/10 rounded-full blur-[150px] mix-blend-screen" />
      </div>

      <div className="w-full">
        <PageHeader 
          title="Audit Logs" 
          description="Comprehensive immutable record of all AI interactions, agent decisions, and security events."
          actions={
            <button className="flex items-center gap-2 bg-[#2A0B12] hover:bg-[#4B0F18] border border-[#DC143C]/30 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors">
              <Download className="h-4 w-4 text-[#FF4D6D]" /> Export Logs
            </button>
          }
        />

        {/* Filters */}
        <div className="bg-gradient-to-br from-[#1a0c0e]/90 to-[#120809]/80 backdrop-blur-xl border border-[#2A0B12] rounded-2xl p-4 mb-6 flex flex-wrap gap-4 items-center shadow-lg">
          <div className="relative flex-1 min-w-[200px]">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-500" />
            <input 
              type="text" 
              placeholder="Search by Prompt ID, User, or Keyword..." 
              className="w-full bg-[#120809] border border-[#4B0F18] rounded-lg pl-10 pr-4 py-2 text-sm text-white focus:outline-none focus:border-[#DC143C] transition-colors placeholder:text-slate-600"
            />
          </div>
          <div className="flex gap-2 flex-wrap">
            <button className="flex items-center gap-2 bg-[#120809] border border-[#4B0F18] hover:border-[#DC143C]/50 text-slate-300 px-3 py-2 rounded-lg text-sm transition-colors">
              <Calendar className="h-4 w-4 text-[#FF4D6D]" /> Date Range
            </button>
            <button className="flex items-center gap-2 bg-[#120809] border border-[#4B0F18] hover:border-[#DC143C]/50 text-slate-300 px-3 py-2 rounded-lg text-sm transition-colors">
              <Filter className="h-4 w-4 text-[#FF4D6D]" /> Severity
            </button>
            <button className="flex items-center gap-2 bg-[#120809] border border-[#4B0F18] hover:border-[#DC143C]/50 text-slate-300 px-3 py-2 rounded-lg text-sm transition-colors">
              <Filter className="h-4 w-4 text-[#FF4D6D]" /> Agent
            </button>
          </div>
        </div>

        {/* Audit Table */}
        <div className="bg-gradient-to-br from-[#1a0c0e]/90 to-[#120809]/80 backdrop-blur-xl border border-[#2A0B12] rounded-2xl overflow-hidden shadow-lg pb-12">
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-[#120809] border-b border-[#4B0F18]">
                  <th className="px-6 py-4 text-xs font-semibold text-slate-400 uppercase tracking-wider">Timestamp</th>
                  <th className="px-6 py-4 text-xs font-semibold text-slate-400 uppercase tracking-wider">User</th>
                  <th className="px-6 py-4 text-xs font-semibold text-slate-400 uppercase tracking-wider">AI Tool</th>
                  <th className="px-6 py-4 text-xs font-semibold text-slate-400 uppercase tracking-wider">Prompt ID</th>
                  <th className="px-6 py-4 text-xs font-semibold text-slate-400 uppercase tracking-wider">Decision</th>
                  <th className="px-6 py-4 text-xs font-semibold text-slate-400 uppercase tracking-wider">Risk Score</th>
                  <th className="px-6 py-4 text-xs font-semibold text-slate-400 uppercase tracking-wider">Agent</th>
                  <th className="px-6 py-4 text-xs font-semibold text-slate-400 uppercase tracking-wider">Status</th>
                </tr>
              </thead>
              <tbody>
                {mockAuditLogs.map((log) => (
                  <AuditRow key={log.id} log={log} />
                ))}
              </tbody>
            </table>
          </div>
          
          <div className="p-4 border-t border-[#2A0B12] flex justify-between items-center text-sm text-slate-400">
            <span>Showing 1 to 4 of 48,291 entries</span>
            <div className="flex gap-2">
              <button className="px-3 py-1 border border-[#4B0F18] rounded hover:bg-[#2A0B12] transition-colors disabled:opacity-50" disabled>Prev</button>
              <button className="px-3 py-1 border border-[#4B0F18] rounded hover:bg-[#2A0B12] transition-colors text-white bg-[#4B0F18]">1</button>
              <button className="px-3 py-1 border border-[#4B0F18] rounded hover:bg-[#2A0B12] transition-colors">2</button>
              <button className="px-3 py-1 border border-[#4B0F18] rounded hover:bg-[#2A0B12] transition-colors">3</button>
              <span className="px-2">...</span>
              <button className="px-3 py-1 border border-[#4B0F18] rounded hover:bg-[#2A0B12] transition-colors">Next</button>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}
