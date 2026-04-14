import { useEffect, useState } from 'react'
import { FaCheck, FaComment, FaExclamationTriangle, FaFire, FaHandPaper } from 'react-icons/fa'
import { api } from '../api/api'
import Layout from '../components/Layout'

export default function Dashboard() {
    const [updates, setUpdates] = useState<any[]>([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState('')
    const [newComments, setNewComments] = useState<{ [key: number]: string }>({})
    const [showCommentBox, setShowCommentBox] = useState<number | null>(null)
    const [collabLoading, setCollabLoading] = useState<{ [key: string]: boolean }>({})

    useEffect(() => {
        const loadUpdates = async () => {
            try {
                setLoading(true)
                const data = await api.getUpdates()
                setUpdates(data)
            } catch (err: any) {
                setError(err.message)
            } finally {
                setLoading(false)
            }
        }
        loadUpdates()
    }, [])

    const handleComment = async (updateId: number) => {
        const content = newComments[updateId]
        if (!content?.trim()) return

        try {
            await api.createComment({
                update_id: updateId,
                content,
            })
            setNewComments({ ...newComments, [updateId]: '' })
            setShowCommentBox(null)
            // Reload updates
            const data = await api.getUpdates()
            setUpdates(data)
        } catch (err: any) {
            alert('Failed to post comment: ' + err.message)
        }
    }

    const handleCollabRequest = async (projectId: number, updateId: number) => {
        const key = `${projectId}-${updateId}`
        try {
            setCollabLoading({ ...collabLoading, [key]: true })
            await api.requestCollab({
                project_id: projectId,
                message: 'I would like to collaborate on this project',
            })
            // Reload updates to get new status
            const data = await api.getUpdates()
            setUpdates(data)
        } catch (err: any) {
            alert('Failed to send collaboration request: ' + err.message)
        } finally {
            setCollabLoading({ ...collabLoading, [key]: false })
        }
    }

    return (
        <Layout>
            <div className="max-w-4xl mx-auto">
                <div className="mb-10">
                    <h1 className="text-4xl font-black text-gray-900 mb-2 flex items-center gap-3">
                        <FaFire className="text-red-500" size={32} />
                        Live Feed
                    </h1>
                    <p className="text-gray-600">Real-time updates from developers building in public</p>
                </div>

                {/* Loading state */}
                {loading && (
                    <div className="text-center py-12">
                        <p className="text-gray-500 font-medium">Loading updates...</p>
                    </div>
                )}

                {/* Error state */}
                {error && (
                    <div className="bg-red-50 border-2 border-red-200 rounded-2xl p-4">
                        <p className="text-red-700 font-medium flex items-center gap-2">
                            <FaExclamationTriangle /> {error}
                        </p>
                    </div>
                )}

                {/* Updates Feed */}
                {!loading && updates.length > 0 ? (
                    <div className="space-y-6">
                        {updates.map((update: any) => (
                            <div key={update.update_id} className="bg-white rounded-2xl p-6 border border-gray-200 hover:shadow-lg hover:scale-105 transition-transform">
                                {/* Project Header */}
                                <div className="mb-4 pb-4 border-b border-gray-200">
                                    <div className="flex justify-between items-start gap-4">
                                        <div className="flex-1">
                                            <h3 className="text-lg font-bold text-gray-900">{update.project?.title || 'Project'}</h3>
                                            <p className="text-xs text-gray-500 mt-1">By {update.project_owner?.name || 'Unknown'}</p>
                                        </div>
                                    </div>
                                </div>

                                {/* Update Content */}
                                <div className="mb-4">
                                    <div className="flex gap-3 mb-3">
                                        <div className="w-10 h-10 rounded-full bg-green-100 text-green-700 flex items-center justify-center text-sm font-bold flex-shrink-0">
                                            {update.author?.name?.charAt(0).toUpperCase() || 'U'}
                                        </div>
                                        <div className="flex-1">
                                            <p className="font-semibold text-gray-900">{update.author?.name || 'Unknown'}</p>
                                            <p className="text-xs text-gray-500">{new Date(update.created_at).toLocaleDateString()} at {new Date(update.created_at).toLocaleTimeString()}</p>
                                        </div>
                                    </div>
                                    <p className="text-gray-800 mb-3">{update.content}</p>
                                </div>

                                {/* Comments Section */}
                                {update.comments && update.comments.length > 0 && (
                                    <div className="space-y-3 mb-4">
                                        <p className="text-xs font-semibold text-gray-700">{update.comments.length} Comment{update.comments.length !== 1 ? 's' : ''}</p>
                                        {update.comments.map((comment: any) => (
                                            <div key={comment.com_id} className="bg-white rounded-xl p-4 border border-gray-200 hover:shadow-lg transition-shadow ml-4">
                                                <div className="flex gap-3">
                                                    <div className="w-8 h-8 rounded-full bg-blue-100 text-blue-700 flex items-center justify-center text-xs font-bold flex-shrink-0">
                                                        {comment.name?.charAt(0).toUpperCase() || 'C'}
                                                    </div>
                                                    <div className="flex-1">
                                                        <p className="text-xs font-semibold text-gray-800">{comment.name}</p>
                                                        <p className="text-xs text-gray-600 mt-2">{comment.content}</p>
                                                    </div>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                )}

                                {/* Action Buttons */}
                                <div className="flex gap-3 items-center flex-wrap">
                                    <button
                                        onClick={() => setShowCommentBox(showCommentBox === update.update_id ? null : update.update_id)}
                                        className="px-3 py-2 rounded-2xl bg-blue-50 text-blue-600 text-sm font-semibold hover:bg-blue-100 transition-colors flex items-center gap-2"
                                    >
                                        <FaComment size={14} /> Comment
                                    </button>

                                    {!update.is_owner && update.collab_status === null && (
                                        <button
                                            onClick={() => handleCollabRequest(update.project?.proj_id, update.update_id)}
                                            disabled={collabLoading[`${update.project?.proj_id}-${update.update_id}`]}
                                            className="px-3 py-2 rounded-2xl bg-green-50 text-green-600 text-sm font-semibold hover:bg-green-100 transition-colors flex items-center gap-2 disabled:opacity-60"
                                        >
                                            <FaHandPaper size={14} /> Collaborate
                                        </button>
                                    )}

                                    {update.collab_status && (
                                        <div className={`px-3 py-2 rounded-2xl text-sm font-semibold flex items-center gap-2 ${update.collab_status === 'Accepted'
                                            ? 'bg-green-100 text-green-700'
                                            : 'bg-yellow-100 text-yellow-700'
                                            }`}>
                                            <FaCheck size={14} />
                                            {update.collab_status === 'Accepted' ? 'Collaborating' : 'Request Pending'}
                                        </div>
                                    )}
                                </div>

                                {/* Comment Input */}
                                {showCommentBox === update.update_id && (
                                    <div className="mt-4 pt-4 border-t border-gray-200">
                                        <textarea
                                            placeholder="Share your thoughts..."
                                            value={newComments[update.update_id] || ''}
                                            onChange={(e) => setNewComments({ ...newComments, [update.update_id]: e.target.value })}
                                            className="w-full px-4 py-2 rounded-2xl border border-gray-300 bg-gray-50 text-gray-900 text-sm outline-none focus:border-green-600 focus:bg-white resize-none"
                                            rows={2}
                                        />
                                        <div className="flex gap-2 mt-2">
                                            <button
                                                onClick={() => handleComment(update.update_id)}
                                                disabled={!(newComments[update.update_id]?.trim())}
                                                className="px-3 py-2 rounded-2xl bg-green-600 text-white text-sm font-semibold hover:bg-green-700 transition-colors disabled:opacity-60"
                                            >
                                                Post
                                            </button>
                                            <button
                                                onClick={() => setShowCommentBox(null)}
                                                className="px-3 py-2 rounded-2xl border-2 border-gray-300 text-gray-700 text-sm font-semibold hover:bg-gray-50"
                                            >
                                                Cancel
                                            </button>
                                        </div>
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>
                ) : !loading ? (
                    <div className="text-center py-16 bg-white rounded-2xl border border-gray-200">
                        <p className="text-gray-500 font-medium mb-2">No updates yet</p>
                        <p className="text-gray-400 text-sm">Create a project and share updates to get the conversation started!</p>
                    </div>
                ) : null}
            </div>
        </Layout>
    )
}
