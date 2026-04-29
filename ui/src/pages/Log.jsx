import React, { useEffect, useState } from 'react';
import { getLog } from '../api';
import CommitCard from '../components/CommitCard';

function Log() {
    const [logs, setLogs] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        async function loadLogs() {
            try {
                const data = await getLog();
                // Assume data returns { logs: [...] } or array of commits.
                setLogs(Array.isArray(data) ? data : data.logs || []);
            } catch (err) {
                setError('Could not connect to backend API');
            } finally {
                setLoading(false);
            }
        }
        loadLogs();
    }, []);

    if (loading) return <div className="center-content"><div className="loader"></div><p style={{ marginTop: '1rem' }}>Loading history...</p></div>;

    return (
        <div className="fade-in">
            <div className="page-header">
                <h1 className="page-title">Commit Log</h1>
                <p className="page-subtitle">Timeline of repository changes</p>
            </div>

            {error && <div className="alert error">{error}</div>}

            <div className="list-container">
                {logs.length === 0 ? (
                    <div className="glass-panel" style={{ color: 'var(--text-secondary)' }}>No commits found.</div>
                ) : (
                    logs.map(log => <CommitCard key={log.id || log.hash} commit={log} />)
                )}
            </div>
        </div>
    );
}

export default Log;
