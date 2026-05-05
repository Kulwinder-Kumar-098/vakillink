import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from './AuthContext';
import { 
  MessageSquare, 
  Search, 
  Users, 
  Calendar, 
  User as UserIcon, 
  Scale,
  Menu,
  X,
  LayoutDashboard,
  Archive,
  BookOpen,
  LogOut
} from 'lucide-react';

const UserSidebar = () => {
  const { user, logout } = useAuth();
  const location = useLocation();
  const [isOpen, setIsOpen] = useState(false);

  const userRole = (user?.role || '').toLowerCase();
  const isLawyer = userRole === 'lawyer';
  const isClient = userRole === 'client';

  const navItems = isLawyer ? [
    { name: 'Dashboard', path: '/my-cases', icon: LayoutDashboard },
    { name: 'AI Assistant', path: '/case-curator', icon: MessageSquare },
    { name: 'Case Search', path: '/case-search', icon: Search },
    { name: 'Statutes', path: '/statutes', icon: BookOpen },
    { name: 'Case Archive', path: '/archive', icon: Archive },
    { name: 'Consultations', path: '/consultations', icon: Calendar },
    { name: 'Profile', path: '/profile', icon: UserIcon },
  ] : [
    { name: 'AI Assistant', path: '/case-curator', icon: MessageSquare },
    { name: 'Case Search', path: '/case-search', icon: Search },
    { name: 'Find Lawyers', path: '/lawyers', icon: Users },
    { name: 'Statutes', path: '/statutes', icon: BookOpen },
    { name: 'Consultations', path: '/consultations', icon: Calendar },
    { name: 'Profile', path: '/profile', icon: UserIcon },
  ];

  const getInitials = (name) => {
    if (!name) return 'U';
    return name
      .split(' ')
      .filter(Boolean)
      .map(n => n[0])
      .join('')
      .toUpperCase()
      .substring(0, 2);
  };

  return (
    <>
      {/* Mobile Toggle */}
      <button 
        onClick={() => setIsOpen(!isOpen)}
        className="md:hidden fixed top-6 left-6 z-[60] glass-effect text-white p-3 rounded-2xl shadow-2xl"
      >
        {isOpen ? <X size={20} /> : <Menu size={20} />}
      </button>

      {/* Sidebar */}
      <aside className={`
        fixed left-0 top-0 h-screen bg-[#020617]/80 backdrop-blur-xl border-r border-white/5 text-white flex flex-col z-50 transition-all duration-500 ease-in-out
        ${isOpen ? 'w-[280px] translate-x-0' : 'w-[280px] -translate-x-full md:translate-x-0'}
      `}>
        <div className="p-8 flex items-center gap-4">
          <div className="w-10 h-10 rounded-xl primary-gradient flex items-center justify-center shadow-lg shadow-indigo-500/20">
            <Scale className="text-white" size={22} />
          </div>
          <span className="text-2xl font-black tracking-tighter text-gradient">VakeelLink</span>
        </div>
        
        <nav className="flex-1 mt-8 px-6 space-y-3">
          <div className="text-[10px] font-bold text-slate-500 uppercase tracking-[0.2em] mb-4 px-4">Main Menu</div>
          {navItems.map((item) => {
            const isActive = location.pathname === item.path;
            const Icon = item.icon;
            
            if (!Icon) return null;

            return (
              <Link
                key={item.path}
                to={item.path}
                onClick={() => setIsOpen(false)}
                className={`flex items-center gap-4 px-5 py-4 rounded-2xl transition-all duration-300 group ${
                  isActive 
                    ? 'bg-indigo-600/10 text-indigo-400 border border-indigo-500/20 shadow-[0_0_20px_rgba(99,102,241,0.1)]' 
                    : 'text-slate-400 hover:bg-white/5 hover:text-white'
                }`}
              >
                <div className={`transition-colors duration-300 ${isActive ? 'text-indigo-400' : 'group-hover:text-white'}`}>
                  <Icon size={20} />
                </div>
                <span className="font-semibold text-[15px]">{item.name}</span>
                {isActive && (
                  <div className="ml-auto w-1.5 h-1.5 rounded-full bg-indigo-500 shadow-[0_0_10px_rgba(99,102,241,0.8)]" />
                )}
              </Link>
            );
          })}
        </nav>

        <div className="p-6 mt-auto">
          <div className="glass-effect rounded-[24px] p-5 border border-white/5 relative overflow-hidden group">
            <div className="absolute top-0 right-0 w-24 h-24 bg-indigo-500/10 blur-2xl rounded-full -mr-12 -mt-12 transition-all group-hover:bg-indigo-500/20" />
            <div className="flex items-center gap-4">
              <div className="relative">
                <div className="w-11 h-11 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-sm font-bold shadow-lg text-white">
                  {getInitials(user?.name)}
                </div>
                <div className="absolute -bottom-1 -right-1 w-4 h-4 bg-emerald-500 border-2 border-[#0f172a] rounded-full shadow-lg" />
              </div>
              <div className="flex flex-col overflow-hidden">
                <span className="text-sm font-bold text-white truncate">{user?.name || 'Authorized User'}</span>
                <span className="text-[11px] font-medium text-slate-500 capitalize">{user?.role || 'Guest'} Plan</span>
              </div>
              <button 
                onClick={logout}
                className="ml-auto p-2 text-slate-500 hover:text-rose-400 transition-colors"
                title="Sign Out"
              >
                <LogOut size={18} />
              </button>
            </div>
          </div>
        </div>
      </aside>

      {/* Overlay for mobile */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40 md:hidden animate-in fade-in duration-300"
          onClick={() => setIsOpen(false)}
        ></div>
      )}
    </>
  );
};

export default UserSidebar;
