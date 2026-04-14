import { Navigate, Route, Routes } from 'react-router-dom'
import ProtectedRoute from './components/ProtectedRoute'
import Celebrations from './pages/celebrations'
import Collaborations from './pages/collaborations'
import CreateProject from './pages/create-project'
import Dashboard from './pages/dashboard'
import Login from './pages/login'
import MyProjects from './pages/my-projects'
import Profile from './pages/profile'
import ProjectDetail from './pages/project-detail'
import Register from './pages/register'

function App() {
  return (
    <Routes>
      {/* Auth Pages */}
      <Route path="/" element={<Login />} />
      <Route path="/register" element={<Register />} />

      {/* Protected Pages */}
      <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
      <Route path="/my-projects" element={<ProtectedRoute><MyProjects /></ProtectedRoute>} />
      <Route path="/create-project" element={<ProtectedRoute><CreateProject /></ProtectedRoute>} />
      <Route path="/project/:id" element={<ProtectedRoute><ProjectDetail /></ProtectedRoute>} />
      <Route path="/celebrations" element={<ProtectedRoute><Celebrations /></ProtectedRoute>} />
      <Route path="/collaborations" element={<ProtectedRoute><Collaborations /></ProtectedRoute>} />
      <Route path="/profile" element={<ProtectedRoute><Profile /></ProtectedRoute>} />

      {/* Fallback */}
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  )
}

export default App