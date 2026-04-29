import React, { useState } from 'react';
import { visualizeAst } from '../api';
import Button from '../components/Button';

function Visualize() {
    const [filename, setFilename] = useState('core/index.py');
    const [status, setStatus] = useState({ type: '', text: '' });
    const [astOutput, setAstOutput] = useState(null);
    const [isSubmitting, setIsSubmitting] = useState(false);

    const handleVisualize = async (e) => {
        e.preventDefault();
        if (!filename.trim()) return;

        setIsSubmitting(true);
        setStatus({ type: '', text: '' });
        setAstOutput(null);

        try {
            const res = await visualizeAst(filename);
            if (res.error) {
                setStatus({ type: 'error', text: '❌ ' + res.error });
            } else {
                setAstOutput(Array.isArray(res) ? res : res.ast || []);
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
                <h1 className="page-title">⭐ Visualize Logic</h1>
                <p className="page-subtitle">Peek under the hood securely</p>
            </div>

            {status.text && (
                <div className={`alert ${status.type}`}>
                    {status.text}
                </div>
            )}

            <div style={{ display: 'flex', gap: '2rem', flexWrap: 'wrap' }}>
                <div className="glass-panel" style={{ flex: '1', minWidth: '300px', maxWidth: '500px' }}>
                    <form onSubmit={handleVisualize}>
                        <div className="input-group">
                            <label className="input-label" htmlFor="visualizeFilename">Filename</label>
                            <input
                                id="visualizeFilename"
                                placeholder="e.g. main.py"
                                className="input-field"
                                value={filename}
                                onChange={(e) => setFilename(e.target.value)}
                                disabled={isSubmitting}
                            />
                        </div>
                        <Button type="submit" disabled={isSubmitting || !filename.trim()}>
                            {isSubmitting ? 'Analyzing...' : 'Visualize AST'}
                        </Button>
                    </form>
                </div>

                <div className="glass-panel" style={{ flex: '2', minWidth: '400px' }}>
                    <h3 style={{ marginBottom: '1rem' }}>AST Result:</h3>
                    {astOutput ? (
                        <div className="code-block">
                            {astOutput.length === 0 ? (
                                <div style={{ color: 'var(--text-secondary)' }}>No logical units found.</div>
                            ) : (
                                astOutput.map((node, i) => {
                                    // e.g. "FUNCTION: add_files" or { type: "FUNCTION", name: "add_files", line: 12 }
                                    const textContent = typeof node === 'string'
                                        ? node
                                        : `${node.type || ''}: ${node.name || ''} (line: ${node.line || 'unknown'})`;

                                    return (
                                        <div key={i} className="ast-node">
                                            {textContent}
                                        </div>
                                    );
                                })
                            )}
                        </div>
                    ) : (
                        <p style={{ color: 'var(--text-secondary)' }}>Submit a valid file path to see its execution structure.</p>
                    )}
                </div>
            </div>
        </div>
    );
}

export default Visualize;
