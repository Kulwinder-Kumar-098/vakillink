import { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../components/AuthContext';
import { ArrowRight, Mail, Lock, Shield, Gavel, Cpu, Scale, User } from 'lucide-react';

export default function Login() {
  const navigate = useNavigate();
  const location = useLocation();
  const { login } = useAuth();
  
  const [roleSelection, setRoleSelection] = useState('Client');
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const successMessage = location.state?.message;

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      await new Promise(resolve => setTimeout(resolve, 1500));
      // Use the explicit role selection instead of the email hack
      const userData = { 
        email: formData.email, 
        role: roleSelection, 
        name: formData.email.split('@')[0] || 'Premium User' 
      };
      const token = 'mock_jwt_token';
      login(userData, token);
      
      if (roleSelection === 'Lawyer') {
        navigate('/my-cases');
      } else {
        navigate('/case-search');
      }
    } catch (err) {
      setError('Invalid email or password');
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

      <div className="glass-effect rounded-[48px] border border-white/10 shadow-2xl flex flex-col md:flex-row w-full max-w-[1200px] min-h-[750px] overflow-hidden">
        {/* Left Side: Branding/Visual */}
        <div className="w-full md:w-[50%] relative overflow-hidden hidden md:flex flex-col justify-between p-16">
          <div className="absolute inset-0 z-0">
             <img 
               src="https://images.unsplash.com/photo-1589829545856-d10d557cf95f?q=80&w=2070&auto=format&fit=crop" 
               alt="Legal background" 
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

          <div className="relative z-10 space-y-6">
            <h2 className="text-6xl font-black text-white leading-tight">Elite Legal <br /> <span className="text-indigo-500">Infrastructure.</span></h2>
            <p className="text-slate-400 font-medium text-lg max-w-sm">Access advanced AI tools and the nation's most prestigious advocate network.</p>
          </div>

          <div className="relative z-10 pt-10 border-t border-white/5 flex gap-8">
             <div className="flex flex-col gap-1">
                <span className="text-2xl font-black text-white">500+</span>
                <span className="text-[10px] font-black uppercase tracking-widest text-slate-500">Vetted Experts</span>
             </div>
             <div className="flex flex-col gap-1">
                <span className="text-2xl font-black text-white">4.9/5</span>
                <span className="text-[10px] font-black uppercase tracking-widest text-slate-500">Client Satisfaction</span>
             </div>
          </div>
        </div>

        {/* Right Side: Form */}
        <div className="w-full md:w-[50%] p-10 md:p-20 flex flex-col justify-center bg-white/[0.02]">
          <div className="mb-12">
            <h1 className="text-4xl font-black text-white mb-4">Welcome Back.</h1>
            <p className="text-slate-500 font-bold text-xs uppercase tracking-widest">Sign in to your premium legal dashboard</p>
          </div>

          <div className="flex glass-effect p-1.5 rounded-[24px] border border-white/5 mb-10 overflow-hidden">
            <button 
              type="button"
              onClick={() => setRoleSelection('Lawyer')}
              className={`flex-1 flex items-center justify-center gap-3 py-4 rounded-[20px] transition-all duration-500 ${roleSelection === 'Lawyer' ? 'bg-indigo-600 text-white shadow-xl shadow-indigo-600/20' : 'text-slate-500 hover:text-white'}`}
            >
              <Gavel size={18} />
              <span className="text-[11px] font-black uppercase tracking-widest">Lawyer</span>
            </button>
            <button 
              type="button"
              onClick={() => setRoleSelection('Client')}
              className={`flex-1 flex items-center justify-center gap-3 py-4 rounded-[20px] transition-all duration-500 ${roleSelection === 'Client' ? 'bg-indigo-600 text-white shadow-xl shadow-indigo-600/20' : 'text-slate-500 hover:text-white'}`}
            >
              <User size={18} />
              <span className="text-[11px] font-black uppercase tracking-widest">Client</span>
            </button>
          </div>

          {successMessage && (
            <div className="mb-8 p-5 bg-emerald-500/10 border border-emerald-500/20 rounded-[20px] text-emerald-400 text-[10px] font-black uppercase tracking-widest flex items-center gap-3">
              <Shield size={18} />
              {successMessage}
            </div>
          )}
          
          {error && (
            <div className="mb-8 p-5 bg-rose-500/10 border border-rose-500/20 rounded-[20px] text-rose-400 text-[10px] font-black uppercase tracking-widest flex items-center gap-3">
              <Shield size={18} />
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="space-y-2">
              <label className="text-[10px] font-black uppercase tracking-widest text-slate-500 ml-4">Authorized Email</label>
              <div className="relative group">
                <div className="absolute inset-y-0 left-6 flex items-center text-slate-500 group-focus-within:text-indigo-500 transition-colors">
                  <Mail size={20} />
                </div>
                <input 
                  type="email" 
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  placeholder="name@institution.com" 
                  className="w-full pl-16 pr-8 py-5 rounded-2xl bg-white/5 border border-white/10 focus:border-indigo-500 focus:bg-white/10 outline-none transition-all text-white font-bold"
                  required
                />
              </div>
            </div>

            <div className="space-y-2">
              <div className="flex justify-between items-center ml-4 mr-4">
                <label className="text-[10px] font-black uppercase tracking-widest text-slate-500">Secret Key</label>
                <Link to="#" className="text-[10px] font-black uppercase tracking-widest text-indigo-500 hover:text-white transition-colors">Recovery</Link>
              </div>
              <div className="relative group">
                <div className="absolute inset-y-0 left-6 flex items-center text-slate-500 group-focus-within:text-indigo-500 transition-colors">
                  <Lock size={20} />
                </div>
                <input 
                  type="password" 
                  name="password"
                  value={formData.password}
                  onChange={handleChange}
                  placeholder="••••••••" 
                  className="w-full pl-16 pr-8 py-5 rounded-2xl bg-white/5 border border-white/10 focus:border-indigo-500 focus:bg-white/10 outline-none transition-all text-white font-bold"
                  required
                />
              </div>
            </div>

            <button 
              type="submit" 
              disabled={loading}
              className="w-full py-5 rounded-[24px] bg-indigo-600 text-white font-black uppercase tracking-[0.2em] text-[11px] shadow-xl shadow-indigo-600/20 hover:bg-indigo-500 hover:-translate-y-0.5 transition-all relative overflow-hidden group disabled:opacity-50"
            >
              <div className="flex items-center justify-center gap-3">
                {loading ? (
                  <div className="w-5 h-5 border-2 border-white/20 border-t-white rounded-full animate-spin"></div>
                ) : (
                  <>
                    Initialize Dashboard
                    <ArrowRight size={18} className="group-hover:translate-x-1 transition-transform" />
                  </>
                )}
              </div>
            </button>
          </form>

          <div className="mt-12 flex items-center justify-center gap-4">
            <div className="flex-1 h-px bg-white/5"></div>
            <span className="text-[10px] font-black uppercase tracking-widest text-slate-700">New around here?</span>
            <div className="flex-1 h-px bg-white/5"></div>
          </div>

          <Link 
            to="/signup" 
            className="mt-8 w-full py-5 rounded-[24px] border border-white/10 text-slate-400 font-black uppercase tracking-widest text-[10px] hover:bg-white/5 transition-all text-center"
          >
            Create Institutional Account
          </Link>
        </div>
      </div>
    </div>
  );
}
