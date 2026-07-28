import React from 'react';
import PageHeader from '@/components/PageHeader';
import { Download, FileText, Calendar, ShieldCheck, Activity, Brain, Clock, Plus } from 'lucide-react';

const reportTypes = [
  { id: 1, title: "Executive Summary", desc: "High-level overview of AI risk, trust, and usage across the enterprise.", icon: Activity },
  { id: 2, title: "Compliance Audit", desc: "Detailed breakdown of HIPAA, GDPR, and internal policy adherence.", icon: ShieldCheck },
  { id: 3, title: "Threat Landscape", desc: "Analysis of blocked prompt injections and identified vulnerabilities.", icon: Calendar },
  { id: 4, title: "Agent Performance", desc: "Latency, accuracy, and task load metrics for all active agents.", icon: Brain },
];

const recentReports = [
  { id: "REP-104", name: "Q3 AI Security Posture", date: "Oct 24, 2023", type: "Executive", author: "j.doe@enterprise.com", status: "Ready" },
  { id: "REP-103", name: "Weekly Compliance Sync", date: "Oct 18, 2023", type: "Compliance", author: "system_auto", status: "Ready" },
  { id: "REP-102", name: "Incident: Copilot Data Leak", date: "Oct 12, 2023", type: "Threat", author: "m.smith@enterprise.com", status: "Ready" },
  { id: "REP-101", name: "Agent Latency Review", date: "Oct 05, 2023", type: "Performance", author: "j.doe@enterprise.com", status: "Archived" },
];

export default function Reports() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-[#120809] via-[#1A090D] to-[#2A0B12] text-slate-200 p-4 md:p-8 font-sans selection:bg-[#DC143C]/30 relative overflow-hidden z-0">
      <div className="fixed inset-0 pointer-events-none -z-10">
        <div className="absolute top-0 left-1/4 w-[800px] h-[600px] bg-[#4B0F18]/20 rounded-full blur-[120px] mix-blend-screen" />
        <div className="absolute bottom-0 right-1/4 w-[600px] h-[600px] bg-[#DC143C]/10 rounded-full blur-[150px] mix-blend-screen" />
      </div>

      <div className="w-full">
        <PageHeader 
          title="Reports & Analytics" 
          description="Generate, schedule, and export enterprise AI governance reports."
          actions={
            <button className="flex items-center gap-2 bg-[#DC143C] hover:bg-[#FF4D6D] text-white px-5 py-2.5 rounded-lg font-medium text-sm transition-all shadow-[0_0_15px_rgba(220,20,60,0.4)]">
              <Plus className="h-4 w-4" /> New Report
            </button>
          }
        />

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 pb-12">
          
          {/* Left Column: Report Types */}
          <div className="lg:col-span-2 space-y-6">
            <h2 className="text-xl font-bold text-white mb-4">Available Report Templates</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {reportTypes.map((report) => {
                const Icon = report.icon;
                return (
                  <div key={report.id} className="bg-gradient-to-br from-[#1a0c0e]/90 to-[#120809]/80 backdrop-blur-xl border border-[#2A0B12] rounded-2xl p-6 shadow-lg hover:border-[#DC143C]/40 hover:shadow-[0_0_20px_rgba(220,20,60,0.15)] transition-all duration-300 group cursor-pointer">
                    <div className="flex items-start gap-4 mb-4">
                      <div className="h-12 w-12 rounded-xl bg-[#2A0B12] flex items-center justify-center border border-[#4B0F18] shadow-[0_0_15px_rgba(255,77,109,0.1)]">
                        <Icon className="h-6 w-6 text-[#FF4D6D]" />
                      </div>
                      <div>
                        <h3 className="font-bold text-white text-lg group-hover:text-[#FF4D6D] transition-colors">{report.title}</h3>
                        <p className="text-sm text-slate-400 mt-1">{report.desc}</p>
                      </div>
                    </div>
                    <div className="flex gap-3 mt-6">
                      <button className="flex-1 flex items-center justify-center gap-2 bg-[#120809] hover:bg-[#2A0B12] border border-[#4B0F18] text-slate-300 px-3 py-2 rounded-lg text-sm transition-colors">
                        <Download className="h-4 w-4" /> PDF
                      </button>
                      <button className="flex-1 flex items-center justify-center gap-2 bg-[#120809] hover:bg-[#2A0B12] border border-[#4B0F18] text-slate-300 px-3 py-2 rounded-lg text-sm transition-colors">
                        <Download className="h-4 w-4" /> CSV
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Right Column: Recent Reports */}
          <div className="space-y-6">
            <h2 className="text-xl font-bold text-white mb-4">Recent Generations</h2>
            <div className="bg-gradient-to-br from-[#1a0c0e]/90 to-[#120809]/80 backdrop-blur-xl border border-[#2A0B12] rounded-2xl p-2 shadow-lg">
              <div className="space-y-1">
                {recentReports.map((report) => (
                  <div key={report.id} className="p-4 rounded-xl hover:bg-[#2A0B12]/50 transition-colors border border-transparent hover:border-[#4B0F18] cursor-pointer flex items-center gap-4">
                    <div className="p-2 bg-[#120809] rounded-lg border border-[#4B0F18]">
                      <FileText className="h-5 w-5 text-slate-400" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <h4 className="text-sm font-bold text-white truncate">{report.name}</h4>
                      <div className="flex items-center gap-3 text-xs text-slate-400 mt-1">
                        <span className="flex items-center gap-1"><Clock className="h-3 w-3" /> {report.date}</span>
                        <span>{report.type}</span>
                      </div>
                    </div>
                    <div>
                      <span className={`px-2 py-1 rounded text-xs font-semibold ${
                        report.status === 'Ready' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-slate-500/10 text-slate-400 border border-slate-500/20'
                      }`}>
                        {report.status}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
              <div className="p-4 mt-2 border-t border-[#2A0B12]">
                <button className="w-full text-center text-sm font-medium text-[#FF4D6D] hover:text-white transition-colors">
                  View All Reports
                </button>
              </div>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
}
