import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ArrowLeft, User, Mail, Lock, FileText, CheckCircle2, Scale, Shield, ArrowRight } from 'lucide-react';

export default function Signup() {
  const navigate = useNavigate();
  const [role, setRole] = useState('Lawyer');
  const [formData, setFormData] = useState({
    fullName: '',
    email: '',
    password: '',
    barRegistration: ''
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await new Promise(resolve => setTimeout(resolve, 1500));
      navigate('/login', { state: { message: 'Institutional account created. Please authenticate.' } });
    } catch (err) {
      setError('System rejected registration. Please verify details.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#020617] flex items-center justify-center p-6 md:p-12 font-inter">
      {/* Decorative Glows */}
      <div className="absolute top-0 left-0 w-full h-full overflow-hidden -z-10">
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-indigo-600/10 rounded-full blur-[120px]"></div>
        <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-purple-600/10 rounded-full blur-[120px]"></div>
      </div>

      <div className="glass-effect rounded-[48px] border border-white/10 shadow-2xl flex flex-col md:flex-row w-full max-w-[1200px] min-h-[800px] overflow-hidden">
        {/* Left Side: Branding/Visual */}
        <div className="w-full md:w-[45%] relative overflow-hidden hidden md:flex flex-col justify-between p-16">
          <div className="absolute inset-0 z-0">
             <img 
               src="https://images.unsplash.com/photo-1505664194779-8beaceb93744?q=80&w=2070&auto=format&fit=crop" 
               alt="Legal chambers" 
               className="w-full h-full object-cover opacity-20 grayscale"
             />
             <div className="absolute inset-0 bg-gradient-to-br from-[#020617] via-transparent to-indigo-900/20"></div>
          </div>
          
          <div className="relative z-10">
            <Link to="/" className="flex items-center gap-3 group">
                <div className="w-10 h-10 rounded-xl bg-indigo-600 flex items-center justify-center shadow-lg shadow-indigo-600/20 transition-transform group-hover:scale-110">
                    <Scale size={24} className="text-white" />
                </div>
                <span className="text-xl font-black tracking-tighter text-white">Vakeel<span className="text-indigo-500">Link</span></span>
            </Link>
          </div>

          <div className="relative z-10 space-y-8">
            <h2 className="text-5xl font-black text-white leading-tight">Join the <br /> <span className="text-indigo-500">Legal Elite.</span></h2>
            <p className="text-slate-400 font-medium text-lg">Be part of India's fastest growing digital legal infrastructure.</p>
            
            <div className="space-y-4 pt-10">
               {[
                 'Advanced AI Research Engine',
                 'Institutional Grade Security',
                 'Verified Network Access'
               ].map((benefit) => (
                 <div key={benefit} className="flex items-center gap-3 text-sm font-bold text-slate-300">
                    <CheckCircle2 size={18} className="text-indigo-500" />
                    {benefit}
                 </div>
               ))}
            </div>
          </div>

          <div className="relative z-10 flex items-center gap-2 text-[10px] font-black uppercase tracking-widest text-slate-500">
             <Shield size={14} className="text-indigo-500" />
             Protected by VakeelLink Cryptography
          </div>
        </div>

        {/* Right Side: Form */}
        <div className="w-full md:w-[55%] p-10 md:p-20 flex flex-col justify-center bg-white/[0.02] border-l border-white/5">
          <header className="mb-12 flex justify-between items-start">
            <div>
              <h1 className="text-4xl font-black text-white mb-4">Create Account</h1>
              <p className="text-slate-500 font-bold text-xs uppercase tracking-widest">Select your institutional role to begin</p>
            </div>
            <Link to="/login" className="text-[10px] font-black uppercase tracking-widest text-indigo-500 hover:text-white transition-colors">Sign In Instead</Link>
          </header>

          <div className="flex glass-effect p-1.5 rounded-[24px] border border-white/5 mb-10 overflow-hidden">
            <button 
              onClick={() => setRole('Client')}
              className={`flex-1 py-4 rounded-[20px] font-black text-[10px] uppercase tracking-widest transition-all ${role === 'Client' ? 'bg-indigo-600 text-white shadow-xl shadow-indigo-600/20' : 'text-slate-500 hover:text-white'}`}
            >
              Public Client
            </button>
            <button 
              onClick={() => setRole('Lawyer')}
              className={`flex-1 py-4 rounded-[20px] font-black text-[10px] uppercase tracking-widest transition-all ${role === 'Lawyer' ? 'bg-indigo-600 text-white shadow-xl shadow-indigo-600/20' : 'text-slate-500 hover:text-white'}`}
            >
              Licensed Advocate
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <label className="text-[10px] font-black uppercase tracking-widest text-slate-500 ml-4">Full Name</label>
                <div className="relative">
                  <User size={18} className="absolute left-6 top-1/2 -translate-y-1/2 text-slate-500" />
                  <input 
                    name="fullName"
                    value={formData.fullName}
                    onChange={handleChange}
                    className="w-full pl-16 pr-8 py-5 rounded-2xl bg-white/5 border border-white/10 focus:border-indigo-500 focus:bg-white/10 outline-none transition-all text-white font-bold" 
                    placeholder="Enter Name" 
                    required 
                    type="text" 
                  />
                </div>
              </div>

              <div className="space-y-2">
                <label className="text-[10px] font-black uppercase tracking-widest text-slate-500 ml-4">Email Address</label>
                <div className="relative">
                  <Mail size={18} className="absolute left-6 top-1/2 -translate-y-1/2 text-slate-500" />
                  <input 
                    name="email"
                    value={formData.email}
                    onChange={handleChange}
                    className="w-full pl-16 pr-8 py-5 rounded-2xl bg-white/5 border border-white/10 focus:border-indigo-500 focus:bg-white/10 outline-none transition-all text-white font-bold" 
                    placeholder="name@email.com" 
                    required 
                    type="email" 
                  />
                </div>
              </div>
            </div>

            <div className="space-y-2">
              <label className="text-[10px] font-black uppercase tracking-widest text-slate-500 ml-4">Password Security</label>
              <div className="relative">
                <Lock size={18} className="absolute left-6 top-1/2 -translate-y-1/2 text-slate-500" />
                <input 
                  name="password"
                  value={formData.password}
                  onChange={handleChange}
                  className="w-full pl-16 pr-8 py-5 rounded-2xl bg-white/5 border border-white/10 focus:border-indigo-500 focus:bg-white/10 outline-none transition-all text-white font-bold" 
                  placeholder="Min 8 characters" 
                  minLength="8" 
                  required 
                  type="password" 
                />
              </div>
            </div>

            {role === 'Lawyer' && (
              <div className="space-y-2 animate-in fade-in slide-in-from-top-4">
                <label className="text-[10px] font-black uppercase tracking-widest text-slate-500 ml-4">Bar Registration No.</label>
                <div className="relative">
                  <FileText size={18} className="absolute left-6 top-1/2 -translate-y-1/2 text-slate-500" />
                  <input 
                    name="barRegistration"
                    value={formData.barRegistration}
                    onChange={handleChange}
                    className="w-full pl-16 pr-8 py-5 rounded-2xl bg-white/5 border border-white/10 focus:border-indigo-500 focus:bg-white/10 outline-none transition-all text-white font-bold" 
                    placeholder="Format: XXX/0000/0000" 
                    required={role === 'Lawyer'}
                    type="text" 
                  />
                </div>
              </div>
            )}

            {error && (
              <div className="p-4 bg-rose-500/10 border border-rose-500/20 rounded-2xl text-rose-400 text-[10px] font-black uppercase tracking-widest flex items-center gap-3">
                <Shield size={14} />
                {error}
              </div>
            )}

            <div className="flex items-start gap-4 py-4 px-2">
              <input 
                className="mt-1 w-5 h-5 rounded-lg appearance-none border-2 border-white/10 checked:bg-indigo-600 checked:border-transparent transition-all cursor-pointer" 
                required 
                type="checkbox" 
              />
              <p className="text-slate-500 font-bold text-[10px] uppercase tracking-[0.2em] leading-relaxed">
                I verify that the information provided is correct and I agree to the <span className="text-indigo-500 cursor-pointer">Protocol</span> and <span className="text-indigo-500 cursor-pointer">Compliance Policy</span>.
              </p>
            </div>

            <button 
              type="submit"
              disabled={loading}
              className="w-full py-6 rounded-[28px] bg-indigo-600 text-white font-black uppercase tracking-[0.2em] text-[11px] shadow-xl shadow-indigo-600/20 hover:bg-indigo-500 hover:-translate-y-0.5 transition-all flex items-center justify-center gap-3 group disabled:opacity-50"
            >
              {loading ? (
                <div className="w-5 h-5 border-2 border-white/20 border-t-white rounded-full animate-spin"></div>
              ) : (
                <>
                  Establish Identity
                  <ArrowRight size={18} className="group-hover:translate-x-1 transition-transform" />
                </>
              )}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
