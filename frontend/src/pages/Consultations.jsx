import React, { useState } from 'react';
import { 
  Calendar as CalendarIcon, 
  Clock, 
  User, 
  Video, 
  MoreVertical, 
  CheckCircle2, 
  XCircle, 
  MessageSquare,
  Search,
  Filter,
  ChevronRight
} from 'lucide-react';
import UserSidebar from '../components/UserSidebar';

const MOCK_CONSULTATIONS = [
  {
    id: 1,
    clientName: 'Rahul Deshmukh',
    type: 'Video Call',
    date: '2024-05-15',
    time: '10:30 AM',
    status: 'Upcoming',
    caseDomain: 'Property Dispute',
    fee: '₹2,500'
  },
  {
    id: 2,
    clientName: 'Sanjana Verma',
    type: 'In-Person',
    date: '2024-05-15',
    time: '02:00 PM',
    status: 'Upcoming',
    caseDomain: 'Family Law',
    fee: '₹3,000'
  },
  {
    id: 3,
    clientName: 'Amit Shah',
    type: 'Video Call',
    date: '2024-05-14',
    time: '11:00 AM',
    status: 'Completed',
    caseDomain: 'Corporate Law',
    fee: '₹5,000'
  },
  {
    id: 4,
    clientName: 'Kiran Devi',
    type: 'Voice Call',
    date: '2024-05-13',
    time: '04:30 PM',
    status: 'Cancelled',
    caseDomain: 'Criminal Defense',
    fee: '₹2,000'
  }
];

