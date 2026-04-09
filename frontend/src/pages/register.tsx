import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api/api'
import '../styles/auth.css'

export default function Register() {
    const [name, setName] = useState('')
    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')
    const [bio, setBio] = useState('')
    const [error, setError] = useState('')
    const [success, setSuccess] = useState('')
    const navigate = useNavigate()

    const handleRegister = async (e: React.FormEvent) => {
        e.preventDefault()
        setError('')
        setSuccess('')

        try {
            const res = await api.register({
                name,
                email,
                password,
                bio,
            })

            setSuccess('Account created successfully!')

            // redirect to login after short delay
            setTimeout(() => navigate('/'), 1500)

        } catch (err: any) {
            setError(err.message)
        }
    }

    return (
        <div className="auth-container">
            <div className="auth-card">

                <div className="auth-logo">
                    <h1> MzansBuilds </h1>
                    <p>Build in public. Ship together.</p>
                </div>

                <h2 className="auth-title">Create Account</h2>

                <form onSubmit={handleRegister} className="auth-form">

                    <input
                        className="auth-input"
                        type="text"
                        placeholder="Full Name"
                        value={name}
                        onChange={(e) => setName(e.target.value)}
                        required
                    />

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

                    <textarea
                        className="auth-input"
                        placeholder="Bio (optional)"
                        value={bio}
                        onChange={(e) => setBio(e.target.value)}
                        rows={3}
                    />

                    <button className="auth-btn" type="submit">
                        Register →
                    </button>
                </form>

                {error && <p className="auth-error">{error}</p>}
                {success && <p className="auth-success">{success}</p>}

                <p
                    className="auth-switch"
                    onClick={() => navigate('/')}
                >
                    Already have an account? <span>Login</span>
                </p>
            </div>
        </div>
    )
}