import React, { useState, useEffect } from 'react';
import './DebugReportViewer.css';

const DebugReportViewer = () => {
  const [systemInfo, setSystemInfo] = useState(null);
  const [logs, setLogs] = useState([]);
  const [errors, setErrors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('system');

  useEffect(() => {
    fetchSystemInfo();
    fetchLogs();
    fetchErrors();
  }, []);

  const fetchSystemInfo = async () => {
    try {
      // Get system info from browser
      const info = {
        browser: navigator.userAgent,
        platform: navigator.platform,
        language: navigator.language,
        onLine: navigator.onLine,
        cookiesEnabled: navigator.cookieEnabled,
        screenResolution: `${window.screen.width}x${window.screen.height}`,
        viewportSize: `${window.innerWidth}x${window.innerHeight}`,
        timestamp: new Date().toISOString(),
        localStorage: {
          available: typeof(Storage) !== "undefined",
          items: localStorage.length
        },
        react: {
          version: React.version,
          mode: process.env.NODE_ENV
        }
      };

      setSystemInfo(info);
    } catch (error) {
      console.error('Error fetching system info:', error);
    }
  };

  const fetchLogs = () => {
    // Get console logs from localStorage if available
    const storedLogs = JSON.parse(localStorage.getItem('yeschef_logs') || '[]');
    setLogs(storedLogs.slice(-100)); // Last 100 logs
  };

  const fetchErrors = () => {
    // Get error logs from localStorage if available
    const storedErrors = JSON.parse(localStorage.getItem('yeschef_errors') || '[]');
    setErrors(storedErrors.slice(-50)); // Last 50 errors
    setLoading(false);
  };

  const clearLogs = () => {
    localStorage.removeItem('yeschef_logs');
    setLogs([]);
  };

  const clearErrors = () => {
    localStorage.removeItem('yeschef_errors');
    setErrors([]);
  };

  const exportDebugReport = () => {
    const report = {
      timestamp: new Date().toISOString(),
      systemInfo,
      logs,
      errors,
      userAgent: navigator.userAgent
    };

    const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `yeschef-debug-report-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const formatTimestamp = (timestamp) => {
    try {
      return new Date(timestamp).toLocaleString();
    } catch {
      return timestamp;
    }
  };

  return (
    <div className="debug-report-viewer">
      <div className="debug-header">
        <h1>🐛 Debug Report Viewer</h1>
        <button onClick={exportDebugReport} className="export-debug-btn">
          📥 Export Report
        </button>
      </div>

      {/* Tab Navigation */}
      <div className="debug-tabs">
        <button
          className={`debug-tab ${activeTab === 'system' ? 'active' : ''}`}
          onClick={() => setActiveTab('system')}
        >
          💻 System Info
        </button>
        <button
          className={`debug-tab ${activeTab === 'logs' ? 'active' : ''}`}
          onClick={() => setActiveTab('logs')}
        >
          📋 Logs ({logs.length})
        </button>
        <button
          className={`debug-tab ${activeTab === 'errors' ? 'active' : ''}`}
          onClick={() => setActiveTab('errors')}
        >
          ❌ Errors ({errors.length})
        </button>
        <button
          className={`debug-tab ${activeTab === 'network' ? 'active' : ''}`}
          onClick={() => setActiveTab('network')}
        >
          🌐 Network
        </button>
      </div>

      {/* System Info Tab */}
      {activeTab === 'system' && systemInfo && (
        <div className="debug-content">
          <div className="info-section">
            <h3>Browser Information</h3>
            <div className="info-grid">
              <div className="info-item">
                <span className="info-label">User Agent:</span>
                <span className="info-value">{systemInfo.browser}</span>
              </div>
              <div className="info-item">
                <span className="info-label">Platform:</span>
                <span className="info-value">{systemInfo.platform}</span>
              </div>
              <div className="info-item">
                <span className="info-label">Language:</span>
                <span className="info-value">{systemInfo.language}</span>
              </div>
              <div className="info-item">
                <span className="info-label">Online:</span>
                <span className={`info-value ${systemInfo.onLine ? 'online' : 'offline'}`}>
                  {systemInfo.onLine ? '✅ Yes' : '❌ No'}
                </span>
              </div>
              <div className="info-item">
                <span className="info-label">Cookies:</span>
                <span className="info-value">
                  {systemInfo.cookiesEnabled ? '✅ Enabled' : '❌ Disabled'}
                </span>
              </div>
            </div>
          </div>

          <div className="info-section">
            <h3>Display Information</h3>
            <div className="info-grid">
              <div className="info-item">
                <span className="info-label">Screen Resolution:</span>
                <span className="info-value">{systemInfo.screenResolution}</span>
              </div>
              <div className="info-item">
                <span className="info-label">Viewport Size:</span>
                <span className="info-value">{systemInfo.viewportSize}</span>
              </div>
            </div>
          </div>

          <div className="info-section">
            <h3>Application Information</h3>
            <div className="info-grid">
              <div className="info-item">
                <span className="info-label">React Version:</span>
                <span className="info-value">{systemInfo.react.version}</span>
              </div>
              <div className="info-item">
                <span className="info-label">Environment:</span>
                <span className="info-value">{systemInfo.react.mode}</span>
              </div>
              <div className="info-item">
                <span className="info-label">LocalStorage:</span>
                <span className="info-value">
                  {systemInfo.localStorage.available ? 
                    `✅ Available (${systemInfo.localStorage.items} items)` : 
                    '❌ Not Available'}
                </span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Logs Tab */}
      {activeTab === 'logs' && (
        <div className="debug-content">
          <div className="logs-header">
            <h3>Application Logs</h3>
            <button onClick={clearLogs} className="clear-btn">
              🗑️ Clear Logs
            </button>
          </div>
          {logs.length === 0 ? (
            <div className="empty-state">
              <p>No logs available</p>
              <p className="hint">Logs will appear here when the application generates them</p>
            </div>
          ) : (
            <div className="logs-list">
              {logs.map((log, index) => (
                <div key={index} className={`log-entry log-${log.level || 'info'}`}>
                  <span className="log-time">{formatTimestamp(log.timestamp)}</span>
                  <span className="log-level">{log.level || 'INFO'}</span>
                  <span className="log-message">{log.message}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Errors Tab */}
      {activeTab === 'errors' && (
        <div className="debug-content">
          <div className="logs-header">
            <h3>Error Logs</h3>
            <button onClick={clearErrors} className="clear-btn">
              🗑️ Clear Errors
            </button>
          </div>
          {errors.length === 0 ? (
            <div className="empty-state success">
              <p>✅ No errors logged</p>
              <p className="hint">This is good! Your app is running smoothly.</p>
            </div>
          ) : (
            <div className="errors-list">
              {errors.map((error, index) => (
                <div key={index} className="error-entry">
                  <div className="error-header">
                    <span className="error-time">{formatTimestamp(error.timestamp)}</span>
                    <span className="error-type">{error.type || 'Error'}</span>
                  </div>
                  <div className="error-message">{error.message}</div>
                  {error.stack && (
                    <details className="error-stack">
                      <summary>Stack Trace</summary>
                      <pre>{error.stack}</pre>
                    </details>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Network Tab */}
      {activeTab === 'network' && (
        <div className="debug-content">
          <h3>Network Status</h3>
          <div className="network-info">
            <div className="network-status">
              <span className={`status-indicator ${navigator.onLine ? 'online' : 'offline'}`}>
                {navigator.onLine ? '🟢' : '🔴'}
              </span>
              <span className="status-text">
                {navigator.onLine ? 'Connected' : 'Offline'}
              </span>
            </div>
            <div className="info-section">
              <h4>API Endpoints</h4>
              <div className="endpoint-list">
                <div className="endpoint-item">
                  <span className="endpoint-name">Backend API:</span>
                  <span className="endpoint-url">http://localhost:5000</span>
                  <button 
                    className="test-endpoint-btn"
                    onClick={() => fetch('http://localhost:5000/api/direct-test')
                      .then(r => r.json())
                      .then(d => alert(`✅ Backend: ${d.message}`))
                      .catch(e => alert(`❌ Backend Error: ${e.message}`))}
                  >
                    Test
                  </button>
                </div>
              </div>
            </div>
            <div className="info-section">
              <p className="hint">
                💡 Network requests and responses will be logged here in future updates
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DebugReportViewer;
