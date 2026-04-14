import { useEffect, useState } from 'react'
import { FaExclamationTriangle } from 'react-icons/fa'
import { useNavigate } from 'react-router-dom'
import { api } from '../api/api'
import Layout from '../components/Layout'

export default function Profile() {
    const navigate = useNavigate()
    const [user, setUser] = useState<any>(null)
    const [userProjects, setUserProjects] = useState<any[]>([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState('')
    const [editMode, setEditMode] = useState(false)
    const [name, setName] = useState('')
    const [bio, setBio] = useState('')
    const [saving, setSaving] = useState(false)

    useEffect(() => {
        const loadUserData = async () => {
            try {
                setLoading(true)
                const userData = await api.getMe()
                setUser(userData)
                setName(userData.name)
                setBio(userData.bio || '')

                // Load user's projects
                const projects = await api.getProjects()
                const myProjects = projects.filter((p: any) => p.user_id === userData.user_id)
                setUserProjects(myProjects)
            } catch (err: any) {
                setError(err.message)
            } finally {
                setLoading(false)
            }
        }
        loadUserData()
    }, [])

    const handleSaveProfile = async () => {
        if (!name.trim()) {
            alert('Name is required')
            return
        }

        try {
            setSaving(true)
            // Note: You may need to add an update endpoint to your backend
            setUser({ ...user, name, bio })
            setEditMode(false)
        } catch (err: any) {
            alert('Failed to save: ' + err.message)
        } finally {
            setSaving(false)
        }
    }

    if (loading) {
        return (
            <Layout>
                <div className="max-w-4xl mx-auto text-center">
                    <p className="text-gray-500 font-medium">Loading profile...</p>
                </div>
            </Layout>
        )
    }

    if (error || !user) {
        return (
            <Layout>
                <div className="max-w-4xl mx-auto">
                    <div className="bg-red-50 border-2 border-red-200 rounded-2xl p-6 text-center">
                        <p className="text-red-700 font-medium flex items-center justify-center gap-2">
                            <FaExclamationTriangle /> {error || 'Failed to load profile'}
                        </p>
                    </div>
                </div>
            </Layout>
        )
    }

    return (
        <Layout>
            <div className="max-w-4xl mx-auto">
                {/* Profile Card */}
                <div className="bg-white rounded-3xl p-8 border border-gray-300 mb-8">
                    <div className="flex items-center gap-6 mb-6">
                        <div className="w-24 h-24 rounded-full bg-green-100 text-green-700 flex items-center justify-center text-4xl font-bold">
                            {user.name?.charAt(0).toUpperCase() || 'U'}
                        </div>
                        <div className="flex-1">
                            {editMode ? (
                                <div className="space-y-3">
                                    <input
                                        type="text"
                                        value={name}
                                        onChange={(e) => setName(e.target.value)}
                                        className="w-full px-4 py-2 rounded-2xl border border-gray-300 bg-gray-50 text-gray-900 font-bold text-2xl outline-none transition-colors focus:border-green-600 focus:bg-white"
                                    />
                                    <textarea
                                        value={bio}
                                        onChange={(e) => setBio(e.target.value)}
                                        placeholder="Tell us about yourself..."
                                        rows={3}
                                        className="w-full px-4 py-2 rounded-2xl border border-gray-300 bg-gray-50 text-gray-900 text-sm outline-none transition-colors focus:border-green-600 focus:bg-white resize-none"
                                    />
                                </div>
                            ) : (
                                <div>
                                    <h1 className="text-3xl font-black text-gray-900 mb-2">{user.name}</h1>
                                    <p className="text-gray-600">{user.bio || 'No bio yet'}</p>
                                    <p className="text-sm text-gray-500 mt-3">{user.email}</p>
                                </div>
                            )}
                        </div>
                    </div>

                    <div className="border-t border-gray-200 pt-6 flex gap-3">
                        {editMode ? (
                            <>
                                <button
                                    onClick={handleSaveProfile}
                                    disabled={saving}
                                    className="flex-1 px-4 py-3 rounded-2xl bg-green-600 text-white font-semibold text-sm hover:bg-green-700 transition-colors disabled:opacity-60"
                                >
                                    {saving ? 'Saving...' : 'Save Changes'}
                                </button>
                                <button
                                    onClick={() => {
                                        setEditMode(false)
                                        setName(user.name)
                                        setBio(user.bio || '')
                                    }}
                                    className="flex-1 px-4 py-3 rounded-2xl border border-gray-300 text-gray-700 font-semibold text-sm hover:bg-gray-50 transition-colors"
                                >
                                    Cancel
                                </button>
                            </>
                        ) : (
                            <button
                                onClick={() => setEditMode(true)}
                                className="flex-1 px-4 py-3 rounded-2xl bg-green-600 text-white font-semibold text-sm hover:bg-green-700 transition-colors"
                            >
                                Edit Profile
                            </button>
                        )}
                    </div>
                </div>

                {/* My Projects */}
                <div>
                    <h2 className="text-2xl font-black text-gray-900 mb-6">My Projects</h2>

                    {userProjects.length > 0 ? (
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            {userProjects.map(project => (
                                <div
                                    key={project.proj_id}
                                    onClick={() => navigate(`/project/${project.proj_id}`)}
                                    className="bg-white rounded-2xl p-6 border border-gray-200 hover:shadow-lg hover:scale-105 cursor-pointer transition-transform"
                                >
                                    <div className="flex justify-between items-start mb-3">
                                        <h3 className="text-lg font-bold text-gray-900 flex-1">{project.title}</h3>
                                        <span className="px-3 py-1 rounded-full text-xs font-semibold bg-green-100 text-green-700">
                                            {project.stage}
                                        </span>
                                    </div>
                                    <p className="text-sm text-gray-600 line-clamp-2">{project.description}</p>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <div className="bg-white rounded-2xl p-12 border border-gray-200 text-center">
                            <p className="text-gray-500 font-medium mb-3">No projects yet</p>
                            <button
                                onClick={() => navigate('/create-project')}
                                className="px-4 py-2 bg-green-600 text-white rounded-2xl text-sm font-semibold hover:bg-green-700"
                            >
                                Create Your First Project
                            </button>
                        </div>
                    )}
                </div>
            </div>
        </Layout>
    )
}
