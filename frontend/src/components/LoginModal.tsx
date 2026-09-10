import React, { useState, useEffect, useRef } from 'react';
import { Anchor, Lock, User, Mail, Shield, CheckCircle2, AlertCircle, ArrowRight, Eye, EyeOff, Sparkles, X, UserCheck, Clock, FlaskConical, Server, Settings } from 'lucide-react';
import { PersonaType, UserResponse } from '../types';
import { varunaAPI, API_BASE_URL, setCustomApiUrl, getStoredApiUrl } from '../services/api';

interface LoginModalProps {
  isOpen: boolean;
  onClose: () => void;
  onLoginSuccess: (user: UserResponse, token: string) => void;
  canClose?: boolean; // When false, X button is hidden (login gate mode)
}

export const LoginModal: React.FC<LoginModalProps> = ({ isOpen, onClose, onLoginSuccess, canClose = false }) => {
  const [isRegisterMode, setIsRegisterMode] = useState<boolean>(false);
  const [showPassword, setShowPassword] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [otpEmail, setOtpEmail] = useState<string>('');
  const [otp, setOtp] = useState<string>('');
  const [otpSent, setOtpSent] = useState<boolean>(false);
  const [otpCountdown, setOtpCountdown] = useState<number>(0);
  const [peekLoading, setPeekLoading] = useState<boolean>(false);
  const countdownRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // Form Fields
  const [username, setUsername] = useState<string>('');
  const [email, setEmail] = useState<string>('');
  const [password, setPassword] = useState<string>('');
  const [fullName, setFullName] = useState<string>('');
  const [role, setRole] = useState<PersonaType>('Fisherman');

  // Backend API URL configuration
  const [showServerConfig, setShowServerConfig] = useState<boolean>(false);
  const [serverUrlInput, setServerUrlInput] = useState<string>(getStoredApiUrl() || '');

  if (!isOpen) return null;

  // ── Helpers ────────────────────────────────────────────────────────────────
  const startCountdown = (seconds: number) => {
    if (countdownRef.current) clearInterval(countdownRef.current);
    setOtpCountdown(seconds);
    countdownRef.current = setInterval(() => {
      setOtpCountdown(prev => {
        if (prev <= 1) { clearInterval(countdownRef.current!); return 0; }
        return prev - 1;
      });
    }, 1000);
  };

  // Preset Demo Accounts
  const demoAccounts: { role: PersonaType; username: string; label: string; icon: string; desc: string }[] = [
    { role: 'Fisherman', username: 'fisherman', label: 'Fisherman Ops', icon: '🎣', desc: 'PFZ Advisory & Local Wave Safety' },
    { role: 'Shipping', username: 'shipping', label: 'Shipping Captain', icon: '🚢', desc: 'A* Pathfinder & Fuel Risk' },
    { role: 'Disaster', username: 'disaster', label: 'Disaster Command', icon: '🌪️', desc: 'Cyclone Warning & Anomalies' },
    { role: 'Researcher', username: 'researcher', label: 'Marine Researcher', icon: '🔬', desc: 'SHAP Explainability & Simulator' },
    { role: 'Admin', username: 'admin', label: 'System Admin', icon: '🛡️', desc: 'Model Benchmarks & Infrastructure' },
  ];

  const handleQuickLogin = async (demoUsername: string) => {
    setLoading(true);
    setErrorMessage(null);
    setSuccessMessage(null);
    try {
      const auth = await varunaAPI.login(demoUsername, 'demo123');
      onLoginSuccess(auth.user, auth.access_token);
      onClose();
    } catch (err: any) {
      const msg = err?.message || 'Login failed. Please check credentials.';
      if (msg.includes('405') || msg.includes('404')) {
        setErrorMessage('Backend API returned Method Not Allowed (HTTP 405/404). Please configure your live backend URL below or verify VITE_API_URL.');
      } else {
        setErrorMessage(msg);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setErrorMessage(null);
    setSuccessMessage(null);

    if (!username || !password) {
      setErrorMessage('Please fill in all required fields.');
      setLoading(false);
      return;
    }

    try {
      if (isRegisterMode) {
        if (!email) {
          setErrorMessage('Email address is required for registration.');
          setLoading(false);
          return;
        }
        await varunaAPI.register({
          username,
          email,
          password,
          role,
          full_name: fullName || username
        });
        setSuccessMessage('Registration successful! Logging you in...');
        setTimeout(async () => {
          const auth = await varunaAPI.login(username, password);
          onLoginSuccess(auth.user, auth.access_token);
          onClose();
        }, 800);
      } else {
        const auth = await varunaAPI.login(username, password);
        onLoginSuccess(auth.user, auth.access_token);
        onClose();
      }
    } catch (err: any) {
      const msg = err?.message || 'Authentication error. Please try again.';
      if (msg.includes('405') || msg.includes('404')) {
        setErrorMessage('Backend API returned Method Not Allowed (HTTP 405/404). Please configure your live backend URL below or verify VITE_API_URL.');
      } else {
        setErrorMessage(msg);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleRequestOTP = async () => {
    if (!otpEmail.trim()) {
      setErrorMessage('Enter your registered email address first.');
      return;
    }
    setLoading(true);
    setErrorMessage(null);
    try {
      const result = await varunaAPI.requestLoginOTP(otpEmail.trim());
      setOtpSent(true);
      startCountdown(600); // 10-minute expiry
      setSuccessMessage(result.demo_mode
        ? 'OTP generated in demo mode. Use \'Show Demo OTP\' button below to retrieve it.'
        : 'OTP sent. Check your email inbox or spam folder.');
    } catch (err: any) {
      setErrorMessage(err.message || 'Unable to send OTP.');
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyOTP = async () => {
    if (!otpEmail.trim() || otp.length !== 6) {
      setErrorMessage('Enter the 6-digit OTP sent to your email.');
      return;
    }
    setLoading(true);
    setErrorMessage(null);
    try {
      const auth = await varunaAPI.verifyLoginOTP(otpEmail.trim(), otp);
      onLoginSuccess(auth.user, auth.access_token);
      onClose();
    } catch (err: any) {
      setErrorMessage(err.message || 'Invalid or expired OTP.');
    } finally {
      setLoading(false);
    }
  };

  const handleDemoPeek = async () => {
    if (!otpEmail.trim()) {
      setErrorMessage('Enter the email you used to request the OTP.');
      return;
    }
    setPeekLoading(true);
    setErrorMessage(null);
    try {
      const res = await varunaAPI.getOTPDemoPeek(otpEmail.trim());
      setOtp(res.demo_otp);
      setSuccessMessage(`Demo OTP retrieved: ${res.demo_otp} — auto-filled above. Expires in ${Math.floor(res.expires_in_seconds / 60)}m ${res.expires_in_seconds % 60}s.`);
    } catch (err: any) {
      setErrorMessage(err.message?.includes('404') ? 'No active OTP found. Request a new OTP first.' : (err.message || 'Could not retrieve demo OTP.'));
    } finally {
      setPeekLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-[2000] flex items-center justify-center p-4 sm:p-6 overflow-y-auto bg-slate-950/95 backdrop-blur-md animate-fadeIn">
      {/* Container card */}
      <div className="relative w-full max-w-xl max-h-[calc(100vh-2rem)] overflow-y-auto bg-slate-950 border border-cyan-400/40 rounded-3xl shadow-2xl shadow-black/80 p-6 sm:p-8 space-y-6 text-slate-100">
        
        {/* Glow ambient background graphics */}
        <div className="absolute -top-24 -right-24 w-60 h-60 rounded-full bg-cyan-500/10 blur-3xl pointer-events-none" />
        <div className="absolute -bottom-24 -left-24 w-60 h-60 rounded-full bg-blue-600/10 blur-3xl pointer-events-none" />

        {/* Header Bar */}
        <div className="flex items-center justify-between border-b border-slate-800 pb-4">
          <div className="flex items-center space-x-3">
            <div className="p-2.5 rounded-2xl bg-gradient-to-tr from-cyan-500 to-blue-600 shadow-lg shadow-cyan-500/20 text-white">
              <Anchor className="w-6 h-6 animate-pulse" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-extrabold text-xl tracking-wider text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-400">
                  VARUNA LOGIN
                </span>
                <span className="px-2 py-0.5 rounded text-[10px] font-extrabold bg-cyan-950 text-cyan-400 border border-cyan-800">
                  SIH 2026
                </span>
              </div>
              <p className="text-xs text-slate-400">Agentic AI Marine Intelligence & Safety Platform</p>
            </div>
          </div>

          {canClose && (
            <button
              onClick={onClose}
              className="p-2 rounded-xl text-slate-400 hover:text-slate-100 hover:bg-slate-800 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          )}
        </div>


        {/* Tab Toggle: Sign In vs Register */}
        <div className="flex p-1 rounded-2xl bg-black border border-slate-700 text-xs font-bold">
          <button
            type="button"
            onClick={() => { setIsRegisterMode(false); setErrorMessage(null); }}
            className={`flex-1 py-2.5 rounded-xl transition-all ${
              !isRegisterMode
                ? 'bg-gradient-to-r from-cyan-500 to-blue-600 text-white shadow-md'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Sign In
          </button>
          <button
            type="button"
            onClick={() => { setIsRegisterMode(true); setErrorMessage(null); }}
            className={`flex-1 py-2.5 rounded-xl transition-all ${
              isRegisterMode
                ? 'bg-gradient-to-r from-cyan-500 to-blue-600 text-white shadow-md'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Create Account
          </button>
        </div>

        {/* Quick Persona Demo Login Shortcuts */}
        {!isRegisterMode && (
          <div className="space-y-2">
            <div className="flex items-center justify-between text-[11px] font-bold uppercase tracking-wider text-slate-400">
              <span className="flex items-center space-x-1">
                <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
                <span>Quick SIH Demo Persona Login</span>
              </span>
              <span className="text-cyan-400 font-mono">1-Click Auth</span>
            </div>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
              {demoAccounts.map((demo) => (
                <button
                  key={demo.username}
                  type="button"
                  onClick={() => handleQuickLogin(demo.username)}
                  disabled={loading}
                  className="p-2.5 rounded-xl bg-slate-900 border border-slate-700 hover:border-cyan-400/70 text-left transition-all group"
                >
                  <div className="flex items-center space-x-2 font-bold text-xs text-slate-200 group-hover:text-cyan-300">
                    <span>{demo.icon}</span>
                    <span className="truncate">{demo.label}</span>
                  </div>
                  <div className="text-[10px] text-slate-400 truncate mt-0.5">{demo.desc}</div>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Status Alerts */}
        {errorMessage && (
          <div className="p-3 rounded-xl bg-red-950/50 border border-red-500/40 text-red-300 text-xs flex items-center space-x-2">
            <AlertCircle className="w-4 h-4 text-red-400 shrink-0" />
            <span>{errorMessage}</span>
          </div>
        )}

        {successMessage && (
          <div className="p-3 rounded-xl bg-emerald-950/50 border border-emerald-500/40 text-emerald-300 text-xs flex items-center space-x-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
            <span>{successMessage}</span>
          </div>
        )}

        {/* Login / Register Form */}
        <form onSubmit={handleSubmit} className="space-y-4 text-xs">
          {!isRegisterMode && (
            <div className="rounded-2xl border border-cyan-400/30 bg-slate-900 p-4 space-y-3">
              <div>
                <div className="font-bold text-cyan-300">Email OTP Login</div>
                <div className="text-[11px] text-slate-400 mt-1">Use the email registered with your VARUNA account.</div>
              </div>
              <div className="flex gap-2">
                <input
                  type="email"
                  value={otpEmail}
                  onChange={(e) => setOtpEmail(e.target.value)}
                  placeholder="you@example.com"
                  className="min-w-0 flex-1 bg-black border border-slate-700 rounded-xl py-2.5 px-3 text-white placeholder-slate-500 focus:outline-none focus:border-cyan-400"
                />
                <button
                  type="button"
                  onClick={handleRequestOTP}
                  disabled={loading}
                  className="rounded-xl bg-cyan-600 px-3 font-bold text-white hover:bg-cyan-500 disabled:opacity-50"
                >
                  Send OTP
                </button>
              </div>
              {otpSent && (
                <div className="space-y-2">
                  <div className="flex gap-2">
                    <input
                      type="text"
                      inputMode="numeric"
                      autoComplete="one-time-code"
                      maxLength={6}
                      value={otp}
                      onChange={(e) => setOtp(e.target.value.replace(/\D/g, '').slice(0, 6))}
                      placeholder="6-digit OTP"
                      className="min-w-0 flex-1 bg-black border border-slate-700 rounded-xl py-2.5 px-3 text-white tracking-[0.35em] placeholder-slate-500 placeholder:tracking-normal focus:outline-none focus:border-cyan-400"
                    />
                    <button
                      type="button"
                      onClick={handleVerifyOTP}
                      disabled={loading || otp.length !== 6}
                      className="rounded-xl bg-emerald-600 px-3 font-bold text-white hover:bg-emerald-500 disabled:opacity-50"
                    >
                      Verify & Login
                    </button>
                  </div>
                  {/* OTP countdown + demo peek row */}
                  <div className="flex items-center justify-between gap-2">
                    {otpCountdown > 0 ? (
                      <span className="flex items-center gap-1 text-[11px] text-slate-400">
                        <Clock className="w-3 h-3" />
                        Expires in {Math.floor(otpCountdown / 60)}:{String(otpCountdown % 60).padStart(2, '0')}
                      </span>
                    ) : (
                      <button type="button" onClick={handleRequestOTP} disabled={loading}
                        className="text-[11px] text-cyan-400 hover:text-cyan-300 underline">
                        Resend OTP
                      </button>
                    )}
                    <button
                      type="button"
                      onClick={handleDemoPeek}
                      disabled={peekLoading}
                      className="flex items-center gap-1 px-2.5 py-1.5 rounded-lg bg-amber-950/60 border border-amber-500/40 text-amber-300 text-[11px] font-bold hover:bg-amber-900/60 disabled:opacity-50 transition-colors"
                    >
                      <FlaskConical className="w-3 h-3" />
                      {peekLoading ? 'Fetching…' : 'Show Demo OTP'}
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Registration Extra Fields */}
          {isRegisterMode && (
            <>
              <div>
                <label className="block text-slate-300 font-semibold mb-1">Full Name</label>
                <div className="relative">
                  <User className="absolute left-3.5 top-3 w-4 h-4 text-slate-400" />
                  <input
                    type="text"
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    placeholder="e.g. Capt. Rajesh Kumar"
                    className="w-full bg-black border border-slate-700 rounded-xl py-2.5 pl-10 pr-4 text-white placeholder-slate-500 focus:outline-none focus:border-cyan-400"
                  />
                </div>
              </div>

              <div>
                <label className="block text-slate-300 font-semibold mb-1">Email Address</label>
                <div className="relative">
                  <Mail className="absolute left-3.5 top-3 w-4 h-4 text-slate-400" />
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="officer@varuna.gov.in"
                    className="w-full bg-black border border-slate-700 rounded-xl py-2.5 pl-10 pr-4 text-white placeholder-slate-500 focus:outline-none focus:border-cyan-400"
                  />
                </div>
              </div>

              <div>
                <label className="block text-slate-300 font-semibold mb-1">Operational Persona / Role</label>
                <div className="relative">
                  <UserCheck className="absolute left-3.5 top-3 w-4 h-4 text-slate-400" />
                  <select
                    value={role}
                    onChange={(e) => setRole(e.target.value as PersonaType)}
                    className="w-full bg-black border border-slate-700 rounded-xl py-2.5 pl-10 pr-4 text-white focus:outline-none focus:border-cyan-400"
                  >
                    <option value="Fisherman">Fisherman (PFZ & Advisory)</option>
                    <option value="Shipping">Shipping Captain (Route Pathfinder)</option>
                    <option value="Disaster">Disaster Specialist (Cyclone Tracking)</option>
                    <option value="Researcher">Marine Researcher (SHAP & What-If)</option>
                    <option value="Admin">Admin Command (System & Models)</option>
                  </select>
                </div>
              </div>
            </>
          )}

          {/* Username */}
          <div>
            <label className="block text-slate-300 font-semibold mb-1">Username</label>
            <div className="relative">
              <User className="absolute left-3.5 top-3 w-4 h-4 text-slate-400" />
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Enter username (e.g. fisherman)"
                required
                className="w-full bg-black border border-slate-700 rounded-xl py-2.5 pl-10 pr-4 text-white placeholder-slate-500 focus:outline-none focus:border-cyan-400"
              />
            </div>
          </div>

          {/* Password */}
          <div>
            <label className="block text-slate-300 font-semibold mb-1">Password</label>
            <div className="relative">
              <Lock className="absolute left-3.5 top-3 w-4 h-4 text-slate-400" />
              <input
                type={showPassword ? 'text' : 'password'}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter password"
                required
                className="w-full bg-black border border-slate-700 rounded-xl py-2.5 pl-10 pr-10 text-white placeholder-slate-500 focus:outline-none focus:border-cyan-400"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3.5 top-3 text-slate-400 hover:text-slate-200"
              >
                {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 rounded-xl bg-gradient-to-r from-cyan-500 via-teal-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white font-bold text-xs uppercase tracking-wider shadow-lg shadow-cyan-500/25 flex items-center justify-center space-x-2 transition-all disabled:opacity-50"
          >
            {loading ? (
              <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
            ) : (
              <>
                <span>{isRegisterMode ? 'Complete Registration' : 'Sign In to VARUNA'}</span>
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </button>
        </form>

        {/* Backend Server Configuration Toggle */}
        <div className="border-t border-slate-800/80 pt-3">
          <div className="flex items-center justify-between text-[11px] text-slate-400">
            <span className="truncate max-w-[280px]">
              API: <strong className="text-cyan-400 font-mono">{API_BASE_URL}</strong>
            </span>
            <button
              type="button"
              onClick={() => setShowServerConfig(!showServerConfig)}
              className="text-cyan-400 hover:text-cyan-300 font-semibold underline flex items-center space-x-1 shrink-0"
            >
              <Settings className="w-3 h-3" />
              <span>{showServerConfig ? 'Hide Config' : 'Configure Server'}</span>
            </button>
          </div>

          {showServerConfig && (
            <div className="mt-2.5 p-3 rounded-xl bg-slate-900/90 border border-cyan-500/30 text-xs space-y-2">
              <div className="text-slate-200 font-bold flex items-center space-x-1.5">
                <Server className="w-3.5 h-3.5 text-cyan-400" />
                <span>Custom FastAPI Backend URL</span>
              </div>
              <p className="text-[11px] text-slate-400">
                If deployed on Render, Railway, or VPS, enter your service URL (e.g. <code>https://varuna-api.onrender.com</code>):
              </p>
              <div className="flex space-x-2">
                <input
                  type="text"
                  value={serverUrlInput}
                  onChange={(e) => setServerUrlInput(e.target.value)}
                  placeholder="https://your-backend.onrender.com"
                  className="flex-1 bg-black border border-slate-700 rounded-lg px-2.5 py-1.5 text-white text-xs font-mono focus:outline-none focus:border-cyan-400"
                />
                <button
                  type="button"
                  onClick={() => {
                    setCustomApiUrl(serverUrlInput);
                    window.location.reload();
                  }}
                  className="px-3 py-1.5 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white font-bold text-xs shrink-0"
                >
                  Save & Reload
                </button>
                {serverUrlInput && (
                  <button
                    type="button"
                    onClick={() => {
                      setCustomApiUrl('');
                      setServerUrlInput('');
                      window.location.reload();
                    }}
                    className="px-2.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs shrink-0"
                  >
                    Reset
                  </button>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Footer Note */}
        <div className="text-center text-[11px] text-slate-500 pt-1">
          Protected by VARUNA Encrypted JWT Auth Protocol • SIH 2026
        </div>
      </div>
    </div>
  );
};
