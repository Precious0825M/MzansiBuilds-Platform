import { useNavigate } from 'react-router-dom';

export default function ProjectCard({ project, ownerName }: { project: any; ownerName?: string }) {
    const navigate = useNavigate()
    const stageColors: any = {
        'Planning': { bg: 'bg-blue-100', text: 'text-blue-700' },
        'Development': { bg: 'bg-yellow-100', text: 'text-yellow-700' },
        'Testing': { bg: 'bg-green-100', text: 'text-green-700' },
        'Completed': { bg: 'bg-purple-100', text: 'text-purple-700' },
    }

    const colors = stageColors[project.stage] || { bg: 'bg-gray-100', text: 'text-gray-700' }

    return (
        <div
            onClick={() => navigate(`/project/${project.proj_id}`)}
            className="bg-white rounded-2xl p-6 border border-gray-200 hover:shadow-lg hover:scale-105 cursor-pointer transition-transform"
        >
            <div className="flex justify-between items-start mb-3">
                <h3 className="text-lg font-bold text-gray-900 flex-1">{project.title}</h3>
                <span className={`px-3 py-1 rounded-full text-xs font-semibold ${colors.bg} ${colors.text}`}>
                    {project.stage}
                </span>
            </div>

            <p className="text-sm text-gray-600 mb-4 line-clamp-2">{project.description}</p>

            <div className="flex items-center justify-between pt-3 border-t border-gray-200">
                <div className="flex items-center gap-2">
                    <div className="w-8 h-8 rounded-full bg-green-100 text-green-700 flex items-center justify-center text-xs font-bold">
                        {ownerName?.charAt(0).toUpperCase() || 'U'}
                    </div>
                    <span className="text-xs text-gray-600">{ownerName || 'Unknown'}</span>
                </div>
                <span className="text-xs text-gray-500">{project.support_needed || 'Open'}</span>
            </div>
        </div>
    )
}
