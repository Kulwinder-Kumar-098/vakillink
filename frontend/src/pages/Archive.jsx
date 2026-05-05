import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import UserSidebar from '../components/UserSidebar';
import { 
  Download, 
  Trash2, 
  Bookmark, 
  Calendar, 
  ChevronLeft, 
  ChevronRight, 
  Search, 
  Filter, 
  Clock, 
  Shield, 
  Gavel, 
  BookOpen, 
  ArrowUpRight,
  Plus,
  X
} from 'lucide-react';

const MOCK_CASES = [
  {
    id: 1,
    title: 'Maneka Gandhi vs Union of India',
    citation: '1978 AIR 597, 1978 SCR (2) 621 • Supreme Court of India',
    domain: 'CONSTITUTIONAL',
    date: 'Saved 3 days ago',
  },
  {
    id: 2,
    title: 'Kesavananda Bharati v. State of Kerala',
    citation: 'AIR 1973 SC 1461 • Supreme Court of India',
    domain: 'CONSTITUTIONAL',
    date: 'Saved 5 days ago',
  },
  {
    id: 3,
    title: 'State of Punjab vs Dalbir Singh',
    citation: 'Civil Appeal No. 117 of 2012 • Supreme Court of India',
    domain: 'CRIMINAL LAW',
    date: 'Saved 1 week ago',
  },
  {
    id: 4,
    title: 'Vishaka & Ors vs State of Rajasthan',
    citation: 'AIR 1997 SC 3011 • Supreme Court of India',
    domain: 'CONSTITUTIONAL',
    date: 'Saved 2 weeks ago',
  },
];

