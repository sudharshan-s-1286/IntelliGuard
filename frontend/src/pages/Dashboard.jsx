import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import AnalyzeWidget from '../components/AnalyzeWidget';
import { 
  LineChart, Line, AreaChart, Area, PieChart, Pie, Cell, 
  RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, 
  XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer 
} from 'recharts';
import { 
  Shield, ShieldAlert, FileCheck, Activity, Brain, Server, 
  Lock, Eye, AlertTriangle, CheckCircle2, XCircle, Clock,
  ChevronRight, RefreshCw, Download, Search, Settings2, Fingerprint, ShieldCheck
} from 'lucide-react';

// --- THEME COLORS ---
const colors = {
  bg1: "#120809",
  bg2: "#2A0B12",
  bg3: "#4B0F18",
  primary: "#DC143C",
  secondary: "#FF4D6D",
  textMuted: "#94a3b8",
  success: "#10b981",
  warning: "#f59e0b",
  danger: "#ef4444",
};

// --- MOCK DATA ---
const mockKPIs = [
  { title: "Overall Trust Score", value: "92%", trend: "+2.4%", icon: Shield, type: "success" },
  { title: "Trust Verified Systems", value: "24", trend: "+3", icon: Server, type: "neutral" },
  { title: "Critical Alerts", value: "7", trend: "-2", icon: AlertTriangle, type: "danger" },
  { title: "Policies Enforced", value: "148", trend: "+12", icon: FileCheck, type: "neutral" },
  { title: "Today's Requests", value: "1,324", trend: "+14%", icon: Activity, type: "neutral" },
  { title: "Blocked Requests", value: "46", trend: "-5%", icon: ShieldAlert, type: "warning" },
];

const mockAgents = [
  { name: "Trust Agent", role: "Threat Detection & Trust", score: 98, confidence: 95, lastActive: "2s ago", finding: "No immediate threats", icon: Lock, status: "Active" },
  { name: "Privacy Agent", role: "PII & Data Masking", score: 94, confidence: 92, lastActive: "5s ago", finding: "Masked 2 SSNs", icon: Eye, status: "Active" },
  { name: "Compliance Agent", role: "Policy Enforcement", score: 89, confidence: 88, lastActive: "12s ago", finding: "Flagged GDPR risk", icon: FileCheck, status: "Warning" },
  { name: "Trust Agent", role: "Bias & Hallucination", score: 91, confidence: 90, lastActive: "1s ago", finding: "Low hallucination risk", icon: Brain, status: "Active" },
  { name: "Decision Agent", role: "Final Routing", score: 99, confidence: 98, lastActive: "0s ago", finding: "Approved 96% of requests", icon: Activity, status: "Active" },
  { name: "Remediation Agent", role: "Automated Fixes", score: 85, confidence: 82, lastActive: "1m ago", finding: "Applied 4 prompt filters", icon: Settings2, status: "Active" },
];

const trustTrendData = [
  { time: '08:00', score: 88 }, { time: '09:00', score: 89 }, { time: '10:00', score: 92 },
  { time: '11:00', score: 90 }, { time: '12:00', score: 94 }, { time: '13:00', score: 93 },
  { time: '14:00', score: 95 }, { time: '15:00', score: 92 }
];

const riskDistributionData = [
  { name: 'Trust', value: 45 }, { name: 'Privacy', value: 30 },
  { name: 'Compliance', value: 15 }, { name: 'Trust', value: 10 }
];

const pieColors = ["#DC143C", "#FF4D6D", "#f59e0b", "#10b981"];

const requestsData = [
  { time: 'Mon', reqs: 4000 }, { time: 'Tue', reqs: 3000 }, { time: 'Wed', reqs: 2000 },
  { time: 'Thu', reqs: 2780 }, { time: 'Fri', reqs: 1890 }, { time: 'Sat', reqs: 2390 },
  { time: 'Sun', reqs: 3490 }
];

