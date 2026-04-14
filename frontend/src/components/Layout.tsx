import Sidebar from './Sidebar'

interface LayoutProps {
    children: React.ReactNode
}

export default function Layout({ children }: LayoutProps) {
    return (
        <div className="flex min-h-screen bg-green-50">
            <Sidebar />
            <div className="ml-64 flex-1">
                <main className="p-8">
                    {children}
                </main>
            </div>
        </div>
    )
}
