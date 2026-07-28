import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  LineChart, Line, ResponsiveContainer, YAxis 
} from 'recharts';
import { 
  Shield, Lock, FileCheck, Brain, Activity, Settings2, 
  ChevronDown, ChevronUp, Clock, AlertTriangle, CheckCircle2
} from 'lucide-react';
import PageHeader from '@/components/PageHeader';

const mockAgents = [
  { 
    id: 'trust1', name: "Trust Agent", role: "Threat Detection & Trust", icon: Lock, status: "Active", health: "100%", currentTask: "Scanning payload #REQ-8291", 
    responseTime: "14ms", riskScore: 98, lastActivity: "2s ago", confidence: 95, requestsProcessed: "1.4M",
    recentFindings: ["Blocked SQLi attempt from IP 192.168.1.45", "Detected abnormal prompt length"],
    performanceData: [{v: 98},{v: 97},{v: 99},{v: 95},{v: 98},{v: 99},{v: 98}]
  },
  { 
    id: 'priv', name: "Privacy Agent", role: "PII & Data Masking", icon: Shield, status: "Active", health: "98%", currentTask: "Masking response #REQ-8290", 
    responseTime: "22ms", riskScore: 94, lastActivity: "5s ago", confidence: 92, requestsProcessed: "1.2M",
    recentFindings: ["Masked 2 SSNs in outgoing response", "Flagged potential email exposure"],
    performanceData: [{v: 90},{v: 92},{v: 94},{v: 91},{v: 94},{v: 96},{v: 94}]
  },
  { 
    id: 'comp', name: "Compliance Agent", role: "Policy Enforcement", icon: FileCheck, status: "Warning", health: "92%", currentTask: "Evaluating HIPAA rules", 
    responseTime: "45ms", riskScore: 89, lastActivity: "12s ago", confidence: 88, requestsProcessed: "850K",
    recentFindings: ["Flagged GDPR risk on user query", "HIPAA compliance check passed"],
    performanceData: [{v: 85},{v: 88},{v: 86},{v: 89},{v: 85},{v: 89},{v: 89}]
  },
  { 
    id: 'trust', name: "Trust Agent", role: "Bias & Hallucination", icon: Brain, status: "Active", health: "99%", currentTask: "Analyzing factuality score", 
    responseTime: "110ms", riskScore: 91, lastActivity: "1s ago", confidence: 90, requestsProcessed: "920K",
    recentFindings: ["Low hallucination risk detected (0.02)", "Verified source citations"],
    performanceData: [{v: 88},{v: 89},{v: 90},{v: 92},{v: 91},{v: 90},{v: 91}]
  },
  { 
    id: 'dec', name: "Decision Agent", role: "Final Routing", icon: Activity, status: "Active", health: "100%", currentTask: "Routing approved request", 
    responseTime: "8ms", riskScore: 99, lastActivity: "0s ago", confidence: 98, requestsProcessed: "2.1M",
    recentFindings: ["Approved 96% of requests in last hour", "Routed 4% to Remediation"],
    performanceData: [{v: 97},{v: 98},{v: 99},{v: 99},{v: 98},{v: 99},{v: 99}]
  },
  { 
    id: 'rem', name: "Remediation Agent", role: "Automated Fixes", icon: Settings2, status: "Active", health: "95%", currentTask: "Applying prompt filters", 
    responseTime: "65ms", riskScore: 85, lastActivity: "1m ago", confidence: 82, requestsProcessed: "140K",
    recentFindings: ["Applied 4 prompt filters", "Sanitized malicious script tags"],
    performanceData: [{v: 80},{v: 82},{v: 85},{v: 81},{v: 84},{v: 86},{v: 85}]
  },
];

const StatusBadge = ({ status }) => {
  const styles = {
    Active: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
    Warning: "bg-orange-500/10 text-orange-400 border-orange-500/20",
    Error: "bg-red-500/10 text-red-400 border-red-500/20",
  };
  return (
    <span className={`px-2.5 py-0.5 rounded-full text-xs font-semibold border uppercase tracking-wider ${styles[status] || "bg-slate-500/10 text-slate-400 border-slate-500/20"}`}>
      {status}
    </span>
  );
};

