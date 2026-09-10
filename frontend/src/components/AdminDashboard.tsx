import React, { useEffect, useState } from 'react';
import { Users, Activity, MessageSquare, Clock, ShieldCheck, ChevronRight, LogOut, ArrowLeft } from 'lucide-react';
import { varunaAPI } from '../services/api';
import { UserResponse } from '../types';

interface AdminDashboardProps {
  currentUser: UserResponse;
  onLogout: () => void;
}

export const AdminDashboard: React.FC<AdminDashboardProps> = ({ currentUser, onLogout }) => {
  const [activeTab, setActiveTab] = useState<'overview' | 'users' | 'activity'>('overview');
  const [overview, setOverview] = useState<any>(null);
  const [users, setUsers] = useState<any[]>([]);
  const [selectedUserId, setSelectedUserId] = useState<number | null>(null);
  const [selectedUserDetail, setSelectedUserDetail] = useState<any>(null);
  const [selectedUserQueries, setSelectedUserQueries] = useState<any[]>([]);
  const [activityLogs, setActivityLogs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchOverview = async () => {
    try {
      const data = await varunaAPI.getAdminOverview();
      setOverview(data.overview);
      setActivityLogs(data.recent_activity);
    } catch (e) {
      console.error(e);
    }
  };

  const fetchUsers = async () => {
    try {
      const data = await varunaAPI.getAdminUsers();
      setUsers(data);
    } catch (e) {
      console.error(e);
    }
  };

  const fetchActivity = async () => {
    try {
      const data = await varunaAPI.getAdminActivity();
      setActivityLogs(data);
    } catch (e) {
      console.error(e);
    }
  };

  const loadUserDetail = async (id: number) => {
    try {
      setLoading(true);
      setSelectedUserId(id);
      const detail = await varunaAPI.getAdminUserDetails(id);
      const queries = await varunaAPI.getAdminUserQueries(id);
      setSelectedUserDetail(detail);
      setSelectedUserQueries(queries);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    setLoading(true);
    if (activeTab === 'overview') fetchOverview().finally(() => setLoading(false));
    if (activeTab === 'users') fetchUsers().finally(() => setLoading(false));
    if (activeTab === 'activity') fetchActivity().finally(() => setLoading(false));
    setSelectedUserId(null);
  }, [activeTab]);

  if (currentUser?.role?.toLowerCase() !== 'admin' && currentUser?.username?.toLowerCase() !== 'admin') {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-900 text-white font-sans">
        <div className="text-center p-8 bg-slate-800 rounded-xl max-w-md">
          <ShieldCheck className="w-16 h-16 text-red-500 mx-auto mb-4" />
          <h1 className="text-2xl font-bold mb-2">Access Denied</h1>
          <p className="text-slate-400 mb-6">You do not have administrator privileges to view this dashboard.</p>
          <button onClick={() => window.location.href = '/'} className="px-6 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg font-medium transition-colors">
            Return to VARUNA
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex font-sans">
      {/* Sidebar */}
      <div className="w-64 bg-slate-900 text-white flex flex-col">
        <div className="p-6 border-b border-slate-800">
          <div className="flex items-center gap-3 text-blue-400 mb-2">
            <ShieldCheck className="w-8 h-8" />
            <h1 className="text-xl font-bold tracking-wider">VARUNA<span className="text-white">ADMIN</span></h1>
          </div>
          <p className="text-xs text-slate-400 font-medium tracking-widest uppercase">System Management</p>
        </div>

        <nav className="flex-1 px-4 space-y-2 mt-6">
          <button 
            onClick={() => setActiveTab('overview')}
            className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-colors ${activeTab === 'overview' ? 'bg-blue-600 text-white shadow-lg' : 'text-slate-400 hover:bg-slate-800 hover:text-white'}`}
          >
            <Activity className="w-5 h-5" /> Dashboard
          </button>
          <button 
            onClick={() => setActiveTab('users')}
            className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-colors ${activeTab === 'users' ? 'bg-blue-600 text-white shadow-lg' : 'text-slate-400 hover:bg-slate-800 hover:text-white'}`}
          >
            <Users className="w-5 h-5" /> Users
          </button>
          <button 
            onClick={() => setActiveTab('activity')}
            className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-colors ${activeTab === 'activity' ? 'bg-blue-600 text-white shadow-lg' : 'text-slate-400 hover:bg-slate-800 hover:text-white'}`}
          >
            <Clock className="w-5 h-5" /> Activity Logs
          </button>
        </nav>

        <div className="p-4 border-t border-slate-800">
          <button onClick={() => window.location.href = '/'} className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 rounded-lg text-sm font-medium text-slate-300 transition-colors mb-4">
            <ArrowLeft className="w-4 h-4" /> Back to App
          </button>
          <div className="flex items-center gap-3 px-2 bg-slate-800/50 py-3 rounded-lg border border-slate-700/50">
            <div className="w-9 h-9 rounded-full bg-blue-600 flex items-center justify-center font-bold text-lg shadow-sm">
              {currentUser.username.charAt(0).toUpperCase()}
            </div>
            <div className="flex-1 overflow-hidden">
              <p className="text-sm font-bold truncate text-white">{currentUser.username}</p>
              <p className="text-[10px] text-blue-400 uppercase tracking-wider font-semibold truncate">Administrator</p>
            </div>
            <button onClick={onLogout} className="p-2 text-slate-400 hover:text-white hover:bg-slate-700 rounded-lg transition-colors">
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-auto bg-slate-50/50">
        <div className="p-8 max-w-7xl mx-auto">
          {loading && !selectedUserId ? (
            <div className="flex items-center justify-center h-[60vh]">
              <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600"></div>
            </div>
          ) : (
            <>
              {activeTab === 'overview' && overview && (
                <div className="space-y-8 animate-in fade-in duration-300">
                  <header>
                    <h2 className="text-3xl font-bold text-slate-900 tracking-tight">Dashboard Overview</h2>
                    <p className="text-slate-500 mt-1">Real-time metrics and system activity</p>
                  </header>
                  
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                    <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200/60 hover:shadow-md transition-shadow">
                      <div className="flex items-center justify-between mb-4">
                        <h3 className="text-sm font-semibold text-slate-500 uppercase tracking-wider">Total Users</h3>
                        <div className="p-2 bg-blue-50 rounded-lg"><Users className="w-5 h-5 text-blue-600" /></div>
                      </div>
                      <p className="text-4xl font-bold text-slate-900">{overview.total_users}</p>
                    </div>
                    
                    <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200/60 hover:shadow-md transition-shadow">
                      <div className="flex items-center justify-between mb-4">
                        <h3 className="text-sm font-semibold text-slate-500 uppercase tracking-wider">Active (24h)</h3>
                        <div className="p-2 bg-emerald-50 rounded-lg"><Activity className="w-5 h-5 text-emerald-600" /></div>
                      </div>
                      <p className="text-4xl font-bold text-slate-900">{overview.active_users}</p>
                    </div>

                    <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200/60 hover:shadow-md transition-shadow">
                      <div className="flex items-center justify-between mb-4">
                        <h3 className="text-sm font-semibold text-slate-500 uppercase tracking-wider">Total Queries</h3>
                        <div className="p-2 bg-purple-50 rounded-lg"><MessageSquare className="w-5 h-5 text-purple-600" /></div>
                      </div>
                      <p className="text-4xl font-bold text-slate-900">{overview.total_queries}</p>
                    </div>

                    <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200/60 hover:shadow-md transition-shadow">
                      <div className="flex items-center justify-between mb-4">
                        <h3 className="text-sm font-semibold text-slate-500 uppercase tracking-wider">Queries Today</h3>
                        <div className="p-2 bg-amber-50 rounded-lg"><Clock className="w-5 h-5 text-amber-600" /></div>
                      </div>
                      <p className="text-4xl font-bold text-slate-900">{overview.queries_today}</p>
                    </div>
                  </div>

                  <div className="bg-white rounded-2xl shadow-sm border border-slate-200/60 overflow-hidden">
                    <div className="p-6 border-b border-slate-100 bg-white">
                      <h3 className="font-bold text-slate-900 text-lg">Recent System Activity</h3>
                    </div>
                    <div className="divide-y divide-slate-50">
                      {activityLogs.slice(0, 8).map((log: any) => (
                        <div key={log.id} className="p-4 flex items-start gap-4 hover:bg-slate-50/80 transition-colors">
                          <div className={`mt-1 p-2.5 rounded-xl ${
                            log.action.includes('LOGIN') ? 'bg-emerald-100/50 text-emerald-600' :
                            log.action.includes('QUERY') ? 'bg-blue-100/50 text-blue-600' :
                            log.action.includes('LOGOUT') ? 'bg-slate-100 text-slate-600' :
                            'bg-purple-100/50 text-purple-600'
                          }`}>
                            <Activity className="w-4 h-4" />
                          </div>
                          <div>
                            <p className="text-sm text-slate-700">
                              <span className="font-bold text-slate-900">{log.username}</span> performed <span className="font-mono text-xs bg-slate-100 px-1.5 py-0.5 rounded-md text-slate-700 border border-slate-200">{log.action}</span>
                            </p>
                            <p className="text-xs text-slate-400 mt-1.5">{new Date(log.created_at).toLocaleString()}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {activeTab === 'users' && !selectedUserId && (
                <div className="space-y-6 animate-in fade-in duration-300">
                  <header>
                    <h2 className="text-3xl font-bold text-slate-900 tracking-tight">User Management</h2>
                    <p className="text-slate-500 mt-1">Manage and view user accounts</p>
                  </header>
                  <div className="bg-white rounded-2xl shadow-sm border border-slate-200/60 overflow-hidden">
                    <table className="w-full text-left border-collapse">
                      <thead>
                        <tr className="bg-slate-50/80 border-b border-slate-200/80">
                          <th className="p-5 text-xs font-bold text-slate-500 uppercase tracking-widest">User</th>
                          <th className="p-5 text-xs font-bold text-slate-500 uppercase tracking-widest">Role</th>
                          <th className="p-5 text-xs font-bold text-slate-500 uppercase tracking-widest">Joined</th>
                          <th className="p-5 text-xs font-bold text-slate-500 uppercase tracking-widest">Last Login</th>
                          <th className="p-5 text-xs font-bold text-slate-500 uppercase tracking-widest">Queries</th>
                          <th className="p-5 text-xs font-bold text-slate-500 uppercase tracking-widest"></th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-100">
                        {users.map(user => (
                          <tr key={user.id} className="hover:bg-blue-50/30 transition-colors group">
                            <td className="p-5">
                              <div className="flex items-center gap-4">
                                <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-100 to-indigo-100 text-blue-700 border border-blue-200/50 flex items-center justify-center font-bold shadow-sm">
                                  {user.username.charAt(0).toUpperCase()}
                                </div>
                                <div>
                                  <p className="font-bold text-slate-900 group-hover:text-blue-700 transition-colors">{user.username}</p>
                                  <p className="text-xs text-slate-500">{user.email}</p>
                                </div>
                              </div>
                            </td>
                            <td className="p-5">
                              <span className="px-2.5 py-1 bg-slate-100 text-slate-700 text-xs font-semibold rounded-md border border-slate-200/60">
                                {user.role}
                              </span>
                            </td>
                            <td className="p-5 text-sm text-slate-600 font-medium">
                              {new Date(user.created_at).toLocaleDateString()}
                            </td>
                            <td className="p-5 text-sm text-slate-500">
                              {user.last_login ? new Date(user.last_login).toLocaleString() : 'Never'}
                            </td>
                            <td className="p-5 text-sm text-slate-700 font-bold">
                              {user.queries_count}
                            </td>
                            <td className="p-5 text-right">
                              <button 
                                onClick={() => loadUserDetail(user.id)}
                                className="p-2 text-slate-400 hover:text-blue-600 hover:bg-blue-50 rounded-xl transition-all"
                              >
                                <ChevronRight className="w-5 h-5" />
                              </button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {activeTab === 'users' && selectedUserId && selectedUserDetail && (
                <div className="space-y-6 animate-in slide-in-from-right-8 duration-300">
                  <div className="flex items-center gap-5">
                    <button 
                      onClick={() => setSelectedUserId(null)}
                      className="p-2.5 bg-white border border-slate-200 shadow-sm rounded-xl hover:bg-slate-50 hover:text-blue-600 transition-colors"
                    >
                      <ArrowLeft className="w-5 h-5 text-slate-600" />
                    </button>
                    <div>
                      <h2 className="text-3xl font-bold text-slate-900 tracking-tight">{selectedUserDetail.username}'s Profile</h2>
                      <p className="text-slate-500 font-medium">{selectedUserDetail.email}</p>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200/60 h-fit">
                      <h3 className="font-bold text-slate-900 mb-6 text-lg">Account Details</h3>
                      <div className="space-y-4 text-sm">
                        <div className="flex justify-between border-b border-slate-100 pb-3">
                          <span className="text-slate-500 font-medium">Role</span>
                          <span className="font-bold text-slate-900">{selectedUserDetail.role}</span>
                        </div>
                        <div className="flex justify-between border-b border-slate-100 pb-3">
                          <span className="text-slate-500 font-medium">Joined</span>
                          <span className="font-bold text-slate-900">{new Date(selectedUserDetail.created_at).toLocaleDateString()}</span>
                        </div>
                        <div className="flex justify-between border-b border-slate-100 pb-3">
                          <span className="text-slate-500 font-medium">Status</span>
                          <span className={`font-bold px-2 py-0.5 rounded-md ${selectedUserDetail.is_active ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' : 'bg-red-50 text-red-700 border border-red-200'}`}>
                            {selectedUserDetail.is_active ? 'ACTIVE' : 'DISABLED'}
                          </span>
                        </div>
                      </div>
                    </div>

                    <div className="md:col-span-2 bg-white rounded-2xl shadow-sm border border-slate-200/60 overflow-hidden flex flex-col h-[600px]">
                      <div className="p-5 border-b border-slate-100 bg-white">
                        <h3 className="font-bold text-slate-900 text-lg flex items-center gap-2">
                          <MessageSquare className="w-5 h-5 text-blue-600" />
                          Query History <span className="bg-blue-100 text-blue-700 py-0.5 px-2 rounded-full text-xs">{selectedUserDetail.queries_count}</span>
                        </h3>
                      </div>
                      <div className="flex-1 overflow-y-auto p-5 space-y-4 bg-slate-50/50">
                        {selectedUserQueries.length === 0 ? (
                          <div className="flex flex-col items-center justify-center h-full text-slate-400 space-y-3">
                            <MessageSquare className="w-12 h-12 text-slate-200" />
                            <p>No queries recorded yet.</p>
                          </div>
                        ) : (
                          selectedUserQueries.map(q => (
                            <div key={q.id} className="bg-white p-5 rounded-xl border border-slate-200/60 shadow-sm hover:shadow-md transition-shadow">
                              <div className="flex items-center justify-between mb-3">
                                <span className="text-xs font-bold uppercase tracking-wider bg-indigo-50 text-indigo-700 border border-indigo-100 px-2.5 py-1 rounded-md">{q.language}</span>
                                <span className="text-xs text-slate-400 font-medium">{new Date(q.created_at).toLocaleString()}</span>
                              </div>
                              <p className="text-[15px] text-slate-800 mb-4 font-medium leading-relaxed">"{q.query}"</p>
                              
                              <div className="flex items-center justify-between mt-4 pt-3 border-t border-slate-100">
                                {q.latitude && q.longitude ? (
                                  <p className="text-xs text-slate-500 font-medium flex items-center gap-1.5 bg-slate-50 px-2 py-1 rounded-md border border-slate-100">
                                    <span>📍</span> {q.latitude.toFixed(4)}°N, {q.longitude.toFixed(4)}°E
                                  </p>
                                ) : <div />}
                                <div className={`text-xs font-bold flex items-center gap-1.5 ${q.response_status === 'SUCCESS' ? 'text-emerald-600' : 'text-red-600'}`}>
                                  {q.response_status === 'SUCCESS' ? <div className="w-1.5 h-1.5 rounded-full bg-emerald-500" /> : <div className="w-1.5 h-1.5 rounded-full bg-red-500" />}
                                  {q.response_status}
                                </div>
                              </div>
                            </div>
                          ))
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {activeTab === 'activity' && (
                <div className="space-y-6 animate-in fade-in duration-300">
                  <header>
                    <h2 className="text-3xl font-bold text-slate-900 tracking-tight">System Activity Logs</h2>
                    <p className="text-slate-500 mt-1">Audit trail of all system events</p>
                  </header>
                  <div className="bg-white rounded-2xl shadow-sm border border-slate-200/60 overflow-hidden">
                    <table className="w-full text-left border-collapse">
                      <thead>
                        <tr className="bg-slate-50/80 border-b border-slate-200/80">
                          <th className="p-5 text-xs font-bold text-slate-500 uppercase tracking-widest">Time</th>
                          <th className="p-5 text-xs font-bold text-slate-500 uppercase tracking-widest">User</th>
                          <th className="p-5 text-xs font-bold text-slate-500 uppercase tracking-widest">Action</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-100">
                        {activityLogs.map(log => (
                          <tr key={log.id} className="hover:bg-slate-50 transition-colors">
                            <td className="p-5 text-sm text-slate-500 font-medium">
                              {new Date(log.created_at).toLocaleString()}
                            </td>
                            <td className="p-5 text-sm font-bold text-slate-900">
                              {log.username}
                            </td>
                            <td className="p-5">
                              <span className="font-mono text-xs font-semibold bg-slate-100 border border-slate-200 px-2 py-1 rounded text-slate-700">
                                {log.action}
                              </span>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
};
