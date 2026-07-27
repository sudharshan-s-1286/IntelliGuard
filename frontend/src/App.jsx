import React from 'react'
import { Routes, Route } from 'react-router-dom'
import AppLayout from './layouts/AppLayout'

import Home from './pages/Home'
import Dashboard from './pages/Dashboard'
import Agents from './pages/Agents'
import Analytics from './pages/Analytics'
import Audit from './pages/Audit'
import Reports from './pages/Reports'
import Settings from './pages/Settings'
import ScrollToTop from './components/ScrollToTop'

function App() {
  return (
    <>
      <ScrollToTop />
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
