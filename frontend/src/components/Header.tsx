import { Link, useNavigate } from '@tanstack/react-router'
import { useState } from 'react'
import { Home, Menu, X, RefreshCw } from 'lucide-react'
import { Button } from './ui/button'

export default function Header() {
  const [isOpen, setIsOpen] = useState(false)
  const [isRefreshing, setIsRefreshing] = useState(false)
  const navigate = useNavigate()

  const handleRefresh = async () => {
    setIsRefreshing(true)
    try {
      await fetch(`${import.meta.env.VITE_API_URL || '/api'}/posts/refresh`, {
        method: 'POST',
      })
      // Invalidate and refetch posts
      window.location.reload()
    } catch (error) {
      console.error('Failed to refresh:', error)
    } finally {
      setIsRefreshing(false)
    }
  }

  return (
    <>
      <header className="p-4 flex items-center justify-between bg-background border-b shadow-sm">
        <div className="flex items-center gap-4">
          <button
            onClick={() => setIsOpen(true)}
            className="p-2 hover:bg-accent rounded-lg transition-colors"
            aria-label="Open menu"
          >
            <Menu size={24} />
          </button>
          <h1 className="text-xl font-bold">
            <Link to="/" className="flex items-center gap-2">
              <span className="text-primary">Info</span>Matrix
            </Link>
          </h1>
        </div>
        <Button
          variant="outline"
          size="sm"
          onClick={handleRefresh}
          disabled={isRefreshing}
          className="gap-2"
        >
          <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
      </header>

      <aside
        className={`fixed top-0 left-0 h-full w-80 bg-background shadow-2xl z-50 transform transition-transform duration-300 ease-in-out flex flex-col border-r ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div className="flex items-center justify-between p-4 border-b">
          <h2 className="text-xl font-bold">Navigation</h2>
          <button
            onClick={() => setIsOpen(false)}
            className="p-2 hover:bg-accent rounded-lg transition-colors"
            aria-label="Close menu"
          >
            <X size={24} />
          </button>
        </div>

        <nav className="flex-1 p-4 overflow-y-auto">
          <Link
            to="/"
            onClick={() => setIsOpen(false)}
            className="flex items-center gap-3 p-3 rounded-lg hover:bg-accent transition-colors mb-2"
            activeProps={{
              className:
                'flex items-center gap-3 p-3 rounded-lg bg-primary text-primary-foreground hover:bg-primary/90 transition-colors mb-2',
            }}
          >
            <Home size={20} />
            <span className="font-medium">Home</span>
          </Link>
        </nav>
      </aside>

      {/* Overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40"
          onClick={() => setIsOpen(false)}
          onKeyDown={(e) => {
            if (e.key === 'Escape') setIsOpen(false)
          }}
          role="button"
          tabIndex={0}
          aria-label="Close menu"
        />
      )}
    </>
  )
}
