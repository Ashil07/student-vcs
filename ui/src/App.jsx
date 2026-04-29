import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import Navbar from './components/Navbar';
import Dashboard from './pages/Dashboard';
import Status from './pages/Status';
import Log from './pages/Log';
import Commit from './pages/Commit';
import Undo from './pages/Undo';
import Export from './pages/Export';
import Import from './pages/Import';
import Visualize from './pages/Visualize';
import Login from './pages/Login';

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="app-container">
          <Navbar />
          <main className="content-area">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/status" element={<Status />} />
              <Route path="/log" element={<Log />} />
              <Route path="/commit" element={<Commit />} />
              <Route path="/undo" element={<Undo />} />
              <Route path="/export" element={<Export />} />
              <Route path="/import" element={<Import />} />
              <Route path="/visualize" element={<Visualize />} />
              <Route path="/login" element={<Login />} />
            </Routes>
          </main>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
