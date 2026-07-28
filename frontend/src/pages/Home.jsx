import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import LandingNavbar from '../components/LandingNavbar';
import { motion, useScroll, useTransform } from 'framer-motion';
import { 
  Shield, 
  Lock, 
  FileCheck, 
  Activity, 
  ArrowRight, 
  Server, 
  ShieldCheck, 
  Search, 
  Cpu,
  ChevronRight,
  Menu,
  X
} from 'lucide-react';

const colors = {
  bg1: "#120809",
  bg2: "#2A0B12",
  bg3: "#4B0F18",
  primary: "#DC143C",
  secondary: "#FF4D6D"
};

// Replaced local Navbar with shared component

const AnimatedVisualization = () => {
  return (
    <div className="relative w-full h-[500px] flex items-center justify-center p-8">
      {/* Background glow */}
      <div className="absolute inset-0 bg-gradient-to-tr from-[#DC143C]/5 to-[#FF4D6D]/10 rounded-full blur-3xl" />
      
      <div className="relative w-full max-w-md mx-auto flex flex-col items-center gap-6">
        {/* User Node */}
        <motion.div 
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="bg-[#2A0B12]/80 backdrop-blur-sm border border-[#4B0F18] px-6 py-3 rounded-full shadow-[0_0_15px_rgba(220,20,60,0.2)] flex items-center gap-2 z-10"
        >
          <div className="h-3 w-3 rounded-full bg-[#FF4D6D] animate-pulse" />
          <span className="text-sm font-semibold text-slate-200">User Input</span>
        </motion.div>

        <div className="w-px h-8 bg-gradient-to-b from-[#DC143C] to-transparent relative">
          <motion.div 
            animate={{ y: [0, 32, 0], opacity: [0, 1, 0] }}
            transition={{ repeat: Infinity, duration: 2, ease: "linear" }}
            className="absolute top-0 left-1/2 -translate-x-1/2 w-1.5 h-1.5 rounded-full bg-[#FF4D6D] shadow-[0_0_8px_#FF4D6D]"
          />
        </div>

        {/* Orchestrator Node */}
        <motion.div 
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5, delay: 0.4 }}
          className="bg-[#120809] border border-[#DC143C]/50 p-4 rounded-xl shadow-[0_0_20px_rgba(220,20,60,0.3)] z-10 w-48 text-center relative overflow-hidden"
        >
          <div className="absolute inset-0 bg-gradient-to-r from-transparent via-[#DC143C]/10 to-transparent -translate-x-full animate-[shimmer_2s_infinite]" />
          <Cpu className="h-6 w-6 text-[#DC143C] mx-auto mb-2" />
          <span className="text-sm font-bold text-white tracking-wide">Orchestrator Agent</span>
        </motion.div>

        {/* Connecting lines to agents */}
        <div className="flex w-64 justify-between relative h-12">
          {/* Central drop */}
          <div className="absolute left-1/2 top-0 bottom-0 w-px bg-[#4B0F18]" />
          {/* Top horizontal */}
          <div className="absolute top-0 left-4 right-4 h-px bg-[#4B0F18]" />
          {/* Drops to agents */}
          <div className="absolute left-4 top-0 bottom-0 w-px bg-[#4B0F18]" />
          <div className="absolute left-[30%] top-0 bottom-0 w-px bg-[#4B0F18]" />
          <div className="absolute right-[30%] top-0 bottom-0 w-px bg-[#4B0F18]" />
          <div className="absolute right-4 top-0 bottom-0 w-px bg-[#4B0F18]" />
          
          {/* Animated particles */}
          <motion.div animate={{ y: [0, 48, 0], opacity: [0, 1, 0] }} transition={{ repeat: Infinity, duration: 1.5, delay: 0 }} className="absolute left-4 w-1 h-1 bg-[#FF4D6D] rounded-full blur-[1px]" />
          <motion.div animate={{ y: [0, 48, 0], opacity: [0, 1, 0] }} transition={{ repeat: Infinity, duration: 1.5, delay: 0.3 }} className="absolute left-[30%] w-1 h-1 bg-[#FF4D6D] rounded-full blur-[1px]" />
          <motion.div animate={{ y: [0, 48, 0], opacity: [0, 1, 0] }} transition={{ repeat: Infinity, duration: 1.5, delay: 0.6 }} className="absolute right-[30%] w-1 h-1 bg-[#FF4D6D] rounded-full blur-[1px]" />
          <motion.div animate={{ y: [0, 48, 0], opacity: [0, 1, 0] }} transition={{ repeat: Infinity, duration: 1.5, delay: 0.9 }} className="absolute right-4 w-1 h-1 bg-[#FF4D6D] rounded-full blur-[1px]" />
        </div>

        {/* Specialized Agents */}
        <div className="flex gap-3 z-10 w-full justify-center">
          {[
            { name: "Security", icon: Lock },
            { name: "Privacy", icon: ShieldCheck },
            { name: "Compliance", icon: FileCheck },
            { name: "Trust", icon: Activity }
          ].map((agent, i) => (
            <motion.div 
              key={agent.name}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.6 + (i * 0.1) }}
              className="bg-[#2A0B12]/60 backdrop-blur-sm border border-[#4B0F18] p-3 rounded-lg flex flex-col items-center gap-1 hover:border-[#DC143C]/50 transition-colors w-20"
            >
              <agent.icon className="h-4 w-4 text-[#FF4D6D]" />
              <span className="text-[10px] font-medium text-slate-300">{agent.name}</span>
            </motion.div>
          ))}
        </div>

        {/* Connecting lines to Decision */}
        <div className="flex w-64 justify-between relative h-12">
          <div className="absolute bottom-0 left-1/2 right-1/2 w-px bg-[#4B0F18]" />
          <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-px h-full bg-gradient-to-t from-[#DC143C] to-transparent">
             <motion.div 
              animate={{ y: [-48, 0, -48], opacity: [0, 1, 0] }}
              transition={{ repeat: Infinity, duration: 2, ease: "linear" }}
              className="absolute bottom-0 left-1/2 -translate-x-1/2 w-1.5 h-1.5 rounded-full bg-[#FF4D6D] shadow-[0_0_8px_#FF4D6D]"
            />
          </div>
        </div>

        {/* Decision & Enterprise Node */}
        <motion.div 
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5, delay: 1.2 }}
          className="bg-[#120809] border border-[#DC143C] px-6 py-4 rounded-xl shadow-[0_0_25px_rgba(220,20,60,0.4)] z-10 w-56 text-center"
        >
          <div className="text-xs font-semibold text-[#FF4D6D] uppercase tracking-wider mb-1">Validated</div>
          <span className="text-base font-bold text-white flex items-center justify-center gap-2">
            <Server className="h-4 w-4" /> Enterprise System
          </span>
        </motion.div>
      </div>
    </div>
  );
};

