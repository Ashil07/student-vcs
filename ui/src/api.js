import { supabase, isSupabaseEnabled } from './supabaseClient';

const API = "http://localhost:8000";
const V2 = "http://localhost:8000/v2";

function getToken() {
    const session = JSON.parse(localStorage.getItem('sb-localhost-token') || '{}');
    return session?.access_token || '';
}

function getHeaders() {
    const token = getToken();
    const headers = { "Content-Type": "application/json" };
    if (token) headers["Authorization"] = `Bearer ${token}`;
    return headers;
}

function useCloud() {
    return isSupabaseEnabled() && getToken();
}

export async function getStatus() {
    if (useCloud()) {
        const { data, error } = await supabase
            .from('commits')
            .select('*')
            .order('timestamp', { ascending: false })
            .limit(1);
        if (error) return { error: error.message };
        return {
            branch: 'main',
            commit_id: data?.[0]?.id || null,
            staged: [],
            staged_count: 0,
            new_files: [],
            modified_files: [],
            deleted_files: []
        };
    }
    const res = await fetch(`${API}/status`);
    return res.json();
}

export async function getLog() {
    if (useCloud()) {
        const { data, error } = await supabase
            .from('commits')
            .select('*')
            .order('timestamp', { ascending: false });
        if (error) return { error: error.message };
        return { commits: data || [] };
    }
    const res = await fetch(`${API}/log`);
    return res.json();
}

export async function commit(message) {
    if (useCloud()) {
        const res = await fetch(`${V2}/commit`, {
            method: "POST",
            headers: getHeaders(),
            body: JSON.stringify({ message, repo_name: 'default' })
        });
        return res.json();
    }
    const res = await fetch(`${API}/commit`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message })
    });
    return res.json();
}

export async function undo() {
    if (useCloud()) {
        const res = await fetch(`${V2}/undo`, {
            method: "POST",
            headers: getHeaders()
        });
        return res.json();
    }
    const res = await fetch(`${API}/undo`, { method: "POST" });
    return res.json();
}

export async function exportRepo(filename) {
    if (useCloud()) {
        return { success: false, message: 'Export not yet implemented for cloud mode' };
    }
    const res = await fetch(`${API}/export`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ filename })
    });
    return res.json();
}

export async function importRepo(filename) {
    if (useCloud()) {
        return { success: false, message: 'Import not yet implemented for cloud mode' };
    }
    const res = await fetch(`${API}/import`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ filename })
    });
    return res.json();
}

export async function visualizeAst(filename) {
    const res = await fetch(`${API}/ast`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ file: filename })
    });
    return res.json();
}

export async function initRepo(repoName = 'default') {
    if (useCloud()) {
        const res = await fetch(`${V2}/init`, {
            method: "POST",
            headers: getHeaders(),
            body: JSON.stringify({ repo_name: repoName })
        });
        return res.json();
    }
    const res = await fetch(`${API}/init`, { method: "POST" });
    return res.json();
}

export async function getBranches(repoName = 'default') {
    if (useCloud()) {
        const res = await fetch(`${V2}/branches?repo_name=${repoName}`, {
            headers: getHeaders()
        });
        return res.json();
    }
    const res = await fetch(`${API}/branches`);
    return res.json();
}
