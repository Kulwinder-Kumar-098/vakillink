import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  Scale, 
  FileText, 
  History, 
  Search, 
  TriangleAlert, 
  Gavel, 
  Shield,
  Plus,
  Zap,
  ChevronRight,
  ArrowRight,
  X,
  Loader2,
  User as UserIcon,
  Cpu,
  CircleCheckBig
} from 'lucide-react';
import UserSidebar from '../components/UserSidebar';
import { useAuth } from '../components/AuthContext';

const CaseCurator = () => {
    const { user } = useAuth();
    
    // Form States
    const [caseType, setCaseType] = useState('');
    const [incidentDate, setIncidentDate] = useState('');
    const [complexity, setComplexity] = useState('Standard');
    const [description, setDescription] = useState('');
    const [opposingParty, setOpposingParty] = useState('');
    
    // UI States
    const [isLoading, setIsLoading] = useState(false);
    const [report, setReport] = useState(null);
    const [isArchiveModalOpen, setIsArchiveModalOpen] = useState(false);
    const [errors, setErrors] = useState({});

    const caseTypes = [
        'Property Dispute', 'Custody & Family', 'Contractual Breach', 
        'Criminal Defense', 'Consumer Complaint', 'Labour Dispute', 
        'Motor Accident Claim', 'Constitutional Matter', 'Cyber Crime', 
        'Cheque Bounce (NI Act)'
    ];

    const opposingPartyTypes = [
        'Individual', 'Corporation', 'Government Body', 'Employer', 'Bank/NBFC'
    ];

    const handleGenerateReport = async () => {
        const newErrors = {};
        if (!caseType) newErrors.caseType = 'Required';
        if (!description.trim()) newErrors.description = 'Required';
        
        if (Object.keys(newErrors).length > 0) {
            setErrors(newErrors);
            return;
        }

        setErrors({});
        setIsLoading(true);
        setReport(null);
        
        try {
            const token = localStorage.getItem('vakeellink_token');
            const queryText = `Case Type: ${caseType}. Complexity: ${complexity}. Opposing Party: ${opposingParty}. Incident Date: ${incidentDate}. Description: ${description}`;
            
            const res = await fetch('http://127.0.0.1:9000/api/v1/query', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ query: queryText })
            });

            if (!res.ok) throw new Error('AI Inquiry failed');
            const data = await res.json();
            
            // Map RAG response to the report UI
            setReport({
                caseType: data.domain || caseType,
                analysis: data.analysis,
                framework: data.cited_acts && data.cited_acts.length > 0 ? data.cited_acts : (data.cited_sections || []),
                cited_sections: data.cited_sections || [],
                cited_cases: data.cited_cases || [],
                risk: complexity === 'Litigation' ? 'High' : complexity === 'Complex' ? 'Medium' : 'Low',
                timeline: complexity === 'Litigation' ? '18-24 months' : complexity === 'Complex' ? '12-18 months' : '6-12 months',
                actions: [
                    'Review cited legal sections and acts',
                    'Document all communications and financial records',
                    'Consult a specialized advocate for procedural filing'
                ],
                specialization: `${(data.domain || caseType).split(' ')[0]} Specialist`,
                raw_citations: data.citations || []
            });
        } catch (error) {
            console.error('AI Report Error:', error);
            // Minimal fallback for stability
            setReport({
                caseType,
                analysis: "Our AI engine is temporarily unavailable. Please try again shortly.",
                framework: ['Legal Framework Loading...'],
                risk: 'Unknown',
                actions: ['Please retry in a few moments'],
                specialization: 'Legal Professional'
            });
        } finally {
            setIsLoading(false);
        }
    };

    const getInitials = (name) => {
        if (!name) return 'U';
        return name.split(' ').map(n => n[0]).join('').toUpperCase().substring(0, 2);
    };

    return (
        <div className="flex min-h-screen bg-[#020617] text-slate-200 font-inter">
            <UserSidebar />

            <main className="flex-1 md:ml-[280px] p-6 md:p-12 overflow-y-auto">
                <div className="max-w-7xl mx-auto space-y-12">
                    
                    {/* Header with User Info */}
                    <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
                        <div>
                            <h1 className="text-4xl lg:text-5xl font-black text-white leading-tight tracking-tight">
                                AI <span className="text-indigo-500">Assistant</span>
                            </h1>
                            <p className="text-slate-500 text-sm font-bold uppercase tracking-widest mt-2">Premium Legal Intelligence</p>
                        </div>

                        <div className="flex items-center gap-4 glass-effect p-3 pr-8 rounded-3xl border border-white/10 shadow-sm">
                            <div className="w-12 h-12 rounded-2xl bg-indigo-600 flex items-center justify-center text-white font-black text-lg shadow-lg shadow-indigo-600/20">
                                {getInitials(user?.name)}
                            </div>
                            <div className="flex flex-col">
                                <span className="text-sm font-black text-white leading-none">{user?.name || 'Authorized User'}</span>
                                <span className="text-[10px] font-black text-indigo-400 uppercase tracking-widest mt-1">{user?.role || 'Premium'} Plan</span>
                            </div>
                        </div>
                    </div>

                    <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 items-start">
                        {/* Input Interface Column */}
                        <div className="lg:col-span-5 space-y-8">
                            <div className="glass-effect p-8 rounded-[40px] border border-white/10 space-y-8 shadow-sm">
                                <div className="space-y-6">
                                    <label className="text-[10px] font-black uppercase tracking-[0.3em] text-indigo-400 flex items-center gap-2">
                                        <FileText size={14} /> Incident Particulars
                                    </label>
                                    
                                    <div className="space-y-2">
                                        <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Brief Description</label>
                                        <textarea 
                                            value={description}
                                            onChange={(e) => setDescription(e.target.value)}
                                            className={`w-full h-32 p-5 bg-white/5 border ${errors.description ? 'border-rose-500' : 'border-white/10'} rounded-2xl outline-none text-white placeholder:text-slate-600 resize-none text-sm leading-relaxed focus:border-indigo-500/50 transition-all`} 
                                            placeholder="Describe what happened in 2–3 sentences..."
                                        />
                                    </div>

                                    <div className="grid grid-cols-2 gap-4">
                                        <div className="space-y-2">
                                            <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Case Type</label>
                                            <select 
                                                value={caseType}
                                                onChange={(e) => setCaseType(e.target.value)}
                                                className={`w-full bg-white/5 border ${errors.caseType ? 'border-rose-500' : 'border-white/10'} rounded-xl px-4 py-3 text-xs text-white focus:border-indigo-500/50 outline-none transition-all appearance-none cursor-pointer`}
                                            >
                                                <option value="" disabled className="bg-[#020617]">Select Type</option>
                                                {caseTypes.map(t => <option key={t} value={t} className="bg-[#020617]">{t}</option>)}
                                            </select>
                                        </div>

                                        <div className="space-y-2">
                                            <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Incident Date</label>
                                            <input 
                                                type="date"
                                                value={incidentDate}
                                                onChange={(e) => setIncidentDate(e.target.value)}
                                                className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-xs text-white focus:border-indigo-500/50 outline-none transition-all color-scheme-dark" 
                                            />
                                        </div>

                                        <div className="space-y-2 col-span-2">
                                            <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Opposing Party</label>
                                            <select 
                                                value={opposingParty}
                                                onChange={(e) => setOpposingParty(e.target.value)}
                                                className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-xs text-white focus:border-indigo-500/50 outline-none transition-all appearance-none cursor-pointer"
                                            >
                                                <option value="" disabled className="bg-[#020617]">Select Type</option>
                                                {opposingPartyTypes.map(o => <option key={o} value={o} className="bg-[#020617]">{o}</option>)}
                                            </select>
                                        </div>
                                    </div>

                                    <div className="space-y-4">
                                        <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest block">Complexity Tier</label>
                                        <div className="flex gap-3">
                                            {['Standard', 'Complex', 'Litigation'].map(tier => (
                                                <button 
                                                    key={tier} 
                                                    type="button"
                                                    onClick={() => setComplexity(tier)}
                                                    className={`flex-1 py-3 border rounded-xl text-[10px] font-black uppercase tracking-widest transition-all ${
                                                        complexity === tier 
                                                        ? 'bg-indigo-600 border-indigo-600 text-white shadow-lg shadow-indigo-600/20' 
                                                        : 'bg-white/5 border-white/10 text-slate-500 hover:bg-white/10'
                                                    }`}
                                                >
                                                    {tier}
                                                </button>
                                            ))}
                                        </div>
                                    </div>
                                </div>

                                <div className="pt-4 space-y-4">
                                    <button 
                                        onClick={handleGenerateReport}
                                        disabled={isLoading}
                                        className="w-full py-5 bg-indigo-600 text-white rounded-2xl font-black tracking-[0.2em] uppercase text-[10px] shadow-2xl shadow-indigo-600/40 hover:scale-[1.02] active:scale-[0.98] transition-all flex items-center justify-center gap-3 disabled:opacity-50"
                                    >
                                        {isLoading ? <Loader2 size={18} className="animate-spin" /> : <Zap size={18} className="fill-white" />}
                                        Generate Intelligence Report
                                    </button>

                                    <button 
                                        onClick={() => setIsArchiveModalOpen(true)}
                                        className="w-full py-5 bg-white/5 border border-white/10 text-white rounded-2xl font-black tracking-[0.2em] uppercase text-[10px] hover:bg-white/10 transition-all flex items-center justify-center gap-3"
                                    >
                                        <History size={18} className="text-indigo-400" />
                                        Archival Context
                                    </button>
                                </div>
                            </div>
                        </div>

                        {/* AI Assistant Column */}
                        <div className="lg:col-span-7 h-full min-h-[600px]">
                            <div className="glass-effect rounded-[48px] border border-white/10 p-8 lg:p-12 shadow-sm flex flex-col h-full relative overflow-hidden group min-h-[600px]">
                                
                                {!report && !isLoading ? (
                                    <div className="flex-1 flex flex-col items-center justify-center text-center space-y-6 relative z-10">
                                        <div className="w-24 h-24 bg-white/5 rounded-[32px] flex items-center justify-center border border-white/10 shadow-inner">
                                            <Gavel size={40} className="text-slate-700" />
                                        </div>
                                        <div className="space-y-2">
                                            <h3 className="text-2xl font-black text-white tracking-tight">Describe your legal situation</h3>
                                            <p className="text-slate-500 text-sm max-w-xs mx-auto leading-relaxed font-medium">
                                                Fill in the case details and generate an intelligence report to see AI-powered analysis.
                                            </p>
                                        </div>
                                    </div>
                                ) : isLoading ? (
                                    <div className="flex-1 flex flex-col items-center justify-center space-y-6 relative z-10">
                                        <div className="relative">
                                            <div className="w-20 h-20 border-4 border-indigo-500/10 border-t-indigo-500 rounded-full animate-spin" />
                                            <div className="absolute inset-0 flex items-center justify-center">
                                                <Cpu size={24} className="text-indigo-500 animate-pulse" />
                                            </div>
                                        </div>
                                        <div className="text-center space-y-2">
                                            <p className="text-[10px] font-black text-indigo-500 uppercase tracking-[0.3em]">Synthesizing Data</p>
                                            <p className="text-slate-500 text-xs font-bold uppercase tracking-widest">Scanning precedents and legal codes...</p>
                                        </div>
                                    </div>
                                ) : (
                                    <div className="space-y-10 flex-1 relative animate-in fade-in slide-in-from-bottom-4 duration-700">
                                        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
                                            <div className="space-y-3">
                                                <div className="flex items-center gap-3">
                                                    <span className="px-3 py-1 bg-indigo-500/10 text-indigo-400 text-[10px] font-black uppercase tracking-widest rounded-lg border border-indigo-500/20">
                                                        AI Synthesized
                                                    </span>
                                                    <span className="text-slate-500 text-[10px] font-black uppercase tracking-widest">v4.2.0 Stable</span>
                                                </div>
                                                <h2 className="text-3xl font-black text-white">Intelligence Report — {report.caseType}</h2>
                                            </div>
                                        </div>

                                        <div className="space-y-4">
                                            <h3 className="text-[10px] font-black text-slate-500 uppercase tracking-widest flex items-center gap-2">
                                                <Shield size={14} className="text-indigo-500" /> Legal Framework
                                            </h3>
                                            <div className="flex flex-wrap gap-2">
                                                {report.framework?.map((act, i) => (
                                                    <span key={i} className="px-4 py-2 bg-white/5 border border-white/10 rounded-xl text-[11px] font-black uppercase tracking-widest text-slate-300">
                                                        {act}
                                                    </span>
                                                ))}
                                            </div>
                                        </div>

                                        <div className="grid grid-cols-2 gap-6 py-8 border-y border-white/5">
                                            <div className="space-y-4">
                                                <p className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Analysis</p>
                                                <p className="text-sm text-slate-300 leading-relaxed font-medium">
                                                    {report.analysis}
                                                </p>
                                            </div>
                                            <div className="space-y-4">
                                                <p className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Recommended Actions</p>
                                                <ul className="space-y-2">
                                                    {report.actions?.map((action, i) => (
                                                        <li key={i} className="flex items-start gap-2">
                                                            <CheckCircle2 size={12} className="text-emerald-500 mt-0.5" />
                                                            <span className="text-[11px] font-medium text-slate-400">{action}</span>
                                                        </li>
                                                    ))}
                                                </ul>
                                            </div>
                                        </div>

                                        <div className="grid grid-cols-2 gap-6 py-8 border-b border-white/5">
                                            <div className="space-y-2">
                                                <p className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Risk Assessment</p>
                                                <div className="flex items-center gap-2">
                                                    <div className={`w-2 h-2 rounded-full ${report.risk === 'High' ? 'bg-rose-500 shadow-[0_0_10px_rgba(244,63,94,0.3)]' : 'bg-indigo-500 shadow-[0_0_10px_rgba(99,102,241,0.3)]'}`} />
                                                    <span className="text-sm font-bold text-white">{report.risk} Complexity</span>
                                                </div>
                                                <p className="text-[11px] text-slate-500 mt-1 leading-relaxed font-medium">
                                                    Estimated timeline: {report.timeline}.
                                                </p>
                                            </div>
                                            <div className="space-y-2">
                                                <p className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Cited Statutes</p>
                                                <div className="flex flex-wrap gap-2">
                                                    {report.cited_sections?.slice(0, 3).map((section, i) => (
                                                        <span key={i} className="px-2 py-1 bg-white/5 border border-white/10 rounded-lg text-[9px] font-black text-slate-400">
                                                            {section}
                                                        </span>
                                                    ))}
                                                    {(report.cited_sections?.length || 0) > 3 && <span className="text-[9px] text-slate-500 font-bold">+{report.cited_sections.length - 3} more</span>}
                                                    {(!report.cited_sections || report.cited_sections.length === 0) && <span className="text-[9px] text-slate-600 font-bold italic">No sections cited</span>}
                                                </div>
                                            </div>
                                        </div>

                                        <div className="p-6 bg-white/5 rounded-3xl border border-white/10 flex items-center justify-between">
                                            <div>
                                                <p className="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-1">Suggested Lawyer Specialization</p>
                                                <p className="text-sm font-black text-white">{report.specialization}</p>
                                            </div>
                                            <Link to="/lawyers" className="p-3 bg-white/5 rounded-xl border border-white/10 hover:border-indigo-500/50 transition-colors shadow-sm text-indigo-400">
                                                <Search size={18} />
                                            </Link>
                                        </div>

                                        <div className="flex items-center gap-2 text-slate-600">
                                            <AlertTriangle size={14} />
                                            <span className="text-[10px] font-bold uppercase tracking-widest">AI-generated analysis. Not legal advice.</span>
                                        </div>
                                    </div>
                                )}

                                {report && (
                                    <div className="pt-10 flex flex-col sm:flex-row items-center justify-between gap-8 border-t border-white/5 mt-auto relative">
                                        <div className="flex items-center gap-5">
                                            <div className="flex -space-x-3">
                                                {[1, 2, 3].map(i => (
                                                    <img key={i} className="w-11 h-11 rounded-2xl border-4 border-[#020617] object-cover" src={`https://i.pravatar.cc/150?u=lawyer${i}`} alt="Specialist" />
                                                ))}
                                            </div>
                                            <p className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Qualified Specialists Ready</p>
                                        </div>
                                        <Link to="/lawyers" className="w-full sm:w-auto px-10 py-5 bg-indigo-600 text-white rounded-[22px] font-black text-[10px] uppercase tracking-[0.2em] hover:bg-indigo-500 transition-all shadow-xl shadow-indigo-500/20 flex items-center justify-center gap-3 group">
                                            Expert Consultation <ArrowRight size={16} className="group-hover:translate-x-1 transition-transform" />
                                        </Link>
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
                </div>
            </main>

            {/* Precedent Archive Modal */}
            {isArchiveModalOpen && (
                <div className="fixed inset-0 z-[100] flex items-center justify-center p-6 backdrop-blur-md bg-[#020617]/60 animate-in fade-in duration-300">
                    <div className="w-full max-w-2xl glass-effect border border-white/10 rounded-[40px] shadow-2xl overflow-hidden relative">
                        <button 
                            onClick={() => setIsArchiveModalOpen(false)}
                            className="absolute top-8 right-8 text-slate-500 hover:text-white transition-colors"
                        >
                            <X size={24} />
                        </button>
                        
                        <div className="p-12 space-y-10">
                            <div className="space-y-3">
                                <h3 className="text-3xl font-black text-white">Precedent Archive</h3>
                                <p className="text-slate-500 text-[10px] font-black uppercase tracking-[0.2em]">
                                    Historical judicial decisions related to {caseType || 'General Law'}
                                </p>
                            </div>

                            <div className="space-y-6 max-h-[400px] overflow-y-auto pr-4 custom-scrollbar">
                                {(report?.raw_citations && report.raw_citations.length > 0 ? report.raw_citations : [
                                    { law_name: 'Suraj Lamp & Industries v. State of Haryana', domain: 'Supreme Court', year: '2011', legal_issue: 'GPA/SA/Will transfers do not confer title.' },
                                    { law_name: 'Anathula Sudhakar v. P. Buchi Reddy', domain: 'Supreme Court', year: '2008', legal_issue: 'Scope of suits for prohibition, injunction and declaration.' }
                                ]).map((precedent, i) => (
                                    <div key={i} className="p-6 bg-white/5 border border-white/10 rounded-3xl hover:border-indigo-500/30 transition-all group mb-4">
                                        <div className="flex justify-between items-start mb-4">
                                            <h4 className="text-sm font-black text-white group-hover:text-indigo-400 transition-colors">{precedent.law_name || precedent.name}</h4>
                                            <span className="text-[10px] font-black text-slate-500 uppercase tracking-widest bg-white/5 px-3 py-1 rounded-lg border border-white/10">
                                                {precedent.year || 'N/A'}
                                            </span>
                                        </div>
                                        <div className="flex gap-4 items-center mb-3">
                                            <span className="text-[10px] font-black text-indigo-500 uppercase tracking-widest">{precedent.domain || precedent.court}</span>
                                        </div>
                                        <p className="text-xs text-slate-400 leading-relaxed font-medium">
                                            {precedent.legal_issue || precedent.summary}
                                        </p>
                                    </div>
                                ))}
                            </div>

                            <button 
                                onClick={() => setIsArchiveModalOpen(false)}
                                className="w-full py-5 bg-indigo-600 text-white rounded-2xl font-black uppercase tracking-widest text-[10px] hover:bg-indigo-500 transition-all shadow-xl shadow-indigo-600/20"
                            >
                                Close Archive
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default CaseCurator;