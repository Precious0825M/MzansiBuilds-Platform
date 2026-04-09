import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api/api'
import '../styles/auth.css'

export default function Login() {
    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')
    const [error, setError] = useState('')
    const navigate = useNavigate()

    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault()
        setError('')

        try {
            const res = await api.login({ email, password })

            // Save token
            localStorage.setItem('token', res.access_token)

            //redirect after login
            navigate('/dashboard')

        } catch (err: any) {
            setError(err.message)
        }
    }

    return (
        <div className="auth-container">
            <div className="auth-card">

                <div className="auth-logo">
                    <h1> DevLog</h1>
                    <p>Build in public. Ship together.</p>
                </div>

                <h2 className="auth-title">Login</h2>
                <form onSubmit={handleLogin} className="auth-form">
                    <input
                        className="auth-input"
                        type="email"
                        placeholder="Email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        required
                    />

                    <input
                        className="auth-input"
                        type="password"
                        placeholder="Password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                    />

                    <button className="auth-btn" type="submit">
                        Login →
                    </button>
                </form>

                {error && <p className="auth-error">{error}</p>}

                <p
                    className="auth-switch"
                    onClick={() => navigate('/register')}
                >
                    Don’t have an account? <span>Register</span>
                </p>
            </div>
        </div>
    )
}