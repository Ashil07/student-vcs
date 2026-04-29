import React, { useState } from 'react';
import { undo as undoApi } from '../api';
import Button from '../components/Button';

function Undo() {
    const [status, setStatus] = useState({ type: '', text: '' });
    const [isSubmitting, setIsSubmitting] = useState(false);

    const handleUndo = async () => {
        setIsSubmitting(true);
        setStatus({ type: '', text: '' });

        try {
            const res = await undoApi();
            if (res.error) {
                setStatus({ type: 'error', text: '❌ ' + res.error });
            } else {
                setStatus({ type: 'success', text: '✅ Commit undone successfully.' });
            }
        } catch (err) {
            setStatus({ type: 'error', text: '❌ No commits to undo or server error.' });
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <div className="fade-in">
            <div className="page-header">
                <h1 className="page-title">Revert Commit</h1>
                <p className="page-subtitle">Undo the very last snapshot of your project</p>
            </div>

            {status.text && (
                <div className={`alert ${status.type}`}>
                    {status.text}
                </div>
            )}

            <div className="glass-panel" style={{ maxWidth: '400px', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                <p style={{ color: 'var(--text-secondary)' }}>
                    Click the button below to revert the most recent commit. Warning: This action modifies your repository state!
                </p>
                <Button variant="secondary" onClick={handleUndo} disabled={isSubmitting}>
                    {isSubmitting ? 'Undoing...' : 'Undo Last Commit'}
                </Button>
            </div>
        </div>
    );
}

export default Undo;
