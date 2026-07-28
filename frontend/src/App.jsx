import React, { useEffect, useState } from 'react'
import { Routes, Route } from 'react-router-dom'
import AppLayout from './layouts/AppLayout'
import { getHealth } from './services/securityApi'

import Home from './pages/Home'
import Dashboard from './pages/Dashboard'
import Agents from './pages/Agents'
import Analytics from './pages/Analytics'
import Audit from './pages/Audit'
import Reports from './pages/Reports'
import Settings from './pages/Settings'
import ScrollToTop from './components/ScrollToTop'

function App() {
  const [healthStatus, setHealthStatus] = useState(null);

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const data = await getHealth();
        if (data && (data.status === 'SUCCESS' || data.status === 'ok' || data.status === 'healthy' || Object.keys(data).length > 0)) {
          setHealthStatus('online');
          console.log('🟢 Security Agent Online');
        } else {
          setHealthStatus('offline');
          console.error('🔴 Security Agent Offline - Unexpected response', data);
        }
      } catch (error) {
        setHealthStatus('offline');
        console.error('🔴 Security Agent Offline', error);
      }
    };
    checkHealth();
  }, []);

  return (
    <>
      <ScrollToTop />
      {healthStatus && (
        <div className={`fixed bottom-4 right-4 z-50 px-4 py-2 rounded-full shadow-lg border text-sm font-medium flex items-center gap-2 ${
          healthStatus === 'online' 
            ? 'bg-[#120809] text-emerald-400 border border-[#2A0B12]'
            : 'bg-[#120809] text-red-400 border border-[#2A0B12]'
        }`}>
          <div className={`w-2 h-2 rounded-full ${healthStatus === 'online' ? 'bg-emerald-400' : 'bg-red-400'} animate-pulse`} />
          {healthStatus === 'online' ? 'Security Agent Online' : 'Security Agent Offline'}
        </div>
      )}
      <Routes>
        <Route path="/" element={<Home />} />
        <Route element={<AppLayout />}>
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/agents" element={<Agents />} />
          <Route path="/analytics" element={<Analytics />} />
          <Route path="/audit" element={<Audit />} />
          <Route path="/reports" element={<Reports />} />
          <Route path="/settings" element={<Settings />} />
        </Route>
      </Routes>
    </>
  )
}

export default App
