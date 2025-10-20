import React, { useState, useEffect } from 'react';
import './WaitlistAdmin.css';

const WaitlistAdmin = () => {
  const [waitlist, setWaitlist] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    fetchWaitlist();
  }, [filter]);

  const fetchWaitlist = async () => {
    setLoading(true);
    try {
      const url = filter === 'all' 
        ? 'http://localhost:5000/api/admin/waitlist'
        : `http://localhost:5000/api/admin/waitlist?status=${filter}`;
      
      const response = await fetch(url);
      const data = await response.json();

      if (data.success) {
        setWaitlist(data.waitlist);
        setStats(data.stats);
      }
    } catch (error) {
      console.error('Error fetching waitlist:', error);
    } finally {
      setLoading(false);
    }
  };

  const exportCSV = () => {
    window.open('http://localhost:5000/api/admin/waitlist/export', '_blank');
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString();
  };

  return (
    <div className="waitlist-admin">
      <div className="admin-header">
        <h1>📧 YesChef Waitlist Dashboard</h1>
        <button onClick={exportCSV} className="export-btn">
          📥 Export to CSV
        </button>
      </div>

      {/* Stats Section */}
      {stats && (
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-number">{stats.total}</div>
            <div className="stat-label">Total Signups</div>
          </div>
          <div className="stat-card">
            <div className="stat-number">{stats.pending}</div>
            <div className="stat-label">Pending</div>
          </div>
          <div className="stat-card">
            <div className="stat-number">{stats.invited}</div>
            <div className="stat-label">Invited</div>
          </div>
          <div className="stat-card">
            <div className="stat-number">{stats.ios || 0}</div>
            <div className="stat-label">iOS</div>
          </div>
          <div className="stat-card">
            <div className="stat-number">{stats.android || 0}</div>
            <div className="stat-label">Android</div>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="filters">
        <button 
          className={filter === 'all' ? 'active' : ''}
          onClick={() => setFilter('all')}
        >
          All
        </button>
        <button 
          className={filter === 'pending' ? 'active' : ''}
          onClick={() => setFilter('pending')}
        >
          Pending
        </button>
        <button 
          className={filter === 'invited' ? 'active' : ''}
          onClick={() => setFilter('invited')}
        >
          Invited
        </button>
      </div>

      {/* Waitlist Table */}
      <div className="waitlist-table-container">
        {loading ? (
          <div className="loading">Loading...</div>
        ) : (
          <table className="waitlist-table">
            <thead>
              <tr>
                <th>Email</th>
                <th>Source</th>
                <th>Platform</th>
                <th>Signup Date</th>
                <th>Status</th>
                <th>IP Address</th>
              </tr>
            </thead>
            <tbody>
              {waitlist.map((entry) => (
                <tr key={entry.id}>
                  <td className="email-cell">{entry.email}</td>
                  <td>{entry.source}</td>
                  <td>{entry.platform_preference || '—'}</td>
                  <td>{formatDate(entry.signup_date)}</td>
                  <td>
                    <span className={`status-badge status-${entry.status}`}>
                      {entry.status}
                    </span>
                  </td>
                  <td className="ip-cell">{entry.ip_address}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}

        {!loading && waitlist.length === 0 && (
          <div className="empty-state">
            <p>No waitlist signups yet.</p>
            <p>Share your landing page to start collecting emails!</p>
          </div>
        )}
      </div>

      {/* Quick Actions */}
      <div className="quick-actions">
        <h3>Quick Actions</h3>
        <div className="action-buttons">
          <button onClick={() => alert('Send invite emails feature coming soon!')}>
            📧 Send Invites to Pending
          </button>
          <button onClick={() => alert('Google Sheets sync coming soon!')}>
            📊 Sync to Google Sheets
          </button>
          <button onClick={() => alert('TestFlight integration coming soon!')}>
            ✈️ Add to TestFlight
          </button>
        </div>
      </div>
    </div>
  );
};

export default WaitlistAdmin;
