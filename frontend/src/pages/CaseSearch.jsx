import React, { useState, useEffect, useMemo } from 'react';
import { 
  Search, 
  ArrowRight, 
  Scale, 
  Gavel, 
  Calendar, 
  MapPin, 
  Tag, 
  FileText, 
  Quote, 
  X, 
  CheckCircle2,
  Filter,
  ChevronRight
} from 'lucide-react';
import UserSidebar from '../components/UserSidebar';

const MOCK_CASES = [
  {
    id: 1,
    name: "Maneka Gandhi vs Union of India",
    citation: "1978 AIR 597",
    court: "Supreme Court",
    year: 1978,
    domain: "Constitutional Law",
    judges: ["Justice Y.V. Chandrachud", "Justice V.R. Krishna Iyer"],
    summary: "The court established that the procedure established by law must be just, fair, and reasonable, and not arbitrary, fanciful, or oppressive. This case significantly expanded the scope of Article 21.",
    fullText: "This landmark judgment expanded the interpretation of Article 21 of the Indian Constitution. The Supreme Court held that the right to life and personal liberty cannot be curtailed except by a procedure that is just, fair, and reasonable. The court overruled the earlier A.K. Gopalan case and held that Fundamental Rights are not mutually exclusive but are interrelated. Justice V.R. Krishna Iyer observed that the expression 'procedure established by law' in Article 21 must be read in conjunction with Articles 14 and 19, creating what is now known as the 'golden triangle' of fundamental rights."
  },
  {
    id: 2,
    name: "Vishaka vs State of Rajasthan",
    citation: "1997 (6) SCC 241",
    court: "Supreme Court",
    year: 1997,
    domain: "Constitutional Law",
    judges: ["Justice J.S. Verma", "Justice Sujata Manohar"],
    summary: "Landmark judgment that laid down guidelines to prevent sexual harassment of women at the workplace, before the enactment of the POSH Act.",
    fullText: "In this landmark PIL, the Supreme Court of India laid down exhaustive guidelines — popularly known as the Vishaka Guidelines — to be mandatorily followed by employers to prevent and address sexual harassment of women at workplaces. The court held that gender equality and the right to work with dignity are Fundamental Rights under Articles 14, 15, and 21 of the Constitution. These guidelines remained the law of the land until the Sexual Harassment of Women at Workplace (Prevention, Prohibition and Redressal) Act, 2013 was enacted."
  },
  {
    id: 3,
    name: "State of Maharashtra vs Madhkar Narayan",
    citation: "1991 AIR 207",
    court: "Supreme Court",
    year: 1991,
    domain: "Criminal Law",
    judges: ["Justice K.N. Singh"],
    summary: "The court held that every woman is entitled to her privacy and no one can trespass into her privacy at any time.",
    fullText: "The Supreme Court in this judgment strongly affirmed the right to privacy of women. The court categorically stated that every woman is entitled to sexual privacy and it is not open to any and every person to violate her privacy as and when he wishes. The judgment reinforced that consent is central to any sexual act and its absence constitutes a criminal offence regardless of the social standing or character of the woman."
  },
  {
    id: 4,
    name: "Lakhanpal vs National Insurance Co.",
    citation: "2021 ACJ 1450",
    court: "High Court",
    year: 2021,
    domain: "Motor Accident",
    judges: ["Justice Sureshwar Thakur"],
    summary: "Compensation awarded for permanent disability in a motor accident claim. Court applied structured formula for loss of future earnings and medical expenses.",
    fullText: "The claimant suffered 40% permanent disability following a road accident involving an uninsured vehicle. The High Court applied the multiplier method as laid down by the Supreme Court in Sarla Verma vs Delhi Transport Corporation. The court awarded enhanced compensation including loss of earning capacity, pain and suffering, and future medical expenses. The court emphasized that just compensation must be awarded without being niggardly and the victim's rehabilitation must be the primary consideration."
  },
  {
    id: 5,
    name: "Naveen Kohli vs Neelu Kohli",
    citation: "2006 (4) SCC 558",
    court: "Supreme Court",
    year: 2006,
    domain: "Family Law",
    judges: ["Justice R.C. Lahoti", "Justice G.P. Mathur"],
    summary: "The Supreme Court recommended amendment to the Hindu Marriage Act to include irretrievable breakdown of marriage as a ground for divorce.",
    fullText: "The Supreme Court in this significant matrimonial case held that where there has been a complete breakdown of marital relationship, compelling the parties to live together would serve no useful purpose. The court recommended to the Parliament to consider adding irretrievable breakdown of marriage as an additional ground for divorce under the Hindu Marriage Act 1955. The judgment noted that both parties had been living separately for several years and forcing continuation of a dead marriage caused more harm than allowing a dignified separation."
  }
];

