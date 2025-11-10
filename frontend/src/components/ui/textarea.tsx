import * as React from "react"
import { cn } from "../../lib/utils"

export interface TextareaProps
  extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {}

const Textarea = React.forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({ className, ...props }, ref) => {
    return (
      <textarea
        className={cn(
          "flex min-h-[80px] w-full rounded-xl bg-white/[0.03] border border-white/[0.06] px-4 py-3 text-sm text-zinc-100 placeholder:text-zinc-600 transition-all duration-200",
          "focus-visible:outline-none focus-visible:border-indigo-500/50 focus-visible:ring-2 focus-visible:ring-indigo-500/10",
          "hover:bg-white/[0.04] hover:border-white/[0.08]",
          "disabled:cursor-not-allowed disabled:opacity-50",
          "resize-none",
          className
        )}
        ref={ref}
        {...props}
      />
    )
  }
)
Textarea.displayName = "Textarea"

export { Textarea }