const radarData = [
  { subject: 'Speed', A: 120, fullMark: 150 },
  { subject: 'Accuracy', A: 98, fullMark: 150 },
  { subject: 'Trust', A: 86, fullMark: 150 },
  { subject: 'Privacy', A: 99, fullMark: 150 },
  { subject: 'Compliance', A: 85, fullMark: 150 },
  { subject: 'Trust', A: 65, fullMark: 150 },
];

const mockThreats = [
  { id: 1, time: "10:42 AM", title: "Prompt Injection Detected", desc: "Blocked Malicious payload targeting DB", severity: "Critical" },
  { id: 2, time: "10:15 AM", title: "PII Exposure Prevented", desc: "Masked 3 credit card numbers in response", severity: "High" },
  { id: 3, time: "09:30 AM", title: "Compliance Policy Triggered", desc: "Flagged response for GDPR non-compliance", severity: "Medium" },
  { id: 4, time: "08:45 AM", title: "Hallucination Risk High", desc: "Trust Agent flagged low confidence in factuality", severity: "Medium" },
  { id: 5, time: "08:10 AM", title: "Unsafe AI Tool Blocked", desc: "Prevented routing to unauthorized shadow AI", severity: "Critical" },
];

const mockRequestsTable = [
  { id: "REQ-001", time: "10:45:12", user: "j.smith", tool: "GPT-4 Enterprise", category: "Data Analysis", sec: "Low", priv: "High", comp: "Low", decision: "Modified", status: "Modified" },
  { id: "REQ-002", time: "10:44:50", user: "m.doe", tool: "Claude 3 Opus", category: "Code Gen", sec: "Low", priv: "Low", comp: "Low", decision: "Approved", status: "Approved" },
  { id: "REQ-003", time: "10:42:01", user: "system_api", tool: "Internal RAG", category: "Customer Support", sec: "Critical", priv: "High", comp: "High", decision: "Blocked", status: "Blocked" },
  { id: "REQ-004", time: "10:38:22", user: "a.wang", tool: "GPT-4 Enterprise", category: "Drafting", sec: "Low", priv: "Medium", comp: "Medium", decision: "Warning", status: "Warning" },
  { id: "REQ-005", time: "10:35:10", user: "p.jones", tool: "Gemini Pro", category: "Research", sec: "Low", priv: "Low", comp: "Low", decision: "Approved", status: "Approved" },
];

// --- REUSABLE COMPONENTS ---

