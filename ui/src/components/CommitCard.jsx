import React from 'react';

function CommitCard({ commit }) {
    // Commit structure expectation:
    // { hash: 'abcd', message: 'xyz', time: '12:30' } 
    // or depending on actual api { id: 'abcd', message: 'xyz', timestamp: '12:30' }
    const hash = commit.hash || commit.id || 'N/A';
    const message = commit.message || 'No message';
    const time = commit.time || commit.timestamp || new Date().toISOString();

    return (
        <div className="glass-panel commit-card">
            <div className="commit-hash">{hash.substring(0, 7)}</div>
            <div className="commit-msg">{message}</div>
            <div className="commit-time">{new Date(time).toLocaleString()}</div>
        </div>
    );
}

export default CommitCard;
