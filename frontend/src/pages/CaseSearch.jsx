import React, { useState, useEffect, useMemo, useRef } from 'react';
import {
  Scale, Gavel, Calendar, Tag, FileText, Quote, X, Filter,
  ChevronRight, Loader2, ArrowRight, MapPin, CheckCircle2, BookOpen, Shield, Users, Search
} from 'lucide-react';
import UserSidebar from '../components/UserSidebar';
import { ragRetrieve, ragDomains } from '../lib/api';

// ── Domain styling ────────────────────────────────────────────────────────────
const DOMAIN_STYLES = {
  constitutional: { bg: 'bg-purple-500/15', text: 'text-purple-300', border: 'border-purple-500/30', glow: 'shadow-purple-500/20' },
  criminal:       { bg: 'bg-red-500/15',    text: 'text-red-300',    border: 'border-red-500/30',    glow: 'shadow-red-500/20' },
  family:         { bg: 'bg-pink-500/15',   text: 'text-pink-300',   border: 'border-pink-500/30',   glow: 'shadow-pink-500/20' },
  consumer:       { bg: 'bg-emerald-500/15',text: 'text-emerald-300',border: 'border-emerald-500/30',glow: 'shadow-emerald-500/20' },
  labour:         { bg: 'bg-amber-500/15',  text: 'text-amber-300',  border: 'border-amber-500/30',  glow: 'shadow-amber-500/20' },
  civil:          { bg: 'bg-blue-500/15',   text: 'text-blue-300',   border: 'border-blue-500/30',   glow: 'shadow-blue-500/20' },
  default:        { bg: 'bg-slate-500/15',  text: 'text-slate-300',  border: 'border-slate-500/30',  glow: 'shadow-slate-500/20' },
};

const getDomainStyle = (domain = '') => {
  const key = Object.keys(DOMAIN_STYLES).find(k => k !== 'default' && domain.toLowerCase().includes(k));
  return DOMAIN_STYLES[key] || DOMAIN_STYLES.default;
};

// ── Court options ─────────────────────────────────────────────────────────────
const COURTS = [
  { id: 'All Courts',    label: 'All Jurisdictions', sub: 'Browse everything', Icon: Gavel,   gradient: 'from-slate-600/40 to-slate-800/60',   accent: 'text-slate-300',  active: 'border-slate-400 shadow-slate-400/20' },
  { id: 'Supreme Court', label: 'Supreme Court',      sub: '12 000+ judgments', Icon: Scale,   gradient: 'from-indigo-600/30 to-indigo-900/60',  accent: 'text-indigo-300', active: 'border-indigo-500 shadow-indigo-500/20' },
  { id: 'High Court',    label: 'High Courts',         sub: '38 000+ judgments', Icon: Shield,  gradient: 'from-cyan-600/30 to-cyan-900/60',       accent: 'text-cyan-300',   active: 'border-cyan-500 shadow-cyan-500/20' },
  { id: 'Tribunals',     label: 'Tribunals & Forums',  sub: '5 000+ judgments',  Icon: Users,   gradient: 'from-emerald-600/30 to-emerald-900/60', accent: 'text-emerald-300',active: 'border-emerald-500 shadow-emerald-500/20' },
];

// ── Map raw API data to UI model ──────────────────────────────────────────────
const mapCase = (c) => ({
  id:       c.chunk_id || `${Math.random()}`,
  name:     c.case_name || 'Untitled Case',
  citation: c.source   || 'N/A',
  court:    c.court    || 'N/A',
  year:     c.year     || '',
  domain:   c.domain   || 'General',
  summary:  (c.legal_issue && c.legal_issue !== 'unknown') ? c.legal_issue : (c.text?.substring(0, 220) + '…'),
  fullText: c.text     || 'No full text available.',
});

