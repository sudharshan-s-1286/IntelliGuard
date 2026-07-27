import React, { useState } from 'react';
import PageHeader from '@/components/PageHeader';
import { Settings as SettingsIcon, Shield, Bell, Key, Users, Sliders, Database, Box, Palette, Save } from 'lucide-react';

const settingsTabs = [
  { id: 'general', name: 'General', icon: SettingsIcon },
  { id: 'agents', name: 'AI Agents', icon: Shield },
  { id: 'thresholds', name: 'Risk Thresholds', icon: Sliders },
  { id: 'policies', name: 'Policies', icon: Database },
  { id: 'notifications', name: 'Notifications', icon: Bell },
  { id: 'keys', name: 'API Keys', icon: Key },
  { id: 'integrations', name: 'Integrations', icon: Box },
  { id: 'users', name: 'User Management', icon: Users },
  { id: 'theme', name: 'Theme', icon: Palette },
];

export default function Settings() {
  const [activeTab, setActiveTab] = useState('general');

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#120809] via-[#1A090D] to-[#2A0B12] text-slate-200 p-4 md:p-8 font-sans selection:bg-[#DC143C]/30 relative overflow-hidden z-0">
      <div className="fixed inset-0 pointer-events-none -z-10">
        <div className="absolute top-0 left-1/4 w-[800px] h-[600px] bg-[#4B0F18]/20 rounded-full blur-[120px] mix-blend-screen" />
        <div className="absolute bottom-0 right-1/4 w-[600px] h-[600px] bg-[#DC143C]/10 rounded-full blur-[150px] mix-blend-screen" />
      </div>

      <div className="w-full">
        <PageHeader 
          title="Enterprise Settings" 
          description="Configure AI governance rules, risk thresholds, and platform integrations."
          actions={
            <button className="flex items-center gap-2 bg-[#DC143C] hover:bg-[#FF4D6D] text-white px-5 py-2.5 rounded-lg font-medium text-sm transition-all shadow-[0_0_15px_rgba(220,20,60,0.4)]">
              <Save className="h-4 w-4" /> Save Changes
            </button>
          }
        />

        <div className="flex flex-col lg:flex-row gap-8 pb-12">
          
          {/* Sidebar Navigation */}
          <div className="w-full lg:w-64 shrink-0">
            <div className="bg-gradient-to-br from-[#1a0c0e]/90 to-[#120809]/80 backdrop-blur-xl border border-[#2A0B12] rounded-2xl p-4 shadow-lg flex flex-col gap-1">
              {settingsTabs.map((tab) => {
                const Icon = tab.icon;
                const isActive = activeTab === tab.id;
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all text-sm font-medium ${
                      isActive 
                        ? 'bg-[#2A0B12] text-white border border-[#4B0F18] shadow-[0_0_10px_rgba(255,77,109,0.1)]' 
                        : 'text-slate-400 hover:text-white hover:bg-[#1a0c0e] border border-transparent'
                    }`}
                  >
                    <Icon className={`h-4 w-4 ${isActive ? 'text-[#DC143C]' : ''}`} />
                    {tab.name}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Settings Content Area */}
          <div className="flex-1 bg-gradient-to-br from-[#1a0c0e]/90 to-[#120809]/80 backdrop-blur-xl border border-[#2A0B12] rounded-2xl p-6 md:p-8 shadow-lg min-h-[500px]">
            
            {activeTab === 'general' && (
              <div className="space-y-8 animate-in fade-in duration-300">
                <div>
                  <h2 className="text-xl font-bold text-white mb-1">General Settings</h2>
                  <p className="text-sm text-slate-400">Manage basic organization details and preferences.</p>
                </div>
                
                <div className="space-y-6 max-w-2xl">
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">Organization Name</label>
                    <input type="text" defaultValue="Acme Corp Enterprise" className="w-full bg-[#120809] border border-[#4B0F18] rounded-lg px-4 py-2 text-white focus:outline-none focus:border-[#DC143C] transition-colors" />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">Support Email</label>
                    <input type="email" defaultValue="security@acmecorp.com" className="w-full bg-[#120809] border border-[#4B0F18] rounded-lg px-4 py-2 text-white focus:outline-none focus:border-[#DC143C] transition-colors" />
                  </div>
                  <div className="flex items-center justify-between p-4 bg-[#2A0B12]/50 border border-[#4B0F18] rounded-lg">
                    <div>
                      <h4 className="text-sm font-bold text-white">Maintenance Mode</h4>
                      <p className="text-xs text-slate-400 mt-1">Suspend all AI integrations globally during updates.</p>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input type="checkbox" className="sr-only peer" />
                      <div className="w-11 h-6 bg-[#120809] peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-slate-400 peer-checked:after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-[#DC143C] border border-[#4B0F18]"></div>
                    </label>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'agents' && (
              <div className="space-y-8 animate-in fade-in duration-300">
                <div>
                  <h2 className="text-xl font-bold text-white mb-1">AI Agent Configuration</h2>
                  <p className="text-sm text-slate-400">Toggle active agents and configure their global behavior.</p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {['Security Agent', 'Privacy Agent', 'Compliance Agent', 'Trust Agent', 'Decision Agent', 'Remediation Agent'].map((agent, i) => (
                    <div key={i} className="p-4 bg-[#120809] border border-[#4B0F18] rounded-xl flex items-center justify-between group hover:border-[#DC143C]/50 transition-colors">
                      <div className="flex items-center gap-3">
                        <div className="h-2 w-2 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.8)]" />
                        <span className="font-medium text-slate-200">{agent}</span>
                      </div>
                      <label className="relative inline-flex items-center cursor-pointer">
                        <input type="checkbox" defaultChecked className="sr-only peer" />
                        <div className="w-9 h-5 bg-[#2A0B12] rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-[#DC143C]"></div>
                      </label>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {activeTab === 'keys' && (
              <div className="space-y-8 animate-in fade-in duration-300">
                <div>
                  <h2 className="text-xl font-bold text-white mb-1">API Keys</h2>
                  <p className="text-sm text-slate-400">Manage API keys used by external systems to push requests to IntelliGuard.</p>
                </div>

                <div className="space-y-4">
                  <div className="flex justify-end mb-4">
                    <button className="bg-[#2A0B12] hover:bg-[#4B0F18] border border-[#DC143C]/30 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors">
                      + Generate New Key
                    </button>
                  </div>
                  
                  <div className="border border-[#4B0F18] rounded-lg overflow-hidden">
                    <table className="w-full text-left">
                      <thead className="bg-[#120809]">
                        <tr>
                          <th className="px-4 py-3 text-xs font-semibold text-slate-400 uppercase">Key Name</th>
                          <th className="px-4 py-3 text-xs font-semibold text-slate-400 uppercase">Prefix</th>
                          <th className="px-4 py-3 text-xs font-semibold text-slate-400 uppercase">Created</th>
                          <th className="px-4 py-3 text-xs font-semibold text-slate-400 uppercase">Status</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-[#2A0B12] bg-[#1a0c0e]">
                        <tr>
                          <td className="px-4 py-3 text-sm text-white">Production Gateway</td>
                          <td className="px-4 py-3 text-sm text-slate-400 font-mono">ig_live_****</td>
                          <td className="px-4 py-3 text-sm text-slate-400">Oct 10, 2023</td>
                          <td className="px-4 py-3"><span className="px-2 py-1 rounded text-xs bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">Active</span></td>
                        </tr>
                        <tr>
                          <td className="px-4 py-3 text-sm text-white">Staging CRM</td>
                          <td className="px-4 py-3 text-sm text-slate-400 font-mono">ig_test_****</td>
                          <td className="px-4 py-3 text-sm text-slate-400">Sep 24, 2023</td>
                          <td className="px-4 py-3"><span className="px-2 py-1 rounded text-xs bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">Active</span></td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            )}

            {activeTab !== 'general' && activeTab !== 'agents' && activeTab !== 'keys' && (
              <div className="flex flex-col items-center justify-center h-64 text-center animate-in fade-in duration-300">
                <SettingsIcon className="h-12 w-12 text-[#4B0F18] mb-4" />
                <h3 className="text-lg font-bold text-slate-300">Configuration Pane Placeholder</h3>
                <p className="text-sm text-slate-500 mt-2 max-w-sm">This section is available in the enterprise edition. Configuration options will be exposed once the backend API is connected.</p>
              </div>
            )}

          </div>

        </div>
      </div>
    </div>
  );
}
