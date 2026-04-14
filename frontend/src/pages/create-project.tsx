import { useState } from 'react'
import { FaExclamationTriangle } from 'react-icons/fa'
import { useNavigate } from 'react-router-dom'
import { api } from '../api/api'
import Layout from '../components/Layout'

export default function CreateProject() {
    const navigate = useNavigate()
    const [title, setTitle] = useState('')
    const [description, setDescription] = useState('')
    const [stage, setStage] = useState('Planning')
    const [support_needed, setSupportNeeded] = useState('')
    const [otherSupport, setOtherSupport] = useState('')
    const [error, setError] = useState('')
    const [loading, setLoading] = useState(false)

    const stages = ['Planning', 'Development', 'Testing', 'Completed']
    const supportTypes = ['Design', 'Development', 'Marketing', 'Funding', 'Mentorship', 'Other']

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        setError('')

        if (!title.trim() || !description.trim()) {
            setError('Title and description are required')
            return
        }

        try {
            setLoading(true)
            const finalSupport = support_needed === 'Other' ? otherSupport : support_needed
            await api.createProject({
                title,
                description,
                stage,
                support_needed: finalSupport || undefined,
            })
            navigate('/dashboard')
        } catch (err: any) {
            setError(err.message)
        } finally {
            setLoading(false)
        }
    }

    return (
        <Layout>
            <div className="max-w-2xl mx-auto">
                <div className="mb-8">
                    <h1 className="text-4xl font-black text-gray-900 mb-2">Start a Project</h1>
                    <p className="text-gray-600">Share your idea with the community</p>
                </div>

                <div className="bg-white rounded-3xl p-8 border border-gray-300">
                    <form onSubmit={handleSubmit} className="space-y-6">
                        {/* Title */}
                        <div>
                            <label className="block text-sm font-bold text-gray-900 mb-2">Project Title</label>
                            <input
                                type="text"
                                placeholder="What's your project called?"
                                value={title}
                                onChange={(e) => setTitle(e.target.value)}
                                className="w-full px-4 py-3 rounded-2xl border border-gray-300 bg-gray-50 text-gray-900 text-sm outline-none transition-colors focus:border-green-600 focus:bg-white"
                                required
                            />
                        </div>

                        {/* Description */}
                        <div>
                            <label className="block text-sm font-bold text-gray-900 mb-2">Description</label>
                            <textarea
                                placeholder="Tell us about your project..."
                                value={description}
                                onChange={(e) => setDescription(e.target.value)}
                                rows={5}
                                className="w-full px-4 py-3 rounded-2xl border border-gray-300 bg-gray-50 text-gray-900 text-sm outline-none transition-colors focus:border-green-600 focus:bg-white resize-none"
                                required
                            />
                        </div>

                        {/* Stage */}
                        <div>
                            <label className="block text-sm font-bold text-gray-900 mb-2">Current Stage</label>
                            <div className="grid grid-cols-2 gap-3">
                                {stages.map(s => (
                                    <button
                                        key={s}
                                        type="button"
                                        onClick={() => setStage(s)}
                                        className={`px-4 py-3 rounded-2xl font-semibold text-sm transition-colors capitalize ${stage === s
                                            ? 'bg-green-600 text-white border-2 border-green-600'
                                            : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
                                            }`}
                                    >
                                        {s}
                                    </button>
                                ))}
                            </div>
                        </div>

                        {/* Support Needed */}
                        <div>
                            <label className="block text-sm font-bold text-gray-900 mb-2">Support Needed (Optional)</label>
                            <select
                                aria-label="Support Needed"
                                value={support_needed}
                                onChange={(e) => setSupportNeeded(e.target.value)}
                                className="w-full px-4 py-3 rounded-2xl border border-gray-300 bg-gray-50 text-gray-900 text-sm outline-none transition-colors focus:border-green-600 focus:bg-white"
                            >
                                <option value="">Select support type</option>
                                {supportTypes.map(type => (
                                    <option key={type} value={type}>{type}</option>
                                ))}
                            </select>

                            {support_needed === 'Other' && (
                                <input
                                    type="text"
                                    placeholder="Describe the support you need..."
                                    value={otherSupport}
                                    onChange={(e) => setOtherSupport(e.target.value)}
                                    className="w-full px-4 py-3 rounded-2xl border border-gray-300 bg-gray-50 text-gray-900 text-sm outline-none transition-colors focus:border-green-600 focus:bg-white mt-3"
                                />
                            )}
                        </div>

                        {/* Error */}
                        {error && (
                            <div className="bg-red-50 border-2 border-red-200 rounded-2xl p-3 text-red-700 text-sm font-medium flex items-center gap-2">
                                <FaExclamationTriangle /> {error}
                            </div>
                        )}

                        {/* Buttons */}
                        <div className="flex gap-3 pt-4">
                            <button
                                type="button"
                                onClick={() => navigate('/dashboard')}
                                className="flex-1 px-4 py-3 rounded-2xl border border-gray-300 text-gray-700 font-semibold text-sm hover:bg-gray-50 transition-colors"
                            >
                                Cancel
                            </button>
                            <button
                                type="submit"
                                disabled={loading}
                                className="flex-1 px-4 py-3 rounded-2xl bg-green-600 text-white font-semibold text-sm hover:bg-green-700 transition-colors disabled:opacity-60"
                            >
                                {loading ? 'Creating...' : 'Create Project →'}
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </Layout>
    )
}
