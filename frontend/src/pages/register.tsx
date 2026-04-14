import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api/api'

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
            await api.register({
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
        <div className="min-h-screen flex items-center justify-center bg-green-50 px-5 font-system">
            <div className="w-full max-w-md bg-white rounded-3xl p-8 border border-gray-300 shadow-lg">

                <div className="text-center mb-7">
                    <h1 className="text-2xl font-black text-gray-900">MzansBuilds</h1>
                    <p className="text-sm text-gray-500 mt-1">Build in public. Ship together.</p>
                </div>

                <h2 className="text-lg font-bold text-gray-900 mb-5">Create Account</h2>

                <form onSubmit={handleRegister} className="flex flex-col gap-3.5">

                    <input
                        className="w-full px-3.5 py-3 rounded-2xl border border-gray-300 bg-gray-50 text-gray-900 text-sm outline-none transition-colors focus:border-green-600 focus:bg-white"
                        type="text"
                        placeholder="Full Name"
                        value={name}
                        onChange={(e) => setName(e.target.value)}
                        required
                    />

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

                    <textarea
                        className="w-full px-3.5 py-3 rounded-2xl border border-gray-300 bg-gray-50 text-gray-900 text-sm outline-none transition-colors focus:border-green-600 focus:bg-white resize-none"
                        placeholder="Bio (optional)"
                        value={bio}
                        onChange={(e) => setBio(e.target.value)}
                        rows={3}
                    />

                    <button className="w-full px-3.5 py-3 rounded-2xl bg-green-600 border-2 border-green-600 text-white font-semibold text-sm cursor-pointer transition-colors hover:bg-green-700" type="submit">
                        Register →
                    </button>
                </form>

                {error && <p className="text-red-500 text-xs mt-1.5 mb-2.5">{error}</p>}
                {success && <p className="text-green-600 text-xs mt-1.5 mb-2.5 font-semibold">{success}</p>}

                <p
                    className="mt-4 text-sm text-center text-gray-500 cursor-pointer hover:text-gray-700 transition-colors"
                    onClick={() => navigate('/')}
                >
                    Already have an account? <span className="font-semibold">Login</span>
                </p>
            </div>
        </div>
    )
}