import React from 'react';
import { Link } from 'react-router-dom';

function Dashboard() {
    const cards = [
        { title: 'Status', desc: 'Check file changes and status', path: '/status' },
        { title: 'Log', desc: 'View commit history and timeline', path: '/log' },
        { title: 'Commit', desc: 'Snapshot your current progress', path: '/commit' },
        { title: 'Undo', desc: 'Revert your last action', path: '/undo' },
        { title: 'Visualize Logic', desc: 'Understand core execution logic', path: '/visualize' },
        { title: 'Export', desc: 'Save your VCS repository', path: '/export' },
        { title: 'Import', desc: 'Load a VCS repository', path: '/import' },
    ];

    return (
        <div className="fade-in">
            <div className="page-header">
                <h1 className="page-title">Welcome to Student VCS</h1>
                <p className="page-subtitle">Central navigation dashboard</p>
            </div>

            <div className="dashboard-grid">
                {cards.map((c) => (
                    <Link to={c.path} key={c.path} className="glass-panel dashboard-card">
                        <div className="dashboard-card-title">{c.title}</div>
                        <div className="dashboard-card-desc">{c.desc}</div>
                    </Link>
                ))}
            </div>
        </div>
    );
}

export default Dashboard;