const DetailedAgentCard = ({ agent }) => {
  const [expanded, setExpanded] = useState(false);
  const Icon = agent.icon;

  return (
    <div className="bg-gradient-to-br from-[#1a0c0e]/90 to-[#120809]/80 backdrop-blur-xl border border-[#2A0B12] rounded-2xl overflow-hidden shadow-lg hover:border-[#DC143C]/40 hover:shadow-[0_0_20px_rgba(220,20,60,0.15)] transition-all duration-300">
      <div className="p-6 cursor-pointer" onClick={() => setExpanded(!expanded)}>
        <div className="flex justify-between items-start mb-6">
          <div className="flex items-center gap-4">
            <div className="h-12 w-12 rounded-xl bg-[#2A0B12] flex items-center justify-center border border-[#4B0F18] shadow-[0_0_15px_rgba(255,77,109,0.1)]">
              <Icon className="h-6 w-6 text-[#FF4D6D]" />
            </div>
            <div>
              <h3 className="font-bold text-white text-lg">{agent.name}</h3>
              <p className="text-sm text-slate-400 font-medium">{agent.role}</p>
            </div>
          </div>
          <StatusBadge status={agent.status} />
        </div>

        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <div>
            <p className="text-xs text-slate-500 uppercase tracking-wider font-semibold mb-1">Health</p>
            <p className="text-lg font-bold text-emerald-400 flex items-center gap-1">
              <CheckCircle2 className="h-4 w-4" /> {agent.health}
            </p>
          </div>
          <div>
            <p className="text-xs text-slate-500 uppercase tracking-wider font-semibold mb-1">Risk Score</p>
            <p className="text-lg font-bold text-white">{agent.riskScore}/100</p>
          </div>
          <div>
            <p className="text-xs text-slate-500 uppercase tracking-wider font-semibold mb-1">Confidence</p>
            <p className="text-lg font-bold text-white">{agent.confidence}%</p>
          </div>
          <div>
            <p className="text-xs text-slate-500 uppercase tracking-wider font-semibold mb-1">Response Time</p>
            <p className="text-lg font-bold text-white flex items-center gap-1">
              <Clock className="h-4 w-4 text-[#FF4D6D]" /> {agent.responseTime}
            </p>
          </div>
        </div>

        <div className="flex justify-between items-center text-sm border-t border-[#2A0B12] pt-4">
          <div className="text-slate-400 truncate flex-1 pr-4">
            <span className="font-semibold text-slate-300">Current Task:</span> {agent.currentTask}
          </div>
          <div className="text-slate-500 flex items-center gap-1">
            {expanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
            {expanded ? 'Hide Details' : 'View Details'}
          </div>
        </div>
      </div>

      <AnimatePresence>
        {expanded && (
          <motion.div 
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="border-t border-[#2A0B12] bg-[#120809]/50 overflow-hidden"
          >
            <div className="p-6 grid grid-cols-1 md:grid-cols-2 gap-8">
              <div className="space-y-4">
                <div>
                  <h4 className="text-xs text-slate-500 uppercase tracking-wider font-semibold mb-2">Recent Findings</h4>
                  <ul className="space-y-2">
                    {agent.recentFindings.map((finding, idx) => (
                      <li key={idx} className="flex items-start gap-2 text-sm text-slate-300 bg-[#2A0B12]/30 p-2 rounded-lg border border-[#4B0F18]/30">
                        <AlertTriangle className="h-4 w-4 text-[#FF4D6D] shrink-0 mt-0.5" />
                        {finding}
                      </li>
                    ))}
                  </ul>
                </div>
                <div className="flex justify-between items-center text-sm bg-[#1a0c0e] p-3 rounded-lg border border-[#2A0B12]">
                  <span className="text-slate-400">Total Requests Processed:</span>
                  <span className="font-bold text-white">{agent.requestsProcessed}</span>
                </div>
                <div className="flex justify-between items-center text-sm bg-[#1a0c0e] p-3 rounded-lg border border-[#2A0B12]">
                  <span className="text-slate-400">Last Activity:</span>
                  <span className="font-bold text-white">{agent.lastActivity}</span>
                </div>
              </div>

              <div>
                <h4 className="text-xs text-slate-500 uppercase tracking-wider font-semibold mb-4">Performance Trend (Last 7 Days)</h4>
                <div className="h-32 w-full bg-[#1a0c0e] rounded-xl border border-[#2A0B12] p-4">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={agent.performanceData}>
                      <YAxis domain={['dataMin - 5', 'dataMax + 5']} hide />
                      <Line type="monotone" dataKey="v" stroke="#DC143C" strokeWidth={3} dot={{ fill: '#120809', stroke: '#FF4D6D', strokeWidth: 2 }} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
                <p className="text-xs text-slate-500 mt-2 text-center">Average Risk Score stability</p>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default function Agents() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-[#120809] via-[#1A090D] to-[#2A0B12] text-slate-200 p-4 md:p-8 font-sans selection:bg-[#DC143C]/30 relative overflow-hidden z-0">
      {/* Dynamic Background Effects */}
      <div className="fixed inset-0 pointer-events-none -z-10">
        <div className="absolute top-0 left-1/4 w-[800px] h-[600px] bg-[#4B0F18]/20 rounded-full blur-[120px] mix-blend-screen" />
        <div className="absolute bottom-0 right-1/4 w-[600px] h-[600px] bg-[#DC143C]/10 rounded-full blur-[150px] mix-blend-screen" />
      </div>

      <div className="w-full">
        <PageHeader 
          title="AI Agent Monitoring" 
          description="Detailed health, performance, and status overview for the IntelliGuard AI agent fleet."
        />
        
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-6 pb-12">
          {mockAgents.map((agent) => (
            <DetailedAgentCard key={agent.id} agent={agent} />
          ))}
        </div>
      </div>
    </div>
  );
}
