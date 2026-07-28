import React from 'react';

export default function PageHeader({ title, description, actions }) {
  return (
    <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6 bg-gradient-to-br from-[#1a0c0e]/90 to-[#120809]/80 p-8 rounded-2xl border border-[#2A0B12] backdrop-blur-xl shadow-[0_8px_30px_rgba(0,0,0,0.5)] relative overflow-hidden group mb-8">
      <div className="absolute inset-0 bg-gradient-to-r from-[#DC143C]/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-700 pointer-events-none" />
      <div className="relative z-10">
        <h1 className="text-3xl md:text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-white to-slate-400 tracking-tight flex items-center gap-3">
          {title}
        </h1>
        <p className="text-sm md:text-base text-slate-400 mt-2 font-medium">
          {description}
        </p>
      </div>
      {actions && (
        <div className="flex items-center gap-3 relative z-10 w-full md:w-auto">
          {actions}
        </div>
      )}
    </div>
  );
}
