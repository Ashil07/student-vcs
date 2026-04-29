import React from 'react';

function Button({ children, onClick, type = 'button', variant = 'primary', className = '', disabled = false }) {
    const baseClass = variant === 'secondary' ? 'btn secondary' : 'btn';

    return (
        <button
            type={type}
            className={`${baseClass} ${className}`}
            onClick={onClick}
            disabled={disabled}
            style={{ opacity: disabled ? 0.6 : 1, cursor: disabled ? 'not-allowed' : 'pointer' }}
        >
            {children}
        </button>
    );
}

export default Button;
