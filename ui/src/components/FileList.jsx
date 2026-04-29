import React from 'react';

function FileList({ title, files, type }) {
    if (!files || files.length === 0) return null;

    return (
        <div className="list-container" style={{ marginBottom: '1.5rem' }}>
            <h3 style={{ marginBottom: '0.5rem' }}>{title}</h3>
            {files.map((file, idx) => (
                <div key={idx} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <span className={`file-badge ${type}`}>
                        {type === 'new' && '🟢 New'}
                        {type === 'modified' && '🟡 Mod'}
                        {type === 'deleted' && '🔴 Del'}
                    </span>
                    <span>{file}</span>
                </div>
            ))}
        </div>
    );
}

export default FileList;