const CaseSearch = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [activeCourt, setActiveCourt] = useState('All Courts');
  const [selectedCase, setSelectedCase] = useState(null);
  const [toast, setToast] = useState({ show: false, message: '' });
  
  // Filters state
  const [tempFilters, setTempFilters] = useState({
    yearFrom: '',
    yearTo: '',
    judgeName: '',
    domains: []
  });

  const [appliedFilters, setAppliedFilters] = useState({
    yearFrom: '',
    yearTo: '',
    judgeName: '',
    domains: []
  });

  const [isTransitioning, setIsTransitioning] = useState(false);

  const domains = [
    "Constitutional Law", 
    "Criminal Law", 
    "Consumer Law", 
    "Family Law", 
    "Labour Law", 
    "Motor Accident"
  ];

  const getDomainStyles = (domain) => {
    switch (domain) {
      case "Constitutional Law": return "bg-purple-500/10 text-purple-400";
      case "Criminal Law": return "bg-red-500/10 text-red-400";
      case "Family Law": return "bg-pink-500/10 text-pink-400";
      case "Consumer Law": return "bg-emerald-500/10 text-emerald-400";
      case "Labour Law": return "bg-orange-500/10 text-orange-400";
      case "Motor Accident": return "bg-amber-500/10 text-amber-400";
      default: return "bg-slate-500/10 text-slate-400";
    }
  };

  const filteredCases = useMemo(() => {
    return MOCK_CASES.filter(c => {
      // Search Query
      const matchesSearch = searchQuery === '' || 
        c.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        c.citation.toLowerCase().includes(searchQuery.toLowerCase()) ||
        c.summary.toLowerCase().includes(searchQuery.toLowerCase());
      
      // Court Tab
      const matchesCourt = activeCourt === 'All Courts' || c.court === activeCourt;
      
      // Sidebar Filters
      const matchesYearFrom = appliedFilters.yearFrom === '' || c.year >= parseInt(appliedFilters.yearFrom);
      const matchesYearTo = appliedFilters.yearTo === '' || c.year <= parseInt(appliedFilters.yearTo);
      const matchesJudge = appliedFilters.judgeName === '' || c.judges.some(j => j.toLowerCase().includes(appliedFilters.judgeName.toLowerCase()));
      const matchesDomain = appliedFilters.domains.length === 0 || appliedFilters.domains.includes(c.domain);
      
      return matchesSearch && matchesCourt && matchesYearFrom && matchesYearTo && matchesJudge && matchesDomain;
    });
  }, [searchQuery, activeCourt, appliedFilters]);

  const handleCite = (citation) => {
    navigator.clipboard.writeText(citation);
    setToast({ show: true, message: 'Citation copied to clipboard' });
    setTimeout(() => setToast({ show: false, message: '' }), 2500);
  };

  const toggleDomainFilter = (domain) => {
    setTempFilters(prev => ({
      ...prev,
      domains: prev.domains.includes(domain) 
        ? prev.domains.filter(d => d !== domain)
        : [...prev.domains, domain]
    }));
  };

  const handleApplyFilters = () => {
    setIsTransitioning(true);
    setTimeout(() => {
      setAppliedFilters(tempFilters);
      setIsTransitioning(false);
      if (window.innerWidth < 768) {
        window.scrollTo({ top: 400, behavior: 'smooth' });
      }
    }, 400);
  };

  const clearFilters = () => {
    const defaultFilters = {
      yearFrom: '',
      yearTo: '',
      judgeName: '',
      domains: []
    };
    setTempFilters(defaultFilters);
    setAppliedFilters(defaultFilters);
    setActiveCourt('All Courts');
    setSearchQuery('');
  };

  return (
    <div className="flex min-h-screen bg-[#020617] text-slate-200 font-inter">
      <UserSidebar />
      
      <main className="flex-1 md:ml-[280px] p-6 md:p-12 overflow-y-auto">
        {/* Header Section */}
        <div className="mb-12">
          <h1 className="text-4xl md:text-5xl font-black tracking-tight text-white mb-3">
            Case <span className="text-indigo-500">Search</span>
          </h1>
          <p className="text-slate-400 text-lg max-w-2xl leading-relaxed font-medium">
            Access over 2.5 million judgments with AI-powered semantic search.
          </p>
        </div>

        {/* Search Bar */}
        <div className="glass-effect p-2 rounded-[28px] border border-white/10 flex flex-col md:flex-row items-center gap-2 mb-12 shadow-2xl shadow-indigo-500/10">
          <div className="flex-1 flex items-center px-6 gap-4 w-full">
            <Search className="text-indigo-400" size={22} />
            <input 
              type="text" 
              placeholder="Search by case name, citation, or legal query..."
              className="w-full py-5 bg-transparent outline-none text-white text-lg placeholder:text-slate-500 font-medium"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
          <button className="primary-gradient hover:scale-[1.02] active:scale-[0.98] text-white px-10 py-5 rounded-[22px] font-black text-[10px] uppercase tracking-widest transition-all shadow-xl shadow-indigo-500/20 w-full md:w-auto flex items-center justify-center gap-3">
            Search Judgments <ArrowRight size={18} />
          </button>
        </div>

        {/* Court Tabs */}
        <div className="flex flex-wrap gap-3 mb-12">
          {['All Courts', 'Supreme Court', 'High Court', 'Tribunals'].map(court => (
            <button
              key={court}
              onClick={() => setActiveCourt(court)}
              className={`px-8 py-3 rounded-2xl text-[10px] font-black uppercase tracking-widest transition-all duration-300 border ${
                activeCourt === court 
                  ? 'bg-indigo-600 text-white border-indigo-500 shadow-xl shadow-indigo-600/20' 
                  : 'bg-white/5 text-slate-500 border-white/5 hover:bg-white/10 hover:text-white'
              }`}
            >
              {court}
            </button>
          ))}
        </div>

        <div className="flex flex-col xl:flex-row gap-12">
          {/* Results List */}
          <div className="flex-1 space-y-8">
            <div className={`flex items-center justify-between transition-opacity duration-300 ${isTransitioning ? 'opacity-50' : 'opacity-100'}`}>
              <h3 className="text-[10px] font-black text-slate-500 uppercase tracking-[0.2em]">
                Found {filteredCases.length} relevant cases
              </h3>
            </div>
            
            <div className={`space-y-8 transition-all duration-500 ${isTransitioning ? 'opacity-0 translate-y-8' : 'opacity-100 translate-y-0'}`}>
              {filteredCases.map((c, index) => (
                <div 
                  key={c.id} 
                  className="glass-effect rounded-[32px] p-8 hover:bg-white/[0.04] transition-all duration-500 group relative overflow-hidden animate-in fade-in slide-in-from-bottom-8"
                  style={{ animationDelay: `${index * 100}ms`, animationFillMode: 'both' }}
                >
                  <div className="absolute top-0 right-0 w-32 h-32 bg-indigo-500/5 blur-3xl rounded-full -mr-16 -mt-16 transition-all group-hover:bg-indigo-500/10" />
                  
                  <div className="flex justify-between items-start mb-6 relative">
                    <div className="flex-1">
                      <h2 className="text-2xl font-black text-white group-hover:text-indigo-400 transition-colors leading-snug max-w-2xl">
                        {c.name}
                      </h2>
                      <div className="flex flex-wrap gap-3 mt-4">
                        <span className="bg-indigo-500/10 text-indigo-400 text-[10px] font-black px-4 py-2 rounded-xl border border-indigo-500/20 uppercase tracking-widest">
                          {c.court} • {c.year}
                        </span>
                        <span className={`text-[10px] font-black px-4 py-2 rounded-xl uppercase tracking-widest border border-current ${getDomainStyles(c.domain)}`}>
                          {c.domain}
                        </span>
                      </div>
                    </div>
                    <div className="text-right flex flex-col items-end">
                      <span className="text-[10px] font-black text-slate-600 uppercase tracking-widest mb-1">Citation</span>
                      <span className="text-sm font-black text-slate-300 bg-white/5 px-4 py-2 rounded-xl border border-white/5">
                        {c.citation}
                      </span>
                    </div>
                  </div>
                  
                  <p className="text-slate-400 line-clamp-2 mb-8 text-base leading-relaxed font-medium">
                    {c.summary}
                  </p>

                  <div className="flex flex-col sm:flex-row items-center justify-between pt-6 border-t border-white/5 gap-4">
                    <div className="flex gap-4 w-full sm:w-auto">
                      <button 
                        onClick={() => setSelectedCase(c)}
                        className="flex-1 sm:flex-none px-8 py-4 bg-white text-black hover:bg-indigo-600 hover:text-white rounded-2xl text-[10px] font-black uppercase tracking-widest transition-all flex items-center justify-center gap-3 shadow-xl shadow-white/5"
                      >
                        <FileText size={16} /> Read Judgment
                      </button>
                      <button 
                        onClick={() => handleCite(c.citation)}
                        className="flex-1 sm:flex-none px-8 py-4 text-slate-400 hover:text-white rounded-2xl text-[10px] font-black uppercase tracking-widest transition-all flex items-center justify-center gap-3 hover:bg-white/5"
                      >
                        <Quote size={16} /> Copy Cite
                      </button>
                    </div>
                    <button className="w-full sm:w-auto p-4 text-slate-500 hover:text-indigo-400 transition-colors">
                      <ChevronRight size={24} />
                    </button>
                  </div>
                </div>
              ))}
            </div>

            {filteredCases.length === 0 && (
              <div className="glass-effect rounded-[40px] border border-dashed border-white/10 p-20 text-center">
                <div className="bg-indigo-500/10 w-24 h-24 rounded-3xl flex items-center justify-center mx-auto mb-6">
                  <Search className="text-indigo-400" size={40} />
                </div>
                <h3 className="text-2xl font-black text-white mb-2">No judgments found</h3>
                <p className="text-slate-500 max-w-md mx-auto font-medium">Try broadening your search criteria or adjusting the filters in the sidebar.</p>
                <button onClick={clearFilters} className="mt-8 text-indigo-400 font-black uppercase tracking-widest hover:text-indigo-300 transition-colors underline-offset-8 underline">Reset all filters</button>
              </div>
            )}
          </div>

          {/* Filters Sidebar */}
          <aside className="w-full xl:w-[360px] space-y-8">
            <div className="glass-effect rounded-[40px] border border-white/10 p-8 sticky top-12 shadow-2xl">
              <div className="flex items-center justify-between mb-10">
                <h3 className="text-xl font-black text-white flex items-center gap-3">
                  <Filter className="text-indigo-400" size={20} /> Filters
                </h3>
                <button 
                  onClick={clearFilters}
                  className="text-[10px] font-black text-slate-500 hover:text-rose-400 transition-colors uppercase tracking-[0.2em]"
                >
                  Clear All
                </button>
              </div>

              <div className="space-y-10">
                <div>
                  <label className="block text-[10px] font-black text-slate-500 uppercase tracking-[0.2em] mb-4">Date Range</label>
                  <div className="flex items-center gap-4">
                    <input 
                      type="number" 
                      placeholder="YYYY"
                      className="w-full bg-white/5 border border-white/5 rounded-2xl px-5 py-4 text-sm text-white focus:border-indigo-500 outline-none transition-all font-bold"
                      value={tempFilters.yearFrom}
                      onChange={(e) => setTempFilters(prev => ({ ...prev, yearFrom: e.target.value }))}
                    />
                    <span className="text-slate-700 font-black">-</span>
                    <input 
                      type="number" 
                      placeholder="YYYY"
                      className="w-full bg-white/5 border border-white/5 rounded-2xl px-5 py-4 text-sm text-white focus:border-indigo-500 outline-none transition-all font-bold"
                      value={tempFilters.yearTo}
                      onChange={(e) => setTempFilters(prev => ({ ...prev, yearTo: e.target.value }))}
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-[10px] font-black text-slate-500 uppercase tracking-[0.2em] mb-4">Bench / Judge</label>
                  <div className="relative group">
                    <Search className="absolute left-5 top-1/2 -translate-y-1/2 text-slate-500 group-focus-within:text-indigo-400 transition-colors" size={16} />
                    <input 
                      type="text" 
                      placeholder="Enter judge name..."
                      className="w-full bg-white/5 border border-white/5 rounded-2xl pl-12 pr-6 py-4 text-sm text-white focus:border-indigo-500 outline-none transition-all font-bold"
                      value={tempFilters.judgeName}
                      onChange={(e) => setTempFilters(prev => ({ ...prev, judgeName: e.target.value }))}
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-[10px] font-black text-slate-500 uppercase tracking-[0.2em] mb-4">Legal Domain</label>
                  <div className="grid grid-cols-1 gap-3">
                    {domains.map(domain => (
                      <label key={domain} className="flex items-center gap-4 group cursor-pointer p-1">
                        <div className="relative flex items-center">
                          <input 
                            type="checkbox" 
                            className="peer h-6 w-6 cursor-pointer appearance-none rounded-xl border border-white/10 transition-all checked:bg-indigo-600 checked:border-transparent shadow-xl"
                            checked={tempFilters.domains.includes(domain)}
                            onChange={() => toggleDomainFilter(domain)}
                          />
                          <CheckCircle2 className="absolute left-1 w-4 h-4 text-white opacity-0 peer-checked:opacity-100 transition-opacity" />
                        </div>
                        <span className="text-[10px] font-black uppercase tracking-widest text-slate-400 group-hover:text-white transition-colors">{domain}</span>
                      </label>
                    ))}
                  </div>
                </div>

                <button 
                  onClick={handleApplyFilters}
                  disabled={isTransitioning}
                  className={`w-full py-6 rounded-[24px] font-black uppercase tracking-[0.2em] text-[11px] shadow-2xl transition-all flex items-center justify-center gap-3 ${
                    isTransitioning 
                      ? 'bg-white/5 text-slate-600 cursor-not-allowed' 
                      : 'bg-indigo-600 text-white shadow-indigo-600/20 hover:scale-[1.02] active:scale-[0.98]'
                  }`}
                >
                  {isTransitioning ? (
                    <div className="w-4 h-4 border-2 border-slate-600 border-t-white rounded-full animate-spin" />
                  ) : (
                    'Apply Filters'
                  )}
                </button>
              </div>
            </div>
          </aside>
        </div>
      </main>

      {/* Modal */}
      {selectedCase && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 md:p-8 bg-black/80 backdrop-blur-md animate-in fade-in duration-300">
          <div className="glass-effect w-full max-w-6xl max-h-[90vh] overflow-hidden rounded-[48px] border border-white/10 flex flex-col shadow-2xl">
            <div className="p-8 md:p-12 border-b border-white/5 flex items-center justify-between sticky top-0 bg-[#020617]/50 backdrop-blur-xl z-10">
              <div className="flex items-center gap-6">
                <div className="w-16 h-16 rounded-[24px] bg-indigo-500/10 flex items-center justify-center text-indigo-400">
                  <Scale size={32} />
                </div>
                <div>
                  <h2 className="text-3xl font-black text-white tracking-tight">{selectedCase.name}</h2>
                  <div className="flex items-center gap-4 mt-2">
                    <span className="text-[10px] font-black text-slate-500 uppercase tracking-widest bg-white/5 px-4 py-1.5 rounded-lg border border-white/5">
                      {selectedCase.citation}
                    </span>
                    <span className="w-1.5 h-1.5 rounded-full bg-slate-700" />
                    <span className="text-[10px] font-black text-indigo-400/80 uppercase tracking-widest">{selectedCase.court}</span>
                  </div>
                </div>
              </div>
              <button 
                onClick={() => setSelectedCase(null)}
                className="p-4 hover:bg-white/10 text-slate-400 hover:text-white rounded-full transition-all"
              >
                <X size={32} />
              </button>
            </div>
            
            <div className="flex-1 overflow-y-auto p-8 md:p-16">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-16">
                {[
                  { label: 'Judgment Date', val: selectedCase.year, icon: Calendar },
                  { label: 'Coram / Bench', val: selectedCase.judges.join(', '), icon: Gavel },
                  { label: 'Legal Domain', val: selectedCase.domain, icon: Tag, isDomain: true }
                ].map((stat, i) => (
                  <div key={i} className="bg-white/5 p-8 rounded-[32px] border border-white/5 relative overflow-hidden group">
                    <stat.icon size={48} className="absolute -right-2 -top-2 text-white/5 group-hover:text-white/10 transition-colors" />
                    <label className="block text-[10px] font-black text-slate-500 uppercase tracking-[0.3em] mb-4">{stat.label}</label>
                    <p className={`text-lg font-black text-white leading-tight ${stat.isDomain ? getDomainStyles(stat.val) : ''}`}>{stat.val}</p>
                  </div>
                ))}
              </div>

              <div className="max-w-4xl mx-auto space-y-12">
                <div className="h-px bg-white/5" />
                <div className="text-slate-300 leading-relaxed space-y-10 text-xl font-outfit italic opacity-90 relative">
                  <Quote size={40} className="absolute -left-12 -top-12 text-indigo-500/20" />
                  {selectedCase.fullText}
                </div>
              </div>
            </div>

            <div className="p-8 border-t border-white/5 bg-white/[0.02] flex flex-col sm:flex-row justify-end gap-6">
              <button 
                onClick={() => handleCite(selectedCase.citation)}
                className="px-10 py-5 bg-white/5 hover:bg-white/10 border border-white/10 text-white rounded-[24px] font-black uppercase tracking-widest text-[10px] transition-all flex items-center justify-center gap-3"
              >
                <Quote size={16} /> Generate Citation
              </button>
              <button 
                onClick={() => setSelectedCase(null)}
                className="px-12 py-5 bg-indigo-600 text-white rounded-[24px] font-black uppercase tracking-widest text-[10px] transition-all shadow-xl shadow-indigo-600/20 hover:scale-[1.02] active:scale-[0.98]"
              >
                Close View
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Toast */}
      {toast.show && (
        <div className="fixed bottom-12 right-12 z-[200] glass-effect text-white px-8 py-5 rounded-[24px] shadow-2xl flex items-center gap-4 border border-indigo-500/30 animate-in fade-in slide-in-from-bottom-8">
          <CheckCircle2 size={24} className="text-emerald-400" />
          <span className="font-black text-[10px] uppercase tracking-widest">{toast.message}</span>
        </div>
      )}
    </div>
  );
};

export default CaseSearch;