const Consultations = () => {
  const [activeTab, setActiveTab] = useState('upcoming');
  const [consultations] = useState(MOCK_CONSULTATIONS);

  const filteredConsultations = consultations.filter(c => {
    if (activeTab === 'upcoming') return c.status === 'Upcoming';
    if (activeTab === 'past') return c.status === 'Completed' || c.status === 'Cancelled';
    return true;
  });

  const getStatusColor = (status) => {
    switch (status) {
      case 'Upcoming': return 'text-indigo-400 bg-indigo-500/10 border-indigo-500/20';
      case 'Completed': return 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20';
      case 'Cancelled': return 'text-rose-400 bg-rose-500/10 border-rose-500/20';
      default: return 'text-slate-400 bg-slate-500/10 border-slate-500/20';
    }
  };

  return (
    <div className="flex min-h-screen bg-[#020617] text-slate-200 font-inter">
      <UserSidebar />
      
      <main className="flex-1 md:ml-[280px] p-6 md:p-12 overflow-y-auto">
        <div className="max-w-6xl mx-auto space-y-10">
          {/* Header */}
          <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
            <div className="space-y-4">
              <h1 className="text-4xl md:text-5xl font-black tracking-tight text-white leading-tight">
                Your <span className="text-indigo-500">Consultations</span>
              </h1>
              <p className="text-slate-400 text-lg max-w-xl leading-relaxed font-medium">
                Manage your legal appointments, video calls, and client meetings in one place.
              </p>
            </div>
            
            <div className="flex bg-white/5 p-1.5 rounded-2xl border border-white/5">
              <button 
                onClick={() => setActiveTab('upcoming')}
                className={`px-6 py-3 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all ${activeTab === 'upcoming' ? 'bg-indigo-600 text-white shadow-lg' : 'text-slate-500 hover:text-white'}`}
              >
                Upcoming
              </button>
              <button 
                onClick={() => setActiveTab('past')}
                className={`px-6 py-3 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all ${activeTab === 'past' ? 'bg-indigo-600 text-white shadow-lg' : 'text-slate-500 hover:text-white'}`}
              >
                Past Sessions
              </button>
            </div>
          </div>

          {/* Search & Filter */}
          <div className="flex flex-col md:flex-row gap-4">
            <div className="relative flex-1 group">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500 group-focus-within:text-indigo-500 transition-colors" size={20} />
              <input 
                type="text" 
                placeholder="Search by client name or case type..." 
                className="w-full bg-white/5 border border-white/10 rounded-2xl py-4 pl-12 pr-6 text-white outline-none focus:border-indigo-500/50 focus:bg-white/[0.07] transition-all font-medium"
              />
            </div>
            <button className="px-6 py-4 glass-effect border border-white/10 rounded-2xl text-slate-400 hover:text-white flex items-center gap-3 transition-all">
              <Filter size={20} />
              <span className="text-[10px] font-black uppercase tracking-widest">Filter</span>
            </button>
          </div>

          {/* Consultation List */}
          <div className="space-y-4">
            {filteredConsultations.length > 0 ? filteredConsultations.map((c) => (
              <div key={c.id} className="group relative overflow-hidden glass-effect border border-white/10 rounded-[32px] p-6 md:p-8 hover:bg-white/[0.04] transition-all">
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
                  <div className="flex items-center gap-6">
                    <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-indigo-500/20 to-purple-600/20 flex items-center justify-center border border-white/10 text-indigo-400">
                      {c.type === 'Video Call' ? <Video size={28} /> : <User size={28} />}
                    </div>
                    <div className="space-y-1">
                      <div className="flex items-center gap-3">
                        <h3 className="text-xl font-black text-white">{c.clientName}</h3>
                        <span className={`px-3 py-1 rounded-full text-[9px] font-black uppercase tracking-widest border ${getStatusColor(c.status)}`}>
                          {c.status}
                        </span>
                      </div>
                      <p className="text-slate-500 font-bold text-xs uppercase tracking-widest flex items-center gap-2">
                        {c.caseDomain} • <span className="text-indigo-400">{c.fee}</span>
                      </p>
                    </div>
                  </div>

                  <div className="flex flex-wrap items-center gap-4 md:gap-8">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-xl bg-white/5 flex items-center justify-center text-slate-400">
                        <CalendarIcon size={18} />
                      </div>
                      <div>
                        <p className="text-[10px] font-black uppercase tracking-widest text-slate-500">Date</p>
                        <p className="text-sm font-bold text-white">{c.date}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-xl bg-white/5 flex items-center justify-center text-slate-400">
                        <Clock size={18} />
                      </div>
                      <div>
                        <p className="text-[10px] font-black uppercase tracking-widest text-slate-500">Time</p>
                        <p className="text-sm font-bold text-white">{c.time}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2 ml-auto">
                      {c.status === 'Upcoming' && (
                        <>
                          <button className="w-12 h-12 rounded-xl bg-emerald-500/10 text-emerald-500 border border-emerald-500/20 flex items-center justify-center hover:bg-emerald-500 hover:text-white transition-all shadow-lg shadow-emerald-500/10">
                            <CheckCircle2 size={20} />
                          </button>
                          <button className="w-12 h-12 rounded-xl bg-rose-500/10 text-rose-500 border border-rose-500/20 flex items-center justify-center hover:bg-rose-500 hover:text-white transition-all shadow-lg shadow-rose-500/10">
                            <XCircle size={20} />
                          </button>
                        </>
                      )}
                      <button className="w-12 h-12 rounded-xl bg-white/5 text-slate-400 border border-white/10 flex items-center justify-center hover:bg-white/10 hover:text-white transition-all">
                        <MoreVertical size={20} />
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            )) : (
              <div className="py-20 glass-effect rounded-[40px] border-2 border-dashed border-white/5 text-center">
                <CalendarIcon size={48} className="mx-auto text-slate-700 mb-4" />
                <div className="text-slate-500 font-black uppercase tracking-widest text-xs">No consultations found in this category</div>
              </div>
            )}
          </div>

          {/* Quick Stats */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 pt-6">
            <div className="glass-effect p-8 rounded-[32px] border border-white/10 relative overflow-hidden group">
              <div className="absolute top-0 right-0 p-6 opacity-5 group-hover:opacity-10 transition-opacity">
                <CheckCircle2 size={80} className="text-emerald-500" />
              </div>
              <p className="text-[10px] font-black uppercase tracking-widest text-slate-500 mb-2">Weekly Earnings</p>
              <h4 className="text-3xl font-black text-white">₹24,500</h4>
              <div className="mt-4 flex items-center gap-2 text-emerald-400 text-[10px] font-black uppercase">
                <span>+12% from last week</span>
              </div>
            </div>
            <div className="glass-effect p-8 rounded-[32px] border border-white/10 relative overflow-hidden group">
              <div className="absolute top-0 right-0 p-6 opacity-5 group-hover:opacity-10 transition-opacity">
                <Clock size={80} className="text-indigo-500" />
              </div>
              <p className="text-[10px] font-black uppercase tracking-widest text-slate-500 mb-2">Avg. Session Time</p>
              <h4 className="text-3xl font-black text-white">42 Min</h4>
              <div className="mt-4 flex items-center gap-2 text-indigo-400 text-[10px] font-black uppercase">
                <span>Optimized Schedule</span>
              </div>
            </div>
            <div className="glass-effect p-8 rounded-[32px] border border-white/10 relative overflow-hidden group">
              <div className="absolute top-0 right-0 p-6 opacity-5 group-hover:opacity-10 transition-opacity">
                <MessageSquare size={80} className="text-purple-500" />
              </div>
              <p className="text-[10px] font-black uppercase tracking-widest text-slate-500 mb-2">Client Satisfaction</p>
              <h4 className="text-3xl font-black text-white">98%</h4>
              <div className="mt-4 flex items-center gap-2 text-purple-400 text-[10px] font-black uppercase">
                <span>Top Rated Expert</span>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Consultations;
