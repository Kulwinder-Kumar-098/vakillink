import React from 'react';
import UserSidebar from '../components/UserSidebar';
import { Search, Filter, BookOpen, ChevronRight, FileText, Scale } from 'lucide-react';

export default function Statutes() {
  const categories = [
    { name: 'Constitutional Law', count: 12 },
    { name: 'Criminal Law', count: 8, active: true },
    { name: 'Civil Procedure', count: 5 },
    { name: 'Consumer Protection', count: 4 },
    { name: 'Family & Personal Laws', count: 9 },
    { name: 'Labour & Employment', count: 11 },
    { name: 'Property & Land', count: 7 },
    { name: 'Motor Vehicles', count: 3 },
  ];

  const acts = [
    {
      title: "Code of Criminal Procedure, 1973",
      desc: "The main legislation on procedure for administration of substantive criminal law in India.",
      status: "In Force", color: "text-emerald-400"
    },
    {
      title: "Hindu Marriage Act, 1955",
      desc: "An Act to amend and codify the law relating to marriage among Hindus.",
      status: "Amended", color: "text-amber-400"
    },
    {
      title: "Consumer Protection Act, 2019",
      desc: "Replaced the 1986 Act to provide better protection to consumers and for settlement of disputes.",
      status: "In Force", color: "text-emerald-400"
    },
    {
      title: "Industrial Disputes Act, 1947",
      desc: "Enacted to make provision for the investigation and settlement of industrial disputes.",
      status: "In Force", color: "text-emerald-400"
    }
  ];

  return (
    <div className="flex min-h-screen bg-[#020617] text-slate-200">
      <UserSidebar />
      
      <main className="flex-1 md:ml-[280px] p-6 md:p-12 overflow-y-auto">
        {/* Header Section */}
        <div className="mb-12">
          <h1 className="text-4xl md:text-5xl font-black tracking-tight text-white mb-3">
            Statutes <span className="text-indigo-500">& Acts</span>
          </h1>
          <p className="text-slate-400 text-lg max-w-2xl leading-relaxed">
            Browse the complete corpus of Indian legislation — Central Acts, State Acts, and Regulations.
          </p>
        </div>

        {/* Search & Filter Bar */}
        <div className="flex flex-col lg:flex-row gap-6 mb-12">
          <div className="glass-effect flex-1 flex items-center px-6 gap-4 rounded-[24px] border border-white/10 shadow-xl shadow-indigo-500/5">
            <Search className="text-indigo-400" size={22} />
            <input 
              type="text" 
              placeholder="Search by act name, section, or keyword..."
              className="w-full py-5 bg-transparent outline-none text-white text-lg placeholder:text-slate-500"
            />
          </div>
          <div className="flex gap-4">
            <div className="glass-effect px-6 py-4 rounded-[24px] border border-white/10 flex items-center gap-3 min-w-[200px]">
              <Filter className="text-slate-500" size={18} />
              <select className="bg-transparent text-slate-300 outline-none w-full font-bold text-sm cursor-pointer appearance-none">
                <option>All Categories</option>
                <option>Criminal Law</option>
                <option>Civil Procedure</option>
              </select>
            </div>
            <button className="primary-gradient px-10 py-4 rounded-[24px] font-black uppercase tracking-widest text-xs text-white shadow-xl shadow-indigo-500/20 hover:scale-[1.02] active:scale-[0.98] transition-all">
              Search
            </button>
          </div>
        </div>

        <div className="flex flex-col xl:flex-row gap-12">
          {/* Categories Sidebar */}
          <aside className="hidden xl:block w-[300px] flex-shrink-0">
            <div className="glass-effect rounded-[32px] border border-white/10 overflow-hidden sticky top-12">
              <div className="p-6 border-b border-white/5 bg-white/[0.02]">
                <h3 className="text-[10px] font-black text-slate-500 uppercase tracking-[0.3em]">Browse Categories</h3>
              </div>
              <nav className="p-4 space-y-2">
                {categories.map((cat) => (
                  <button
                    key={cat.name}
                    className={`w-full flex justify-between items-center px-5 py-4 rounded-2xl transition-all duration-300 ${
                      cat.active 
                        ? 'bg-indigo-600/10 text-indigo-400 border border-indigo-500/20' 
                        : 'text-slate-400 hover:bg-white/5 hover:text-white'
                    }`}
                  >
                    <span className="font-bold text-[14px]">{cat.name}</span>
                    <span className={`text-[10px] font-black px-2 py-1 rounded-md ${cat.active ? 'bg-indigo-500/20 text-indigo-400' : 'bg-white/5 text-slate-600'}`}>
                      {cat.count}
                    </span>
                  </button>
                ))}
              </nav>
            </div>
          </aside>

          {/* Main Content */}
          <div className="flex-1 space-y-8">
            {/* Featured Act */}
            <div className="glass-effect rounded-[40px] border border-white/10 overflow-hidden relative group">
              <div className="absolute top-0 right-0 w-64 h-64 bg-indigo-500/5 blur-3xl rounded-full -mr-32 -mt-32 transition-all group-hover:bg-indigo-500/10" />
              
              <div className="p-8 md:p-12 border-b border-white/5 relative">
                <div className="flex flex-col md:flex-row justify-between items-start gap-6">
                  <div>
                    <div className="flex items-center gap-3 mb-4">
                      <span className="px-3 py-1 bg-indigo-500/10 text-indigo-400 text-[10px] font-black uppercase tracking-widest rounded-lg border border-indigo-500/20">Central Act</span>
                      <span className="px-3 py-1 bg-emerald-500/10 text-emerald-400 text-[10px] font-black uppercase tracking-widest rounded-lg border border-emerald-500/20">In Force</span>
                    </div>
                    <h2 className="text-3xl font-black text-white mb-4">Indian Penal Code, 1860</h2>
                    <p className="text-slate-400 text-lg leading-relaxed max-w-3xl">
                      The principal criminal code of India. It is a comprehensive code intended to cover all substantive aspects of criminal law.
                    </p>
                  </div>
                  <button className="flex items-center gap-3 px-8 py-4 bg-white/5 hover:bg-white/10 text-white rounded-[20px] font-bold text-sm border border-white/10 transition-all">
                    <FileText className="text-indigo-400" size={18} /> Full Text (PDF)
                  </button>
                </div>
              </div>

              <div className="p-8 md:p-12 bg-white/[0.01]">
                <h4 className="text-[10px] font-black text-slate-500 uppercase tracking-[0.3em] mb-8 px-2">Key Sections</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {[
                    { sec: "Section 1", title: "Title and extent of operation of the Code" },
                    { sec: "Section 2", title: "Punishment of offences committed within India" },
                    { sec: "Section 3", title: "Punishment of offences beyond India" },
                    { sec: "Section 4", title: "Extension to extra-territorial offences" },
                  ].map((item, idx) => (
                    <div key={idx} className="glass-effect p-5 rounded-3xl border border-white/5 hover:bg-white/5 transition-all group cursor-pointer flex items-center justify-between">
                      <div className="flex items-center gap-6">
                        <span className="text-indigo-400 font-black text-xs uppercase tracking-widest w-20">{item.sec}</span>
                        <span className="text-white font-bold text-sm">{item.title}</span>
                      </div>
                      <ChevronRight className="text-slate-600 group-hover:text-white transition-colors" size={20} />
                    </div>
                  ))}
                </div>
                <button className="w-full mt-8 py-5 text-center text-slate-400 hover:text-white font-black uppercase tracking-[0.3em] text-[10px] bg-white/5 rounded-[24px] border border-white/5 hover:bg-white/10 transition-all">
                  Load All 511 Sections
                </button>
              </div>
            </div>

            {/* Other Acts Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {acts.map((act, idx) => (
                <div key={idx} className="glass-effect p-8 rounded-[32px] border border-white/5 hover:bg-white/[0.04] transition-all group relative overflow-hidden flex flex-col h-full">
                  <div className="flex justify-between items-start mb-6">
                    <h3 className="font-black text-xl text-white leading-tight group-hover:text-indigo-400 transition-colors">{act.title}</h3>
                  </div>
                  <p className="text-slate-400 text-sm leading-relaxed line-clamp-2 mb-8">{act.desc}</p>
                  <div className="mt-auto flex items-center justify-between">
                    <div className="flex gap-2">
                      <span className="px-2 py-1 bg-white/5 text-slate-500 text-[9px] font-black uppercase tracking-widest rounded border border-white/5">Central</span>
                      <span className={`px-2 py-1 bg-white/5 ${act.color} text-[9px] font-black uppercase tracking-widest rounded border border-white/5`}>{act.status}</span>
                    </div>
                    <ChevronRight className="text-slate-700 group-hover:text-white" size={18} />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