// ── CaseSearch component ──────────────────────────────────────────────────────
export default function CaseSearch() {
  const [cases,         setCases]         = useState([]);
  const [domains,       setDomains]       = useState([]);
  const [activeCourt,   setActiveCourt]   = useState('All Courts');
  const [activeDomain,  setActiveDomain]  = useState('');
  const [yearFrom,      setYearFrom]      = useState('');
  const [yearTo,        setYearTo]        = useState('');
  const [isLoading,     setIsLoading]     = useState(false);
  const [error,         setError]         = useState(null);
  const [selectedCase,  setSelectedCase]  = useState(null);
  const [toast,         setToast]         = useState({ show: false, message: '' });
  const [keyword,       setKeyword]        = useState('');
  const resultsRef = useRef(null);
  const abortRef   = useRef(null);

  // ── Unified fetch ────────────────────────────────────────────────────────
  const fetchData = React.useCallback(async (kw, court, domain) => {
    // Build natural-language query from active filters
    const parts = [];
    if (kw?.trim()) parts.push(kw.trim());
    if (court && court !== 'All Courts') parts.push(`${court} India`);
    if (!parts.length) parts.push('landmark Indian judgments law');
    const query = parts.join(' ');

    // Cancel any in-flight request
    if (abortRef.current) abortRef.current.abort();
    const ctrl = new AbortController();
    abortRef.current = ctrl;

    setIsLoading(true);
    setError(null);
    try {
      const data = await ragRetrieve({
        query,
        domain: domain || null,
        top_k:  20,
        use_hybrid: true,
      });
      if (ctrl.signal.aborted) return;
      if (!Array.isArray(data)) throw new Error('Invalid response from server');
      setCases(data.map(mapCase));
      resultsRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
    } catch (err) {
      if (ctrl.signal.aborted) return;
      setError(err.message);
    } finally {
      if (!ctrl.signal.aborted) setIsLoading(false);
    }
  }, []);

  // Initial load
  useEffect(() => {
    fetchData('', 'All Courts', '');
  }, [fetchData]);

  // Refetch when court or domain pill changes
  useEffect(() => {
    fetchData(keyword, activeCourt, activeDomain);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeCourt, activeDomain]);

  // Load domain list once
  useEffect(() => {
    ragDomains().then(d => Array.isArray(d) && setDomains(d)).catch(() => {});
  }, []);

  // Client-side year filter only (no extra network call)
  const filtered = useMemo(() => cases.filter(c => {
    if (yearFrom && parseInt(c.year) < parseInt(yearFrom)) return false;
    if (yearTo   && parseInt(c.year) > parseInt(yearTo))   return false;
    return true;
  }), [cases, yearFrom, yearTo]);

  const handleSearch = () => fetchData(keyword, activeCourt, activeDomain);

  const showToast = (msg) => {
    setToast({ show: true, message: msg });
    setTimeout(() => setToast({ show: false, message: '' }), 2500);
  };

  const handleCite = (citation) => {
    navigator.clipboard.writeText(citation);
    showToast('Citation copied!');
  };

  // ── JSX ─────────────────────────────────────────────────────────────────────
  return (
    <div className="flex min-h-screen bg-[#020617] text-slate-200 font-inter">
      <UserSidebar />

      <main className="flex-1 md:ml-[280px] overflow-y-auto">

        {/* ── Page Header ────────────────────────────────────────────────────── */}
        <div className="relative px-8 md:px-16 pt-12 pb-10 border-b border-white/5">
          <div className="absolute top-0 right-0 w-[400px] h-[300px] bg-indigo-700/8 blur-[120px] rounded-full pointer-events-none" />
          <div className="relative flex flex-col md:flex-row md:items-end md:justify-between gap-6">
            <div>
              <p className="text-[10px] font-black uppercase tracking-[0.3em] text-indigo-400 mb-3 flex items-center gap-3">
                <span className="inline-block w-6 h-px bg-indigo-500" />
                Legal Discovery
              </p>
              <h1 className="text-4xl md:text-5xl font-black tracking-tight text-white leading-none">
                Case <span className="text-indigo-400">Search</span>
              </h1>
              <p className="text-slate-500 text-base mt-3 font-medium">
                55 000+ judgments · AI-powered semantic retrieval
              </p>
            </div>

            {/* Inline stats */}
            <div className="flex items-center gap-8 pb-1">
              {[['55K+', 'Judgments'], ['426', 'Cases'], ['24/7', 'AI']].map(([num, label]) => (
                <div key={label} className="text-right">
                  <div className="text-2xl font-black text-white">{num}</div>
                  <div className="text-[10px] font-black uppercase tracking-[0.2em] text-slate-600">{label}</div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* ── Court Jurisdiction Cards ───────────────────────────────────────── */}
        <div className="px-8 md:px-16 mb-12">
          <h2 className="text-[10px] font-black uppercase tracking-[0.3em] text-slate-600 mb-6">
            Select Jurisdiction
          </h2>
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            {COURTS.map(({ id, label, sub, Icon, gradient, accent, active }) => {
              const isActive = activeCourt === id;
              return (
                <button
                  key={id}
                  onClick={() => setActiveCourt(id)}
                  className={`group relative p-7 rounded-[32px] border text-left transition-all duration-500 overflow-hidden
                    ${isActive
                      ? `border-opacity-100 shadow-2xl ${active} bg-gradient-to-br ${gradient}`
                      : 'border-white/5 hover:border-white/15 bg-white/[0.02] hover:bg-white/[0.04]'
                    }`}
                >
                  {/* Hover fill */}
                  <div className={`absolute inset-0 bg-gradient-to-br ${gradient} opacity-0 group-hover:opacity-100 transition-opacity duration-500`} />

                  <div className="relative">
                    <div className={`w-12 h-12 rounded-2xl flex items-center justify-center mb-5 transition-all duration-300
                      ${isActive ? `bg-white/10 ${accent}` : 'bg-white/5 text-slate-500 group-hover:text-slate-300'}`}>
                      <Icon size={22} />
                    </div>
                    <div className={`text-base font-black leading-tight mb-1 ${isActive ? 'text-white' : 'text-slate-300'}`}>{label}</div>
                    <div className={`text-[10px] font-bold uppercase tracking-widest ${isActive ? accent : 'text-slate-600 group-hover:text-slate-500'}`}>{sub}</div>
                  </div>

                  {isActive && (
                    <div className={`absolute top-4 right-4 w-2 h-2 rounded-full animate-pulse ${accent.replace('text-', 'bg-')}`} />
                  )}
                </button>
              );
            })}
          </div>
        </div>

        {/* ── Keyword Search Bar ─────────────────────────────────────────────── */}
        {/* <div className="px-8 md:px-16 mb-10">
          <div className="flex items-center gap-3 glass-effect border border-white/10 rounded-2xl px-6 py-1 shadow-xl shadow-indigo-500/5 focus-within:border-indigo-500/40 transition-colors">
            <Search size={18} className="text-slate-500 shrink-0" />
            <input
              type="text"
              placeholder="Search by case name, citation, legal issue…"
              value={keyword}
              onChange={e => setKeyword(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && handleSearch()}
              className="flex-1 py-4 bg-transparent outline-none text-white text-[15px] placeholder:text-slate-600 font-medium"
            />
            {keyword && (
              <button onClick={() => { setKeyword(''); fetchData('', activeCourt, activeDomain); }}
                className="text-slate-500 hover:text-white transition-colors">
                <X size={16} />
              </button>
            )} */}
            {/* <button
              onClick={handleSearch}
              disabled={isLoading}
              className="flex items-center gap-2 px-6 py-3 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl font-black text-[10px] uppercase tracking-widest transition-all shadow-lg shadow-indigo-600/20 hover:scale-[1.02] active:scale-[0.98] disabled:opacity-50"
            >
              {isLoading ? <Loader2 size={14} className="animate-spin" /> : <><Search size={14} /> Search</>}
            </button>
          </div>
        </div> */}

        {/* ── Domain Pill Row ────────────────────────────────────────────────── */}
        {domains.length > 0 && (
          <div className="px-8 md:px-16 mb-16">
            <div className="flex items-center gap-4 mb-5">
              <h2 className="text-[10px] font-black uppercase tracking-[0.3em] text-slate-600">Filter by Domain</h2>
              <div className="flex-1 h-px bg-white/5" />
              {activeDomain && (
                <button onClick={() => setActiveDomain('')} className="text-[10px] font-black uppercase tracking-widest text-rose-400 hover:text-rose-300 transition-colors">
                  Clear ×
                </button>
              )}
            </div>
            <div className="flex flex-wrap gap-3">
              <button
                onClick={() => setActiveDomain('')}
                className={`px-6 py-3 rounded-xl text-[10px] font-black uppercase tracking-widest border transition-all
                  ${!activeDomain ? 'bg-indigo-600 border-indigo-500 text-white shadow-lg shadow-indigo-500/20' : 'bg-white/5 border-white/5 text-slate-500 hover:text-white hover:border-white/10'}`}
              >
                All
              </button>
              {domains.slice(0, 14).map(d => {
                const s = getDomainStyle(d);
                const isActive = activeDomain === d;
                return (
                  <button
                    key={d}
                    onClick={() => setActiveDomain(d)}
                    className={`px-6 py-3 rounded-xl text-[10px] font-black uppercase tracking-widest border transition-all
                      ${isActive ? `${s.bg} ${s.text} ${s.border} shadow-lg ${s.glow}` : 'bg-white/5 border-white/5 text-slate-500 hover:text-white hover:border-white/10'}`}
                  >
                    {d}
                  </button>
                );
              })}
            </div>

            {/* Year range + Apply */}
            <div className="flex items-center gap-4 mt-6">
              <Calendar size={14} className="text-slate-600" />
              <span className="text-[10px] font-black uppercase tracking-widest text-slate-600">Year</span>
              <input type="text" placeholder="From" value={yearFrom} onChange={e => setYearFrom(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && fetchData(keyword, activeCourt, activeDomain)}
                className="w-16 bg-white/5 border border-white/5 rounded-lg px-3 py-2 text-[11px] text-white placeholder:text-slate-700 outline-none focus:border-indigo-500 transition-colors" />
              <span className="text-slate-700">–</span>
              <input type="text" placeholder="To" value={yearTo} onChange={e => setYearTo(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && fetchData(keyword, activeCourt, activeDomain)}
                className="w-16 bg-white/5 border border-white/5 rounded-lg px-3 py-2 text-[11px] text-white placeholder:text-slate-700 outline-none focus:border-indigo-500 transition-colors" />
              {(yearFrom || yearTo) && (
                <button
                  onClick={() => { setYearFrom(''); setYearTo(''); }}
                  className="text-[10px] font-black uppercase tracking-widest text-rose-400 hover:text-rose-300 transition-colors"
                >Clear</button>
              )}
            </div>
          </div>
        )}

        {/* ── Results ───────────────────────────────────────────────────────── */}
        <div ref={resultsRef} className="px-8 md:px-16 pb-24">

          {/* Results header */}
          <div className="flex items-center gap-4 mb-8">
            <h2 className="text-[10px] font-black uppercase tracking-[0.3em] text-slate-600">
              {isLoading ? 'Loading…' : `${filtered.length} Judgments`}
            </h2>
            <div className="flex-1 h-px bg-white/5" />
          </div>

          {/* Loading skeleton */}
          {isLoading && (
            <div className="space-y-6">
              {[1,2,3,4].map(i => (
                <div key={i} className="h-52 rounded-[32px] bg-white/[0.02] border border-white/5 animate-pulse" />
              ))}
            </div>
          )}

          {/* Error */}
          {!isLoading && error && (
            <div className="glass-effect rounded-[32px] border border-red-500/20 bg-red-500/5 p-12 text-center">
              <X className="text-red-400 mx-auto mb-4" size={48} />
              <h3 className="text-2xl font-black text-white mb-2">Failed to Load</h3>
              <p className="text-slate-500 mb-6">{error}</p>
              <button onClick={() => setActiveCourt(activeCourt)}
                className="px-8 py-4 bg-indigo-600 text-white rounded-2xl font-black text-[10px] uppercase tracking-widest hover:bg-indigo-500 transition-colors">
                Retry
              </button>
            </div>
          )}

          {/* Empty */}
          {!isLoading && !error && filtered.length === 0 && (
            <div className="rounded-[40px] border border-dashed border-white/10 p-24 text-center">
              <BookOpen className="text-indigo-500/30 mx-auto mb-6" size={64} />
              <h3 className="text-2xl font-black text-white mb-2">No Judgments Found</h3>
              <p className="text-slate-500">Try selecting a different jurisdiction or domain.</p>
            </div>
          )}

          {/* Case Cards */}
          {!isLoading && !error && (
            <div className="space-y-5">
              {filtered.map((c, idx) => {
                const ds = getDomainStyle(c.domain);
                return (
                  <div
                    key={c.id}
                    className="group glass-effect rounded-[32px] border border-white/[0.06] p-8 md:p-10 hover:border-indigo-500/40 transition-all duration-500 hover:shadow-2xl hover:shadow-indigo-500/5 cursor-pointer"
                    style={{ animationDelay: `${idx * 40}ms` }}
                    onClick={() => setSelectedCase(c)}
                  >
                    <div className="flex flex-col lg:flex-row lg:items-start gap-8">
                      {/* Left: content */}
                      <div className="flex-1 min-w-0">
                        {/* Tags row */}
                        <div className="flex flex-wrap items-center gap-3 mb-5">
                          <span className={`px-4 py-1.5 rounded-lg text-[9px] font-black uppercase tracking-widest border ${ds.bg} ${ds.text} ${ds.border}`}>
                            {c.domain}
                          </span>
                          {c.year && (
                            <span className="flex items-center gap-1.5 text-[10px] font-bold text-slate-500">
                              <Calendar size={12} /> {c.year}
                            </span>
                          )}
                          <span className="flex items-center gap-1.5 text-[10px] font-bold text-slate-500">
                            <Scale size={12} /> {c.court}
                          </span>
                        </div>

                        {/* Case name */}
                        <h3 className="text-xl md:text-2xl font-black text-white leading-tight mb-4 group-hover:text-indigo-300 transition-colors line-clamp-2">
                          {c.name}
                        </h3>

                        {/* Summary */}
                        <p className="text-slate-400 leading-relaxed line-clamp-3 text-[15px]">
                          {c.summary}
                        </p>
                      </div>

                      {/* Right: actions */}
                      <div className="flex lg:flex-col gap-3 shrink-0">
                        <button
                          onClick={e => { e.stopPropagation(); setSelectedCase(c); }}
                          className="flex items-center gap-2 px-6 py-3.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-2xl text-[10px] font-black uppercase tracking-widest transition-all shadow-xl shadow-indigo-600/20 hover:scale-[1.02]"
                        >
                          <FileText size={14} /> Read
                        </button>
                        <button
                          onClick={e => { e.stopPropagation(); handleCite(c.citation); }}
                          className="flex items-center gap-2 px-6 py-3.5 bg-white/5 hover:bg-white/10 text-slate-400 hover:text-white rounded-2xl text-[10px] font-black uppercase tracking-widest transition-all"
                        >
                          <Quote size={14} /> Cite
                        </button>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </main>

      {/* ── Full Judgment Modal ─────────────────────────────────────────────── */}
      {selectedCase && (
        <div
          className="fixed inset-0 z-[100] flex items-center justify-center p-4 md:p-10 bg-black/75 backdrop-blur-lg"
          onClick={() => setSelectedCase(null)}
        >
          <div
            className="glass-effect w-full max-w-5xl max-h-[90vh] flex flex-col rounded-[40px] border border-white/10 shadow-2xl overflow-hidden"
            onClick={e => e.stopPropagation()}
          >
            {/* Modal Header */}
            <div className="flex items-start justify-between p-8 md:p-12 border-b border-white/5 bg-white/[0.02]">
              <div className="flex items-center gap-5">
                <div className="w-14 h-14 rounded-2xl bg-indigo-500/10 flex items-center justify-center text-indigo-400">
                  <Scale size={26} />
                </div>
                <div>
                  <h2 className="text-2xl font-black text-white leading-tight">{selectedCase.name}</h2>
                  <div className="flex items-center gap-3 mt-2">
                    <span className="text-[10px] font-black text-slate-500 uppercase tracking-widest bg-white/5 px-3 py-1 rounded-lg">
                      {selectedCase.citation}
                    </span>
                    <span className="text-[10px] font-black text-indigo-400 uppercase tracking-widest">{selectedCase.court}</span>
                  </div>
                </div>
              </div>
              <button onClick={() => setSelectedCase(null)}
                className="p-3 rounded-xl bg-white/5 hover:bg-white/10 text-slate-400 hover:text-white transition-all">
                <X size={22} />
              </button>
            </div>

            {/* Modal Body */}
            <div className="flex-1 overflow-y-auto p-8 md:p-12">
              {/* Metadata grid */}
              <div className="grid grid-cols-3 gap-4 mb-10">
                {[
                  { label: 'Year', value: selectedCase.year || 'N/A', Icon: Calendar },
                  { label: 'Court', value: selectedCase.court, Icon: Gavel },
                  { label: 'Domain', value: selectedCase.domain, Icon: Tag },
                ].map(({ label, value, Icon }) => (
                  <div key={label} className="bg-white/[0.03] rounded-2xl border border-white/5 p-6">
                    <div className="flex items-center gap-2 mb-2">
                      <Icon size={14} className="text-indigo-400" />
                      <span className="text-[10px] font-black uppercase tracking-widest text-slate-500">{label}</span>
                    </div>
                    <p className="text-white font-black text-lg">{value}</p>
                  </div>
                ))}
              </div>

              {/* Full text */}
              <div className="prose prose-invert max-w-none">
                <h4 className="text-[10px] font-black uppercase tracking-[0.3em] text-slate-500 mb-6 flex items-center gap-3">
                  <span className="inline-block w-6 h-px bg-indigo-500" /> Judgment Text
                </h4>
                <div className="text-slate-300 leading-relaxed text-[15px] whitespace-pre-wrap">
                  {selectedCase.fullText}
                </div>
              </div>
            </div>

            {/* Modal Footer */}
            <div className="flex justify-end gap-4 p-8 border-t border-white/5 bg-white/[0.02]">
              <button onClick={() => handleCite(selectedCase.citation)}
                className="flex items-center gap-2 px-8 py-4 bg-white/5 border border-white/10 hover:bg-white/10 text-white rounded-2xl font-black text-[10px] uppercase tracking-widest transition-all">
                <Quote size={14} /> Copy Citation
              </button>
              <button onClick={() => setSelectedCase(null)}
                className="flex items-center gap-2 px-8 py-4 bg-indigo-600 hover:bg-indigo-500 text-white rounded-2xl font-black text-[10px] uppercase tracking-widest transition-all shadow-xl shadow-indigo-600/20">
                Close <X size={14} />
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ── Toast ──────────────────────────────────────────────────────────── */}
      {toast.show && (
        <div className="fixed bottom-10 right-10 z-[200] glass-effect border border-indigo-500/30 text-white px-8 py-5 rounded-2xl shadow-2xl flex items-center gap-4 animate-in fade-in slide-in-from-bottom-4">
          <CheckCircle2 size={20} className="text-emerald-400" />
          <span className="font-black text-[10px] uppercase tracking-widest">{toast.message}</span>
        </div>
      )}
    </div>
  );
}
