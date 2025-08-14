import React from 'react';

const Debug = () => {
  const envVars = Object.keys(process.env)
    .filter(key => key.startsWith('REACT_APP_'))
    .reduce((obj, key) => {
      obj[key] = process.env[key];
      return obj;
    }, {});

  const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:5000';

  return (
    <div style={{ 
      position: 'fixed', 
      top: 0, 
      right: 0, 
      background: '#000', 
      color: '#fff', 
      padding: '10px',
      fontSize: '12px',
      zIndex: 9999,
      maxWidth: '300px'
    }}>
      <h4>🔧 Debug Info</h4>
      <p><strong>Environment:</strong> {process.env.NODE_ENV}</p>
      <p><strong>API URL:</strong> {apiUrl}</p>
      <p><strong>All REACT_APP_ vars:</strong></p>
      <pre>{JSON.stringify(envVars, null, 2)}</pre>
    </div>
  );
};

export default Debug;
