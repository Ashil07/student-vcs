import React, { useState } from 'react';
import { importRepo as importApi } from '../api';
import Button from '../components/Button';

function Import() {
    const [filename, setFilename] = useState('project.vcs');
    const [status, setStatus] = useState({ type: '', text: '' });
    const [isSubmitting, setIsSubmitting] = useState(false);

    const handleImport = async (e) => {
        e.preventDefault();
        if (!filename.trim()) return;

        setIsSubmitting(true);
        setStatus({ type: '', text: '' });

        try {
            const res = await importApi(filename);
            if (res.error) {
                setStatus({ type: 'error', text: '❌ ' + res.error });
            } else {
                setStatus({ type: 'success', text: `✅ Successfully imported from ${filename}` });
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
                <h1 className="page-title">Import Repository</h1>
                <p className="page-subtitle">Restore state from a bundled VCS repository</p>
            </div>

            {status.text && (
                <div className={`alert ${status.type}`}>
                    {status.text}
                </div>
            )}

            <div className="glass-panel" style={{ maxWidth: '500px' }}>
                <form onSubmit={handleImport}>
                    <div className="input-group">
                        <label className="input-label" htmlFor="importFilename">Filename (.vcs archive path)</label>
                        <input
                            id="importFilename"
                            className="input-field"
                            value={filename}
                            onChange={(e) => setFilename(e.target.value)}
                            disabled={isSubmitting}
                        />
                    </div>
                    <Button type="submit" disabled={isSubmitting || !filename.trim()}>
                        {isSubmitting ? 'Importing...' : 'Import'}
                    </Button>
                </form>
            </div>
        </div>
    );
}

export default Import;
