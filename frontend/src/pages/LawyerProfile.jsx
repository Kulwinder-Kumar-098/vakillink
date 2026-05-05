import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { 
  Star, 
  Verified, 
  MapPin, 
  Briefcase, 
  Gavel, 
  Calendar, 
  MessageSquare, 
  Award, 
  Shield, 
  ChevronRight, 
  Mail, 
  Phone,
  ArrowLeft,
  GraduationCap
} from 'lucide-react';
import UserSidebar from '../components/UserSidebar';

export default function LawyerProfile() {
  const { id } = useParams();
  const [lawyer, setLawyer] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const res = await fetch(`http://localhost:8000/api/v1/lawyers/${id}`);
        if (!res.ok) throw new Error('Failed to fetch profile');
        const data = await res.json();
        setLawyer(data);
      } catch (error) {
        console.error(error);
        // Fallback demo data
        setLawyer({
          id,
          name: 'Adv. Rajesh Khanna',
          specialization: 'Criminal Law',
          rating: 4.8,
          review_count: 142,
          experience_years: 25,
          location: 'New Delhi High Court',
          bio: 'With over twenty-five years of distinguished practice at the New Delhi High Court and the Supreme Court of India, Adv. Rajesh Khanna has cultivated an impeccable reputation as one of the nation\'s premier defense counsel.',
          areas_of_practice: ['White Collar & Economic Crimes', 'Supreme Court Appellate Matters', 'Constitutional & Public Law'],
          is_online: true
        });
      } finally {
        setLoading(false);
      }
    };
    fetchProfile();
  }, [id]);

  if (loading) {
    return (
      <div className="flex min-h-screen bg-[#020617] items-center justify-center">
        <div className="w-8 h-8 border-4 border-indigo-500/20 border-t-indigo-500 rounded-full animate-spin"></div>
      </div>
    );
  }

  if (!lawyer) {
    return (
      <div className="flex min-h-screen bg-[#020617] items-center justify-center flex-col gap-6">
        <h2 className="text-2xl font-black text-white">Expert Profile Not Found</h2>
        <Link to="/lawyers" className="px-8 py-3 bg-indigo-600 text-white rounded-xl font-black text-xs uppercase tracking-widest">Back to Directory</Link>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen bg-[#020617] text-slate-200 font-inter">
      <UserSidebar />
      
      <main className="flex-1 md:ml-[280px] p-6 md:p-12 overflow-y-auto">
        <div className="max-w-6xl mx-auto space-y-12 pb-24 md:pb-0">
          {/* Back Navigation */}
          <Link to="/lawyers" className="inline-flex items-center gap-2 text-slate-500 hover:text-white transition-colors text-xs font-black uppercase tracking-widest">
            <ArrowLeft size={16} />
            Back to Directory
          </Link>

          {/* Hero Profile Section */}
          <section className="relative group">
            <div className="absolute -inset-0.5 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-[48px] opacity-10 group-hover:opacity-20 transition duration-1000"></div>
            <div className="relative glass-effect p-8 md:p-14 rounded-[48px] border border-white/10 flex flex-col md:flex-row gap-12 items-center md:items-start overflow-hidden">
              <div className="absolute top-0 right-0 p-12 opacity-5 pointer-events-none">
                <Gavel size={240} className="text-indigo-500" />
              </div>

              {/* Avatar */}
              <div className="relative shrink-0">
                <div className="relative">
                  <div className="absolute -inset-4 bg-gradient-to-tr from-indigo-500 to-purple-600 rounded-full blur-2xl opacity-20"></div>
                  <div className="relative w-40 h-40 md:w-56 md:h-56 rounded-full border-8 border-white/5 shadow-2xl flex items-center justify-center bg-slate-900 text-5xl font-black text-white overflow-hidden">
                    {lawyer.avatar ? <img src={lawyer.avatar} alt={lawyer.name} className="w-full h-full object-cover" /> : lawyer.name.charAt(5)}
                  </div>
                </div>
                {lawyer.is_online && (
                  <div className="absolute bottom-4 right-4 w-10 h-10 bg-[#020617] rounded-full flex items-center justify-center border-4 border-white/5">
                    <div className="w-4 h-4 bg-emerald-500 rounded-full animate-pulse shadow-[0_0_15px_rgba(16,185,129,0.5)]"></div>
                  </div>
                )}
              </div>

              {/* Profile Main Info */}
              <div className="flex-1 space-y-8 text-center md:text-left relative z-10">
                <div className="space-y-4">
                  <div className="flex flex-col md:flex-row md:items-center gap-4">
                    <h1 className="text-4xl md:text-6xl font-black tracking-tight text-white">{lawyer.name}</h1>
                    <div className="flex items-center justify-center md:justify-start gap-2 px-4 py-1.5 bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 rounded-full text-[10px] font-black uppercase tracking-widest">
                      <Verified size={14} fill="currentColor" className="text-indigo-400" />
                      Elite Tier
                    </div>
                  </div>
                  <p className="text-2xl font-bold text-slate-400">
                    {lawyer.specialization?.replace('legal_', '').replace('_', ' ')} Advocate
                  </p>
                </div>

                <div className="flex flex-wrap justify-center md:justify-start gap-6">
                  <div className="flex items-center gap-3 glass-effect px-6 py-3 rounded-2xl border border-white/10 text-[11px] font-black uppercase tracking-widest text-slate-400">
                    <Gavel size={18} className="text-indigo-500" />
                    Bar Reg: DEL/1234/1998
                  </div>
                  <div className="flex items-center gap-3 glass-effect px-6 py-3 rounded-2xl border border-white/10 text-[11px] font-black uppercase tracking-widest text-slate-400">
                    <MapPin size={18} className="text-indigo-500" />
                    {lawyer.location}
                  </div>
                  <div className="flex items-center gap-3 glass-effect px-6 py-3 rounded-2xl border border-white/10 text-[11px] font-black uppercase tracking-widest text-slate-400">
                    <Briefcase size={18} className="text-indigo-500" />
                    {lawyer.experience_years}+ Yrs Experience
                  </div>
                </div>

                <div className="flex items-center justify-center md:justify-start gap-4">
                  <div className="flex text-amber-400">
                    {[1, 2, 3, 4, 5].map((s) => (
                      <Star key={s} size={24} fill={s <= Math.floor(lawyer.rating || 4.8) ? "currentColor" : "none"} strokeWidth={2} />
                    ))}
                  </div>
                  <span className="text-2xl font-black text-white">{lawyer.rating || '4.8'}</span>
                  <span className="text-sm font-bold text-slate-500">({lawyer.review_count || 142} Premium Reviews)</span>
                </div>
              </div>
            </div>
          </section>

          {/* Content Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-12">
            {/* Main Details */}
            <div className="lg:col-span-8 space-y-16">
              <section>
                <h2 className="text-xs font-black uppercase tracking-[0.3em] text-indigo-500 mb-8 flex items-center gap-4">
                  Professional Biography
                  <div className="flex-1 h-px bg-white/5"></div>
                </h2>
                <div className="prose prose-invert max-w-none text-slate-400 text-lg leading-relaxed font-medium space-y-6">
                  <p>{lawyer.bio}</p>
                </div>
              </section>

              <section>
                <h2 className="text-xs font-black uppercase tracking-[0.3em] text-indigo-500 mb-8 flex items-center gap-4">
                  Areas of Specialization
                  <div className="flex-1 h-px bg-white/5"></div>
                </h2>
                <div className="flex flex-wrap gap-4">
                  {lawyer.areas_of_practice?.map((area, idx) => (
                    <div key={idx} className="glass-effect px-8 py-4 rounded-[24px] border border-white/10 text-white font-bold text-sm hover:border-indigo-500/50 transition-colors">
                      {area}
                    </div>
                  ))}
                </div>
              </section>

              <section>
                <h2 className="text-xs font-black uppercase tracking-[0.3em] text-indigo-500 mb-8 flex items-center gap-4">
                  Education & Credentials
                  <div className="flex-1 h-px bg-white/5"></div>
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="glass-effect p-8 rounded-[32px] border border-white/10 space-y-4">
                    <GraduationCap size={32} className="text-indigo-500" />
                    <div>
                      <h3 className="text-lg font-black text-white leading-tight">LL.M. in Criminal Jurisprudence</h3>
                      <p className="text-sm text-slate-500 mt-2 font-medium">National Law School of India University</p>
                    </div>
                  </div>
                  <div className="glass-effect p-8 rounded-[32px] border border-white/10 space-y-4">
                    <Award size={32} className="text-indigo-500" />
                    <div>
                      <h3 className="text-lg font-black text-white leading-tight">LL.B. (Professional)</h3>
                      <p className="text-sm text-slate-500 mt-2 font-medium">Campus Law Centre, University of Delhi</p>
                    </div>
                  </div>
                </div>
              </section>

              <section>
                <div className="flex justify-between items-center mb-10">
                  <h2 className="text-xs font-black uppercase tracking-[0.3em] text-indigo-500">Client Reviews</h2>
                  <button className="text-[10px] font-black uppercase tracking-widest text-slate-500 hover:text-white transition-colors">View All {lawyer.review_count}</button>
                </div>
                <div className="space-y-6">
                   <div className="glass-effect p-10 rounded-[40px] border border-white/10 relative overflow-hidden group">
                     <div className="absolute top-0 right-0 p-8 opacity-5">
                       <MessageSquare size={80} className="text-indigo-500" />
                     </div>
                     <div className="flex justify-between items-start mb-6">
                       <div className="flex items-center gap-4">
                         <div className="w-12 h-12 rounded-2xl bg-indigo-500/10 flex items-center justify-center font-black text-indigo-400">SK</div>
                         <div>
                           <p className="font-black text-white">Sanjay Kapoor</p>
                           <p className="text-[10px] font-black uppercase tracking-widest text-slate-600">Corporate Director</p>
                         </div>
                       </div>
                       <span className="text-[10px] font-black text-slate-700 uppercase tracking-widest">Oct 12, 2023</span>
                     </div>
                     <p className="text-slate-400 text-lg italic leading-relaxed font-medium">"His approach to our complex white-collar matter was nothing short of brilliant. Truly a top-tier professional."</p>
                   </div>
                </div>
              </section>
            </div>

            {/* Sticky Actions Sidebar */}
            <div className="lg:col-span-4 space-y-8">
              <div className="sticky top-12 space-y-8">
                {/* Consultation Card */}
                <div className="glass-effect p-10 rounded-[48px] border border-white/10 relative overflow-hidden group shadow-2xl">
                  <div className="absolute -inset-0.5 bg-gradient-to-b from-indigo-500/10 to-transparent rounded-[48px] opacity-0 group-hover:opacity-100 transition duration-500"></div>
                  <h3 className="text-xl font-black text-white mb-8">Consultation</h3>
                  <div className="space-y-6">
                    <div className="flex justify-between items-center py-4 border-b border-white/5">
                      <span className="text-sm font-bold text-slate-500 uppercase tracking-widest">Digital Call</span>
                      <span className="text-lg font-black text-white">₹3,500</span>
                    </div>
                    <div className="flex justify-between items-center py-4 border-b border-white/5">
                      <span className="text-sm font-bold text-slate-500 uppercase tracking-widest">Chamber Meeting</span>
                      <span className="text-lg font-black text-white">₹5,000</span>
                    </div>
                  </div>
                  <div className="mt-10 space-y-4">
                    <button className="w-full bg-indigo-600 text-white font-black py-5 rounded-[24px] shadow-xl shadow-indigo-600/20 hover:bg-indigo-500 transition-all uppercase text-[10px] tracking-[0.2em] flex items-center justify-center gap-3">
                      <Calendar size={18} />
                      Book Priority Slot
                    </button>
                    <button className="w-full bg-white/5 border border-white/10 text-white font-black py-5 rounded-[24px] hover:bg-white/10 transition-all uppercase text-[10px] tracking-[0.2em] flex items-center justify-center gap-3">
                      <MessageSquare size={18} />
                      Send Inquiry
                    </button>
                  </div>
                  <p className="text-[10px] font-black text-slate-700 uppercase tracking-widest mt-8 text-center leading-loose">Professional fees are subject to GST and court appearance mandates.</p>
                </div>

                {/* Office Card */}
                <div className="glass-effect p-8 rounded-[40px] border border-white/10 space-y-6">
                  <h4 className="text-[10px] font-black uppercase tracking-widest text-slate-500 flex items-center gap-2">
                    <MapPin size={14} className="text-indigo-500" />
                    Chamber Location
                  </h4>
                  <div className="rounded-3xl overflow-hidden grayscale opacity-50 hover:grayscale-0 hover:opacity-100 transition-all duration-700 border border-white/5 aspect-video">
                    <img alt="Map Location" className="w-full h-full object-cover" src="https://lh3.googleusercontent.com/aida-public/AB6AXuB7HPecyXDaFAbECn9DlBC2UrZlLC4SdzM2N10080M70NRDBEKEiorS5OnemOlUnSbREsqjJuNbI4Y3znYKQPbn69pi4-sfjVe_kDbW2A5-vVg0PCJU5KZ0oOtXIUVnJD6B3GYbHq84e7a14opv0Q4ilW21YrAYVTAv642Pjn1LloEYuyLQJujli2uganU3COmk1nR02MPtMGmYLdeg982cOl2EVfpHu8MIMIkoEbIXDe5zYmUH8Q2cOuGexim8Oan-16Yba5Y_Pns" />
                  </div>
                  <p className="text-xs font-bold text-slate-400 leading-relaxed">
                    Chamber No. 402, Lawyers' Block<br/>
                    Sher Shah Road, New Delhi 110003
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* Mobile Sticky Bar */}
      <div className="md:hidden fixed bottom-0 left-0 right-0 p-4 bg-[#020617]/80 backdrop-blur-2xl border-t border-white/5 z-50">
        <div className="flex gap-4">
           <button className="flex-1 bg-white/5 border border-white/10 text-white font-black py-4 rounded-2xl uppercase text-[10px] tracking-widest">Inquiry</button>
           <button className="flex-[2] bg-indigo-600 text-white font-black py-4 rounded-2xl shadow-xl shadow-indigo-600/20 uppercase text-[10px] tracking-widest">Book Consult</button>
        </div>
      </div>
    </div>
  );
}
