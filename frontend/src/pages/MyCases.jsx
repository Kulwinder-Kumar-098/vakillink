import React from 'react';
import { Link } from 'react-router-dom';
import { 
  History, 
  Search, 
  Filter, 
  SortAsc, 
  Calendar, 
  Paperclip,
  ChevronLeft,
  ChevronRight,
  Plus,
  ArrowUpRight
} from 'lucide-react';
import UserSidebar from '../components/UserSidebar';

const MyCases = () => {
    const cases = [
        {
            id: "VK-8821",
            category: "Criminal Law",
            title: "Liability of automated transport systems in mid-urban crosswalk collisions...",
            summary: "AI Summary: Under current jurisdiction, the primary liability rests with the software maintainer if tele-operation was disengaged during the incident...",
            date: "Oct 12, 2023",
            citations: 4,
            accent: "border-indigo-500",
            glow: "shadow-indigo-500/10"
        },
        {
            id: "VK-4412",
            category: "Property Law",
            title: "Applicability of riparian rights in seasonal wetlands under the 2021 Amendment...",
            summary: "AI Summary: The amendment clarifies that riparian access is maintained even during drought cycles, provided the original waterway was recorded...",
            date: "Sep 28, 2023",
            citations: 12,
            accent: "border-emerald-500",
            glow: "shadow-emerald-500/10"
        },
        {
            id: "VK-1092",
            category: "Family Law",
            title: "Extraterritorial enforcement of child support orders in non-signatory nations...",
            summary: "AI Summary: Reciprocity remains the strongest argument for enforcement in the absence of a formal treaty. Documenting financial interdependence...",
            date: "Aug 05, 2023",
            citations: 7,
            accent: "border-purple-500",
            glow: "shadow-purple-500/10"
        }
    ];

    return (
        <div className="flex min-h-screen bg-[#020617] text-slate-200">
            <UserSidebar />

            <main className="flex-1 md:ml-[280px] p-6 md:p-12 overflow-y-auto">
                <div className="max-w-6xl mx-auto">
                    {/* Header Section */}
                    <div className="mb-12">
                        <h1 className="text-4xl md:text-5xl font-black tracking-tight text-white mb-3">
                            My <span className="text-indigo-500">Cases</span>
                        </h1>
                        <p className="text-slate-400 text-lg max-w-2xl leading-relaxed">
                            A comprehensive repository of your legal inquiries, synthesized research, and archival citations.
                        </p>
                    </div>

                    {/* Search & Filter Bar */}
                    <div className="flex flex-col md:flex-row gap-6 mb-12">
                        <div className="glass-effect flex-1 flex items-center px-6 gap-4 rounded-[24px] border border-white/10 shadow-xl shadow-indigo-500/5">
                            <Search className="text-indigo-400" size={22} />
                            <input 
                                type="text" 
                                placeholder="Search by docket number or keyword..."
                                className="w-full py-5 bg-transparent outline-none text-white text-lg placeholder:text-slate-500"
                            />
                        </div>
                        <div className="flex gap-4">
                            <button className="glass-effect px-8 py-4 rounded-[24px] border border-white/10 flex items-center gap-3 text-slate-400 font-black uppercase tracking-widest text-[10px] hover:text-white transition-all">
                                <Filter size={18} /> Filter
                            </button>
                            <button className="glass-effect px-8 py-4 rounded-[24px] border border-white/10 flex items-center gap-3 text-slate-400 font-black uppercase tracking-widest text-[10px] hover:text-white transition-all">
                                <SortAsc size={18} /> Date
                            </button>
                        </div>
                    </div>

                    {/* Bento Grid of Cases */}
                    <div className="grid grid-cols-1 gap-8">
                        {cases.map((c, idx) => (
                            <div 
                                key={c.id} 
                                className={`glass-effect rounded-[40px] p-8 md:p-12 border-l-[8px] ${c.accent} hover:bg-white/[0.04] transition-all duration-500 group relative overflow-hidden flex flex-col md:flex-row gap-10 ${c.glow}`}
                            >
                                <div className="absolute top-0 right-0 w-64 h-64 bg-white/[0.01] blur-3xl rounded-full -mr-32 -mt-32 transition-all group-hover:bg-white/[0.03]" />
                                
                                <div className="flex-1 relative">
                                    <div className="flex items-center gap-4 mb-6">
                                        <span className={`px-4 py-1.5 bg-white/5 ${c.accent.replace('border-', 'text-')} text-[10px] font-black uppercase tracking-widest rounded-xl border border-white/10`}>
                                            {c.category}
                                        </span>
                                        <span className="text-slate-500 text-[10px] font-black uppercase tracking-widest">Case ID: {c.id}</span>
                                    </div>
                                    <h2 className="text-3xl font-black text-white mb-6 group-hover:text-indigo-400 transition-colors leading-tight">
                                        {c.title}
                                    </h2>
                                    <p className="text-slate-400 leading-relaxed italic mb-8 text-lg opacity-80 group-hover:opacity-100 transition-opacity">
                                        "{c.summary}"
                                    </p>
                                    <div className="flex items-center gap-8 text-slate-500 font-black text-[10px] uppercase tracking-[0.2em]">
                                        <div className="flex items-center gap-2 group-hover:text-slate-300 transition-colors">
                                            <Calendar size={16} />
                                            {c.date}
                                        </div>
                                        <div className="flex items-center gap-2 group-hover:text-slate-300 transition-colors">
                                            <Paperclip size={16} />
                                            {c.citations} Citations
                                        </div>
                                    </div>
                                </div>

                                <div className="flex flex-col justify-between items-end min-w-[180px] relative">
                                    <div className="flex -space-x-3 mb-8">
                                        {[1, 2, 3].map((i) => (
                                            <div key={i} className="w-12 h-12 rounded-2xl border-4 border-[#0f172a] bg-gradient-to-br from-slate-700 to-slate-900 flex items-center justify-center text-xs font-black text-white overflow-hidden">
                                                <img src={`https://i.pravatar.cc/150?u=${c.id}${i}`} alt="Collaborator" className="w-full h-full object-cover" />
                                            </div>
                                        ))}
                                    </div>
                                    <button className="w-full primary-gradient text-white px-8 py-5 rounded-[22px] font-black uppercase tracking-[0.2em] text-[10px] shadow-xl shadow-indigo-500/20 hover:scale-[1.05] active:scale-[0.95] transition-all flex items-center justify-center gap-2">
                                        Analysis <ArrowUpRight size={16} />
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>

                    {/* Pagination */}
                    <div className="mt-20 flex flex-col sm:flex-row justify-between items-center border-t border-white/5 pt-10 gap-8">
                        <span className="text-slate-500 text-[10px] font-black uppercase tracking-[0.3em]">Showing 3 of 124 Archival Records</span>
                        <div className="flex items-center gap-6">
                            <button className="p-3 text-slate-500 hover:text-white transition-all bg-white/5 rounded-2xl border border-white/5">
                                <ChevronLeft size={24} />
                            </button>
                            <div className="flex gap-3">
                                <span className="w-12 h-12 flex items-center justify-center font-black bg-indigo-600 text-white rounded-2xl shadow-xl shadow-indigo-500/20">1</span>
                                <span className="w-12 h-12 flex items-center justify-center font-black text-slate-500 hover:bg-white/5 border border-white/5 hover:text-white rounded-2xl cursor-pointer transition-all">2</span>
                                <span className="w-12 h-12 flex items-center justify-center font-black text-slate-500 hover:bg-white/5 border border-white/5 hover:text-white rounded-2xl cursor-pointer transition-all">3</span>
                            </div>
                            <button className="p-3 text-slate-500 hover:text-white transition-all bg-white/5 rounded-2xl border border-white/5">
                                <ChevronRight size={24} />
                            </button>
                        </div>
                    </div>
                </div>
            </main>

            {/* Mobile FAB */}
            <button className="fixed bottom-8 right-8 w-16 h-16 primary-gradient text-white rounded-[24px] shadow-2xl flex items-center justify-center hover:scale-110 active:scale-95 transition-all duration-300 md:hidden z-50">
                <Plus size={28} />
            </button>
        </div>
    );
};

export default MyCases;