const Archive = () => {
  const [activeTab, setActiveTab] = useState('saved');
  const [items, setItems] = useState([]);
  const [selectedItems, setSelectedItems] = useState([]);
  const [filters, setFilters] = useState({
    constitutional: false,
    criminal: false,
    corporate: false,
    civil: false,
  });
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [page, setPage] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  const [selectedViewItem, setSelectedViewItem] = useState(null);

  const API_BASE = 'http://127.0.0.1:9000/api/v1';

  const fetchData = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('vakeellink_token');
      let url = '';
      if (activeTab === 'saved') {
        url = `${API_BASE}/archive/`;
      } else if (activeTab === 'research') {
        url = `${API_BASE}/cases/?page=${page}&q=${searchQuery}&expand=true`;
      } else {
        // Mock data for other tabs
        setItems([]);
        setLoading(false);
        return;
      }

      const res = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!res.ok) throw new Error('Failed to fetch data');
      const data = await res.json();

      if (activeTab === 'saved') {
        const mapped = data.map(item => ({
          id: item.id,
          title: item.title,
          citation: item.citation,
          domain: item.domain || 'N/A',
          date: new Date(item.date).toLocaleDateString(),
          type: 'archive',
          raw: item
        }));
        setItems(mapped);
      } else {
        const mapped = data.data.map(item => ({
          id: item.id,
          title: item.query,
          citation: item.domain || 'General Research',
          domain: item.domain || 'RESEARCH',
          date: new Date(item.created_at).toLocaleDateString(),
          type: 'history',
          raw: item
        }));
        setItems(mapped);
        setTotalCount(data.total_count);
      }
    } catch (error) {
      console.error('Error fetching archive data:', error);
      // Fallback to mock if error
      if (activeTab === 'saved') {
        setItems(MOCK_CASES.map(c => ({ ...c, type: 'archive' })));
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [activeTab, page]);

  const toggleSelection = (id) => {
    setSelectedItems((prev) =>
      prev.includes(id) ? prev.filter((itemId) => itemId !== id) : [...prev, id]
    );
  };

  const handleSelectAll = (e) => {
    if (e.target.checked) {
      setSelectedItems(items.map((c) => c.id));
    } else {
      setSelectedItems([]);
    }
  };

  const handleFilterChange = (domain) => {
    setFilters((prev) => ({
      ...prev,
      [domain]: !prev[domain],
    }));
  };

  const handleDeleteSelected = async () => {
    if (selectedItems.length === 0) return;
    setLoading(true);
    try {
      const token = localStorage.getItem('vakeellink_token');
      
      if (activeTab === 'saved') {
        await Promise.all(selectedItems.map(id => 
          fetch(`${API_BASE}/archive/${id}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${token}` }
          })
        ));
      }
      
      setItems((prev) => prev.filter((c) => !selectedItems.includes(c.id)));
      setSelectedItems([]);
    } catch (error) {
      console.error('Error deleting items:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e) => {
    if (e.key === 'Enter') {
      fetchData();
    }
  };

  const handleViewItem = (e, item) => {
    e.stopPropagation();
    setSelectedViewItem(item);
  };

  const filteredItems = items.filter((c) => {
    // Basic search filtering if not already filtered by API
    if (activeTab === 'saved' && searchQuery) {
      if (!c.title.toLowerCase().includes(searchQuery.toLowerCase())) return false;
    }

    const domainKey = c.domain.toLowerCase().split(' ')[0];
    const domainMapping = {
      'constitutional': filters.constitutional,
      'criminal': filters.criminal,
      'corporate': filters.corporate,
      'civil': filters.civil,
    };
    const anyFilterSelected = Object.values(filters).some(Boolean);
    if (!anyFilterSelected) return true;
    return domainMapping[domainKey] === true;
  });

  const tabs = [
    { id: 'saved', label: 'Saved Cases', icon: Bookmark },
    { id: 'research', label: 'AI Research', icon: Clock },
    { id: 'downloads', label: 'Downloads', icon: Download },
    { id: 'bookmarks', label: 'Bookmarks', icon: BookOpen },
  ];

  return (
    <div className="flex min-h-screen bg-[#020617] text-slate-200">
      <UserSidebar />
      
      <main className="flex-1 md:ml-[280px] p-6 md:p-12 overflow-y-auto">
        <div className="max-w-6xl mx-auto">
          {/* Header */}
          <div className="mb-12">
            <h1 className="text-4xl md:text-5xl font-black tracking-tight text-white mb-3">
              Case <span className="text-indigo-500">Archive</span>
            </h1>
            <p className="text-slate-400 text-lg max-w-2xl leading-relaxed">
              Your saved cases, research sessions, and AI history records.
            </p>
          </div>

          {/* Tab Navigation */}
          <div className="flex gap-4 p-2 glass-effect rounded-[28px] border border-white/5 mb-10 overflow-x-auto scrollbar-hide">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-3 px-8 py-4 rounded-[22px] font-black uppercase tracking-widest text-[10px] transition-all whitespace-nowrap ${
                  activeTab === tab.id 
                    ? 'bg-indigo-600 text-white shadow-xl shadow-indigo-600/20' 
                    : 'text-slate-500 hover:text-white hover:bg-white/5'
                }`}
              >
                <tab.icon size={16} />
                {tab.label}
              </button>
            ))}
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-12 gap-12">
            {/* Filters Sidebar */}
            <aside className="hidden lg:block lg:col-span-3 space-y-8">
              <div className="glass-effect rounded-[32px] border border-white/10 p-8 space-y-8">
                <div>
                  <h3 className="text-[10px] font-black uppercase tracking-[0.3em] text-slate-500 mb-6">Jurisdictions</h3>
                  <div className="space-y-4">
                    {['Constitutional', 'Criminal', 'Corporate', 'Civil'].map((domain) => (
                      <label key={domain} className="flex items-center gap-4 group cursor-pointer">
                        <div className="relative flex items-center justify-center">
                          <input
                            type="checkbox"
                            className="peer appearance-none w-6 h-6 rounded-lg border-2 border-white/10 checked:border-indigo-500 checked:bg-indigo-500/20 transition-all cursor-pointer"
                            checked={filters[domain.toLowerCase()]}
                            onChange={() => handleFilterChange(domain.toLowerCase())}
                          />
                          <div className="absolute opacity-0 peer-checked:opacity-100 text-indigo-400 pointer-events-none">
                            <Plus size={14} className="rotate-45" />
                          </div>
                        </div>
                        <span className="text-sm font-bold text-slate-400 group-hover:text-white transition-colors">{domain}</span>
                      </label>
                    ))}
                  </div>
                </div>
                
                <div className="pt-8 border-t border-white/5">
                  <h3 className="text-[10px] font-black uppercase tracking-[0.3em] text-slate-500 mb-6">Time Period</h3>
                  <select className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-xs font-bold text-white outline-none appearance-none">
                    <option className="bg-[#020617]">Last 30 Days</option>
                    <option className="bg-[#020617]">Last 6 Months</option>
                    <option className="bg-[#020617]">All Time</option>
                  </select>
                </div>
              </div>
            </aside>

            {/* List Content */}
            <section className="lg:col-span-9 space-y-8">
              {/* Search Bar */}
              <div className="relative group">
                <div className="absolute inset-y-0 left-6 flex items-center pointer-events-none text-slate-500 group-focus-within:text-indigo-500 transition-colors">
                  <Search size={20} />
                </div>
                <input
                  type="text"
                  placeholder="Search archives..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyDown={handleSearch}
                  className="w-full bg-white/5 border border-white/10 rounded-[32px] py-6 pl-16 pr-8 text-white outline-none focus:border-indigo-500/50 focus:bg-indigo-500/5 transition-all font-medium"
                />
              </div>

              {/* Action Bar */}
              <div className="glass-effect px-8 py-5 rounded-[32px] border border-white/10 flex items-center justify-between gap-6">
                <div className="flex items-center gap-6">
                  <input
                    type="checkbox"
                    className="peer appearance-none w-6 h-6 rounded-lg border-2 border-white/10 checked:border-indigo-500 checked:bg-indigo-500/20 transition-all cursor-pointer"
                    onChange={handleSelectAll}
                    checked={selectedItems.length === items.length && items.length > 0}
                  />
                  <span className="text-[10px] font-black uppercase tracking-widest text-indigo-400">
                    {selectedItems.length} Selected
                  </span>
                </div>
                <div className="flex gap-4">
                  <button 
                    disabled={selectedItems.length === 0}
                    className="p-3 bg-white/5 border border-white/10 rounded-2xl text-slate-400 hover:text-white hover:border-white/20 disabled:opacity-30 disabled:cursor-not-allowed transition-all"
                  >
                    <Download size={20} />
                  </button>
                  <button 
                    onClick={handleDeleteSelected}
                    disabled={selectedItems.length === 0 || loading}
                    className="p-3 bg-white/5 border border-white/10 rounded-2xl text-slate-400 hover:text-rose-500 hover:border-rose-500/30 disabled:opacity-30 disabled:cursor-not-allowed transition-all"
                  >
                    <Trash2 size={20} />
                  </button>
                </div>
              </div>

              {/* Items */}
              <div className="space-y-6">
                {loading ? (
                  <div className="flex flex-col items-center justify-center py-20 gap-4">
                    <div className="w-12 h-12 border-4 border-indigo-500/20 border-t-indigo-500 rounded-full animate-spin"></div>
                    <span className="text-[10px] font-black uppercase tracking-[0.3em] text-slate-500">Syncing Archive...</span>
                  </div>
                ) : filteredItems.length > 0 ? (
                  filteredItems.map((c) => (
                    <div
                      key={c.id}
                      onClick={() => toggleSelection(c.id)}
                      className={`glass-effect p-8 rounded-[40px] border border-white/10 hover:bg-white/[0.04] transition-all cursor-pointer group relative overflow-hidden flex gap-8 items-start ${selectedItems.includes(c.id) ? 'ring-2 ring-indigo-500 border-transparent' : ''}`}
                    >
                      <div className="mt-1" onClick={(e) => e.stopPropagation()}>
                        <input
                          type="checkbox"
                          className="peer appearance-none w-6 h-6 rounded-lg border-2 border-white/10 checked:border-indigo-500 checked:bg-indigo-500 transition-all cursor-pointer"
                          checked={selectedItems.includes(c.id)}
                          onChange={() => toggleSelection(c.id)}
                        />
                      </div>
                      <div className="flex-1">
                        <div className="flex justify-between items-start gap-6 mb-4">
                          <h3 className="text-2xl font-black text-white group-hover:text-indigo-400 transition-colors leading-tight">
                            {c.title}
                          </h3>
                          <div className="flex gap-3 shrink-0" onClick={(e) => e.stopPropagation()}>
                            <button 
                              onClick={(e) => handleViewItem(e, c)}
                              className="px-5 py-2 bg-indigo-500/10 text-indigo-400 text-[10px] font-black uppercase tracking-widest rounded-xl border border-indigo-500/20 hover:bg-indigo-500 hover:text-white transition-all"
                            >
                              View
                            </button>
                          </div>
                        </div>
                        <p className="text-slate-500 font-medium text-sm mb-6 font-mono">{c.citation}</p>
                        <div className="flex items-center gap-8">
                          <span className="px-3 py-1 bg-white/5 text-slate-400 text-[9px] font-black uppercase tracking-widest rounded-lg border border-white/5">
                            {c.domain}
                          </span>
                          <div className="flex items-center gap-2 text-slate-600 text-[10px] font-black uppercase tracking-widest">
                            <Calendar size={14} />
                            {c.date}
                          </div>
                        </div>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="glass-effect p-20 rounded-[40px] border border-white/5 text-center">
                    <div className="w-20 h-20 bg-white/5 rounded-3xl flex items-center justify-center mx-auto mb-8 text-slate-600">
                      <Search size={40} />
                    </div>
                    <h3 className="text-2xl font-black text-white mb-2">No items found</h3>
                    <p className="text-slate-500 font-medium">Try adjusting your search or filters to find what you're looking for.</p>
                  </div>
                )}
              </div>

              {/* Pagination */}
              {totalCount > 0 && activeTab === 'research' && (
                <div className="flex justify-center pt-10">
                  <div className="flex items-center gap-3">
                    <button 
                      onClick={() => setPage(p => Math.max(1, p - 1))}
                      disabled={page === 1}
                      className="p-3 bg-white/5 border border-white/5 rounded-2xl text-slate-600 hover:text-white disabled:opacity-20 transition-all"
                    >
                      <ChevronLeft size={24} />
                    </button>
                    <span className="w-12 h-12 flex items-center justify-center font-black bg-indigo-600 text-white rounded-2xl shadow-xl shadow-indigo-600/20">{page}</span>
                    <button 
                      onClick={() => setPage(p => p + 1)}
                      disabled={items.length < 20} // Simple check
                      className="p-3 bg-white/5 border border-white/5 rounded-2xl text-slate-600 hover:text-white disabled:opacity-20 transition-all"
                    >
                      <ChevronRight size={24} />
                    </button>
                  </div>
                </div>
              )}
            </section>
          </div>
        </div>
      </main>

      {/* View Item Modal */}
      {selectedViewItem && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-6 bg-slate-950/80 backdrop-blur-sm">
          <div className="bg-[#0f172a] border border-white/10 w-full max-w-3xl max-h-[80vh] rounded-[40px] shadow-2xl overflow-hidden flex flex-col">
            <div className="p-8 border-b border-white/5 flex justify-between items-center">
              <div>
                <span className="text-indigo-400 text-[10px] font-black uppercase tracking-[0.2em] mb-2 block">
                  {selectedViewItem.type === 'archive' ? 'Saved Case Record' : 'AI Research History'}
                </span>
                <h2 className="text-2xl font-black text-white">{selectedViewItem.title}</h2>
              </div>
              <button 
                onClick={() => setSelectedViewItem(null)}
                className="p-3 hover:bg-white/5 rounded-2xl text-slate-400 hover:text-white transition-all"
              >
                <X size={24} />
              </button>
            </div>
            
            <div className="p-8 overflow-y-auto space-y-8">
              {selectedViewItem.type === 'archive' ? (
                <>
                  <div className="grid grid-cols-2 gap-8">
                    <div className="space-y-2">
                      <h4 className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Citation</h4>
                      <p className="text-white font-medium">{selectedViewItem.citation}</p>
                    </div>
                    <div className="space-y-2">
                      <h4 className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Domain</h4>
                      <p className="text-white font-medium">{selectedViewItem.domain}</p>
                    </div>
                  </div>
                  <div className="space-y-4">
                    <h4 className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Metadata</h4>
                    <div className="glass-effect p-6 rounded-3xl border border-white/5 space-y-3">
                      <div className="flex justify-between text-sm">
                        <span className="text-slate-400">Date Saved</span>
                        <span className="text-white font-bold">{selectedViewItem.date}</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-slate-400">Record ID</span>
                        <span className="text-white font-bold font-mono">{selectedViewItem.id}</span>
                      </div>
                    </div>
                  </div>
                </>
              ) : (
                <>
                  <div className="space-y-4">
                    <h4 className="text-[10px] font-black text-slate-500 uppercase tracking-widest">AI Analysis Result</h4>
                    <div className="glass-effect p-8 rounded-[32px] border border-white/5 prose prose-invert max-w-none">
                      <div className="text-slate-300 leading-relaxed">
                        {selectedViewItem.raw?.answer?.analysis || selectedViewItem.raw?.answer?.answer || "No detailed analysis available for this record."}
                      </div>
                    </div>
                  </div>
                  
                  {selectedViewItem.raw?.answer?.cited_sections && selectedViewItem.raw.answer.cited_sections.length > 0 && (
                    <div className="space-y-4">
                      <h4 className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Cited Statutes</h4>
                      <div className="flex flex-wrap gap-2">
                        {selectedViewItem.raw.answer.cited_sections.map((section, idx) => (
                          <span key={idx} className="px-3 py-1 bg-indigo-500/10 text-indigo-400 text-[10px] font-black rounded-lg border border-indigo-500/20">
                            {section}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </>
              )}
            </div>

            <div className="p-8 border-t border-white/5 bg-white/[0.02] flex justify-end gap-4">
              <button 
                onClick={() => setSelectedViewItem(null)}
                className="px-8 py-3 bg-white/5 text-white text-[10px] font-black uppercase tracking-widest rounded-2xl border border-white/10 hover:bg-white/10 transition-all"
              >
                Close
              </button>
              <button className="px-8 py-3 bg-indigo-600 text-white text-[10px] font-black uppercase tracking-widest rounded-2xl shadow-lg shadow-indigo-600/20 hover:bg-indigo-500 transition-all flex items-center gap-2">
                <Download size={14} />
                Download Report
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Archive;