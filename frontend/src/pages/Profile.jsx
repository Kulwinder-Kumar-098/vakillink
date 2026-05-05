import React, { useState } from 'react';
import { 
  User, 
  Mail, 
  Phone, 
  MapPin, 
  Award, 
  Briefcase, 
  Shield, 
  Star, 
  Camera, 
  Edit3, 
  Save, 
  Lock, 
  Globe,
  Verified,
  ChevronRight
} from 'lucide-react';
import UserSidebar from '../components/UserSidebar';
import { useAuth } from '../components/AuthContext';

const Profile = () => {
  const { user } = useAuth();
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState({
    name: user?.name || 'Adv. Arjun Sharma',
    email: user?.email || 'arjun.sharma@vakeellink.com',
    phone: '+91 98765 43210',
    location: 'New Delhi, India',
    specialization: 'Criminal Defense & Constitutional Law',
    experience: '12 Years',
    barId: 'DEL/4512/2012',
    bio: 'Dedicated legal professional with over a decade of experience in the Supreme Court and High Courts. Specializing in complex criminal litigation and fundamental rights protection.',
    languages: 'English, Hindi, Punjabi',
    education: 'LL.B. (National Law University), LL.M. (Oxford)'
  });

  const handleSave = () => {
    setIsEditing(false);
    // Logic to save profile in backend would go here
  };

  const isLawyer = user?.role?.toLowerCase() === 'lawyer';

  return (
    <div className="flex min-h-screen bg-[#020617] text-slate-200 font-inter">
      <UserSidebar />
      
      <main className="flex-1 md:ml-[280px] p-6 md:p-12 overflow-y-auto">
        <div className="max-w-5xl mx-auto space-y-12">
          {/* Header & Cover */}
          <div className="relative">
            <div className="h-48 md:h-64 w-full rounded-[40px] bg-gradient-to-r from-indigo-600/20 via-purple-600/20 to-indigo-600/20 border border-white/10 overflow-hidden">
              <div className="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/carbon-fibre.png')] opacity-20"></div>
            </div>
            
            <div className="absolute -bottom-16 left-8 md:left-12 flex items-end gap-6">
              <div className="relative group">
                <div className="w-32 h-32 md:w-40 md:h-40 rounded-3xl bg-slate-900 border-4 border-[#020617] shadow-2xl flex items-center justify-center text-4xl font-black text-white overflow-hidden">
                  <span className="bg-gradient-to-br from-indigo-500 to-purple-600 w-full h-full flex items-center justify-center">
                    {formData.name.split(' ').map(n => n[0]).join('').toUpperCase()}
                  </span>
                </div>
                <button className="absolute bottom-2 right-2 p-2 bg-indigo-600 rounded-xl text-white shadow-xl opacity-0 group-hover:opacity-100 transition-opacity border border-white/20">
                  <Camera size={18} />
                </button>
              </div>
              
              <div className="pb-4 space-y-1">
                <div className="flex items-center gap-3">
                  <h1 className="text-3xl font-black text-white">{formData.name}</h1>
                  <div className="px-3 py-1 bg-emerald-500/10 border border-emerald-500/20 rounded-full flex items-center gap-1.5">
                    <Verified size={12} className="text-emerald-400" />
                    <span className="text-[9px] font-black uppercase tracking-widest text-emerald-400">Verified</span>
                  </div>
                </div>
                <p className="text-slate-400 font-bold text-xs uppercase tracking-widest flex items-center gap-2">
                  {isLawyer ? 'Senior Advocate' : 'Premium Client'} • {formData.location}
                </p>
              </div>
            </div>

            <div className="absolute -bottom-12 right-8 flex gap-3">
              {isEditing ? (
                <button 
                  onClick={handleSave}
                  className="px-6 py-3 bg-emerald-600 text-white rounded-xl font-black text-[10px] uppercase tracking-widest shadow-xl shadow-emerald-600/20 hover:bg-emerald-500 transition-all flex items-center gap-2"
                >
                  <Save size={16} />
                  Save Profile
                </button>
              ) : (
                <button 
                  onClick={() => setIsEditing(true)}
                  className="px-6 py-3 glass-effect border border-white/10 text-white rounded-xl font-black text-[10px] uppercase tracking-widest hover:bg-white/5 transition-all flex items-center gap-2"
                >
                  <Edit3 size={16} />
                  Edit Profile
                </button>
              )}
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-12 mt-20 pt-12">
            {/* Left Column: Info Cards */}
            <div className="lg:col-span-1 space-y-8">
              <section className="glass-effect p-8 rounded-[32px] border border-white/10 space-y-6">
                <h2 className="text-[10px] font-black uppercase tracking-[0.2em] text-indigo-500">Contact Details</h2>
                <div className="space-y-4">
                  <div className="flex items-center gap-4 group">
                    <div className="w-10 h-10 rounded-xl bg-white/5 flex items-center justify-center text-slate-500 group-hover:text-white transition-colors">
                      <Mail size={18} />
                    </div>
                    <div>
                      <p className="text-[9px] font-black uppercase tracking-widest text-slate-600">Email Address</p>
                      <p className="text-sm font-bold text-white">{formData.email}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-4 group">
                    <div className="w-10 h-10 rounded-xl bg-white/5 flex items-center justify-center text-slate-500 group-hover:text-white transition-colors">
                      <Phone size={18} />
                    </div>
                    <div>
                      <p className="text-[9px] font-black uppercase tracking-widest text-slate-600">Phone Number</p>
                      <p className="text-sm font-bold text-white">{formData.phone}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-4 group">
                    <div className="w-10 h-10 rounded-xl bg-white/5 flex items-center justify-center text-slate-500 group-hover:text-white transition-colors">
                      <Globe size={18} />
                    </div>
                    <div>
                      <p className="text-[9px] font-black uppercase tracking-widest text-slate-600">Personal Website</p>
                      <p className="text-sm font-bold text-white">vakeellink.com/lawyers/arjun</p>
                    </div>
                  </div>
                </div>
              </section>

              {isLawyer && (
                <section className="glass-effect p-8 rounded-[32px] border border-white/10 space-y-6">
                  <h2 className="text-[10px] font-black uppercase tracking-[0.2em] text-indigo-500">Credentials</h2>
                  <div className="space-y-4">
                    <div className="flex items-center gap-4">
                      <div className="w-10 h-10 rounded-xl bg-amber-500/10 flex items-center justify-center text-amber-500">
                        <Award size={18} />
                      </div>
                      <div>
                        <p className="text-[9px] font-black uppercase tracking-widest text-slate-600">Bar Council ID</p>
                        <p className="text-sm font-bold text-white">{formData.barId}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-4">
                      <div className="w-10 h-10 rounded-xl bg-indigo-500/10 flex items-center justify-center text-indigo-500">
                        <Star size={18} />
                      </div>
                      <div>
                        <p className="text-[9px] font-black uppercase tracking-widest text-slate-600">Rating</p>
                        <p className="text-sm font-bold text-white">4.9 / 5.0 (240 Reviews)</p>
                      </div>
                    </div>
                  </div>
                </section>
              )}
            </div>

            {/* Right Column: Detailed Bio & Settings */}
            <div className="lg:col-span-2 space-y-12">
              <section className="space-y-6">
                <h2 className="text-2xl font-black text-white">Professional <span className="text-indigo-500">Biography</span></h2>
                <div className="glass-effect p-8 rounded-[40px] border border-white/10 relative overflow-hidden group">
                  <div className="absolute top-0 right-0 p-8 opacity-5">
                    <Briefcase size={100} className="text-indigo-500" />
                  </div>
                  {isEditing ? (
                    <textarea 
                      className="w-full bg-white/5 border border-white/10 rounded-2xl p-6 text-white outline-none focus:border-indigo-500/50 min-h-[200px] font-medium leading-relaxed"
                      value={formData.bio}
                      onChange={(e) => setFormData({...formData, bio: e.target.value})}
                    />
                  ) : (
                    <p className="text-slate-300 text-lg leading-relaxed font-medium">
                      {formData.bio}
                    </p>
                  )}
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mt-10 pt-10 border-t border-white/5">
                    <div>
                      <h4 className="text-[10px] font-black uppercase tracking-[0.2em] text-slate-500 mb-4">Specialization</h4>
                      <div className="flex flex-wrap gap-2">
                        {formData.specialization.split('&').map(s => (
                          <span key={s} className="px-4 py-2 bg-indigo-600/10 border border-indigo-600/20 text-indigo-400 rounded-xl text-[10px] font-black uppercase tracking-widest">
                            {s.trim()}
                          </span>
                        ))}
                      </div>
                    </div>
                    <div>
                      <h4 className="text-[10px] font-black uppercase tracking-[0.2em] text-slate-500 mb-4">Languages</h4>
                      <div className="flex flex-wrap gap-2">
                        {formData.languages.split(',').map(l => (
                          <span key={l} className="px-4 py-2 bg-white/5 border border-white/10 text-slate-400 rounded-xl text-[10px] font-black uppercase tracking-widest">
                            {l.trim()}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              </section>

              <section className="space-y-6">
                <h2 className="text-2xl font-black text-white">Account <span className="text-indigo-500">Security</span></h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <button className="p-8 glass-effect border border-white/10 rounded-[32px] flex items-center justify-between group hover:border-indigo-500/30 transition-all">
                    <div className="flex items-center gap-4">
                      <div className="w-12 h-12 rounded-2xl bg-indigo-500/10 flex items-center justify-center text-indigo-500">
                        <Lock size={20} />
                      </div>
                      <div className="text-left">
                        <p className="text-sm font-black text-white">Password Settings</p>
                        <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Last changed 2 months ago</p>
                      </div>
                    </div>
                    <Shield size={20} className="text-slate-600 group-hover:text-indigo-500 transition-colors" />
                  </button>
                  <button className="p-8 glass-effect border border-white/10 rounded-[32px] flex items-center justify-between group hover:border-rose-500/30 transition-all">
                    <div className="flex items-center gap-4">
                      <div className="w-12 h-12 rounded-2xl bg-rose-500/10 flex items-center justify-center text-rose-500">
                        <User size={20} />
                      </div>
                      <div className="text-left">
                        <p className="text-sm font-black text-rose-500">Delete Account</p>
                        <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Irreversible action</p>
                      </div>
                    </div>
                    <ChevronRight size={20} className="text-slate-600 group-hover:text-rose-500 transition-colors" />
                  </button>
                </div>
              </section>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Profile;
