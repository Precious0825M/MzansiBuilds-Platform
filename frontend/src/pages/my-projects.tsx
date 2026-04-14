import { useEffect, useState } from 'react'
import { FaExclamationTriangle, FaFolder } from 'react-icons/fa'
import { useNavigate } from 'react-router-dom'
import { api } from '../api/api'
import Layout from '../components/Layout'

export default function MyProjects() {
    const navigate = useNavigate()
    const [userProjects, setUserProjects] = useState<any[]>([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState('')

    useEffect(() => {
        const loadUserData = async () => {
            try {
                setLoading(true)
                const userData = await api.getMe()

                // Load all projects
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

    return (
        <Layout>
            <div className="max-w-6xl mx-auto">
                <div className="mb-10">
                    <h1 className="text-4xl font-black text-gray-900 mb-2 flex items-center gap-3">
                        <FaFolder className="text-amber-500" size={32} />
                        My Projects
                    </h1>
                    <p className="text-gray-600">Your building journey</p>
                </div>

                {loading ? (
                    <div className="text-center py-12">
                        <p className="text-gray-500 font-medium">Loading projects...</p>
                    </div>
                ) : error ? (
                    <div className="bg-red-50 border-2 border-red-200 rounded-2xl p-6">
                        <p className="text-red-700 font-medium flex items-center justify-center gap-2">
                            <FaExclamationTriangle /> {error}
                        </p>
                    </div>
                ) : userProjects.length > 0 ? (
                    <div className="space-y-6">
                        {userProjects.map(project => (
                            <div
                                key={project.proj_id}
                                onClick={() => navigate(`/project/${project.proj_id}`)}
                                className="bg-white rounded-2xl p-6 border border-gray-200 hover:shadow-lg hover:scale-105 cursor-pointer transition-transform"
                            >
                                <div className="flex justify-between items-start mb-4">
                                    <div className="flex-1">
                                        <h3 className="text-2xl font-black text-gray-900">{project.title}</h3>
                                        <p className="text-gray-600 mt-2">{project.description}</p>
                                    </div>
                                    <div className="ml-4">
                                        <span className={`px-4 py-2 rounded-full text-sm font-bold whitespace-nowrap ${project.stage === 'Planning' ? 'bg-blue-100 text-blue-700' :
                                            project.stage === 'Development' ? 'bg-yellow-100 text-yellow-700' :
                                                project.stage === 'Testing' ? 'bg-green-100 text-green-700' :
                                                    'bg-purple-100 text-purple-700'
                                            }`}>
                                            {project.stage}
                                        </span>
                                    </div>
                                </div>

                                <div className="flex items-center justify-between pt-4 border-t border-gray-200">
                                    <div className="flex flex-wrap gap-2">
                                        {project.support_needed && (
                                            <span className="px-3 py-1 bg-green-50 border border-green-300 rounded-2xl text-xs font-semibold text-green-700">
                                                Looking for: {project.support_needed}
                                            </span>
                                        )}
                                    </div>
                                    <button
                                        onClick={(e) => { e.stopPropagation(); navigate(`/project/${project.proj_id}`); }}
                                        className="px-4 py-2 rounded-2xl bg-green-600 text-white text-sm font-semibold hover:bg-green-700 transition-colors"
                                    >
                                        View →
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                ) : (
                    <div className="bg-white rounded-2xl p-12 border border-gray-200 text-center">
                        <p className="text-gray-500 font-medium mb-3 text-lg">No projects yet</p>
                        <p className="text-gray-400 text-sm mb-6">Start building something amazing today!</p>
                        <button
                            onClick={() => navigate('/create-project')}
                            className="px-6 py-3 bg-green-600 text-white rounded-2xl text-sm font-semibold hover:bg-green-700 transition-colors"
                        >
                            + Create Your First Project
                        </button>
                    </div>
                )}
            </div>
        </Layout>
    )
}
