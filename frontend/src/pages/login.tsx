import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api/api'

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
        <div className="min-h-screen flex items-center justify-center bg-green-50 px-5 font-system">
            <div className="w-full max-w-md bg-white rounded-3xl p-8 border border-gray-300 shadow-lg">

                <div className="text-center mb-7">
                    <h1 className="text-2xl font-black text-gray-900"> MzansiBuilds</h1>
                    <p className="text-sm text-gray-500 mt-1">Build in public. Ship together.</p>
                </div>

                <h2 className="text-lg font-bold text-gray-900 mb-5">Login</h2>
                <form onSubmit={handleLogin} className="flex flex-col gap-3.5">
                    <input
                        className="w-full px-3.5 py-3 rounded-2xl border border-gray-300 bg-gray-50 text-gray-900 text-sm outline-none transition-colors focus:border-green-600 focus:bg-white"
                        type="email"
                        placeholder="Email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        required
                    />

                    <input
                        className="w-full px-3.5 py-3 rounded-2xl border border-gray-300 bg-gray-50 text-gray-900 text-sm outline-none transition-colors focus:border-green-600 focus:bg-white"
                        type="password"
                        placeholder="Password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                    />

                    <button className="w-full px-3.5 py-3 rounded-2xl bg-green-600 border-2 border-green-600 text-white font-semibold text-sm cursor-pointer transition-colors hover:bg-green-700" type="submit">
                        Login →
                    </button>
                </form>

                {error && <p className="text-red-500 text-xs mt-1.5 mb-2.5">{error}</p>}

                <p
                    className="mt-4 text-sm text-center text-gray-500 cursor-pointer hover:text-gray-700 transition-colors"
                    onClick={() => navigate('/register')}
                >
                    Don't have an account? <span className="font-semibold">Register</span>
                </p>
            </div>
        </div>
    )
}