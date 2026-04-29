import React, { useState } from 'react';
import { commit as commitApi } from '../api';
import Button from '../components/Button';

function Commit() {
    const [msg, setMsg] = useState('');
    const [status, setStatus] = useState({ type: '', text: '' });
    const [isSubmitting, setIsSubmitting] = useState(false);

    const handleCommit = async (e) => {
        e.preventDefault();
        if (!msg.trim()) return;

        setIsSubmitting(true);
        setStatus({ type: '', text: '' });

        try {
            const res = await commitApi(msg);
            if (res.error) {
                setStatus({ type: 'error', text: res.error });
            } else {
                setStatus({ type: 'success', text: `✅ Commit created: ${res.hash || ''}` });
                setMsg('');
            }
        } catch (err) {
            setStatus({ type: 'error', text: '❌ Failed to create commit.' });
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <div className="fade-in">
            <div className="page-header">
                <h1 className="page-title">Create Commit</h1>
                <p className="page-subtitle">Save your latest modifications</p>
            </div>

            {status.text && (
                <div className={`alert ${status.type}`}>
                    {status.text}
                </div>
            )}

            <div className="glass-panel" style={{ maxWidth: '500px' }}>
                <form onSubmit={handleCommit}>
                    <div className="input-group">
                        <label className="input-label" htmlFor="commitMessage">Commit Message</label>
                        <input
                            id="commitMessage"
                            type="text"
                            className="input-field"
                            placeholder="e.g. initial commit"
                            value={msg}
                            onChange={(e) => setMsg(e.target.value)}
                            disabled={isSubmitting}
                        />
                    </div>
                    <Button type="submit" disabled={isSubmitting || !msg.trim()}>
                        {isSubmitting ? 'Committing...' : 'Commit Changes'}
                    </Button>
                </form>
            </div>
        </div>
    );
}

export default Commit;
