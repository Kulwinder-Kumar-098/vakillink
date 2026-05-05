import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { AuthProvider } from './components/AuthContext';
import { useAuth } from './components/AuthContext';
import LandingPage from './pages/LandingPage';
import LawyerDirectory from './pages/LawyerDirectory';
import LawyerProfile from './pages/LawyerProfile';
import Login from './pages/Login';
import Signup from './pages/Signup';
import MyCases from './pages/MyCases';
import CaseCurator from './pages/CaseCurator';
import CaseSearch from './pages/CaseSearch';
import Statutes from './pages/Statutes';
import Archive from './pages/Archive';
import Consultations from './pages/Consultations';
import Profile from './pages/Profile';
import UserSidebar from './components/UserSidebar';
import './App.css';

const ProtectedRoute = ({ children, allowedRoles }) => {
  const { user, loading } = useAuth();

  if (loading) return (
    <div className="flex min-h-screen bg-[#020617] items-center justify-center">
      <div className="w-8 h-8 border-4 border-indigo-500/20 border-t-indigo-500 rounded-full animate-spin"></div>
    </div>
  );
  if (!user) return <Login />;
  
  const userRole = (user.role || '').toLowerCase();
  const lowerAllowedRoles = (allowedRoles || []).map(r => r.toLowerCase());

  if (allowedRoles && !lowerAllowedRoles.includes(userRole)) {
    return (
      <div className="flex min-h-screen bg-[#020617] items-center justify-center flex-col gap-6 text-white font-black uppercase tracking-widest text-xs">
        Access Denied
        <Link to="/" className="px-6 py-3 bg-indigo-600 rounded-xl">Return Home</Link>
      </div>
    );
  }

  return children;
};

function AppContent() {
  const location = useLocation();
  // Most pages now have internal sidebars and dark themes
  const isDashboardPage = [
    '/my-cases', 
    '/case-curator', 
    '/case-search', 
    '/lawyers', 
    '/statutes', 
    '/archive',
    '/consultations',
    '/profile'
  ].some(path => location.pathname.startsWith(path));

  const isAuthPage = location.pathname === '/login' || location.pathname === '/signup';
  const isLandingPage = location.pathname === '/';

  return (
    <div className="bg-[#020617] text-slate-200 font-inter min-h-screen flex flex-col w-full selection:bg-indigo-500/30">
      <main className="flex-grow flex flex-col w-full">
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/lawyers" element={<LawyerDirectory />} />
          <Route path="/lawyers/:id" element={<LawyerProfile />} />
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />
          <Route 
            path="/my-cases" 
            element={
              <ProtectedRoute allowedRoles={['Lawyer', 'lawyer']}>
                <MyCases />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/case-curator" 
            element={
              <ProtectedRoute>
                <CaseCurator />
              </ProtectedRoute>
            } 
          />
          <Route path="/case-search" element={<CaseSearch />} />
          <Route path="/statutes" element={<Statutes />} />
          <Route path="/archive" element={
            <ProtectedRoute>
              <Archive />
            </ProtectedRoute>
          } />
          <Route path="/consultations" element={
            <ProtectedRoute>
              <Consultations />
            </ProtectedRoute>
          } />
          <Route path="/profile" element={
            <ProtectedRoute>
              <Profile />
            </ProtectedRoute>
          } />
          
          <Route path="/pricing" element={<div className="min-h-screen flex items-center justify-center text-white">Pricing Page (Coming Soon)</div>} />
        </Routes>
      </main>

      {/* Global Footer only for Landing/Static pages */}
      {!isDashboardPage && !isAuthPage && !isLandingPage && (
        <footer className="bg-slate-950/50 border-t border-white/5 w-full py-12 flex flex-col md:flex-row justify-between items-center px-12">
          <span className="text-[10px] font-black uppercase tracking-widest text-slate-600 mb-4 md:mb-0">
            © 2024 VakeelLink Legal AI. Premium Dashboard Experience.
          </span>
          <div className="flex gap-8">
            <a className="text-[10px] font-black uppercase tracking-widest text-slate-600 hover:text-white transition-colors" href="#">Ethics</a>
            <a className="text-[10px] font-black uppercase tracking-widest text-slate-600 hover:text-white transition-colors" href="#">Terms</a>
            <a className="text-[10px] font-black uppercase tracking-widest text-slate-600 hover:text-white transition-colors" href="#">Support</a>
          </div>
        </footer>
      )}
    </div>
  );
}

function App() {
  return (
    <Router>
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </Router>
  );
}

export default App;
