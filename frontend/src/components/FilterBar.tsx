import { Filter, X } from 'lucide-react'
import { Button } from './ui/button'
import { Badge } from './ui/badge'

interface FilterBarProps {
  selectedBlog: string | null
  selectedCategory: string | null
  categories: string[]
  onBlogClear: () => void
  onCategoryChange: (category: string | null) => void
}

export default function FilterBar({
  selectedBlog,
  selectedCategory,
  categories,
  onBlogClear,
  onCategoryChange,
}: FilterBarProps) {
  return (
    <div className="flex flex-wrap items-center gap-3 p-4 bg-card border-b">
      <div className="flex items-center gap-2">
        <Filter className="w-4 h-4 text-muted-foreground" />
        <span className="text-sm font-medium text-muted-foreground">Filters:</span>
      </div>

      {selectedBlog && (
        <Badge variant="secondary" className="gap-1">
          Blog: {selectedBlog}
          <button
            type="button"
            onClick={onBlogClear}
            className="ml-1 hover:bg-destructive/20 rounded-full p-0.5"
          >
            <X className="w-3 h-3" />
          </button>
        </Badge>
      )}

      <div className="flex flex-wrap gap-2">
        <Button
          variant={selectedCategory === null ? 'default' : 'outline'}
          size="sm"
          onClick={() => onCategoryChange(null)}
        >
          All
        </Button>
        {categories.map((category) => (
          <Button
            key={category}
            variant={selectedCategory === category ? 'default' : 'outline'}
            size="sm"
            className={
    selectedCategory === category
      ? ''
      : 'bg-muted text-muted-foreground hover:bg-muted/80 cursor-pointer'
  }
            onClick={() => onCategoryChange(category)}
          >
            {category}
          </Button>
        ))}
      </div>
    </div>
  )
}