const HeroSection = () => {
  return (
    <section className="relative pt-32 pb-20 md:pt-48 md:pb-32 overflow-hidden" id="home">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          <motion.div 
            initial={{ opacity: 0, x: -30 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.7 }}
            className="max-w-2xl"
          >
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#2A0B12] border border-[#4B0F18] mb-6">
              <span className="flex h-2 w-2 rounded-full bg-[#DC143C] animate-pulse"></span>
              <span className="text-xs font-medium text-[#FF4D6D] tracking-wide uppercase">Enterprise Grade Security</span>
            </div>
            
            <h1 className="text-5xl sm:text-6xl lg:text-7xl font-extrabold text-white leading-[1.1] tracking-tight mb-6">
              Trust Every AI <br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#DC143C] to-[#FF4D6D]">
                Before It Enters
              </span><br />
              Your Enterprise
            </h1>
            
            <p className="text-lg sm:text-xl text-slate-400 mb-8 leading-relaxed max-w-xl">
              IntelliGuard validates enterprise AI systems using collaborative AI agents that analyze security, privacy, compliance, hallucination risk, and governance before deployment.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4">
              <Link to="/dashboard" className="inline-flex justify-center items-center gap-2 bg-[#DC143C] hover:bg-[#FF4D6D] text-white px-8 py-4 rounded-md font-medium text-base transition-all shadow-[0_0_20px_rgba(220,20,60,0.3)] hover:shadow-[0_0_30px_rgba(255,77,109,0.5)]">
                Launch Dashboard <ArrowRight className="h-5 w-5" />
              </Link>
              <a href="#architecture" className="inline-flex justify-center items-center gap-2 bg-transparent hover:bg-[#2A0B12] border border-[#4B0F18] text-white px-8 py-4 rounded-md font-medium text-base transition-all">
                Explore Architecture
              </a>
            </div>
          </motion.div>
          
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.7, delay: 0.2 }}
            className="relative"
          >
            <AnimatedVisualization />
          </motion.div>
        </div>
      </div>
    </section>
  );
};

