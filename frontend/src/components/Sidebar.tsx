import { useEffect, useState } from 'react'
import { FaFire, FaFolder, FaPlus, FaSignOutAlt, FaTrophy, FaUser } from 'react-icons/fa'
import { useLocation, useNavigate } from 'react-router-dom'
import { api } from '../api/api'

export default function Sidebar() {
    const navigate = useNavigate()
    const location = useLocation()
    const [user, setUser] = useState<any>(null)
    const [showDropdown, setShowDropdown] = useState(false)

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

    const isActive = (path: string) => location.pathname === path

    const navItems = [
        { path: '/dashboard', label: 'Live Feed', icon: FaFire },
        { path: '/my-projects', label: 'My Projects', icon: FaFolder },
        { path: '/celebrations', label: 'Wall', icon: FaTrophy },
    ]

    return (
        <div className="w-64 bg-white border-r border-gray-200 h-screen flex flex-col fixed left-0 top-0">
            {/* Logo */}
            <div className="p-6 border-b border-gray-200">
                <h1
                    className="text-2xl font-black text-green-600 cursor-pointer hover:text-green-700 transition-colors"
                    onClick={() => navigate('/dashboard')}
                >
                    MzansiBuilds
                </h1>
                <p className="text-xs text-gray-500 mt-1">Build Public</p>
            </div>

            {/* Navigation */}
            <nav className="flex-1 px-4 py-6 space-y-2">
                {navItems.map(item => {
                    const IconComponent = item.icon
                    return (
                        <button
                            key={item.path}
                            onClick={() => navigate(item.path)}
                            className={`w-full text-left px-4 py-3 rounded-2xl font-medium text-sm transition-colors flex items-center gap-3 ${isActive(item.path)
                                ? 'bg-green-100 text-green-700'
                                : 'text-gray-600 hover:bg-green-50 hover:text-green-600'
                                }`}
                        >
                            <IconComponent className="text-lg" />
                            {item.label}
                        </button>
                    )
                })}

                {/* Create Project Button */}
                <button
                    onClick={() => navigate('/create-project')}
                    className="w-full mt-6 px-4 py-3 rounded-2xl bg-green-600 text-white font-semibold text-sm hover:bg-green-700 transition-colors flex items-center justify-center gap-2"
                >
                    <FaPlus /> New Project
                </button>
            </nav>

            {/* User Profile */}
            <div className="border-t border-gray-200 p-4">
                {user ? (
                    <div className="relative">
                        <button
                            onClick={() => setShowDropdown(!showDropdown)}
                            className="w-full flex items-center gap-3 p-3 rounded-2xl hover:bg-green-50 transition-colors"
                        >
                            <div className="w-10 h-10 rounded-full bg-green-100 text-green-700 flex items-center justify-center font-bold text-sm">
                                {user.name?.charAt(0).toUpperCase() || 'U'}
                            </div>
                            <div className="text-left flex-1 min-w-0">
                                <p className="text-sm font-semibold text-gray-900 truncate">{user.name}</p>
                                <p className="text-xs text-gray-500 truncate">{user.email}</p>
                            </div>
                        </button>

                        {showDropdown && (
                            <div className="absolute bottom-full left-0 right-0 mb-2 bg-white rounded-2xl border border-gray-200 shadow-lg overflow-hidden">
                                <button
                                    onClick={() => { navigate('/profile'); setShowDropdown(false) }}
                                    className="block w-full px-4 py-3 text-left text-sm text-gray-700 hover:bg-green-50 transition-colors flex items-center gap-2"
                                >
                                    <FaUser size={14} /> Profile
                                </button>
                                <button
                                    onClick={handleLogout}
                                    className="block w-full px-4 py-3 text-left text-sm text-red-600 hover:bg-red-50 transition-colors font-medium flex items-center gap-2"
                                >
                                    <FaSignOutAlt size={14} /> Logout
                                </button>
                            </div>
                        )}
                    </div>
                ) : (
                    <p className="text-xs text-gray-500 text-center py-3">Loading...</p>
                )}
            </div>
        </div>
    )
}
