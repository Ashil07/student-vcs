import React, { useEffect, useState } from 'react';
import { getStatus } from '../api';
import FileList from '../components/FileList';

function Status() {
    const [status, setStatus] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        async function loadStatus() {
            try {
                const data = await getStatus();
                setStatus(data);
            } catch (err) {
                setError('Could not connect to backend API');
            } finally {
                setLoading(false);
            }
        }
        loadStatus();
    }, []);

    if (loading) return <div className="center-content"><div className="loader"></div><p style={{ marginTop: '1rem' }}>Loading status...</p></div>;

    return (
        <div className="fade-in">
            <div className="page-header">
                <h1 className="page-title">Repository Status</h1>
                <p className="page-subtitle">Track your modifications</p>
            </div>

            {error && <div className="alert error">{error}</div>}

            {status && (
                <div className="glass-panel">
                    <FileList title="🟢 New Files" files={status.new_files} type="new" />
                    <FileList title="🟡 Modified Files" files={status.modified_files} type="modified" />
                    <FileList title="🔴 Deleted Files" files={status.deleted_files} type="deleted" />

                    {(!status.new_files?.length && !status.modified_files?.length && !status.deleted_files?.length) &&
                        <p style={{ color: 'var(--text-secondary)' }}>No changes detected in working directory.</p>
                    }
                </div>
            )}
        </div>
    );
}

export default Status;
