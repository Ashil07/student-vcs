import React, { useState } from 'react';
import { exportRepo as exportApi } from '../api';
import Button from '../components/Button';

function Export() {
    const [filename, setFilename] = useState('project.vcs');
    const [status, setStatus] = useState({ type: '', text: '' });
    const [isSubmitting, setIsSubmitting] = useState(false);

    const handleExport = async (e) => {
        e.preventDefault();
        if (!filename.trim()) return;

        setIsSubmitting(true);
        setStatus({ type: '', text: '' });

        try {
            const res = await exportApi(filename);
            if (res.error) {
                setStatus({ type: 'error', text: '❌ ' + res.error });
            } else {
                setStatus({ type: 'success', text: `✅ Export successful to ${filename}` });
            }
        } catch (err) {
            setStatus({ type: 'error', text: '❌ Check server connection.' });
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <div className="fade-in">
            <div className="page-header">
                <h1 className="page-title">Export Repository</h1>
                <p className="page-subtitle">Save a portable copy of the exact state</p>
            </div>

            {status.text && (
                <div className={`alert ${status.type}`}>
                    {status.text}
                </div>
            )}

            <div className="glass-panel" style={{ maxWidth: '500px' }}>
                <form onSubmit={handleExport}>
                    <div className="input-group">
                        <label className="input-label" htmlFor="exportFilename">Filename (.vcs format)</label>
                        <input
                            id="exportFilename"
                            className="input-field"
                            value={filename}
                            onChange={(e) => setFilename(e.target.value)}
                            disabled={isSubmitting}
                        />
                    </div>
                    <Button type="submit" disabled={isSubmitting || !filename.trim()}>
                        {isSubmitting ? 'Exporting...' : 'Export'}
                    </Button>
                </form>
            </div>
        </div>
    );
}

export default Export;