const FeaturesSection = () => {
  const features = [
    {
      title: "AI Security Validation",
      description: "Detects prompt injections, jailbreaks, and adversarial attacks before they reach your internal systems.",
      icon: Lock
    },
    {
      title: "Shadow AI Discovery",
      description: "Identifies and maps unsanctioned AI models and endpoints operating within your enterprise network.",
      icon: Search
    },
    {
      title: "Enterprise Compliance",
      description: "Automates policy checks against GDPR, HIPAA, and internal data governance standards.",
      icon: FileCheck
    },
    {
      title: "Trust Scoring Engine",
      description: "Calculates an aggregate trust score based on continuous, real-time agentic evaluation.",
      icon: Activity
    }
  ];

  return (
    <section className="py-24 bg-[#120809] relative border-t border-[#2A0B12]" id="features">
      <div className="absolute top-0 inset-x-0 h-px bg-gradient-to-r from-transparent via-[#DC143C]/20 to-transparent" />
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-3xl mx-auto mb-16">
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">Comprehensive AI Governance</h2>
          <p className="text-slate-400 text-lg">Proactively secure your AI ecosystem with purpose-built evaluations tailored for the enterprise.</p>
        </div>
        
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          {features.map((feature, index) => (
            <motion.div 
              key={feature.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              whileHover={{ y: -5, borderColor: "rgba(220,20,60,0.5)" }}
              className="bg-[#1a0c0e] border border-[#2A0B12] rounded-xl p-6 transition-all group relative overflow-hidden"
            >
              <div className="absolute inset-0 bg-gradient-to-br from-[#DC143C]/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
              <div className="h-12 w-12 rounded-lg bg-[#2A0B12] border border-[#4B0F18] flex items-center justify-center mb-6 group-hover:bg-[#DC143C]/20 transition-colors relative z-10">
                <feature.icon className="h-6 w-6 text-[#FF4D6D]" />
              </div>
              <h3 className="text-xl font-semibold text-white mb-3 relative z-10">{feature.title}</h3>
              <p className="text-slate-400 leading-relaxed text-sm relative z-10">{feature.description}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};

const ArchitectureSection = () => {
  return (
    <section className="py-24 relative overflow-hidden bg-[#0c0506]" id="architecture">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="mb-16">
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">Multi-Agent Workflow</h2>
          <p className="text-slate-400 text-lg max-w-2xl">A unified pipeline where specialized AI agents collaborate to evaluate and secure every interaction.</p>
        </div>

        <div className="relative max-w-5xl mx-auto py-12">
          {/* Horizontal Desktop View */}
          <div className="hidden lg:flex items-center justify-between relative">
            
            {/* Background connecting line */}
            <div className="absolute left-0 right-0 top-1/2 -translate-y-1/2 h-0.5 bg-[#2A0B12] -z-10" />
            <div className="absolute left-0 right-0 top-1/2 -translate-y-1/2 h-0.5 bg-gradient-to-r from-[#DC143C] via-[#FF4D6D] to-[#DC143C] -z-10 opacity-30 animate-pulse" />

            {/* Nodes */}
            <motion.div initial={{opacity: 0, x:-20}} whileInView={{opacity:1, x:0}} viewport={{once:true}} className="bg-[#120809] border border-[#4B0F18] p-4 rounded-lg w-40 text-center shrink-0 z-10">
              <span className="text-sm font-semibold text-white block mb-1">User Prompt</span>
              <span className="text-xs text-slate-500">Input Data</span>
            </motion.div>

            <ChevronRight className="text-[#DC143C] w-6 h-6 shrink-0 bg-[#0c0506]" />

            <motion.div initial={{opacity: 0, x:-20}} whileInView={{opacity:1, x:0}} viewport={{once:true}} transition={{delay: 0.1}} className="bg-[#2A0B12] border border-[#DC143C]/40 p-4 rounded-lg w-44 text-center shrink-0 z-10 shadow-[0_0_15px_rgba(220,20,60,0.2)]">
              <span className="text-sm font-bold text-white block mb-1">Orchestrator</span>
              <span className="text-xs text-[#FF4D6D]">Route & Manage</span>
            </motion.div>

            <ChevronRight className="text-[#DC143C] w-6 h-6 shrink-0 bg-[#0c0506]" />

            {/* Stacked Agents */}
            <motion.div initial={{opacity: 0, y:20}} whileInView={{opacity:1, y:0}} viewport={{once:true}} transition={{delay: 0.2}} className="flex flex-col gap-2 shrink-0 z-10 py-4 bg-[#0c0506]">
              {['Security Agent', 'Privacy Agent', 'Compliance Agent', 'Trust Agent'].map((agent) => (
                <div key={agent} className="bg-[#1a0c0e] border border-[#4B0F18] px-4 py-2 rounded-md w-40 text-center text-xs font-medium text-slate-300">
                  {agent}
                </div>
              ))}
            </motion.div>

            <ChevronRight className="text-[#DC143C] w-6 h-6 shrink-0 bg-[#0c0506]" />

            <motion.div initial={{opacity: 0, x:20}} whileInView={{opacity:1, x:0}} viewport={{once:true}} transition={{delay: 0.3}} className="bg-[#2A0B12] border border-[#DC143C]/40 p-4 rounded-lg w-40 text-center shrink-0 z-10">
              <span className="text-sm font-bold text-white block mb-1">Decision</span>
              <span className="text-xs text-[#FF4D6D]">& Remediation</span>
            </motion.div>

            <div className="w-12 h-0.5" /> {/* Spacer */}

            <div className="flex flex-col gap-6 shrink-0 z-10 py-4 bg-[#0c0506]">
              <motion.div initial={{opacity: 0, x:20}} whileInView={{opacity:1, x:0}} viewport={{once:true}} transition={{delay: 0.4}} className="bg-[#120809] border border-[#4B0F18] p-4 rounded-lg w-40 text-center relative overflow-hidden">
                <div className="absolute top-0 left-0 w-1 h-full bg-[#10b981]" />
                <span className="text-sm font-semibold text-white block">Enterprise LLM</span>
              </motion.div>
              <motion.div initial={{opacity: 0, x:20}} whileInView={{opacity:1, x:0}} viewport={{once:true}} transition={{delay: 0.5}} className="bg-[#120809] border border-[#4B0F18] p-4 rounded-lg w-40 text-center relative overflow-hidden">
                 <div className="absolute top-0 left-0 w-1 h-full bg-[#3b82f6]" />
                <span className="text-sm font-semibold text-white block">Audit Logs</span>
              </motion.div>
            </div>
          </div>

          {/* Vertical Mobile View (Simplified) */}
          <div className="lg:hidden flex flex-col items-center gap-6">
            <div className="bg-[#120809] border border-[#4B0F18] p-4 rounded-lg w-64 text-center">
              <span className="text-sm font-semibold text-white block">User Prompt</span>
            </div>
            <div className="h-6 border-l-2 border-dashed border-[#DC143C]" />
            <div className="bg-[#2A0B12] border border-[#DC143C]/40 p-4 rounded-lg w-64 text-center shadow-[0_0_15px_rgba(220,20,60,0.2)]">
              <span className="text-sm font-bold text-white block">Orchestrator Agent</span>
            </div>
            <div className="h-6 border-l-2 border-dashed border-[#DC143C]" />
            <div className="w-64 border border-[#4B0F18] rounded-lg p-4 bg-[#1a0c0e]">
              <div className="text-center text-xs font-semibold text-[#FF4D6D] mb-3 uppercase">Evaluation Cluster</div>
              <div className="grid grid-cols-2 gap-2">
                {['Security', 'Privacy', 'Compliance', 'Trust'].map((agent) => (
                  <div key={agent} className="bg-[#120809] border border-[#2A0B12] px-2 py-2 rounded text-center text-xs text-slate-300">
                    {agent}
                  </div>
                ))}
              </div>
            </div>
            <div className="h-6 border-l-2 border-dashed border-[#DC143C]" />
            <div className="bg-[#2A0B12] border border-[#DC143C]/40 p-4 rounded-lg w-64 text-center">
              <span className="text-sm font-bold text-white block">Decision & Remediation</span>
            </div>
            <div className="h-6 border-l-2 border-dashed border-[#DC143C]" />
            <div className="bg-[#120809] border-l-4 border-[#10b981] p-4 rounded-lg w-64 text-center">
              <span className="text-sm font-semibold text-white block">Enterprise LLM</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

const StatsSection = () => {
  const stats = [
    { label: "AI Systems Evaluated", value: "14,205+" },
    { label: "Threats Prevented", value: "2.4M" },
    { label: "Policies Enforced", value: "850+" },
    { label: "Avg Trust Score", value: "98.2" }
  ];

  return (
    <section className="py-20 bg-[#120809] border-y border-[#2A0B12]" id="about">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8 divide-x divide-[#4B0F18]/50">
          {stats.map((stat, i) => (
            <motion.div 
              key={stat.label}
              initial={{ opacity: 0, scale: 0.9 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: i * 0.1 }}
              className={`text-center ${i !== 0 ? 'pl-8' : ''} ${i % 2 !== 0 ? 'border-l border-[#4B0F18]/50 md:border-none md:pl-0' : ''}`}
            >
              <div className="text-3xl md:text-5xl font-bold text-white mb-2 tracking-tight">{stat.value}</div>
              <div className="text-sm text-[#FF4D6D] font-medium uppercase tracking-wider">{stat.label}</div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};

const CTASection = () => {
  return (
    <section className="py-24 relative overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-b from-[#120809] to-[#2A0B12] -z-10" />
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-[#DC143C]/20 via-transparent to-transparent opacity-50 -z-10" />
      
      <div className="max-w-4xl mx-auto px-4 text-center relative z-10">
        <h2 className="text-4xl md:text-5xl font-bold text-white mb-6 tracking-tight">Ready to Secure Your AI?</h2>
        <p className="text-xl text-slate-400 mb-10 max-w-2xl mx-auto">
          Deploy IntelliGuard today and gain unparalleled visibility and control over your enterprise AI ecosystem.
        </p>
        <Link to="/dashboard" className="inline-flex justify-center items-center gap-2 bg-[#DC143C] hover:bg-[#FF4D6D] text-white px-10 py-5 rounded-md font-medium text-lg transition-all shadow-[0_0_20px_rgba(220,20,60,0.4)] hover:shadow-[0_0_30px_rgba(255,77,109,0.6)]">
          Launch Dashboard <ArrowRight className="h-6 w-6" />
        </Link>
      </div>
    </section>
  );
};

const Footer = () => {
  return (
    <footer className="bg-[#0c0506] border-t border-[#2A0B12] pt-16 pb-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col md:flex-row justify-between items-center md:items-start gap-8 mb-12">
          <div className="text-center md:text-left">
            <div className="flex items-center gap-2 justify-center md:justify-start mb-4">
              <Shield className="h-6 w-6 text-[#DC143C]" />
              <span className="font-bold text-xl tracking-tight text-white">IntelliGuard</span>
            </div>
            <p className="text-slate-500 text-sm max-w-xs">
              Enterprise AI Trust & Security Validation Platform. Ensuring safety, compliance, and privacy at scale.
            </p>
          </div>
          
          <div className="flex gap-12 text-center md:text-left">
            <div>
              <h4 className="text-white font-semibold mb-4 text-sm uppercase tracking-wider">Quick Links</h4>
              <ul className="space-y-2 text-sm text-slate-500">
                <li><a href="#features" className="hover:text-[#FF4D6D] transition-colors">Features</a></li>
                <li><a href="#architecture" className="hover:text-[#FF4D6D] transition-colors">Architecture</a></li>
                <li><Link to="/dashboard" className="hover:text-[#FF4D6D] transition-colors">Dashboard</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="text-white font-semibold mb-4 text-sm uppercase tracking-wider">Legal</h4>
              <ul className="space-y-2 text-sm text-slate-500">
                <li><a href="#" className="hover:text-[#FF4D6D] transition-colors">Privacy Policy</a></li>
                <li><a href="#" className="hover:text-[#FF4D6D] transition-colors">Terms of Service</a></li>
                <li><a href="https://github.com" target="_blank" rel="noreferrer" className="hover:text-[#FF4D6D] transition-colors">GitHub</a></li>
              </ul>
            </div>
          </div>
        </div>
        
        <div className="border-t border-[#2A0B12] pt-8 flex flex-col md:flex-row justify-between items-center gap-4 text-xs text-slate-600">
          <p>&copy; {new Date().getFullYear()} IntelliGuard Systems, Inc. All rights reserved.</p>
          <p>Designed for Enterprise Security.</p>
        </div>
      </div>
    </footer>
  );
};

export default function Home() {
  return (
    <div className="min-h-screen text-slate-200 selection:bg-[#DC143C]/30 bg-[#120809] font-sans">
      <LandingNavbar />
      <main>
        <HeroSection />
        <FeaturesSection />
        <ArchitectureSection />
        <StatsSection />
        <CTASection />
      </main>
      <Footer />
    </div>
  );
}
