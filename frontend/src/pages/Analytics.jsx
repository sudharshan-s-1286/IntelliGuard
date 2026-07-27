import React from 'react';
import { 
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer,
  BarChart, Bar, PieChart, Pie, Cell, Legend, LineChart, Line
} from 'recharts';
import { 
  ShieldAlert, TrendingUp, AlertOctagon, BrainCircuit, Activity, ShieldCheck, 
  AlertTriangle, CheckCircle2, ChevronRight, Zap, BarChart3, Database
} from 'lucide-react';
import PageHeader from '@/components/PageHeader';

import {
  trustTrendData,
  riskDistributionData,
  promptInjectionData,
  hallucinationTrendData,
  privacyRiskData,
  dailyRequestsData,
  monthlyUsageData,
  allowedVsBlockedData,
  kpiData,
  agentPerformanceData,
  threatFeed,
  recommendations
} from '../mockAnalyticsData';

const COLORS = ['#10B981', '#F59E0B', '#F97316', '#DC143C'];

const customTooltipStyle = {
  backgroundColor: '#120809',
  border: '1px solid #4B0F18',
  borderRadius: '0.5rem',
  color: '#f8fafc',
  boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.5)',
};

const SectionTitle = ({ title, subtitle }) => (
  <div className="mb-6 mt-10">
    <h2 className="text-2xl font-bold text-white tracking-tight">{title}</h2>
    {subtitle && <p className="text-sm text-slate-400 mt-1">{subtitle}</p>}
  </div>
);

const ChartContainer = ({ title, icon: Icon, children, colSpan = 1 }) => (
  <div className={`bg-gradient-to-br from-[#1a0c0e]/90 to-[#120809]/80 backdrop-blur-xl border border-[#2A0B12] rounded-2xl p-6 shadow-lg lg:col-span-${colSpan} flex flex-col hover:border-[#DC143C]/40 hover:shadow-[0_0_20px_rgba(220,20,60,0.15)] transition-all duration-300`}>
    <div className="flex items-center gap-3 mb-6">
      <div className="p-2 bg-[#2A0B12] rounded-lg border border-[#4B0F18]">
        <Icon className="h-5 w-5 text-[#FF4D6D]" />
      </div>
      <h3 className="font-bold text-white tracking-wide">{title}</h3>
    </div>
    <div className="flex-1 w-full min-h-[300px]">
      {children}
    </div>
  </div>
);

