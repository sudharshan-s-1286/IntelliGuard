// src/mockAnalyticsData.js

export const trustTrendData = [
  { month: 'Jan', trust: 82 },
  { month: 'Feb', trust: 84 },
  { month: 'Mar', trust: 86 },
  { month: 'Apr', trust: 85 },
  { month: 'May', trust: 88 },
  { month: 'Jun', trust: 89 },
  { month: 'Jul', trust: 92 },
  { month: 'Aug', trust: 90 },
  { month: 'Sep', trust: 94 },
  { month: 'Oct', trust: 93 },
  { month: 'Nov', trust: 95 },
  { month: 'Dec', trust: 97 },
];

export const riskDistributionData = [
  { name: 'Trust Events', value: 38 },
  { name: 'Privacy', value: 24 },
  { name: 'Compliance', value: 18 },
  { name: 'Trust', value: 20 },
];

export const promptInjectionData = [
  { time: '00:00', attempts: 2 }, { time: '01:00', attempts: 1 }, { time: '02:00', attempts: 0 },
  { time: '03:00', attempts: 3 }, { time: '04:00', attempts: 5 }, { time: '05:00', attempts: 12 },
  { time: '06:00', attempts: 8 }, { time: '07:00', attempts: 15 }, { time: '08:00', attempts: 45 },
  { time: '09:00', attempts: 60 }, { time: '10:00', attempts: 55 }, { time: '11:00', attempts: 75 },
  { time: '12:00', attempts: 89 }, { time: '13:00', attempts: 82 }, { time: '14:00', attempts: 95 },
  { time: '15:00', attempts: 110 }, { time: '16:00', attempts: 120 }, { time: '17:00', attempts: 85 },
  { time: '18:00', attempts: 50 }, { time: '19:00', attempts: 42 }, { time: '20:00', attempts: 65 },
  { time: '21:00', attempts: 30 }, { time: '22:00', attempts: 18 }, { time: '23:00', attempts: 5 },
];

export const hallucinationTrendData = [
  { week: 'Week 1', score: 4.2 },
  { week: 'Week 2', score: 3.8 },
  { week: 'Week 3', score: 4.5 },
  { week: 'Week 4', score: 3.2 },
  { week: 'Week 5', score: 2.9 },
  { week: 'Week 6', score: 2.1 },
  { week: 'Week 7', score: 1.8 },
  { week: 'Week 8', score: 1.5 },
];

export const privacyRiskData = [
  { category: 'Emails', low: 20, medium: 15, high: 5 },
  { category: 'SSN', low: 5, medium: 10, high: 25 },
  { category: 'Cards', low: 10, medium: 20, high: 15 },
  { category: 'Phones', low: 30, medium: 15, high: 2 },
  { category: 'Addresses', low: 25, medium: 10, high: 8 },
];

export const dailyRequestsData = [
  { day: 'Mon', requests: 12500 },
  { day: 'Tue', requests: 14200 },
  { day: 'Wed', requests: 15800 },
  { day: 'Thu', requests: 13900 },
  { day: 'Fri', requests: 16500 },
  { day: 'Sat', requests: 8400 },
  { day: 'Sun', requests: 7200 },
];

export const monthlyUsageData = [
  { month: 'Jan', queries: 250000 },
  { month: 'Feb', queries: 280000 },
  { month: 'Mar', queries: 310000 },
  { month: 'Apr', queries: 290000 },
  { month: 'May', queries: 350000 },
  { month: 'Jun', queries: 420000 },
];

export const allowedVsBlockedData = [
  { month: 'Jan', allowed: 240000, blocked: 10000 },
  { month: 'Feb', allowed: 268000, blocked: 12000 },
  { month: 'Mar', allowed: 295000, blocked: 15000 },
  { month: 'Apr', allowed: 272000, blocked: 18000 },
  { month: 'May', allowed: 325000, blocked: 25000 },
  { month: 'Jun', allowed: 388000, blocked: 32000 },
];

export const kpiData = [
  { title: "Average Enterprise Trust", value: "94.2%", trend: "+1.2%" },
  { title: "Trust Events Today", value: "1,204", trend: "-5.4%" },
  { title: "Prompt Injection Attempts", value: "342", trend: "+12.1%" },
  { title: "Compliance Score", value: "98.5%", trend: "+0.1%" },
];

export const agentPerformanceData = [
  { name: 'Trust Agent', response: '14ms', accuracy: '99.9%', confidence: '95%', health: '100%', risk: 'Low', requests: '1.4M' },
  { name: 'Privacy Agent', response: '22ms', accuracy: '98.5%', confidence: '92%', health: '98%', risk: 'Low', requests: '1.2M' },
  { name: 'Compliance Agent', response: '45ms', accuracy: '97.2%', confidence: '88%', health: '92%', risk: 'Medium', requests: '850K' },
  { name: 'Trust Agent', response: '110ms', accuracy: '94.8%', confidence: '90%', health: '99%', risk: 'Low', requests: '920K' },
  { name: 'Decision Agent', response: '8ms', accuracy: '99.9%', confidence: '98%', health: '100%', risk: 'Low', requests: '2.1M' },
  { name: 'Remediation Agent', response: '65ms', accuracy: '95.5%', confidence: '82%', health: '95%', risk: 'Medium', requests: '140K' },
];

export const threatFeed = [
   { time: "10 mins ago", event: "Critical Prompt Injection Blocked", agent: "Trust Agent", desc: "Blocked SQLi payload targeting internal CRM DB.", severity: "critical" },
  { time: "1 hour ago", event: "PII Exposure Prevented", agent: "Privacy Agent", desc: "Masked 4 SSNs and 2 Credit Card numbers in output.", severity: "high" },
  { time: "3 hours ago", event: "Compliance Policy Violation", agent: "Compliance Agent", desc: "Flagged response for containing unreleased financial data.", severity: "medium" },
];

export const recommendations = [
  { title: "Increase Trust Threshold", desc: "Spike in injection attempts detected between 12:00 and 16:00.", action: "Review Thresholds" },
  { title: "Review Compliance Policies", desc: "Financial data policy violations increased by 4% this week.", action: "Update Policies" },
  { title: "Investigate Hallucinations", desc: "Trust Agent flagged unusual hallucination spike on Wednesday.", action: "View Logs" },
  { title: "Update Privacy Rules", desc: "New regex patterns available for European GDPR masking.", action: "Apply Update" },
];
