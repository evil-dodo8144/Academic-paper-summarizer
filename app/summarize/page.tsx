"use client"

import { useState } from "react"
import Link from "next/link"
import { ArrowLeft, FileText, Loader2 } from "lucide-react"

export default function SummarizePage() {
  const [file, setFile] = useState<File | null>(null)
  const [query, setQuery] = useState("Summarize this paper")
  const [summary, setSummary] = useState("")
  const [error, setError] = useState("")
  const [isLoading, setIsLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!file) return

    setIsLoading(true)
    setError("")
    setSummary("")

    try {
      const formData = new FormData()
      formData.append("file", file)
      formData.append("query", query)

      const response = await fetch("/api/summarize", {
        method: "POST",
        body: formData,
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || "Failed to summarize")
      }

      setSummary(data.summary)
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred")
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-background p-8">
      <div className="max-w-2xl mx-auto">
        <Link
          href="/"
          className="inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors mb-6"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to home
        </Link>

        <h1 className="text-2xl font-bold text-foreground mb-6">Summarize a paper</h1>

        <form onSubmit={handleSubmit}>
          <div className="bg-card border border-border rounded-xl p-6 mb-4">
            <label htmlFor="file" className="block font-semibold text-sm mb-2">
              PDF file
            </label>
            <div className="relative">
              <input
                type="file"
                name="file"
                id="file"
                accept=".pdf"
                required
                onChange={(e) => setFile(e.target.files?.[0] || null)}
                className="w-full p-3 bg-background border border-border rounded-lg text-foreground file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-primary file:text-primary-foreground hover:file:bg-primary/90"
              />
            </div>
            {file && (
              <div className="mt-3 flex items-center gap-2 text-sm text-muted-foreground">
                <FileText className="h-4 w-4" />
                <span>{file.name}</span>
              </div>
            )}
          </div>

          <div className="bg-card border border-border rounded-xl p-6 mb-4">
            <label htmlFor="query" className="block font-semibold text-sm mb-2">
              Query (optional)
            </label>
            <textarea
              name="query"
              id="query"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="e.g. Summarize this paper / What is the main contribution?"
              className="w-full min-h-[100px] p-4 bg-background border border-border rounded-lg text-foreground resize-y placeholder:text-muted-foreground"
            />
          </div>

          <button
            type="submit"
            disabled={isLoading || !file}
            className="px-6 py-3 bg-primary text-primary-foreground rounded-lg font-semibold hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            {isLoading && <Loader2 className="h-4 w-4 animate-spin" />}
            {isLoading ? "Processing..." : "Summarize"}
          </button>
        </form>

        {error && <p className="mt-6 text-destructive font-medium">{error}</p>}

        {summary && (
          <div className="bg-card border border-border rounded-xl p-6 mt-6">
            <p className="text-emerald-500 font-semibold mb-3">Summary</p>
            <div className="bg-background border border-border rounded-lg p-5 whitespace-pre-wrap leading-relaxed text-foreground">
              {summary}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
