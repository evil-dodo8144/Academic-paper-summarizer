import Link from "next/link"

export default function HomePage() {
  return (
    <div className="min-h-screen bg-background flex flex-col items-center justify-center p-8">
      <div className="max-w-xl bg-card border border-border rounded-2xl p-10 text-center">
        <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-4">
          evil-dodo academic paper summarizer
        </p>
        <h1 className="text-2xl font-bold text-foreground mb-2">
          Academic Paper Summarizer
        </h1>
        <p className="text-base leading-relaxed text-muted-foreground mb-6">
          A research paper summarization tool that uses{" "}
          <strong className="text-foreground">compression</strong> to handle lengthy academic papers
          while preserving <strong className="text-foreground">technical accuracy</strong> and reducing
          processing time.
        </p>
        <ul className="text-left text-sm text-muted-foreground space-y-2 mb-6 list-disc list-inside">
          <li>Upload a PDF and get a concise, accurate summary.</li>
          <li>State your work.</li>
          <li>Chunking and compression for long documents.</li>
        </ul>
        <Link
          href="/summarize"
          className="inline-block px-6 py-3 bg-primary text-primary-foreground rounded-lg font-semibold hover:bg-primary/90 transition-colors"
        >
          Try it — Summarize a paper
        </Link>
      </div>
      <p className="mt-8 text-sm text-muted-foreground">
        <span>by Sagnik</span> · evil-dodo8144
      </p>
    </div>
  )
}
