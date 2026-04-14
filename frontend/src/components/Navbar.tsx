import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api/api'

export default function Navbar() {
    const navigate = useNavigate()
    const [user, setUser] = useState<any>(null)
    const [showMenu, setShowMenu] = useState(false)

    useEffect(() => {
        const loadUser = async () => {
            try {
                const data = await api.getMe()
                setUser(data)
            } catch (err) {
                console.error('Failed to load user')
            }
        }
        loadUser()
    }, [])

    const handleLogout = () => {
        localStorage.removeItem('token')
        navigate('/')
    }

    return (
        <nav className="bg-white border-b border-gray-200 sticky top-0 z-40">
            <div className="max-w-7xl mx-auto px-6 py-3 flex justify-between items-center">
                <div className="flex items-center gap-8">
                    <h1 className="text-xl font-black text-gray-900 cursor-pointer" onClick={() => navigate('/dashboard')}>
                        MzansBuilds
                    </h1>
                    <div className="hidden md:flex gap-6">
                        <button onClick={() => navigate('/dashboard')} className="text-sm font-medium text-gray-600 hover:text-green-600 transition-colors">Projects</button>
                        <button onClick={() => navigate('/celebrations')} className="text-sm font-medium text-gray-600 hover:text-green-600 transition-colors">Shipped</button>
                        <button onClick={() => navigate('/collaborations')} className="text-sm font-medium text-gray-600 hover:text-green-600 transition-colors">Collabs</button>
                    </div>
                </div>

                <div className="flex items-center gap-4">
                    <button
                        onClick={() => navigate('/create-project')}
                        className="px-4 py-2 rounded-2xl bg-green-600 text-white text-sm font-semibold hover:bg-green-700 transition-colors"
                    >
                        + New Project
                    </button>

                    <div className="relative">
                        <button
                            onClick={() => setShowMenu(!showMenu)}
                            className="w-10 h-10 rounded-full bg-green-100 flex items-center justify-center text-green-700 font-bold hover:bg-green-200 transition-colors"
                        >
                            {user?.name?.charAt(0).toUpperCase() || 'U'}
                        </button>

                        {showMenu && (
                            <div className="absolute right-0 mt-2 bg-white rounded-2xl border border-gray-200 shadow-lg overflow-hidden">
                                <button onClick={() => { navigate('/profile'); setShowMenu(false) }} className="block w-full px-4 py-3 text-left text-sm text-gray-700 hover:bg-green-50 transition-colors">Profile</button>
                                <button onClick={handleLogout} className="block w-full px-4 py-3 text-left text-sm text-red-600 hover:bg-red-50 transition-colors font-medium">Logout</button>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </nav>
    )
}
