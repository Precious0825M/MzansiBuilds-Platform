import { useEffect, useState } from 'react'
import { FaCheck, FaComments, FaExclamationTriangle, FaHandPaper, FaTimes } from 'react-icons/fa'
import { useNavigate, useParams } from 'react-router-dom'
import { api } from '../api/api'
import Layout from '../components/Layout'

export default function ProjectDetail() {
    const { id } = useParams<{ id: string }>()
    const navigate = useNavigate()
    const [project, setProject] = useState<any>(null)
    const [ownerName, setOwnerName] = useState('')
    const [updates, setUpdates] = useState<any[]>([])
    const [collaborations, setCollaborations] = useState<any[]>([])
    const [currentUser, setCurrentUser] = useState<any>(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState('')
    const [newUpdate, setNewUpdate] = useState('')
    const [showCommentBox, setShowCommentBox] = useState<number | null>(null)
    const [newComments, setNewComments] = useState<{ [key: number]: string }>({})
    const [updatingStage, setUpdatingStage] = useState(false)

    useEffect(() => {
        const loadProject = async () => {
            if (!id) return
            try {
                setLoading(true)
                const [proj, upd, me] = await Promise.all([
                    api.getProject(parseInt(id)),
                    api.getProjectUpdates(parseInt(id)),
                    api.getMe(),
                ])
                setProject(proj)
                setUpdates(upd)
                setCurrentUser(me)

                // Fetch owner name
                if (proj.user_id) {
                    try {
                        const owner = await api.getUser(proj.user_id)
                        setOwnerName(owner.name)
                    } catch (err) {
                        setOwnerName('Unknown')
                    }
                }

                // Load collaboration requests if user is owner
                if (me.user_id === proj.user_id) {
                    try {
                        const collabs = await api.getProjectCollaborations(parseInt(id))
                        setCollaborations(collabs)
                    } catch (err) {
                        console.log('Could not load collab requests')
                    }
                }
            } catch (err: any) {
                setError(err.message)
            } finally {
                setLoading(false)
            }
        }
        loadProject()
    }, [id])

    const handlePostUpdate = async (e: React.FormEvent) => {
        e.preventDefault()
        if (!newUpdate.trim() || !id) return

        try {
            await api.createUpdate({
                project_id: parseInt(id),
                content: newUpdate,
            })
            setNewUpdate('')
            // Reload updates
            const upd = await api.getProjectUpdates(parseInt(id))
            setUpdates(upd)
        } catch (err: any) {
            alert('Failed to post update: ' + err.message)
        }
    }

    const handlePostComment = async (updateId: number) => {
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
            if (id) {
                const upd = await api.getProjectUpdates(parseInt(id))
                setUpdates(upd)
            }
        } catch (err: any) {
            alert('Failed to post comment: ' + err.message)
        }
    }

    const handleAcceptCollaboration = async (collabId: number) => {
        try {
            await api.updateCollaborationStatus(collabId, 'Accepted')
            // Reload collaborations
            if (id && currentUser?.user_id === project?.user_id) {
                const collabs = await api.getProjectCollaborations(parseInt(id))
                setCollaborations(collabs)
            }
        } catch (err: any) {
            alert('Failed to accept request: ' + err.message)
        }
    }

    const handleDeclineCollaboration = async (collabId: number) => {
        try {
            await api.updateCollaborationStatus(collabId, 'Rejected')
            // Reload collaborations
            if (id && currentUser?.user_id === project?.user_id) {
                const collabs = await api.getProjectCollaborations(parseInt(id))
                setCollaborations(collabs)
            }
        } catch (err: any) {
            alert('Failed to decline request: ' + err.message)
        }
    }

    const handleUpdateStage = async (newStage: string) => {
        try {
            setUpdatingStage(true)
            await api.updateProject(parseInt(id!), { stage: newStage })
            setProject({ ...project, stage: newStage })
        } catch (err: any) {
            alert('Failed to update project stage: ' + err.message)
        } finally {
            setUpdatingStage(false)
        }
    }

    if (loading) {
        return (
            <Layout>
                <div className="max-w-4xl mx-auto text-center">
                    <p className="text-gray-500 font-medium">Loading project...</p>
                </div>
            </Layout>
        )
    }

    if (error || !project) {
        return (
            <Layout>
                <div className="max-w-4xl mx-auto">
                    <div className="bg-red-50 border-2 border-red-200 rounded-2xl p-6 text-center">
                        <p className="text-red-700 font-medium flex items-center justify-center gap-2">
                            <FaExclamationTriangle /> {error || 'Project not found'}
                        </p>
                        <button
                            onClick={() => navigate('/dashboard')}
                            className="mt-4 px-4 py-2 bg-red-600 text-white rounded-2xl text-sm font-semibold hover:bg-red-700"
                        >
                            Back to Projects
                        </button>
                    </div>
                </div>
            </Layout>
        )
    }

    const stageColors: any = {
        'Planning': { bg: 'bg-blue-100', text: 'text-blue-700' },
        'Development': { bg: 'bg-yellow-100', text: 'text-yellow-700' },
        'Testing': { bg: 'bg-green-100', text: 'text-green-700' },
        'Completed': { bg: 'bg-purple-100', text: 'text-purple-700' },
    }

    const stages = ['Planning', 'Development', 'Testing', 'Completed']
    const colors = stageColors[project.stage] || { bg: 'bg-gray-100', text: 'text-gray-700' }
    const isOwner = currentUser && currentUser.user_id === project?.user_id

    return (
        <Layout>
            <div className="max-w-4xl mx-auto">
                {/* Project Header */}
                <div className="bg-white rounded-3xl p-8 border border-gray-300 mb-8">
                    <div className="flex justify-between items-start gap-4 mb-6">
                        <div>
                            <h1 className="text-4xl font-black text-gray-900 mb-2">{project.title}</h1>
                            <p className="text-gray-600 text-lg">{project.description}</p>
                        </div>
                        {isOwner ? (
                            <select
                                value={project.stage}
                                onChange={(e) => handleUpdateStage(e.target.value)}
                                disabled={updatingStage}
                                className={`px-4 py-2 rounded-full text-sm font-bold border-2 outline-none transition-all cursor-pointer disabled:opacity-60 ${colors.bg} ${colors.text} border-current`}
                            >
                                {stages.map(s => (
                                    <option key={s} value={s}>{s}</option>
                                ))}
                            </select>
                        ) : (
                            <span className={`px-4 py-2 rounded-full text-sm font-bold ${colors.bg} ${colors.text} whitespace-nowrap`}>
                                {project.stage}
                            </span>
                        )}
                    </div>

                    <div className="flex items-center justify-between pt-6 border-t border-gray-200">
                        <div className="flex items-center gap-3">
                            <div className="w-12 h-12 rounded-full bg-green-100 text-green-700 flex items-center justify-center text-lg font-bold">
                                {ownerName?.charAt(0).toUpperCase() || 'U'}
                            </div>
                            <div>
                                <p className="font-bold text-gray-900">{ownerName || 'Unknown'}</p>
                                <p className="text-sm text-gray-500">Project owner</p>
                            </div>
                        </div>
                        {project.support_needed && (
                            <div className="px-4 py-2 bg-green-50 border-2 border-green-200 rounded-2xl">
                                <p className="text-xs text-gray-600 mb-1">Looking for:</p>
                                <p className="font-semibold text-green-700">{project.support_needed}</p>
                            </div>
                        )}
                    </div>
                </div>

                {/* Collaboration Requests Section (for project owner) */}
                {currentUser && currentUser.user_id === project?.user_id && collaborations.length > 0 && (
                    <div className="bg-white rounded-2xl p-6 border-2 border-purple-100 mb-8">
                        <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
                            <FaHandPaper className="text-purple-500" /> Collaboration Requests ({collaborations.filter((c: any) => c.status === 'Pending').length})
                        </h3>
                        <div className="space-y-3">
                            {collaborations.map((collab: any) => (
                                <div key={collab.collab_id} className="flex items-center justify-between p-3 bg-purple-50 rounded-xl border border-purple-200">
                                    <div className="flex-1">
                                        <p className="font-semibold text-gray-900">Collaboration Request</p>
                                        {collab.message && <p className="text-sm text-gray-600 mt-1">"{collab.message}"</p>}
                                        <p className="text-xs text-gray-500 mt-1">Status: <span className={collab.status === 'Pending' ? 'text-yellow-600 font-semibold' : collab.status === 'Accepted' ? 'text-green-600 font-semibold' : 'text-red-600 font-semibold'}>{collab.status}</span></p>
                                    </div>
                                    {collab.status === 'Pending' && (
                                        <div className="flex gap-2">
                                            <button
                                                onClick={() => handleAcceptCollaboration(collab.collab_id)}
                                                className="px-3 py-1 rounded-xl bg-green-600 text-white text-xs font-semibold hover:bg-green-700 transition-colors flex items-center gap-1"
                                            >
                                                <FaCheck size={12} /> Accept
                                            </button>
                                            <button
                                                onClick={() => handleDeclineCollaboration(collab.collab_id)}
                                                className="px-3 py-1 rounded-xl bg-red-100 text-red-600 text-xs font-semibold hover:bg-red-200 transition-colors flex items-center gap-1"
                                            >
                                                <FaTimes size={12} /> Decline
                                            </button>
                                        </div>
                                    )}
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* Updates Section */}
                <div className="space-y-6">
                    <h2 className="text-2xl font-black text-gray-900">Updates</h2>

                    {/* New Update Form */}
                    <form onSubmit={handlePostUpdate} className="bg-white rounded-2xl p-6 border border-gray-200">
                        <textarea
                            placeholder="Share a project update..."
                            value={newUpdate}
                            onChange={(e) => setNewUpdate(e.target.value)}
                            rows={3}
                            className="w-full px-4 py-3 rounded-2xl border border-gray-300 bg-gray-50 text-gray-900 text-sm outline-none transition-colors focus:border-green-600 focus:bg-white resize-none"
                        />
                        <button
                            type="submit"
                            disabled={!newUpdate.trim()}
                            className="mt-3 px-4 py-2 rounded-2xl bg-green-600 text-white text-sm font-semibold hover:bg-green-700 transition-colors disabled:opacity-60"
                        >
                            Post Update
                        </button>
                    </form>

                    {/* Updates List */}
                    {updates.length > 0 ? (
                        <div className="space-y-4">
                            {updates.map((update: any) => (
                                <div key={update.update_id} className="bg-white rounded-2xl p-6 border border-gray-200">
                                    <div className="flex gap-3 mb-3">
                                        <div className="w-10 h-10 rounded-full bg-green-100 text-green-700 flex items-center justify-center text-sm font-bold flex-shrink-0">
                                            {update.author?.name?.charAt(0).toUpperCase() || 'U'}
                                        </div>
                                        <div className="flex-1">
                                            <p className="font-bold text-gray-900">{update.author?.name || 'Unknown'}</p>
                                            <p className="text-xs text-gray-500">{new Date(update.created_at).toLocaleDateString()}</p>
                                        </div>
                                    </div>

                                    <p className="text-gray-800 mb-4">{update.content}</p>

                                    {/* Comments */}
                                    {update.comments && update.comments.length > 0 && (
                                        <div className="bg-gray-50 rounded-2xl p-4 mb-3 space-y-3">
                                            {update.comments.map((comment: any) => (
                                                <div key={comment.com_id} className="text-sm">
                                                    <p className="font-semibold text-gray-900">{comment.author?.name || 'Unknown'}</p>
                                                    <p className="text-gray-700 mt-1">{comment.content}</p>
                                                </div>
                                            ))}
                                        </div>
                                    )}

                                    {/* Comment Form */}
                                    {showCommentBox === update.update_id ? (
                                        <div className="flex gap-2">
                                            <input
                                                type="text"
                                                placeholder="Add a comment..."
                                                value={newComments[update.update_id] || ''}
                                                onChange={(e) => setNewComments({ ...newComments, [update.update_id]: e.target.value })}
                                                className="flex-1 px-3 py-2 rounded-2xl border border-gray-300 bg-gray-50 text-gray-900 text-sm outline-none transition-colors focus:border-green-600 focus:bg-white"
                                            />
                                            <button
                                                onClick={() => handlePostComment(update.update_id)}
                                                className="px-3 py-2 rounded-2xl bg-green-600 text-white text-sm font-semibold hover:bg-green-700"
                                            >
                                                Send
                                            </button>
                                        </div>
                                    ) : (
                                        <button
                                            onClick={() => setShowCommentBox(update.update_id)}
                                            className="text-sm font-semibold text-green-600 hover:text-green-700 transition-colors flex items-center gap-2"
                                        >
                                            <FaComments size={14} /> Comment
                                        </button>
                                    )}
                                </div>
                            ))}
                        </div>
                    ) : (
                        <div className="bg-white rounded-2xl p-8 border border-gray-200 text-center">
                            <p className="text-gray-500 font-medium">No updates yet</p>
                            <p className="text-gray-400 text-sm mt-1">Be the first to share progress!</p>
                        </div>
                    )}
                </div>
            </div>
        </Layout>
    )
}