const StatusBadge = ({ status }) => {
  const styles = {
    Approved: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
    Blocked: "bg-red-500/10 text-red-400 border-red-500/20",
    Modified: "bg-amber-500/10 text-amber-400 border-amber-500/20",
    Warning: "bg-orange-500/10 text-orange-400 border-orange-500/20",
    Active: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
    Critical: "bg-red-500/10 text-red-400 border-red-500/20",
    High: "bg-orange-500/10 text-orange-400 border-orange-500/20",
    Medium: "bg-amber-500/10 text-amber-400 border-amber-500/20",
    Low: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
  };
  
  return (
    <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium border ${styles[status] || "bg-slate-500/10 text-slate-400 border-slate-500/20"}`}>
      {status}
    </span>
  );
};

const MetricCard = ({ title, value, trend, icon: Icon, type }) => (
  <motion.div 
    whileHover={{ y: -2, borderColor: "rgba(220, 20, 60, 0.4)", boxShadow: "0 0 20px rgba(220,20,60,0.15)" }}
    className="bg-gradient-to-br from-[#1a0c0e]/90 to-[#120809]/80 backdrop-blur-xl border border-[#2A0B12] p-5 rounded-2xl flex flex-col relative overflow-hidden group shadow-lg"
  >
    <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
      <Icon className="h-16 w-16 text-[#DC143C]" />
    </div>
    <div className="flex justify-between items-start mb-4 relative z-10">
      <span className="text-sm font-medium text-slate-400">{title}</span>
      <div className={`p-2 rounded-lg bg-[#2A0B12] text-[#FF4D6D]`}>
        <Icon className="h-4 w-4" />
      </div>
    </div>
    <div className="flex items-baseline gap-2 relative z-10">
      <h3 className="text-3xl font-bold text-white tracking-tight">{value}</h3>
      <span className={`text-xs font-semibold ${trend.startsWith('+') ? 'text-emerald-400' : 'text-red-400'}`}>
        {trend}
      </span>
    </div>
  </motion.div>
);

const AgentCard = ({ agent }) => (
  <div className="bg-gradient-to-br from-[#1a0c0e]/90 to-[#120809]/80 backdrop-blur-xl border border-[#2A0B12] rounded-2xl p-5 hover:border-[#DC143C]/40 hover:shadow-[0_0_20px_rgba(220,20,60,0.15)] transition-all duration-300 shadow-lg">
    <div className="flex justify-between items-start mb-4">
      <div className="flex items-center gap-3">
        <div className="h-10 w-10 rounded-lg bg-[#2A0B12] flex items-center justify-center border border-[#4B0F18]">
          <agent.icon className="h-5 w-5 text-[#FF4D6D]" />
        </div>
        <div>
          <h4 className="font-semibold text-white text-sm">{agent.name}</h4>
          <p className="text-xs text-slate-400">{agent.role}</p>
        </div>
      </div>
      <StatusBadge status={agent.status} />
    </div>
    
    <div className="grid grid-cols-2 gap-4 mb-4">
      <div className="bg-[#120809] rounded-lg p-3 border border-[#2A0B12]">
        <div className="text-xs text-slate-400 mb-1">Risk Score</div>
        <div className="text-lg font-bold text-white">{agent.score}/100</div>
      </div>
      <div className="bg-[#120809] rounded-lg p-3 border border-[#2A0B12]">
        <div className="text-xs text-slate-400 mb-1">Confidence</div>
        <div className="text-lg font-bold text-white">{agent.confidence}%</div>
      </div>
    </div>
    
    <div className="flex items-center justify-between text-xs">
      <div className="flex items-center gap-1.5 text-slate-400">
        <Clock className="h-3 w-3" />
        Updated {agent.lastActive}
      </div>
      <div className="text-[#FF4D6D] truncate max-w-[120px]" title={agent.finding}>
        {agent.finding}
      </div>
    </div>
  </div>
);

const ChartCard = ({ title, children }) => (
  <div className="bg-gradient-to-br from-[#1a0c0e]/90 to-[#120809]/80 backdrop-blur-xl border border-[#2A0B12] p-5 rounded-2xl flex flex-col shadow-lg hover:border-[#DC143C]/20 transition-all duration-300">
    <h3 className="text-sm font-semibold text-white mb-6 uppercase tracking-wider">{title}</h3>
    <div className="flex-1 min-h-[250px] w-full">
      {children}
    </div>
  </div>
);

const ThreatTimeline = ({ threats }) => (
  <div className="space-y-6">
    {threats?.map((threat, idx) => (
      <div key={threat.id} className="relative pl-6 pb-6 last:pb-0">
        {idx !== threats.length - 1 && (
          <div className="absolute left-[11px] top-6 bottom-0 w-px bg-[#4B0F18]" />
        )}
        <div className={`absolute left-0 top-1.5 w-6 h-6 rounded-full flex items-center justify-center border-2 border-[#1a0c0e] ${threat.severity === 'Critical' ? 'bg-red-500' : threat.severity === 'High' ? 'bg-orange-500' : 'bg-amber-500'}`}>
          <div className="w-2 h-2 rounded-full bg-white" />
        </div>
        <div>
          <div className="flex items-center justify-between mb-1">
            <h4 className="text-sm font-semibold text-white">{threat.title}</h4>
            <span className="text-xs text-slate-500">{threat.time}</span>
          </div>
          <p className="text-xs text-slate-400 mb-2">{threat.desc}</p>
          <StatusBadge status={threat.severity} />
        </div>
      </div>
    ))}
  </div>
);

const TrustGauge = () => (
  <div className="relative flex flex-col items-center justify-center h-48 w-full">
    <svg viewBox="0 0 100 50" className="w-full max-w-[200px] overflow-visible">
      <path d="M 10 50 A 40 40 0 0 1 90 50" fill="none" stroke="#2A0B12" strokeWidth="12" strokeLinecap="round" />
      <motion.path 
        initial={{ strokeDasharray: "0 251" }}
        animate={{ strokeDasharray: "230 251" }}
        transition={{ duration: 1.5, ease: "easeOut" }}
        d="M 10 50 A 40 40 0 0 1 90 50" fill="none" stroke="url(#trustGradient)" strokeWidth="12" strokeLinecap="round" 
      />
      <defs>
        <linearGradient id="trustGradient" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stopColor="#DC143C" />
          <stop offset="100%" stopColor="#10b981" />
        </linearGradient>
      </defs>
    </svg>
    <div className="absolute bottom-4 text-center">
      <div className="text-4xl font-bold text-white">92<span className="text-lg text-slate-400">%</span></div>
      <div className="text-xs text-[#FF4D6D] uppercase font-semibold tracking-wider mt-1">Excellent</div>
    </div>
  </div>
);

// --- MAIN DASHBOARD COMPONENT ---

export default function Dashboard() {
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Simulate initial data loading
    const timer = setTimeout(() => setLoading(false), 800);
    return () => clearTimeout(timer);
  }, []);

  const currentDate = new Date().toLocaleDateString('en-US', { 
    weekday: 'long', year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' 
  });

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-[#120809] via-[#1A090D] to-[#2A0B12] p-4 md:p-8 pt-4">
        <div className="w-full space-y-8 animate-pulse">
          <div className="h-24 bg-[#1a0c0e] rounded-2xl border border-[#2A0B12]"></div>
          <div className="flex gap-3"><div className="h-10 w-32 bg-[#2A0B12] rounded-lg"></div><div className="h-10 w-32 bg-[#2A0B12] rounded-lg"></div></div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[...Array(6)].map((_, i) => <div key={i} className="h-32 bg-[#1a0c0e] rounded-xl border border-[#2A0B12]"></div>)}
          </div>
          <div className="h-8 w-48 bg-[#2A0B12] rounded mt-8"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[...Array(6)].map((_, i) => <div key={i} className="h-40 bg-[#1a0c0e] rounded-xl border border-[#2A0B12]"></div>)}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#120809] via-[#1A090D] to-[#2A0B12] text-slate-200 p-4 md:p-8 font-sans selection:bg-[#DC143C]/30 pt-4 relative overflow-hidden z-0">
      {/* Dynamic Background Effects */}
      <div className="fixed inset-0 pointer-events-none -z-10">
        <div className="absolute top-0 left-1/4 w-[800px] h-[600px] bg-[#4B0F18]/20 rounded-full blur-[120px] mix-blend-screen" />
        <div className="absolute bottom-0 right-1/4 w-[600px] h-[600px] bg-[#DC143C]/10 rounded-full blur-[150px] mix-blend-screen" />
      </div>
      
      <div className="w-full space-y-8">
        
        {/* Premium Header Section */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6 bg-gradient-to-br from-[#1a0c0e]/90 to-[#120809]/80 p-8 rounded-2xl border border-[#2A0B12] backdrop-blur-xl shadow-[0_8px_30px_rgba(0,0,0,0.5)] relative overflow-hidden group">
          <div className="absolute inset-0 bg-gradient-to-r from-[#DC143C]/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-700 pointer-events-none" />
          <div className="relative z-10">
            <h1 className="text-3xl md:text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-white to-slate-400 tracking-tight flex items-center gap-3">
              Enterprise AI Governance Dashboard
            </h1>
            <p className="text-sm md:text-base text-slate-400 mt-2 font-medium">
               Monitor enterprise AI trust, privacy, and compliance in real-time.
            </p>
          </div>
          <div className="flex flex-col items-end gap-3 relative z-10">
            <div className="text-sm font-medium text-slate-400 flex items-center gap-2 bg-[#120809] px-3 py-1.5 rounded-lg border border-[#2A0B12]">
              <Clock className="h-4 w-4 text-[#FF4D6D]" /> {currentDate}
            </div>
            <div className="flex items-center gap-2 bg-emerald-500/10 border border-emerald-500/30 px-4 py-2 rounded-lg shadow-[0_0_15px_rgba(16,185,129,0.2)]">
              <ShieldCheck className="h-4 w-4 text-emerald-400 animate-pulse" />
               <span className="text-sm font-bold text-emerald-400 uppercase tracking-wider">Trust Verified</span>
            </div>
          </div>
        </div>

        {/* Enterprise Status Strip */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 bg-gradient-to-br from-[#1a0c0e]/90 to-[#120809]/80 p-5 rounded-2xl border border-[#2A0B12] backdrop-blur-xl shadow-lg">
          <div className="flex items-center gap-4">
            <div className="p-2.5 rounded-xl bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 shadow-[0_0_10px_rgba(16,185,129,0.1)]">
              <Activity className="h-5 w-5" />
            </div>
            <div>
              <p className="text-xs text-slate-400 uppercase tracking-wider font-semibold mb-0.5">System Health</p>
              <p className="text-base font-bold text-emerald-400">Optimal</p>
            </div>
          </div>
          <div className="flex items-center gap-4 border-l border-[#2A0B12] pl-4">
            <div className="p-2.5 rounded-xl bg-[#2A0B12] text-[#FF4D6D] border border-[#4B0F18] shadow-[0_0_10px_rgba(255,77,109,0.1)]">
              <Brain className="h-5 w-5" />
            </div>
            <div>
              <p className="text-xs text-slate-400 uppercase tracking-wider font-semibold mb-0.5">AI Agents Online</p>
              <p className="text-base font-bold text-white">6 / 6 Active</p>
            </div>
          </div>
          <div className="flex items-center gap-4 border-l border-[#2A0B12] pl-4">
            <div className="p-2.5 rounded-xl bg-[#2A0B12] text-[#FF4D6D] border border-[#4B0F18] shadow-[0_0_10px_rgba(255,77,109,0.1)]">
              <FileCheck className="h-5 w-5" />
            </div>
            <div>
              <p className="text-xs text-slate-400 uppercase tracking-wider font-semibold mb-0.5">Policies Active</p>
              <p className="text-base font-bold text-white">148 Enforced</p>
            </div>
          </div>
          <div className="flex items-center gap-4 border-l border-[#2A0B12] pl-4">
            <div className="p-2.5 rounded-xl bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 shadow-[0_0_10px_rgba(16,185,129,0.1)]">
              <ShieldCheck className="h-5 w-5" />
            </div>
            <div>
              <p className="text-xs text-slate-400 uppercase tracking-wider font-semibold mb-0.5">Threat Level</p>
              <p className="text-base font-bold text-emerald-400">Low Risk</p>
            </div>
          </div>
        </div>

        <AnalyzeWidget />

        {/* KPI Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {mockKPIs.map((kpi, idx) => (
            <motion.div key={kpi.title} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: idx * 0.05 }}>
              <MetricCard {...kpi} />
            </motion.div>
          ))}
        </div>

        {/* AI Agent Monitoring Grid */}
        <div className="space-y-4">
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Fingerprint className="h-5 w-5 text-[#FF4D6D]" /> AI Agent Fleet Status
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {mockAgents.map((agent, idx) => (
              <motion.div key={agent.name} initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 0.2 + (idx * 0.05) }}>
                <AgentCard agent={agent} />
              </motion.div>
            ))}
          </div>
        </div>

        {/* Main Analytics Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Trust Analytics & Overview - Takes up 2 cols */}
          <div className="lg:col-span-2 space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <ChartCard title="Trust Score Trend">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={trustTrendData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#2A0B12" vertical={false} />
                    <XAxis dataKey="time" stroke="#64748b" fontSize={12} tickLine={false} axisLine={false} />
                    <YAxis stroke="#64748b" fontSize={12} tickLine={false} axisLine={false} domain={[80, 100]} />
                    <RechartsTooltip 
                      contentStyle={{ backgroundColor: '#120809', borderColor: '#4B0F18', color: '#fff' }}
                      itemStyle={{ color: '#FF4D6D' }}
                    />
                    <Line type="monotone" dataKey="score" stroke="#DC143C" strokeWidth={3} dot={{ fill: '#120809', stroke: '#FF4D6D', strokeWidth: 2 }} activeDot={{ r: 6, fill: '#FF4D6D' }} />
                  </LineChart>
                </ResponsiveContainer>
              </ChartCard>
              
              <ChartCard title="Risk Distribution">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={riskDistributionData}
                      innerRadius={60}
                      outerRadius={80}
                      paddingAngle={5}
                      dataKey="value"
                    >
                      {riskDistributionData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={pieColors[index % pieColors.length]} />
                      ))}
                    </Pie>
                    <RechartsTooltip contentStyle={{ backgroundColor: '#120809', borderColor: '#4B0F18', color: '#fff' }} />
                  </PieChart>
                </ResponsiveContainer>
                <div className="flex justify-center gap-4 mt-2 flex-wrap">
                  {riskDistributionData.map((entry, index) => (
                    <div key={entry.name} className="flex items-center gap-1.5 text-xs text-slate-400">
                      <div className="w-2 h-2 rounded-full" style={{ backgroundColor: pieColors[index] }} />
                      {entry.name}
                    </div>
                  ))}
                </div>
              </ChartCard>

              <ChartCard title="AI Requests Volume">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={requestsData}>
                    <defs>
                      <linearGradient id="colorReq" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#DC143C" stopOpacity={0.3}/>
                        <stop offset="95%" stopColor="#DC143C" stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#2A0B12" vertical={false} />
                    <XAxis dataKey="time" stroke="#64748b" fontSize={12} tickLine={false} axisLine={false} />
                    <YAxis stroke="#64748b" fontSize={12} tickLine={false} axisLine={false} />
                    <RechartsTooltip contentStyle={{ backgroundColor: '#120809', borderColor: '#4B0F18', color: '#fff' }} />
                    <Area type="monotone" dataKey="reqs" stroke="#DC143C" fillOpacity={1} fill="url(#colorReq)" />
                  </AreaChart>
                </ResponsiveContainer>
              </ChartCard>

              <ChartCard title="Agent Performance Radar">
                <ResponsiveContainer width="100%" height="100%">
                  <RadarChart cx="50%" cy="50%" outerRadius="70%" data={radarData}>
                    <PolarGrid stroke="#2A0B12" />
                    <PolarAngleAxis dataKey="subject" tick={{ fill: '#94a3b8', fontSize: 10 }} />
                    <PolarRadiusAxis angle={30} domain={[0, 150]} tick={false} axisLine={false} />
                    <Radar name="Performance" dataKey="A" stroke="#DC143C" fill="#DC143C" fillOpacity={0.4} />
                    <RechartsTooltip contentStyle={{ backgroundColor: '#120809', borderColor: '#4B0F18', color: '#fff' }} />
                  </RadarChart>
                </ResponsiveContainer>
              </ChartCard>
            </div>

            {/* Recent Requests Table */}
            <div className="bg-gradient-to-br from-[#1a0c0e]/90 to-[#120809]/80 backdrop-blur-xl border border-[#2A0B12] rounded-2xl overflow-hidden shadow-lg">
              <div className="p-5 border-b border-[#2A0B12] flex justify-between items-center">
                <h3 className="text-sm font-semibold text-white uppercase tracking-wider">Recent AI Requests</h3>
                <button className="text-xs text-[#FF4D6D] hover:text-white transition-colors flex items-center gap-1">
                  View All <ChevronRight className="h-3 w-3" />
                </button>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-sm text-left">
                  <thead className="text-xs text-slate-400 bg-[#2A0B12]/50 uppercase">
                    <tr>
                      <th className="px-4 py-3 font-medium">Timestamp</th>
                      <th className="px-4 py-3 font-medium">User</th>
                      <th className="px-4 py-3 font-medium">AI Tool</th>
                      <th className="px-4 py-3 font-medium">Category</th>
                      <th className="px-4 py-3 font-medium">Trust</th>
                      <th className="px-4 py-3 font-medium">Privacy</th>
                      <th className="px-4 py-3 font-medium">Decision</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[#2A0B12]">
                    {mockRequestsTable.map((req) => (
                      <tr key={req.id} className="hover:bg-[#2A0B12]/30 transition-colors">
                        <td className="px-4 py-3 text-slate-300 font-mono text-xs">{req.time}</td>
                        <td className="px-4 py-3 text-white">{req.user}</td>
                        <td className="px-4 py-3 text-slate-300">{req.tool}</td>
                        <td className="px-4 py-3 text-slate-400">{req.category}</td>
                        <td className="px-4 py-3"><StatusBadge status={req.sec} /></td>
                        <td className="px-4 py-3"><StatusBadge status={req.priv} /></td>
                        <td className="px-4 py-3"><StatusBadge status={req.decision} /></td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          {/* Right Column - Overview & Live Feed */}
          <div className="space-y-6">
            {/* Enterprise Trust Overview */}
            <div className="bg-gradient-to-br from-[#1a0c0e]/90 to-[#120809]/80 backdrop-blur-xl border border-[#2A0B12] p-6 rounded-2xl relative overflow-hidden shadow-lg hover:border-[#DC143C]/20 transition-all duration-300">
              <div className="absolute top-0 right-0 w-32 h-32 bg-[#DC143C]/5 rounded-full blur-3xl" />
              <h3 className="text-sm font-semibold text-white uppercase tracking-wider mb-2">Enterprise Trust Overview</h3>
               <p className="text-xs text-slate-400 mb-6">Real-time aggregate trust posture</p>
              
              <TrustGauge />
              
              <div className="mt-8 space-y-4">
                <div className="flex justify-between items-center text-sm border-b border-[#2A0B12] pb-2">
                   <span className="text-slate-400">Enterprise Trust Score</span>
                  <span className="font-bold text-emerald-400">A+</span>
                </div>
                <div className="flex justify-between items-center text-sm border-b border-[#2A0B12] pb-2">
                  <span className="text-slate-400">Average Agent Confidence</span>
                  <span className="font-bold text-white">93.4%</span>
                </div>
                <div className="flex justify-between items-center text-sm border-b border-[#2A0B12] pb-2">
                  <span className="text-slate-400">Most Triggered Policy</span>
                  <span className="font-medium text-[#FF4D6D] truncate max-w-[120px]">PII Data Masking</span>
                </div>
                <div>
                  <span className="text-xs text-slate-400 block mb-2">Top Active Threat Categories</span>
                  <div className="flex flex-wrap gap-2">
                    <span className="text-[10px] px-2 py-1 rounded bg-[#2A0B12] text-slate-300 border border-[#4B0F18]">Prompt Injection (42%)</span>
                    <span className="text-[10px] px-2 py-1 rounded bg-[#2A0B12] text-slate-300 border border-[#4B0F18]">Data Exfiltration (28%)</span>
                    <span className="text-[10px] px-2 py-1 rounded bg-[#2A0B12] text-slate-300 border border-[#4B0F18]">Hallucination (15%)</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Live Threat Feed */}
            <div className="bg-gradient-to-br from-[#1a0c0e]/90 to-[#120809]/80 backdrop-blur-xl border border-[#2A0B12] p-6 rounded-2xl flex-1 shadow-lg hover:border-[#DC143C]/20 transition-all duration-300">
              <div className="flex justify-between items-center mb-6">
                <h3 className="text-sm font-semibold text-white uppercase tracking-wider flex items-center gap-2">
                  <div className="w-2 h-2 rounded-full bg-[#DC143C] animate-pulse" /> Live Threat Feed
                </h3>
              </div>
              <ThreatTimeline threats={mockThreats} />
              <button className="w-full mt-6 py-2 border border-[#4B0F18] rounded-md text-xs font-medium text-[#FF4D6D] hover:bg-[#2A0B12] transition-colors">
                 View All Trust Events
              </button>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}