export default function Analytics() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-[#120809] via-[#1A090D] to-[#2A0B12] text-slate-200 p-4 md:p-8 font-sans selection:bg-[#DC143C]/30 relative overflow-hidden z-0">
      <div className="fixed inset-0 pointer-events-none -z-10">
        <div className="absolute top-0 left-1/4 w-[800px] h-[600px] bg-[#4B0F18]/20 rounded-full blur-[120px] mix-blend-screen" />
        <div className="absolute bottom-0 right-1/4 w-[600px] h-[600px] bg-[#DC143C]/10 rounded-full blur-[150px] mix-blend-screen" />
      </div>

      <div className="w-full pb-16">
        <PageHeader 
          title="Executive Intelligence Center" 
          description="Advanced macro-level analytics providing deep insights into enterprise AI risk, trust, and utilization."
        />

        {/* 1. Analytics Overview (KPIs) */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {kpiData.map((kpi, idx) => {
            const icons = [ShieldCheck, ShieldAlert, AlertTriangle, Activity];
            const Icon = icons[idx];
            const bg = idx === 1 ? "bg-[#DC143C]/10" : idx === 2 ? "bg-orange-500/10" : idx === 3 ? "bg-blue-500/10" : "bg-emerald-500/10";
            const border = idx === 1 ? "border-[#DC143C]/20" : idx === 2 ? "border-orange-500/20" : idx === 3 ? "border-blue-500/20" : "border-emerald-500/20";
            const color = idx === 1 ? "text-[#DC143C]" : idx === 2 ? "text-orange-400" : idx === 3 ? "text-blue-400" : "text-emerald-400";
            
            return (
              <div key={idx} className="bg-gradient-to-br from-[#1a0c0e]/90 to-[#120809]/80 backdrop-blur-xl border border-[#2A0B12] rounded-2xl p-6 shadow-lg hover:border-[#DC143C]/40 hover:shadow-[0_0_20px_rgba(220,20,60,0.15)] transition-all duration-300">
                <div className="flex justify-between items-start mb-4">
                  <div className={`p-3 rounded-xl border ${bg} ${border}`}>
                    <Icon className={`h-6 w-6 ${color}`} />
                  </div>
                  <span className={`text-xs font-bold px-2 py-1 rounded bg-[#2A0B12] border border-[#4B0F18] ${kpi.trend.startsWith('+') ? 'text-emerald-400' : 'text-red-400'}`}>
                    {kpi.trend}
                  </span>
                </div>
                <p className="text-sm font-semibold text-slate-400 uppercase tracking-wider">{kpi.title}</p>
                <h3 className="text-3xl font-extrabold text-white mt-1">{kpi.value}</h3>
              </div>
            );
          })}
        </div>

        {/* 2. Risk Intelligence */}
        <SectionTitle title="Risk Intelligence" subtitle="Macro trends in organizational trust and risk distribution." />
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <ChartContainer title="Enterprise Trust Trend" icon={TrendingUp}>
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={trustTrendData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#2A0B12" vertical={false} />
                <XAxis dataKey="month" stroke="#64748b" tickLine={false} axisLine={false} />
                <YAxis stroke="#64748b" tickLine={false} axisLine={false} domain={['dataMin - 2', 'dataMax + 2']} />
                <RechartsTooltip contentStyle={customTooltipStyle} />
                <Line type="monotone" dataKey="trust" stroke="#10B981" strokeWidth={3} dot={{ fill: '#120809', stroke: '#10B981', strokeWidth: 2 }} name="Trust Score" />
              </LineChart>
            </ResponsiveContainer>
          </ChartContainer>

          <ChartContainer title="Risk Distribution" icon={AlertOctagon}>
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={riskDistributionData} cx="50%" cy="50%" innerRadius={70} outerRadius={110} paddingAngle={5} dataKey="value" stroke="none">
                  {riskDistributionData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <RechartsTooltip contentStyle={customTooltipStyle} />
                <Legend verticalAlign="bottom" height={36} iconType="circle" />
              </PieChart>
            </ResponsiveContainer>
          </ChartContainer>
        </div>

        {/* 3. Threat Intelligence */}
        <SectionTitle title="Threat Intelligence" subtitle="Specific attack vectors and AI failure modes." />
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <ChartContainer title="Prompt Injection Timeline" icon={ShieldAlert}>
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={promptInjectionData}>
                <defs>
                  <linearGradient id="colorInjection" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#DC143C" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#DC143C" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#2A0B12" vertical={false} />
                <XAxis dataKey="time" stroke="#64748b" tickLine={false} axisLine={false} />
                <YAxis stroke="#64748b" tickLine={false} axisLine={false} />
                <RechartsTooltip contentStyle={customTooltipStyle} />
                <Area type="monotone" dataKey="attempts" stroke="#DC143C" strokeWidth={2} fillOpacity={1} fill="url(#colorInjection)" name="Injection Attempts" />
              </AreaChart>
            </ResponsiveContainer>
          </ChartContainer>

          <ChartContainer title="Hallucination Trend" icon={BrainCircuit}>
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={hallucinationTrendData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#2A0B12" vertical={false} />
                <XAxis dataKey="week" stroke="#64748b" tickLine={false} axisLine={false} />
                <YAxis stroke="#64748b" tickLine={false} axisLine={false} />
                <RechartsTooltip contentStyle={customTooltipStyle} />
                <Line type="monotone" dataKey="score" stroke="#F59E0B" strokeWidth={3} dot={{ fill: '#120809', stroke: '#F59E0B', strokeWidth: 2 }} name="Avg Hallucination Score" />
              </LineChart>
            </ResponsiveContainer>
          </ChartContainer>

          <ChartContainer title="Privacy Risk Heatmap" icon={AlertTriangle}>
             <ResponsiveContainer width="100%" height="100%">
              <BarChart data={privacyRiskData} layout="vertical" margin={{ top: 0, right: 0, left: 20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#2A0B12" horizontal={false} />
                <XAxis type="number" stroke="#64748b" tickLine={false} axisLine={false} />
                <YAxis dataKey="category" type="category" stroke="#64748b" tickLine={false} axisLine={false} width={80} />
                <RechartsTooltip contentStyle={customTooltipStyle} cursor={{fill: '#2A0B12'}} />
                <Legend />
                <Bar dataKey="low" stackId="a" fill="#10B981" name="Low Risk" />
                <Bar dataKey="medium" stackId="a" fill="#F59E0B" name="Medium Risk" />
                <Bar dataKey="high" stackId="a" fill="#DC143C" name="High Risk" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </ChartContainer>
        </div>

        {/* 4. Agent Performance Analytics & 6. Threat Feed */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-10">
          
          <div className="lg:col-span-2">
            <h2 className="text-2xl font-bold text-white tracking-tight mb-6">Agent Performance Analytics</h2>
            <div className="bg-gradient-to-br from-[#1a0c0e]/90 to-[#120809]/80 backdrop-blur-xl border border-[#2A0B12] rounded-2xl overflow-hidden shadow-lg hover:border-[#DC143C]/40 transition-all duration-300">
              <div className="overflow-x-auto">
                <table className="w-full text-left border-collapse">
                  <thead>
                    <tr className="bg-[#120809] border-b border-[#4B0F18]">
                      <th className="px-6 py-4 text-xs font-semibold text-slate-400 uppercase tracking-wider">Agent</th>
                      <th className="px-6 py-4 text-xs font-semibold text-slate-400 uppercase tracking-wider">Avg Response</th>
                      <th className="px-6 py-4 text-xs font-semibold text-slate-400 uppercase tracking-wider">Accuracy</th>
                      <th className="px-6 py-4 text-xs font-semibold text-slate-400 uppercase tracking-wider">Confidence</th>
                      <th className="px-6 py-4 text-xs font-semibold text-slate-400 uppercase tracking-wider">Health</th>
                      <th className="px-6 py-4 text-xs font-semibold text-slate-400 uppercase tracking-wider">Requests Processed</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[#2A0B12]">
                    {agentPerformanceData.map((agent, idx) => (
                      <tr key={idx} className="hover:bg-[#2A0B12]/50 transition-colors">
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-bold text-white">{agent.name}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-300">{agent.response}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-emerald-400 font-semibold">{agent.accuracy}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-300">{agent.confidence}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm flex items-center gap-2">
                          <CheckCircle2 className="h-4 w-4 text-emerald-500" /> {agent.health}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-400">{agent.requests}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          <div className="lg:col-span-1">
            <h2 className="text-2xl font-bold text-white tracking-tight mb-6">Threat Intelligence Feed</h2>
            <div className="bg-gradient-to-br from-[#1a0c0e]/90 to-[#120809]/80 backdrop-blur-xl border border-[#2A0B12] rounded-2xl p-6 shadow-lg hover:border-[#DC143C]/40 transition-all duration-300 h-[calc(100%-3rem)]">
              <div className="space-y-6 relative before:absolute before:inset-0 before:ml-2 before:-translate-x-px before:h-full before:w-0.5 before:bg-gradient-to-b before:from-transparent before:via-[#4B0F18] before:to-transparent">
                {threatFeed.map((feed, idx) => (
                  <div key={idx} className="relative flex items-start group">
                    <div className={`flex items-center justify-center w-4 h-4 rounded-full border-2 border-[#120809] shrink-0 mt-1 mr-4 z-10 ${
                      feed.severity === 'critical' ? 'bg-[#DC143C] shadow-[0_0_8px_#DC143C]' : 
                      feed.severity === 'high' ? 'bg-orange-500 shadow-[0_0_8px_#f97316]' : 'bg-yellow-500'
                    }`} />
                    <div className="bg-[#120809]/50 p-4 rounded-xl border border-[#4B0F18]/50 w-full group-hover:border-[#DC143C]/30 transition-colors">
                      <div className="flex justify-between items-start mb-2">
                        <span className={`text-xs font-bold uppercase ${
                          feed.severity === 'critical' ? 'text-red-400' : feed.severity === 'high' ? 'text-orange-400' : 'text-yellow-400'
                        }`}>{feed.event}</span>
                        <span className="text-xs text-slate-500">{feed.time}</span>
                      </div>
                      <p className="text-sm text-slate-300 mb-2">{feed.desc}</p>
                      <span className="text-xs text-slate-500 font-medium bg-[#2A0B12] px-2 py-1 rounded">{feed.agent}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

        </div>

        {/* 5. Enterprise AI Usage */}
        <SectionTitle title="Enterprise AI Usage" subtitle="Volume and throughput of LLM requests vs blocked policy violations." />
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <ChartContainer title="Daily AI Requests" icon={BarChart3}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={dailyRequestsData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#2A0B12" vertical={false} />
                <XAxis dataKey="day" stroke="#64748b" tickLine={false} axisLine={false} />
                <YAxis stroke="#64748b" tickLine={false} axisLine={false} />
                <RechartsTooltip contentStyle={customTooltipStyle} cursor={{fill: '#2A0B12'}} />
                <Bar dataKey="requests" fill="#3B82F6" radius={[4, 4, 0, 0]} name="Total Requests" />
              </BarChart>
            </ResponsiveContainer>
          </ChartContainer>

          <ChartContainer title="Monthly AI Usage" icon={TrendingUp}>
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={monthlyUsageData}>
                <defs>
                  <linearGradient id="colorMonthly" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10B981" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#10B981" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#2A0B12" vertical={false} />
                <XAxis dataKey="month" stroke="#64748b" tickLine={false} axisLine={false} />
                <YAxis stroke="#64748b" tickLine={false} axisLine={false} />
                <RechartsTooltip contentStyle={customTooltipStyle} />
                <Area type="monotone" dataKey="queries" stroke="#10B981" strokeWidth={2} fillOpacity={1} fill="url(#colorMonthly)" name="Total Queries" />
              </AreaChart>
            </ResponsiveContainer>
          </ChartContainer>

          <ChartContainer title="Allowed vs Blocked" icon={Database}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={allowedVsBlockedData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#2A0B12" vertical={false} />
                <XAxis dataKey="month" stroke="#64748b" tickLine={false} axisLine={false} />
                <YAxis stroke="#64748b" tickLine={false} axisLine={false} />
                <RechartsTooltip contentStyle={customTooltipStyle} cursor={{fill: '#2A0B12'}} />
                <Legend />
                <Bar dataKey="allowed" stackId="a" fill="#3B82F6" name="Allowed" />
                <Bar dataKey="blocked" stackId="a" fill="#DC143C" name="Blocked" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </ChartContainer>
        </div>

        {/* 7. Enterprise Recommendations */}
        <SectionTitle title="Enterprise Recommendations" subtitle="Actionable insights automatically generated by the Orchestrator Agent." />
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {recommendations.map((rec, idx) => (
            <div key={idx} className="bg-gradient-to-br from-[#1a0c0e]/90 to-[#120809]/80 backdrop-blur-xl border border-[#2A0B12] rounded-2xl p-6 shadow-lg hover:border-[#DC143C]/40 hover:shadow-[0_0_20px_rgba(220,20,60,0.15)] transition-all duration-300 flex flex-col justify-between">
              <div>
                <div className="flex items-center gap-2 mb-3">
                  <Zap className="h-5 w-5 text-yellow-500" />
                  <h4 className="font-bold text-white leading-tight">{rec.title}</h4>
                </div>
                <p className="text-sm text-slate-400 mb-6">{rec.desc}</p>
              </div>
              <button className="w-full flex items-center justify-center gap-2 bg-[#2A0B12] hover:bg-[#4B0F18] border border-[#DC143C]/30 text-[#FF4D6D] hover:text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors">
                {rec.action} <ChevronRight className="h-4 w-4" />
              </button>
            </div>
          ))}
        </div>

      </div>
    </div>
  );
}
