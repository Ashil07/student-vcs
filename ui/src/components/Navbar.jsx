import React from 'react';
import { NavLink } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

function Navbar() {
    const { user } = useAuth();

    const navItems = [
        { name: 'Dashboard', path: '/' },
        { name: 'Status', path: '/status' },
        { name: 'Log', path: '/log' },
        { name: 'Commit', path: '/commit' },
        { name: 'Undo', path: '/undo' },
        { name: 'Export', path: '/export' },
        { name: 'Import', path: '/import' },
        { name: 'Visualize Logic', path: '/visualize' },
    ];

    return (
        <nav className="navbar">
            <div className="nav-brand">Student VCS</div>
            <div className="nav-links">
                {navItems.map((item) => (
                    <NavLink
                        key={item.path}
                        to={item.path}
                        className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
                    >
                        {item.name}
                    </NavLink>
                ))}
                <NavLink
                    to="/login"
                    className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
                >
                    {user ? 'Account' : 'Login'}
                </NavLink>
            </div>
        </nav>
    );
}

export default Navbar;
