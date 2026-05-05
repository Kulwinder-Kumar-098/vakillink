import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { 
  Shield, 
  Gavel, 
  Zap, 
  Users, 
  Search, 
  ArrowRight, 
  Verified, 
  MessageSquare, 
  Scale, 
  Star,
  Globe,
  Award,
  ChevronRight,
  BookOpen,
  CheckCircle2,
  Cpu
} from 'lucide-react';

const LandingPage = () => {
    const [chatQuery, setChatQuery] = useState("");
    const [chatResponse, setChatResponse] = useState(null);
    const [isTyping, setIsTyping] = useState(false);
    const navigate = useNavigate();

    const handleChatSubmit = (e) => {
        if (e.key === 'Enter' || e.type === 'click') {
            if (!chatQuery.trim()) return;
            setIsTyping(true);
            setTimeout(() => {
                setChatResponse({
                    title: "Legal Intelligence Summary",
                    content: "Based on the IPC, Section 420 involves cheating and dishonestly inducing delivery of property. Your case requires evidence of fraudulent intent at the inception of the transaction.",
                    citation: "Section 420 IPC"
                });
                setIsTyping(false);
            }, 1500);
        }
    };

    return (
        <div className="bg-[#020617] text-slate-200 min-h-screen font-inter selection:bg-indigo-500/30 overflow-x-hidden">
            {/* Navigation */}
            <nav className="fixed top-0 left-0 right-0 z-50 glass-effect border-b border-white/5">
                <div className="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
                    <Link to="/" className="flex items-center gap-3 group">
                        <div className="w-10 h-10 rounded-xl bg-indigo-600 flex items-center justify-center shadow-lg shadow-indigo-600/20 group-hover:scale-110 transition-transform">
                            <Scale size={24} className="text-white" />
                        </div>
                        <span className="text-xl font-black tracking-tighter text-white">Vakeel<span className="text-indigo-500">Link</span></span>
                    </Link>
                    
                    <div className="hidden md:flex items-center gap-10">
                        {['Solutions', 'For Lawyers', 'Resources', 'Pricing'].map((item) => (
                          <Link key={item} to="#" className="text-[10px] font-black uppercase tracking-[0.2em] text-slate-500 hover:text-white transition-colors">{item}</Link>
                        ))}
                    </div>

                    <div className="flex items-center gap-6">
                        <Link to="/login" className="text-[10px] font-black uppercase tracking-[0.2em] text-white hover:text-indigo-400 transition-colors">Login</Link>
                        <Link to="/signup" className="px-6 py-3 bg-white text-black rounded-xl font-black text-[10px] uppercase tracking-[0.2em] hover:bg-indigo-500 hover:text-white transition-all shadow-xl shadow-white/5">Get Started</Link>
                    </div>
                </div>
            </nav>

            {/* Hero Section */}
            <section className="relative pt-40 pb-32 md:pt-56 md:pb-56 overflow-hidden">
                {/* Background Glows */}
                <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-full pointer-events-none -z-10">
                    <div className="absolute top-1/4 left-1/4 w-[500px] h-[500px] bg-indigo-600/20 rounded-full blur-[120px] animate-pulse"></div>
                    <div className="absolute bottom-1/4 right-1/4 w-[500px] h-[500px] bg-purple-600/10 rounded-full blur-[120px]"></div>
                </div>

                <div className="max-w-7xl mx-auto px-6 grid lg:grid-cols-2 gap-20 items-center">
                    <div className="space-y-10 text-center lg:text-left">
                        <div className="inline-flex items-center gap-3 px-4 py-2 rounded-full glass-effect border border-white/10 text-indigo-400 text-[10px] font-black uppercase tracking-[0.2em]">
                            <Zap size={14} />
                            Next-Gen Legal Intelligence
                        </div>
                        <h1 className="text-5xl md:text-8xl font-black text-white leading-[0.9] tracking-tight">
                            Justice, <br />
                            <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 via-purple-400 to-indigo-400 bg-300% animate-gradient">Simplified.</span>
                        </h1>
                        <p className="text-slate-400 text-lg md:text-xl max-w-xl mx-auto lg:mx-0 leading-relaxed font-medium">
                            VakeelLink decodes complex Indian law using advanced AI, matching you with specialized advocates in seconds. Professional clarity, finally accessible.
                        </p>
                        <div className="flex flex-col sm:flex-row items-center justify-center lg:justify-start gap-6 pt-4">
                            <Link to="/case-curator" className="w-full sm:w-auto px-10 py-5 bg-indigo-600 text-white rounded-2xl font-black text-xs uppercase tracking-[0.2em] shadow-2xl shadow-indigo-600/40 hover:bg-indigo-500 hover:-translate-y-1 transition-all flex items-center justify-center gap-3">
                                Get Legal Help
                                <ArrowRight size={18} />
                            </Link>
                            <Link to="/signup?role=lawyer" className="w-full sm:w-auto px-10 py-5 glass-effect border border-white/10 text-white rounded-2xl font-black text-xs uppercase tracking-[0.2em] hover:bg-white/5 transition-all">
                                For Legal Experts
                            </Link>
                        </div>
                        <div className="flex items-center justify-center lg:justify-start gap-8 pt-8">
                           <div className="flex -space-x-4">
                             {[1,2,3,4].map(i => (
                               <div key={i} className="w-10 h-10 rounded-full border-2 border-[#020617] bg-slate-800 flex items-center justify-center text-[10px] font-black">U{i}</div>
                             ))}
                           </div>
                           <div className="text-[10px] font-black uppercase tracking-widest text-slate-500">
                             Trusted by <span className="text-white">10k+ citizens</span> across India
                           </div>
                        </div>
                    </div>

                    {/* AI Chat Visualization */}
                    <div className="relative group">
                        <div className="absolute -inset-1 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-[48px] blur-2xl opacity-20 group-hover:opacity-40 transition duration-1000"></div>
                        <div className="relative glass-effect rounded-[48px] border border-white/10 p-10 md:p-14 overflow-hidden">
                           <div className="flex items-center justify-between mb-10">
                              <div className="flex items-center gap-4">
                                 <div className="w-12 h-12 rounded-2xl bg-indigo-600 flex items-center justify-center shadow-lg shadow-indigo-600/20">
                                    <Cpu size={24} className="text-white" />
                                 </div>
                                 <div>
                                    <h3 className="text-sm font-black text-white uppercase tracking-widest">Legal AI v2.0</h3>
                                    <p className="text-[10px] font-black text-emerald-500 uppercase tracking-widest flex items-center gap-1">
                                       <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
                                       Operational
                                    </p>
                                 </div>
                              </div>
                           </div>

                           <div className="space-y-6">
                              <div className="relative">
                                 <input 
                                    type="text" 
                                    className="w-full bg-white/5 border border-white/10 rounded-2xl p-6 text-white font-medium outline-none focus:border-indigo-500/50 transition-all"
                                    placeholder="Ask a legal question..."
                                    value={chatQuery}
                                    onChange={(e) => setChatQuery(e.target.value)}
                                    onKeyDown={handleChatSubmit}
                                 />
                                 <button 
                                    onClick={handleChatSubmit}
                                    className="absolute right-4 top-1/2 -translate-y-1/2 p-3 bg-indigo-600 text-white rounded-xl hover:bg-indigo-500 transition-colors"
                                 >
                                    <ArrowRight size={20} />
                                 </button>
                              </div>

                              {isTyping && (
                                 <div className="flex gap-2 p-4">
                                    <div className="w-2 h-2 bg-indigo-500 rounded-full animate-bounce"></div>
                                    <div className="w-2 h-2 bg-indigo-500 rounded-full animate-bounce [animation-delay:-0.15s]"></div>
                                    <div className="w-2 h-2 bg-indigo-500 rounded-full animate-bounce [animation-delay:-0.3s]"></div>
                                 </div>
                              )}

                              {chatResponse ? (
                                 <div className="p-8 bg-indigo-500/10 border border-indigo-500/20 rounded-[32px] space-y-4 animate-in fade-in slide-in-from-bottom-4">
                                    <h4 className="text-xs font-black uppercase tracking-widest text-indigo-400">{chatResponse.title}</h4>
                                    <p className="text-slate-300 leading-relaxed font-medium italic">"{chatResponse.content}"</p>
                                    <div className="flex items-center gap-2 text-[10px] font-black uppercase tracking-widest text-slate-500 pt-4 border-t border-white/5">
                                       <BookOpen size={14} className="text-indigo-500" />
                                       Citation: {chatResponse.citation}
                                    </div>
                                 </div>
                              ) : (
                                 <div className="p-8 bg-white/5 rounded-[32px] border border-white/5 italic text-slate-500 font-medium">
                                    "Explain Section 420 in the context of digital fraud..."
                                 </div>
                              )}
                           </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* Stats */}
            <section className="relative z-10 -mt-20">
               <div className="max-w-6xl mx-auto px-6">
                  <div className="glass-effect rounded-[40px] border border-white/10 p-12 md:p-16 grid grid-cols-2 lg:grid-cols-4 gap-12 text-center shadow-2xl shadow-indigo-600/10">
                     {[
                        { val: '500+', label: 'Elite Advocates' },
                        { val: '12+', label: 'Legal Domains' },
                        { val: '25k+', label: 'Cases Resolved' },
                        { val: '4.9', label: 'User Rating', icon: Star }
                     ].map((stat, i) => (
                        <div key={i} className="space-y-3">
                           <div className="text-4xl md:text-5xl font-black text-white tracking-tighter flex items-center justify-center gap-2">
                              {stat.val}
                              {stat.icon && <stat.icon className="text-amber-400" size={24} fill="currentColor" />}
                           </div>
                           <div className="text-[10px] font-black uppercase tracking-[0.3em] text-slate-500">{stat.label}</div>
                        </div>
                     ))}
                  </div>
               </div>
            </section>

            {/* Process Section */}
            <section className="py-40">
               <div className="max-w-7xl mx-auto px-6">
                  <div className="text-center space-y-6 mb-24">
                     <h2 className="text-4xl md:text-6xl font-black text-white">Three Steps to <span className="text-indigo-500">Clarity</span></h2>
                     <p className="text-slate-400 font-medium max-w-xl mx-auto text-lg">Institutional legal precision, delivered in minutes.</p>
                  </div>

                  <div className="grid md:grid-cols-3 gap-10">
                     {[
                        { step: '01', title: 'Describe situation', desc: 'Type your legal challenge in plain language. No jargon required.', icon: MessageSquare, link: '/case-curator' },
                        { step: '02', title: 'AI Analysis', desc: 'Our engine maps your case to specific IPC sections and statutes.', icon: Cpu, link: '/case-curator' },
                        { step: '03', title: 'Expert Match', desc: 'Connect with a verified specialist for professional representation.', icon: Users, link: '/lawyers' }
                     ].map((item, i) => (
                        <div 
                           key={i} 
                           onClick={() => navigate(item.link)}
                           className="glass-effect p-12 rounded-[48px] border border-white/10 hover:bg-white/[0.04] hover:-translate-y-2 transition-all cursor-pointer group"
                        >
                           <div className="text-6xl font-black text-white/5 mb-8 group-hover:text-indigo-500/20 transition-colors">{item.step}</div>
                           <item.icon size={48} className="text-indigo-500 mb-8" />
                           <h3 className="text-2xl font-black text-white mb-4">{item.title}</h3>
                           <p className="text-slate-500 font-medium leading-relaxed">{item.desc}</p>
                        </div>
                     ))}
                  </div>
               </div>
            </section>

            {/* Domains Section */}
            <section className="py-40 bg-white/[0.01]">
               <div className="max-w-7xl mx-auto px-6">
                  <div className="flex flex-col md:flex-row justify-between items-end gap-10 mb-20">
                     <div className="space-y-6">
                        <h2 className="text-4xl md:text-6xl font-black text-white">Legal <span className="text-indigo-500">Ecosystem</span></h2>
                        <p className="text-slate-400 font-medium max-w-md text-lg">Specialized intelligence across all major Indian legal frameworks.</p>
                     </div>
                     <Link to="/lawyers" className="flex items-center gap-3 text-[10px] font-black uppercase tracking-widest text-indigo-400 hover:text-white transition-colors group">
                        Explore All Domains
                        <ChevronRight size={16} className="group-hover:translate-x-1 transition-transform" />
                     </Link>
                  </div>

                  <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-6">
                     {[
                        { label: 'Constitutional', icon: Scale, color: 'indigo' },
                        { label: 'Criminal', icon: Gavel, color: 'rose' },
                        { label: 'Corporate', icon: Shield, color: 'blue' },
                        { label: 'Family', icon: Users, color: 'purple' },
                        { label: 'Property', icon: Globe, color: 'emerald' },
                        { label: 'Taxation', icon: Award, color: 'amber' }
                     ].map((domain, i) => (
                        <div 
                           key={i} 
                           onClick={() => navigate(`/lawyers?domain=${domain.label}`)}
                           className="glass-effect p-8 rounded-[32px] border border-white/5 hover:border-indigo-500/30 transition-all cursor-pointer text-center group"
                        >
                           <domain.icon size={32} className="mx-auto mb-6 text-slate-600 group-hover:text-indigo-500 transition-colors" />
                           <span className="text-[10px] font-black uppercase tracking-[0.2em] text-slate-400 group-hover:text-white transition-colors">{domain.label}</span>
                        </div>
                     ))}
                  </div>
               </div>
            </section>

            {/* Lawyer CTA */}
            <section className="py-40">
               <div className="max-w-7xl mx-auto px-6">
                  <div className="relative glass-effect p-12 md:p-24 rounded-[64px] border border-white/10 overflow-hidden text-center space-y-10 group">
                     <div className="absolute top-0 left-0 w-full h-full bg-gradient-to-br from-indigo-600/10 to-transparent pointer-events-none"></div>
                     <h2 className="text-4xl md:text-7xl font-black text-white leading-tight">Professional <br /> <span className="text-indigo-500">Legal Practice</span></h2>
                     <p className="text-slate-400 font-medium text-xl max-w-2xl mx-auto">Digitize your practice. Reach clients who need your specific domain expertise.</p>
                     <div className="flex justify-center pt-6">
                        <Link to="/signup?role=lawyer" className="px-12 py-6 bg-white text-black rounded-[24px] font-black text-sm uppercase tracking-[0.3em] hover:scale-105 transition-all shadow-2xl">Register as Advocate</Link>
                     </div>
                  </div>
               </div>
            </section>

            {/* Footer */}
            <footer className="pt-32 pb-16 border-t border-white/5">
               <div className="max-w-7xl mx-auto px-6 grid grid-cols-1 md:grid-cols-4 gap-20 mb-32">
                  <div className="space-y-8">
                     <Link to="/" className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center">
                           <Scale size={20} className="text-white" />
                        </div>
                        <span className="text-lg font-black tracking-tighter text-white">Vakeel<span className="text-indigo-500">Link</span></span>
                     </Link>
                     <p className="text-slate-500 text-sm leading-relaxed font-medium">
                        Democratizing legal access through cutting-edge technology and verified expertise.
                     </p>
                  </div>
                  
                  {[
                     { title: 'Platform', links: ['Legal AI', 'Lawyer Directory', 'Case Search'] },
                     { title: 'Resources', links: ['Knowledge Base', 'Legal Codes', 'API Docs'] },
                     { title: 'Company', links: ['About Us', 'Contact', 'Privacy Policy'] }
                  ].map((col, i) => (
                     <div key={i} className="space-y-8">
                        <h4 className="text-[10px] font-black uppercase tracking-[0.3em] text-white">{col.title}</h4>
                        <ul className="space-y-4">
                           {col.links.map(link => (
                              <li key={link}><Link to="#" className="text-xs font-bold text-slate-600 hover:text-indigo-400 transition-colors">{link}</Link></li>
                           ))}
                        </ul>
                     </div>
                  ))}
               </div>
               
               <div className="max-w-7xl mx-auto px-6 pt-16 border-t border-white/5 flex flex-col md:flex-row justify-between items-center gap-8">
                  <p className="text-[10px] font-black uppercase tracking-widest text-slate-700">© 2024 VakeelLink Legal Technologies. All Rights Reserved.</p>
                  <div className="flex gap-8">
                     {['LinkedIn', 'Twitter', 'GitHub'].map(social => (
                        <Link key={social} to="#" className="text-[10px] font-black uppercase tracking-widest text-slate-700 hover:text-white transition-colors">{social}</Link>
                     ))}
                  </div>
               </div>
            </footer>
        </div>
    );
};

export default LandingPage;