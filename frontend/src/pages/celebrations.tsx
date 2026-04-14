import { useEffect, useState } from 'react'
import { FaCommentDots, FaRocket, FaStar, FaTrophy, FaUserAstronaut } from 'react-icons/fa'
import { api } from '../api/api'
import Layout from '../components/Layout'

export default function Celebrations() {
    const [celebrations, setCelebrations] = useState<any[]>([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState('')

    useEffect(() => {
        const loadCelebrations = async () => {
            try {
                setLoading(true)
                const data = await api.getCelebrations()
                setCelebrations(data)
            } catch (err: any) {
                setError(err.message)
            } finally {
                setLoading(false)
            }
        }
        loadCelebrations()
    }, [])

    return (
        <Layout>
            <div className="max-w-6xl mx-auto">
                <div className="mb-10">
                    <h1 className="text-4xl font-black text-gray-900 mb-2">
                        <FaTrophy className="text-yellow-500" size={36} />
                        Celebration Wall</h1>
                    <p className="text-gray-600">Celebrate projects that have launched</p>
                </div>

                {loading ? (
                    <div className="text-center py-12">
                        <p className="text-gray-500 font-medium">Loading celebrations...</p>
                    </div>
                ) : error ? (
                    <div className="bg-red-50 border-2 border-red-200 rounded-2xl p-6 text-center">
                        <p className="text-red-700 font-medium"> {error}</p>
                    </div>
                ) : celebrations.length > 0 ? (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {celebrations.map(project => (
                            <div key={project.proj_id} className="bg-white rounded-2xl p-6 border border-gray-200 hover:shadow-lg hover:scale-105 transition-transform flex flex-col">
                                <div className="flex items-start gap-3 mb-4">
                                    <FaRocket className="text-green-500 text-2xl flex-shrink-0 mt-1" />
                                    <h3 className="text-lg font-bold text-gray-900 flex-1">{project.title}</h3>
                                </div>

                                <p className="text-sm text-gray-600 mb-4">{project.description}</p>

                                <div className="bg-green-50 rounded-2xl p-3 mb-4">
                                    <p className="text-xs text-gray-600 mb-1">Launched by</p>
                                    <div className="flex items-center gap-2">
                                        <FaUserAstronaut size={16} />
                                        <div className="w-8 h-8 rounded-full bg-green-100 text-green-700 flex items-center justify-center text-xs font-bold">
                                            {project.name?.charAt(0).toUpperCase() || 'U'}
                                        </div>
                                        <span className="font-semibold text-gray-900">{project.name || 'Unknown'}</span>
                                    </div>
                                </div>

                                {project.total_updates && (
                                    <div className="text-xs text-gray-600 bg-blue-50 rounded-2xl p-3 mb-4">
                                        <FaCommentDots className="text-blue-500" />
                                        <p className="font-semibold text-blue-700">{project.total_updates} updates shared</p>
                                    </div>
                                )}

                                {project.collaborators && project.collaborators.length > 0 && (
                                    <div className="mb-4">
                                        <p className="text-xs font-semibold text-gray-700 mb-2">Collaborators ({project.collaborators.length})</p>
                                        <div className="flex flex-wrap gap-2">
                                            {project.collaborators.map(collab => (
                                                <div key={collab.user_id} className="bg-purple-100 text-purple-700 rounded-full px-3 py-1 text-xs font-medium">
                                                    {collab.name}
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                )}

                                {project.comments && project.comments.length > 0 && (
                                    <div className="space-y-3 mb-4">
                                        <p className="text-xs font-semibold text-gray-700">Recent Comments ({project.comments.length})</p>
                                        <div className="space-y-2 max-h-48 overflow-y-auto">
                                            {project.comments.map(comment => (
                                                <div key={comment.com_id} className="bg-white p-3 rounded-xl border border-gray-200 hover:shadow-lg transition-shadow ml-2">
                                                    <div className="flex gap-2">
                                                        <div className="w-7 h-7 rounded-full bg-blue-100 text-blue-700 flex items-center justify-center text-xs font-bold flex-shrink-0">
                                                            {comment.author_name?.charAt(0).toUpperCase() || 'C'}
                                                        </div>
                                                        <div className="flex-1 min-w-0">
                                                            <p className="text-xs font-semibold text-gray-800">{comment.author_name}</p>
                                                            <p className="text-xs text-gray-600 mt-1 line-clamp-2">{comment.content}</p>
                                                        </div>
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>
                ) : (
                    <div className="text-center py-16 bg-white rounded-2xl border border-gray-200">
                        <FaStar className="text-4xl mb-3 text-yellow-400 mx-auto" />
                        <p className="text-gray-500 font-medium mb-2">Your project could be here!</p>
                        <p className="text-gray-400 text-sm">Mark a project as completed to join the wall of champions!</p>
                    </div>
                )}
            </div>
        </Layout>
    )
}
