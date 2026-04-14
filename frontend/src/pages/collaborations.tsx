import { useEffect, useState } from 'react'
import { FaCheck, FaExclamationTriangle, FaInbox, FaPaperPlane, FaTimes } from 'react-icons/fa'
import { useNavigate } from 'react-router-dom'
import { api } from '../api/api'
import Layout from '../components/Layout'

export default function Collaborations() {
    const navigate = useNavigate()
    const [collaborations, setCollaborations] = useState<any[]>([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState('')

    const loadCollabs = async () => {
        try {
            setLoading(true)
            const data = await api.getMyCollabs()
            setCollaborations(data)
        } catch (err: any) {
            setError(err.message)
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => {
        loadCollabs()
    }, [])

    const handleAccept = async (collabId: number) => {
        try {
            await api.updateCollaborationStatus(collabId, 'Accepted')
            loadCollabs()
        } catch (err: any) {
            alert('Failed to accept request: ' + err.message)
        }
    }

    const handleDecline = async (collabId: number) => {
        try {
            await api.updateCollaborationStatus(collabId, 'Rejected')
            loadCollabs()
        } catch (err: any) {
            alert('Failed to decline request: ' + err.message)
        }
    }

    const incomingRequests = collaborations.filter(c => c.type === 'incoming')
    const outgoingRequests = collaborations.filter(c => c.type === 'outgoing')
    const acceptedRequests = collaborations.filter(c => c.status === 'Accepted')

    const renderCollabCard = (collab: any) => {
        const isIncoming = collab.type === 'incoming'
        const isPending = collab.status === 'Pending'

        return (
            <div key={collab.collab_id} className="bg-white rounded-2xl p-6 border border-gray-200 hover:shadow-lg hover:scale-105 transition-transform">
                <div className="flex justify-between items-start gap-4 mb-3">
                    <div className="flex-1">
                        <h3 className="font-bold text-gray-900">{collab.project_title}</h3>
                        {collab.message && <p className="text-sm text-gray-600 mt-1 italic">"{collab.message}"</p>}
                    </div>
                    <span className={`px-3 py-1 rounded-full text-xs font-bold whitespace-nowrap ${collab.status === 'Accepted' ? 'bg-green-100 text-green-700' :
                        collab.status === 'Rejected' ? 'bg-red-100 text-red-700' :
                            'bg-yellow-100 text-yellow-700'
                        }`}>
                        {collab.status}
                    </span>
                </div>

                <div className="flex items-center gap-3 pt-3 border-t border-gray-200">
                    <div className="w-8 h-8 rounded-full bg-green-100 text-green-700 flex items-center justify-center text-xs font-bold">
                        {isIncoming ? collab.requester_name?.charAt(0).toUpperCase() : collab.project_owner_name?.charAt(0).toUpperCase()}
                    </div>
                    <div className="flex-1">
                        <p className="text-sm font-semibold text-gray-900">
                            {isIncoming ? collab.requester_name : collab.project_owner_name}
                        </p>
                        <p className="text-xs text-gray-500">{isIncoming ? 'Wants to collaborate' : 'Collaboration request'}</p>
                    </div>

                    {isIncoming && isPending && (
                        <div className="flex gap-2">
                            <button
                                onClick={() => handleAccept(collab.collab_id)}
                                className="px-3 py-1 rounded-2xl bg-green-600 text-white text-xs font-semibold hover:bg-green-700 transition-colors flex items-center gap-1"
                            >
                                <FaCheck size={12} /> Accept
                            </button>
                            <button
                                onClick={() => handleDecline(collab.collab_id)}
                                className="px-3 py-1 rounded-2xl bg-red-100 text-red-600 text-xs font-semibold hover:bg-red-200 transition-colors flex items-center gap-1"
                            >
                                <FaTimes size={12} /> Decline
                            </button>
                        </div>
                    )}
                </div>
            </div>
        )
    }

    return (
        <Layout>
            <div className="max-w-5xl mx-auto">
                <div className="mb-8">
                    <h1 className="text-4xl font-black text-gray-900 mb-2">Collaborations</h1>
                    <p className="text-gray-600">Manage your collaboration requests and active partnerships</p>
                </div>

                {loading ? (
                    <div className="text-center py-12">
                        <p className="text-gray-500 font-medium">Loading collaborations...</p>
                    </div>
                ) : error ? (
                    <div className="bg-red-50 border-2 border-red-200 rounded-2xl p-6">
                        <p className="text-red-700 font-medium flex items-center gap-2">
                            <FaExclamationTriangle /> {error}
                        </p>
                    </div>
                ) : (
                    <div className="space-y-8">
                        {/* Incoming Requests */}
                        {incomingRequests.length > 0 && (
                            <div>
                                <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
                                    <FaInbox className="text-blue-500" /> Incoming Requests ({incomingRequests.filter(r => r.status === 'Pending').length})
                                </h2>
                                <div className="space-y-3">
                                    {incomingRequests.map(renderCollabCard)}
                                </div>
                            </div>
                        )}

                        {/* Outgoing Requests */}
                        {outgoingRequests.length > 0 && (
                            <div>
                                <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
                                    <FaPaperPlane className="text-purple-500" /> Sent Requests ({outgoingRequests.filter(r => r.status === 'Pending').length})
                                </h2>
                                <div className="space-y-3">
                                    {outgoingRequests.map(renderCollabCard)}
                                </div>
                            </div>
                        )}

                        {/* Active Collaborations */}
                        {acceptedRequests.length > 0 && (
                            <div>
                                <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
                                    <FaCheck className="text-green-600" /> Active Collaborations ({acceptedRequests.length})
                                </h2>
                                <div className="space-y-3">
                                    {acceptedRequests.map(renderCollabCard)}
                                </div>
                            </div>
                        )}

                        {/* Empty State */}
                        {incomingRequests.length === 0 && outgoingRequests.length === 0 && acceptedRequests.length === 0 && (
                            <div className="bg-white rounded-2xl p-12 border border-gray-200 text-center">
                                <p className="text-gray-500 font-medium mb-2">No collaboration requests yet</p>
                                <p className="text-gray-400 text-sm mb-4">Browse the live feed, find projects you're interested in, and raise a hand to collaborate!</p>
                                <button
                                    onClick={() => navigate('/dashboard')}
                                    className="px-6 py-2 bg-green-600 text-white rounded-2xl text-sm font-semibold hover:bg-green-700 transition-colors"
                                >
                                    Browse Live Feed
                                </button>
                            </div>
                        )}
                    </div>
                )}
            </div>
        </Layout>
    )
}
