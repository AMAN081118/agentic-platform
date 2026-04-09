import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

// ==========================================
// FONT SIZE CONFIGURATION
// Adjust this single variable (in rems) to scale all text.
// By default, 0.875rem = 14px (assuming a standard 16px browser base)
// ==========================================
const BASE_FONT_SIZE_REM = 0.875;

// These maintain the exact proportions from your original pixel values
const FONT_SIZES = {
  base: `${BASE_FONT_SIZE_REM}rem`, // original: 14px
  h1: `${BASE_FONT_SIZE_REM * (18 / 14)}rem`, // original: 18px (text-lg)
  h2: `${BASE_FONT_SIZE_REM * (16 / 14)}rem`, // original: 16px (text-base)
  h3: `${BASE_FONT_SIZE_REM}rem`, // original: 14px (text-sm)
  small: `${BASE_FONT_SIZE_REM * (13 / 14)}rem`, // original: 13px
  tiny: `${BASE_FONT_SIZE_REM * (11 / 14)}rem`, // original: 11px
  codeInline: `${BASE_FONT_SIZE_REM * (20 / 14)}rem`, // original: 20px
};

export default function MessageBubble({ message, agent, isStreaming = false }) {
  // Prevent crash if message is undefined during stream init
  const isUser = message?.role === "user";
  const content = message?.content || "";

  const agentIcons = { health: "🏥", sports: "⚡", education: "📚" };

  if (isUser) {
    return (
      <div className="flex justify-end animate-fade-in">
        <div
          className="max-w-[80%] bg-user-bubble text-text-primary px-4 py-3 rounded-2xl rounded-br-md leading-relaxed whitespace-pre-wrap"
          style={{ fontSize: FONT_SIZES.base }}
        >
          {content}
        </div>
      </div>
    );
  }

  return (
    <div className="flex items-start gap-3 animate-fade-in">
      {/* Avatar */}
      <div
        className="w-7 h-7 rounded-full bg-bg-hover flex items-center justify-center shrink-0 mt-1"
        style={{ fontSize: FONT_SIZES.base }}
      >
        {agentIcons[agent] || "🤖"}
      </div>

      {/* Content */}
      <div className="min-w-0 flex-1 pt-0.5 overflow-hidden">
        <div className="prose-custom">
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            components={markdownComponents}
          >
            {content}
          </ReactMarkdown>
        </div>

        {isStreaming && (
          <span className="inline-block w-0.75 h-4.5 bg-accent cursor-blink align-middle rounded-sm mt-1" />
        )}
      </div>
    </div>
  );
}

/**
 * Custom renderers for react-markdown.
 * Styled to match the dark Claude-like theme.
 */
const markdownComponents = {
  // Paragraphs
  p: ({ children }) => (
    <p
      className="leading-relaxed text-text-secondary mb-3 last:mb-0"
      style={{ fontSize: FONT_SIZES.base }}
    >
      {children}
    </p>
  ),

  // Headings
  h1: ({ children }) => (
    <h1
      className="font-semibold text-text-primary mt-5 mb-2"
      style={{ fontSize: FONT_SIZES.h1 }}
    >
      {children}
    </h1>
  ),
  h2: ({ children }) => (
    <h2
      className="font-semibold text-text-primary mt-4 mb-2"
      style={{ fontSize: FONT_SIZES.h2 }}
    >
      {children}
    </h2>
  ),
  h3: ({ children }) => (
    <h3
      className="font-semibold text-text-primary mt-3 mb-1.5"
      style={{ fontSize: FONT_SIZES.h3 }}
    >
      {children}
    </h3>
  ),

  // Bold & Italic
  strong: ({ children }) => (
    <strong className="font-semibold text-text-primary">{children}</strong>
  ),
  em: ({ children }) => (
    <em className="italic text-text-secondary">{children}</em>
  ),

  // Lists
  ul: ({ children }) => (
    <ul className="space-y-1.5 mb-3 last:mb-0">{children}</ul>
  ),
  ol: ({ children }) => (
    <ol className="space-y-1.5 mb-3 last:mb-0 counter-reset-item">
      {children}
    </ol>
  ),
  li: ({ children, ordered, index }) => (
    <li
      className="flex gap-2 leading-relaxed"
      style={{ fontSize: FONT_SIZES.base }}
    >
      <span className="text-accent shrink-0 mt-0.5">
        {ordered ? `${(index ?? 0) + 1}.` : "•"}
      </span>
      <span className="text-text-secondary min-w-0">{children}</span>
    </li>
  ),

  // Code (Fixed for v9 compatibility)
  code: ({ className, children, ...props }) => {
    const match = /language-(\w+)/.exec(className || "");
    const isInline = !match;

    if (isInline) {
      return (
        <code
          className="bg-bg-hover text-accent px-1.5 py-0.5 rounded font-mono"
          style={{ fontSize: FONT_SIZES.codeInline }}
          {...props}
        >
          {children}
        </code>
      );
    }

    return (
      <div className="my-3 rounded-lg overflow-hidden border border-border-primary">
        <div className="bg-bg-tertiary px-4 py-1.5 border-b border-border-primary">
          <span
            className="text-text-tertiary font-mono"
            style={{ fontSize: FONT_SIZES.tiny }}
          >
            {match[1] || "code"}
          </span>
        </div>
        <pre className="bg-bg-secondary px-4 py-3 overflow-x-auto">
          <code
            className="font-mono text-text-secondary leading-relaxed"
            style={{ fontSize: FONT_SIZES.small }}
            {...props}
          >
            {children}
          </code>
        </pre>
      </div>
    );
  },

  // Block quotes
  blockquote: ({ children }) => (
    <blockquote className="border-l-2 border-accent pl-4 my-3 text-text-secondary italic">
      {children}
    </blockquote>
  ),

  // Horizontal rule
  hr: () => <hr className="my-4 border-border-primary" />,

  // Tables
  table: ({ children }) => (
    <div
      className="my-3 overflow-x-auto rounded-lg border border-border-primary"
      style={{ fontSize: FONT_SIZES.small }}
    >
      <table className="w-full">{children}</table>
    </div>
  ),
  thead: ({ children }) => <thead className="bg-bg-tertiary">{children}</thead>,
  th: ({ children }) => (
    <th className="px-3 py-2 text-left font-semibold text-text-primary border-b border-border-primary">
      {children}
    </th>
  ),
  td: ({ children }) => (
    <td className="px-3 py-2 text-text-secondary border-b border-border-primary">
      {children}
    </td>
  ),

  // Links
  a: ({ href, children }) => (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      className="text-accent hover:text-accent-hover underline underline-offset-2"
    >
      {children}
    </a>
  ),

  // Images
  img: ({ src, alt }) => (
    <img
      src={src}
      alt={alt}
      className="max-w-full rounded-lg my-3 border border-border-primary"
    />
  ),
};
