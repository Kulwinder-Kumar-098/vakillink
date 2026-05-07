import React, { useEffect, useMemo, useState } from 'react';
import {
  ArrowRight,
  Search,
  FileText,
  Quote,
  Loader2,
  Scale,
  Link as LinkIcon,
  Sparkles,
  Cpu,
  Timer,
  Clipboard,
  Share2,
  Download,
  MoreHorizontal,
  Send,
  ChevronRight
} from 'lucide-react';
import UserSidebar from '../components/UserSidebar';
import { apiFetch, ragQuery } from '../lib/api';

const CaseCurator = () => {
  const [domains, setDomains] = useState(['All']);
  const [selectedDomain, setSelectedDomain] = useState('All');
  const [topK, setTopK] = useState(5);
  const [query, setQuery] = useState('');
  const [followUp, setFollowUp] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [showAllRefs, setShowAllRefs] = useState(false);

  useEffect(() => {
    let cancelled = false;
    const loadDomains = async () => {
      try {
        const data = await apiFetch('/api/v1/ai/domains');
        if (cancelled) return;
        const list = Array.isArray(data) ? data : [];
        setDomains(['All', ...list]);
      } catch {
        if (cancelled) return;
        setDomains(['All', 'constitutional', 'criminal', 'consumer', 'family', 'labour', 'motor_accident', 'general']);
      }
    };
    loadDomains();
    return () => { cancelled = true; };
  }, []);

  const chunks = useMemo(() => {
    if (!result || !Array.isArray(result.chunks)) return [];
    return result.chunks;
  }, [result]);

  const confidence = useMemo(() => {
    const scores = chunks.map((c) => c?.score).filter((s) => typeof s === 'number' && Number.isFinite(s));
    if (scores.length === 0) return 0;
    const max = Math.max(...scores);
    const normalized = max > 1 ? scores.map((s) => s / max) : scores;
    const avg = normalized.reduce((a, b) => a + b, 0) / normalized.length;
    return Math.round(Math.max(0, Math.min(1, avg)) * 100);
  }, [chunks]);

  const answerParts = useMemo(() => {
    const raw = (result?.answer || '').toString().trim();
    const normalized = raw.replace(/\r\n/g, '\n');
    const lines = normalized.split('\n').map((l) => l.trim()).filter(Boolean);
    const stripBullet = (l) => l.replace(/^(?:[-*•]|\d+[.)])\s+/, '').trim();
    const bulletLines = lines.filter((l) => /^(?:[-*•]|\d+[.)])\s+/.test(l));
    const keyPointsFromBullets = bulletLines.map(stripBullet).filter(Boolean).slice(0, 8);
    const sentenceText = normalized.replace(/\s*\n+\s*/g, ' ').replace(/\s+/g, ' ').trim();
    const sentences = sentenceText.split(/(?<=[.!?])\s+/).map((s) => s.trim()).filter(Boolean);
    const summary = sentences.slice(0, 2).join(' ');
    const keyPointsFromSentences = sentences.slice(2, 8);
    const keyPoints = keyPointsFromBullets.length >= 2 ? keyPointsFromBullets : keyPointsFromSentences;
    const disclaimerLine = lines.find((l) => /not legal advice|disclaimer/i.test(l)) || '';
    return { raw, summary: summary || raw, keyPoints, disclaimerLine };
  }, [result]);

  const meta = useMemo(() => {
    const model = result?.model ? result.model.toString() : '';
    const usage = result?.usage && typeof result.usage === 'object' ? result.usage : {};
    const totalTokens = Number.isFinite(usage.total_tokens) ? usage.total_tokens : null;
    const latency = Number.isFinite(usage.latency_s) ? usage.latency_s : null;
    return { model, totalTokens, latency };
  }, [result]);

  const topReferences = useMemo(() => {
    return chunks.map((c) => ({
      title: c?.case_name || 'Untitled reference',
      subtitle: c?.legal_issue || '',
      tag: c?.domain || '',
      score: typeof c?.score === 'number' ? c.score : null,
      source: c?.source || '',
      text: c?.text || ''
    }));
  }, [chunks]);

  const visibleReferences = useMemo(() => {
    return showAllRefs ? topReferences : topReferences.slice(0, 4);
  }, [topReferences, showAllRefs]);

  const suggestedFollowUps = useMemo(() => {
    const base = ['How do I file a complaint?', 'What documents do I need?', 'What is the time limit (limitation period)?', 'Which authority/court has jurisdiction?'];
    const domain = selectedDomain && selectedDomain !== 'All' ? selectedDomain : '';
    const extra = domain ? [`More on ${domain} procedure`] : [];
    return [...base, ...extra].slice(0, 4);
  }, [selectedDomain]);

  const handleCopyAnswer = async () => {
    const text = answerParts.raw || '';
    if (!text) return;
    try { await navigator.clipboard.writeText(text); } catch { }
  };

  const handleShare = async () => {
    const text = answerParts.summary || answerParts.raw || '';
    if (!text) return;
    try {
      if (navigator.share) { await navigator.share({ title: 'Vakilink AI Response', text }); return; }
    } catch { }
    try { await navigator.clipboard.writeText(text); } catch { }
  };

  const handleExport = () => {
    const lines = [
      'Vakilink AI Response', '',
      `Question: ${query.trim()}`, `Domain: ${selectedDomain}`, `TopK: ${topK}`,
      meta.model ? `Model: ${meta.model}` : '',
      meta.totalTokens !== null ? `Tokens: ${meta.totalTokens}` : '',
      meta.latency !== null ? `Retrieval time: ${meta.latency}s` : '',
      '', 'Answer:', answerParts.raw || '', '', 'Top References:',
      ...topReferences.slice(0, 12).flatMap((r, idx) => [
        `${idx + 1}. ${r.title}`, r.subtitle ? `   Issue: ${r.subtitle}` : '', r.source ? `   Source: ${r.source}` : '', ''
      ])
    ].filter(Boolean);
    const blob = new Blob([lines.join('\n')], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url; a.download = 'vakilink-ai-response.txt'; a.click();
    URL.revokeObjectURL(url);
  };

  const runSearch = async (overrideQuery) => {
    const q = (overrideQuery ?? query).trim();
    if (q.length < 3) { setError('Please enter a more detailed question.'); return; }
    setError(''); setIsLoading(true); setResult(null); setShowAllRefs(false);
    try {
      const data = await ragQuery({ query: q, top_k: topK, domain: selectedDomain === 'All' ? null : selectedDomain, use_hybrid: true, use_reranker: false, include_chunks: true });
      setResult(data);
    } catch (e) {
      setError(e?.message || 'AI service failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const onKeyDown = (e) => { if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) runSearch(); };

  const handleAskFollowUp = async () => {
    const q = followUp.trim();
    if (q.length < 3) return;
    setQuery(q); setFollowUp('');
    runSearch(q);
  };

  const onFollowUpKeyDown = (e) => { if (e.key === 'Enter') { e.preventDefault(); handleAskFollowUp(); } };

  const handleNewQuestion = () => { setQuery(''); setFollowUp(''); setResult(null); setError(''); setShowAllRefs(false); };

  return (
    <div className="flex min-h-screen bg-[#020617] text-slate-200 font-inter">
      <UserSidebar />

      <main className="flex-1 md:ml-[280px] p-6 md:p-12 overflow-y-auto">
        <div className="max-w-7xl mx-auto space-y-8">

          {/* Page Header */}
          <div className="flex items-center justify-between gap-6 flex-wrap">
            <div>
              <h1 className="text-4xl lg:text-5xl font-black text-white leading-tight tracking-tight">
                AI <span className="text-indigo-500">Assistant</span>
              </h1>
              <p className="text-slate-500 text-sm font-bold uppercase tracking-widest mt-2">VakeeLink • AI Legal Assistant</p>
            </div>
            <button
              type="button"
              onClick={handleNewQuestion}
              className="px-6 py-4 bg-white/5 border border-white/10 text-white rounded-2xl font-black text-[10px] uppercase tracking-[0.2em] hover:bg-white/10 transition-all"
            >
              New Question
            </button>
          </div>

          {/* ── SEARCH PANEL (top, full width) ── */}
          <div className="glass-effect p-6 lg:p-8 rounded-[40px] border border-white/10 shadow-sm space-y-6">

            {/* Row 1: Domain + TopK + header icon */}
            <div className="flex items-center gap-4 flex-wrap">
              <div className="w-10 h-10 rounded-2xl bg-indigo-500/10 flex items-center justify-center text-indigo-400 border border-indigo-500/20 shrink-0">
                <Scale size={20} />
              </div>
              <div className="flex-1 flex items-center gap-4 flex-wrap">
                {/* Domain selector */}
                <div className="flex items-center gap-3 min-w-[200px]">
                  <label className="text-[10px] font-black text-slate-500 uppercase tracking-[0.2em] shrink-0">Domain</label>
                  <select
                    value={selectedDomain}
                    onChange={(e) => setSelectedDomain(e.target.value)}
                    className="flex-1 bg-white/5 border border-white/10 rounded-2xl px-4 py-3 text-xs text-white focus:border-indigo-500/50 outline-none transition-all appearance-none cursor-pointer"
                  >
                    {domains.map((d) => (
                      <option key={d} value={d} className="bg-[#020617]">
                        {d === 'All' ? 'All Domains' : d}
                      </option>
                    ))}
                  </select>
                </div>

                {/* TopK slider */}
                <div className="flex items-center gap-3 flex-1 min-w-[200px]">
                  <label className="text-[10px] font-black text-slate-500 uppercase tracking-[0.2em] shrink-0">Results</label>
                  <input
                    type="range"
                    min={1} max={10}
                    value={Math.max(1, Math.min(10, topK))}
                    onChange={(e) => setTopK(parseInt(e.target.value, 10))}
                    className="flex-1 accent-indigo-500"
                  />
                  <span className="text-[10px] font-black text-indigo-400 uppercase tracking-widest w-4 text-center">{topK}</span>
                </div>

                {/* Advanced Filters button */}
                <button
                  type="button"
                  className="px-5 py-3 bg-white/5 border border-white/10 rounded-2xl text-[10px] font-black uppercase tracking-[0.2em] text-slate-300 hover:text-white hover:bg-white/10 transition-all inline-flex items-center gap-2 shrink-0"
                >
                  Advanced Filters
                  <ChevronRight size={14} className="text-slate-500" />
                </button>
              </div>
            </div>

            {/* Row 2: Textarea + Search button */}
            <div className="flex gap-4 items-end">
              <div className="relative flex-1">
                <Search className="absolute left-5 top-5 text-slate-600" size={18} />
                <textarea
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  onKeyDown={onKeyDown}
                  className="w-full min-h-[110px] bg-white/5 border border-white/10 rounded-[28px] pl-12 pr-6 py-5 text-sm text-white outline-none focus:border-indigo-500/50 transition-all resize-none"
                  placeholder="Ask a legal question... (Ctrl+Enter to search)"
                  maxLength={2000}
                />
                <div className="absolute bottom-4 right-5 text-[10px] font-black uppercase tracking-widest text-slate-600">
                  {query.length}/2000
                </div>
              </div>

              <button
                onClick={() => runSearch()}
                disabled={isLoading}
                className="shrink-0 px-8 py-5 bg-indigo-600 text-white rounded-[22px] font-black text-[10px] uppercase tracking-[0.2em] transition-all shadow-xl shadow-indigo-600/20 hover:bg-indigo-500 disabled:opacity-50 flex items-center gap-3 self-stretch"
              >
                {isLoading ? <Loader2 size={18} className="animate-spin" /> : <Sparkles size={18} />}
                Search
              </button>
            </div>

            {/* Error */}
            {error && (
              <div className="p-4 bg-rose-500/10 border border-rose-500/20 rounded-[20px] text-rose-400 text-[10px] font-black uppercase tracking-widest">
                {error}
              </div>
            )}
          </div>

          {/* ── RESULTS PANEL (below, full width) ── */}
          <div className="glass-effect rounded-[40px] border border-white/10 p-8 lg:p-10 relative overflow-hidden">
            <div className="absolute top-0 right-0 w-80 h-80 bg-indigo-500/10 blur-3xl rounded-full -mr-44 -mt-44" />

            {/* Results header row */}
            <div className="flex items-center justify-between gap-6 flex-wrap relative">
              <div className="flex items-center gap-3">
                <div className="w-11 h-11 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center">
                  <Sparkles size={18} className="text-indigo-400" />
                </div>
                <div>
                  <div className="text-xl font-black text-white">AI Response</div>
                  <div className="text-slate-500 text-[10px] font-black uppercase tracking-widest">Here is what I found for you</div>
                </div>
              </div>

              <div className="flex items-center gap-3">
                <button type="button" onClick={handleShare}
                  className="px-5 py-3 bg-white/5 border border-white/10 rounded-2xl text-[10px] font-black uppercase tracking-widest text-white hover:bg-white/10 transition-all inline-flex items-center gap-2">
                  <Share2 size={16} className="text-indigo-400" /> Share
                </button>
                <button type="button" onClick={handleExport}
                  className="px-5 py-3 bg-white/5 border border-white/10 rounded-2xl text-[10px] font-black uppercase tracking-widest text-white hover:bg-white/10 transition-all inline-flex items-center gap-2">
                  <Download size={16} className="text-indigo-400" /> Export
                </button>
                <button type="button"
                  className="p-3 bg-white/5 border border-white/10 rounded-2xl text-white hover:bg-white/10 transition-all">
                  <MoreHorizontal size={18} className="text-slate-300" />
                </button>
              </div>
            </div>

            {/* Meta badges + confidence bar */}
            <div className="mt-6 flex items-start justify-between gap-6 flex-wrap">
              <div className="flex items-center gap-3 flex-wrap">
                <span className="inline-flex items-center gap-2 px-3 py-1.5 bg-white/5 border border-white/10 rounded-full text-[10px] font-black uppercase tracking-widest text-slate-300">
                  <FileText size={14} className="text-slate-500" /> Chunks: {result?.chunks_used || 0}
                </span>
                <span className="inline-flex items-center gap-2 px-3 py-1.5 bg-white/5 border border-white/10 rounded-full text-[10px] font-black uppercase tracking-widest text-slate-300">
                  <Cpu size={14} className="text-slate-500" /> {meta.model || 'N/A'}
                </span>
                <span className="inline-flex items-center gap-2 px-3 py-1.5 bg-white/5 border border-white/10 rounded-full text-[10px] font-black uppercase tracking-widest text-slate-300">
                  <Quote size={14} className="text-slate-500" /> Tokens: {meta.totalTokens !== null ? meta.totalTokens : 'N/A'}
                </span>
                <span className="inline-flex items-center gap-2 px-3 py-1.5 bg-white/5 border border-white/10 rounded-full text-[10px] font-black uppercase tracking-widest text-slate-300">
                  <Timer size={14} className="text-slate-500" /> {meta.latency !== null ? `${meta.latency}s` : 'N/A'}
                </span>
                {result && (
                  <button type="button" onClick={handleCopyAnswer}
                    className="inline-flex items-center gap-2 px-3 py-1.5 bg-white/5 border border-white/10 rounded-full text-[10px] font-black uppercase tracking-widest text-slate-300 hover:text-white hover:border-white/20 transition-all">
                    <Clipboard size={14} className="text-slate-500" /> Copy
                  </button>
                )}
              </div>

              <div className="min-w-[260px]">
                <div className="flex items-center justify-between text-[10px] font-black uppercase tracking-widest text-slate-500 mb-2">
                  <span>AI Confidence</span>
                  <span className="text-slate-200">{confidence}%</span>
                </div>
                <div className="h-3 bg-white/5 border border-white/10 rounded-full overflow-hidden">
                  <div className="h-full bg-indigo-600 transition-all duration-500" style={{ width: `${confidence}%` }} />
                </div>
              </div>
            </div>

            {/* Empty state */}
            {!result && !isLoading && (
              <div className="mt-10 bg-white/5 border border-white/10 rounded-[32px] p-10 text-slate-400 font-medium leading-relaxed text-center">
                Ask a question above to generate an executive summary, key points, and top legal references.
              </div>
            )}

            {/* Loading state */}
            {isLoading && (
              <div className="mt-10 bg-white/5 border border-white/10 rounded-[32px] p-12 flex items-center justify-center gap-4">
                <Loader2 size={18} className="animate-spin text-indigo-400" />
                <div className="text-[10px] font-black uppercase tracking-[0.3em] text-slate-500">Generating response…</div>
              </div>
            )}

            {/* Results */}
            {result && (
              <>
                <div className="mt-8 grid grid-cols-1 lg:grid-cols-12 gap-6">
                  {/* Executive Summary — full width */}
                  <div className="lg:col-span-12 bg-white/5 border border-white/10 rounded-[32px] p-8">
                    <div className="flex items-center gap-3 mb-4">
                      <FileText size={18} className="text-indigo-400" />
                      <div className="text-[10px] font-black uppercase tracking-widest text-slate-500">Executive Summary</div>
                    </div>
                    <div className="text-slate-200 leading-relaxed font-medium whitespace-pre-wrap">
                      {answerParts.summary || 'No answer returned.'}
                    </div>
                  </div>

                  {/* Key Points */}
                  <div className="lg:col-span-6 bg-white/5 border border-white/10 rounded-[32px] p-8">
                    <div className="flex items-center gap-3 mb-4">
                      <ChevronRight size={18} className="text-indigo-400" />
                      <div className="text-[10px] font-black uppercase tracking-widest text-slate-500">Key Points</div>
                    </div>
                    {answerParts.keyPoints && answerParts.keyPoints.length > 0 ? (
                      <ul className="space-y-3">
                        {answerParts.keyPoints.slice(0, 6).map((p, i) => (
                          <li key={`${i}-${p}`} className="flex gap-3">
                            <span className="mt-2 w-2 h-2 rounded-full bg-indigo-500 shadow-[0_0_10px_rgba(99,102,241,0.35)] shrink-0" />
                            <span className="text-sm text-slate-300 leading-relaxed font-medium">{p}</span>
                          </li>
                        ))}
                      </ul>
                    ) : (
                      <div className="text-slate-500 font-medium">No structured key points detected.</div>
                    )}
                  </div>

                  {/* What You Can Do */}
                  <div className="lg:col-span-6 bg-white/5 border border-white/10 rounded-[32px] p-8">
                    <div className="flex items-center gap-3 mb-4">
                      <ArrowRight size={18} className="text-indigo-400" />
                      <div className="text-[10px] font-black uppercase tracking-widest text-slate-500">What You Can Do</div>
                    </div>
                    <ol className="space-y-3">
                      {(answerParts.keyPoints && answerParts.keyPoints.length > 0 ? answerParts.keyPoints : [answerParts.summary])
                        .filter(Boolean).slice(0, 5).map((step, idx) => (
                          <li key={`${idx}-${step}`} className="flex gap-4">
                            <div className="w-8 h-8 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400 font-black text-[10px] shrink-0">
                              {idx + 1}
                            </div>
                            <div className="text-sm text-slate-300 leading-relaxed font-medium">{step}</div>
                          </li>
                        ))}
                    </ol>
                  </div>

                  {/* Top Legal References — full width */}
                  <div className="lg:col-span-12 bg-white/5 border border-white/10 rounded-[32px] p-8">
                    <div className="flex items-center justify-between gap-4 flex-wrap mb-6">
                      <div className="flex items-center gap-3">
                        <Scale size={18} className="text-indigo-400" />
                        <div className="text-[10px] font-black uppercase tracking-widest text-slate-500">Top Legal References</div>
                      </div>
                      {topReferences.length > 4 && (
                        <button type="button" onClick={() => setShowAllRefs((v) => !v)}
                          className="text-[10px] font-black uppercase tracking-widest text-indigo-400 hover:text-indigo-300 transition-colors">
                          {showAllRefs ? 'View fewer references' : `View more references (${Math.min(12, topReferences.length)})`}
                        </button>
                      )}
                    </div>

                    {visibleReferences.length === 0 ? (
                      <div className="text-slate-500 font-medium">No references returned.</div>
                    ) : (
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {visibleReferences.map((r, i) => (
                          <div key={`${i}-${r.title}`} className="bg-black/20 border border-white/10 rounded-3xl p-6 flex items-start justify-between gap-6">
                            <div className="flex-1">
                              <div className="text-white font-black">{r.title}</div>
                              {r.subtitle && <div className="text-slate-400 text-sm font-medium mt-1">{r.subtitle}</div>}
                              <div className="flex items-center gap-3 mt-4 flex-wrap">
                                {r.tag && (
                                  <span className="px-3 py-1 bg-white/5 border border-white/10 rounded-full text-[10px] font-black uppercase tracking-widest text-slate-400">{r.tag}</span>
                                )}
                                {typeof r.score === 'number' && Number.isFinite(r.score) && (
                                  <span className="px-3 py-1 bg-indigo-500/10 border border-indigo-500/20 rounded-full text-[10px] font-black uppercase tracking-widest text-indigo-400">
                                    score {r.score.toFixed ? r.score.toFixed(2) : r.score}
                                  </span>
                                )}
                              </div>
                            </div>
                            {r.source ? (
                              <a href={r.source} target="_blank" rel="noreferrer"
                                className="shrink-0 inline-flex items-center gap-2 px-4 py-3 bg-white/5 border border-white/10 rounded-2xl text-[10px] font-black uppercase tracking-widest text-slate-300 hover:text-white hover:border-white/20 transition-all">
                                <LinkIcon size={16} className="text-indigo-400" /> View
                              </a>
                            ) : (
                              <div className="shrink-0 px-4 py-3 bg-white/5 border border-white/10 rounded-2xl text-[10px] font-black uppercase tracking-widest text-slate-600">N/A</div>
                            )}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>

                {/* Follow-up */}
                <div className="mt-8 bg-white/5 border border-white/10 rounded-[32px] p-6 space-y-4">
                  <div className="flex items-center justify-between flex-wrap gap-4">
                    <div className="text-[10px] font-black uppercase tracking-widest text-slate-500">Suggested Follow-up</div>
                    <div className="text-[10px] font-black uppercase tracking-widest text-slate-600">
                      {answerParts.disclaimerLine || 'AI-generated analysis. Not legal advice.'}
                    </div>
                  </div>
                  <div className="flex flex-wrap gap-3">
                    {suggestedFollowUps.map((t) => (
                      <button key={t} type="button" onClick={() => setFollowUp(t)}
                        className="px-4 py-2 bg-black/20 border border-white/10 rounded-2xl text-[10px] font-black uppercase tracking-widest text-slate-300 hover:text-white hover:border-white/20 transition-all">
                        {t}
                      </button>
                    ))}
                  </div>
                  <div className="flex items-center gap-3">
                    <input value={followUp} onChange={(e) => setFollowUp(e.target.value)} onKeyDown={onFollowUpKeyDown}
                      className="flex-1 bg-black/20 border border-white/10 rounded-2xl px-5 py-4 text-sm text-white outline-none focus:border-indigo-500/50"
                      placeholder="Ask a follow-up question..." />
                    <button type="button" onClick={handleAskFollowUp} disabled={followUp.trim().length < 3}
                      className="px-5 py-4 bg-indigo-600 text-white rounded-2xl font-black text-[10px] uppercase tracking-[0.2em] shadow-xl shadow-indigo-600/20 hover:bg-indigo-500 disabled:opacity-50 transition-all inline-flex items-center gap-2">
                      <Send size={16} /> Send
                    </button>
                  </div>
                </div>
              </>
            )}
          </div>

        </div>
      </main>
    </div>
  );
};

export default CaseCurator;