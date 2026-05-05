import { useState, useEffect } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { 
  Search, 
  FileText, 
  Paperclip, 
  ArrowRight, 
  Info, 
  Star, 
  Verified, 
  MapPin,
  Briefcase,
  Plus,
  Shield,
  Award,
  Zap,
  Users,
  Filter,
  ArrowUpRight
} from 'lucide-react';
import UserSidebar from '../components/UserSidebar';

export default function LawyerDirectory() {
  const [lawyers, setLawyers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [inquiry, setInquiry] = useState('');
  const [inquiryLoading, setInquiryLoading] = useState(false);
  const [aiResponse, setAiResponse] = useState(null);
  const [searchParams] = useSearchParams();
  const domainFilter = searchParams.get('domain');

  const fetchLawyers = async () => {
    setLoading(true);
    try {
      const baseUrl = 'http://127.0.0.1:9000/api/v1/lawyers';
      const params = new URLSearchParams({
        page: '1',
        limit: '6',
        sort_by: 'rating'
      });
      if (domainFilter) {
        params.append('domain', domainFilter);
      }
      
      const res = await fetch(`${baseUrl}?${params.toString()}`);
      if (!res.ok) throw new Error('Failed to fetch lawyers');
      const data = await res.json();
      setLawyers(data.data);
    } catch (error) {
      console.error(error);
      setLawyers([
        { id: 1, name: 'Adv. Rajesh Kumar', specialization: 'Criminal Law', rating: 4.9, experience_years: 15, avatar: null },
        { id: 2, name: 'Adv. Priya Sharma', specialization: 'Family Law', rating: 4.8, experience_years: 10, avatar: null },
        { id: 3, name: 'Adv. Vikram Singh', specialization: 'Constitutional Law', rating: 5.0, experience_years: 22, avatar: null }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitInquiry = async () => {
    if (!inquiry.trim()) return;
    
    setInquiryLoading(true);
    try {
      const token = localStorage.getItem('vakeellink_token');
      const res = await fetch('http://127.0.0.1:9000/api/v1/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ query: inquiry })
      });

      if (!res.ok) throw new Error('Inquiry failed');
      const data = await res.json();
      setAiResponse(data);
      
      // Update lawyer list with recommendations if any
      if (data.recommended_lawyers && data.recommended_lawyers.length > 0) {
        setLawyers(data.recommended_lawyers);
      }
    } catch (error) {
      console.error('AI Inquiry Error:', error);
    } finally {
      setInquiryLoading(false);
    }
  };

  useEffect(() => {
    fetchLawyers();
  }, [domainFilter]);

  return (
    <div className="flex min-h-screen bg-[#020617] text-slate-200 font-inter">
      <UserSidebar />
      
      <main className="flex-1 md:ml-[280px] p-6 md:p-12 overflow-y-auto">
        <div className="max-w-6xl mx-auto space-y-12">
          {/* Header */}
          <header className="space-y-6">
            <h1 className="text-4xl md:text-5xl font-black tracking-tight text-white leading-tight">
              {domainFilter ? (
                <>Legal <span className="text-indigo-500">{domainFilter}</span> Specialists</>
              ) : (
                <>Verified <span className="text-indigo-500">Legal</span> Experts</>
              )}
            </h1>
            <p className="text-slate-400 text-lg max-w-2xl leading-relaxed font-medium">
              {domainFilter 
                ? `Top-rated advocates specializing in ${domainFilter} law, vetted for their expertise and case history.`
                : 'Connect with verified legal professionals across various domains in India.'}
            </p>
            
            <div className="relative mt-8 group">
              <div className="absolute -inset-1 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-[32px] blur opacity-20 group-hover:opacity-40 transition duration-1000"></div>
              <div className="relative glass-effect rounded-[32px] border border-white/10 p-8 overflow-hidden">
                <textarea 
                  value={inquiry}
                  onChange={(e) => setInquiry(e.target.value)}
                  className="w-full bg-transparent text-white placeholder-slate-500 resize-none min-h-[140px] text-lg font-medium outline-none" 
                  placeholder="Ask our network a legal question... e.g., What are the defenses available under Section 84 of the IPC?"
                ></textarea>
                <div className="flex items-center justify-between mt-6 pt-6 border-t border-white/5">
                  <button className="flex items-center gap-3 text-slate-400 hover:text-white transition-colors text-[10px] font-black uppercase tracking-widest">
                    <Paperclip size={18} className="text-indigo-500" />
                    Attach Case Files
                  </button>
                  <button 
                    onClick={handleSubmitInquiry}
                    disabled={inquiryLoading || !inquiry.trim()}
                    className="bg-indigo-600 text-white px-8 py-4 rounded-2xl font-black text-[10px] uppercase tracking-[0.2em] shadow-xl shadow-indigo-600/20 hover:bg-indigo-500 hover:-translate-y-0.5 transition-all flex items-center gap-3 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {inquiryLoading ? 'Processing...' : 'Submit Inquiry'}
                    <ArrowRight size={16} />
                  </button>
                </div>
              </div>
            </div>
          </header>

          {/* AI Curator Highlight */}
          {aiResponse && (
            <section className="relative group animate-in fade-in slide-in-from-bottom-4 duration-700">
              <div className="absolute -inset-0.5 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-[40px] opacity-10"></div>
              <div className="relative glass-effect p-10 md:p-14 rounded-[40px] border border-white/10 overflow-hidden">
                <div className="absolute top-0 right-0 p-8 opacity-10">
                  <Shield size={120} className="text-indigo-500" />
                </div>
                <div className="flex items-center gap-4 mb-8">
                  <span className="px-4 py-1.5 bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 rounded-full text-[10px] font-black uppercase tracking-widest">AI Intelligence</span>
                  <span className="text-slate-500 font-bold text-[10px] uppercase tracking-widest flex items-center gap-2">
                    <Verified size={14} className="text-indigo-400" />
                    Fact Checked Research
                  </span>
                </div>
                <div className="space-y-6 text-xl md:text-2xl font-bold text-white leading-relaxed max-w-4xl">
                  <p className="italic text-slate-300">"{aiResponse.analysis || 'Analysis processing...'}"</p>
                </div>
                <div className="mt-10 pt-10 border-t border-white/5 grid grid-cols-1 md:grid-cols-3 gap-8">
                  {aiResponse.cited_sections?.length > 0 && (
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-xl bg-indigo-500/10 flex items-center justify-center text-indigo-400">
                        <FileText size={20} />
                      </div>
                      <div>
                        <div className="text-[10px] font-black uppercase tracking-widest text-slate-500">Legal Sections</div>
                        <div className="text-sm font-bold text-white">{(aiResponse.cited_sections || []).join(', ')}</div>
                      </div>
                    </div>
                  )}
                  {aiResponse.cited_acts?.length > 0 && (
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-xl bg-purple-500/10 flex items-center justify-center text-purple-400">
                        <Scale size={20} />
                      </div>
                      <div>
                        <div className="text-[10px] font-black uppercase tracking-widest text-slate-500">Legal Acts</div>
                        <div className="text-sm font-bold text-white">{(aiResponse.cited_acts || []).join(', ')}</div>
                      </div>
                    </div>
                  )}
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-emerald-500/10 flex items-center justify-center text-emerald-400">
                      <Zap size={20} />
                    </div>
                    <div>
                      <div className="text-[10px] font-black uppercase tracking-widest text-slate-500">Domain</div>
                      <div className="text-sm font-bold text-white capitalize">{aiResponse.domain || 'General'}</div>
                    </div>
                  </div>
                </div>
              </div>
            </section>
          )}

          {/* Featured Experts */}
          <section className="space-y-8">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-3xl font-black text-white">Top <span className="text-indigo-500">Experts</span></h2>
                <p className="text-slate-500 font-bold text-xs uppercase tracking-widest mt-2">Vetted legal professionals in your region</p>
              </div>
              <div className="flex gap-4">
                 <button className="p-3 glass-effect rounded-2xl border border-white/10 text-slate-400 hover:text-white transition-all">
                   <Filter size={20} />
                 </button>
              </div>
            </div>
            
            {loading ? (
              <div className="py-20 text-center">
                <div className="inline-block w-8 h-8 border-4 border-indigo-500/20 border-t-indigo-500 rounded-full animate-spin"></div>
                <div className="mt-4 text-slate-500 font-black uppercase tracking-widest text-[10px]">Assembling Expert Network...</div>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                {lawyers.length > 0 ? lawyers.map(lawyer => (
                  <div key={lawyer.id} className="glass-effect p-8 rounded-[40px] border border-white/10 flex flex-col items-center text-center gap-6 group hover:bg-white/[0.04] transition-all relative overflow-hidden">
                    <div className="absolute top-0 right-0 p-6 opacity-0 group-hover:opacity-100 transition-opacity">
                      <Verified size={24} className="text-indigo-400" />
                    </div>
                    <div className="relative">
                      <div className="absolute -inset-2 bg-gradient-to-tr from-indigo-500 to-purple-500 rounded-full blur-md opacity-20 group-hover:opacity-40 transition-all"></div>
                      <div className="relative w-28 h-28 rounded-full border-4 border-white/10 shadow-2xl flex items-center justify-center bg-slate-900 text-3xl font-black text-white overflow-hidden group-hover:scale-105 transition-transform">
                        {lawyer.avatar ? <img src={lawyer.avatar} alt={lawyer.name} className="w-full h-full object-cover" /> : (lawyer.name ? lawyer.name.charAt(5) : 'L')}
                      </div>
                    </div>
                    <div className="space-y-2">
                      <h3 className="text-xl font-black text-white group-hover:text-indigo-400 transition-colors">{lawyer.name}</h3>
                      <div className="inline-flex px-3 py-1 bg-white/5 text-slate-400 text-[9px] font-black uppercase tracking-widest rounded-lg border border-white/5">
                        {lawyer.specialization?.replace('legal_', '').replace('_', ' ') || 'Specialist'}
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-2 gap-4 w-full pt-4 border-t border-white/5">
                      <div className="flex flex-col items-center gap-1">
                        <div className="flex items-center gap-1.5 text-amber-400">
                          <Star size={14} fill="currentColor" />
                          <span className="text-sm font-black text-white">{lawyer.rating || '4.8'}</span>
                        </div>
                        <span className="text-[9px] font-black uppercase tracking-widest text-slate-600">Avg Rating</span>
                      </div>
                      <div className="flex flex-col items-center gap-1">
                        <div className="flex items-center gap-1.5 text-indigo-400">
                          <Briefcase size={14} />
                          <span className="text-sm font-black text-white">{lawyer.experience_years}+</span>
                        </div>
                        <span className="text-[9px] font-black uppercase tracking-widest text-slate-600">Years Exp</span>
                      </div>
                    </div>

                    <Link to={`/lawyers/${lawyer.id}`} className="mt-4 w-full bg-white/5 border border-white/10 text-white font-black py-4 px-6 rounded-2xl group-hover:bg-indigo-600 group-hover:border-transparent transition-all text-[10px] uppercase tracking-widest shadow-xl text-center">
                      View Profile
                    </Link>
                  </div>
                )) : (
                  <div className="col-span-full py-20 glass-effect rounded-[40px] border-2 border-dashed border-white/5 text-center">
                    <Users size={48} className="mx-auto text-slate-700 mb-4" />
                    <div className="text-slate-500 font-black uppercase tracking-widest text-xs">No matching legal experts found</div>
                  </div>
                )}
              </div>
            )}
          </section>

          {/* Legal Citations - Modern Version */}
          <section className="space-y-8">
            <h2 className="text-2xl font-black text-white">Relevant <span className="text-indigo-500">Citations</span></h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              {[
                { title: 'State of M.P. v. Ahmadulla', citation: 'AIR 1961 SC 998', tags: ['IPC SEC. 84', 'IEA SEC. 105'] },
                { title: 'Dahyabhai Chhaganbhai v. State of Gujarat', citation: 'AIR 1964 SC 1563', tags: ['IPC SEC. 84'] }
              ].map((cit, i) => (
                <div key={i} className="glass-effect p-8 rounded-[32px] border border-white/10 hover:border-white/20 transition-all group">
                   <div className="flex justify-between items-start mb-6">
                     <div>
                       <h3 className="text-xl font-bold text-white group-hover:text-indigo-400 transition-colors">{cit.title}</h3>
                       <p className="text-indigo-500 font-mono text-xs font-black mt-1 uppercase">{cit.citation}</p>
                     </div>
                     <div className="w-10 h-10 rounded-xl bg-white/5 flex items-center justify-center text-slate-500 group-hover:text-white transition-colors">
                       <ArrowUpRight size={20} />
                     </div>
                   </div>
                   <div className="flex gap-3">
                     {cit.tags.map(tag => (
                       <span key={tag} className="px-3 py-1 bg-white/5 text-slate-500 text-[9px] font-black uppercase tracking-widest rounded-lg">{tag}</span>
                     ))}
                   </div>
                </div>
              ))}
            </div>
          </section>
        </div>
      </main>
    </div>
  );
}
