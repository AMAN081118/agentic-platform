import { useState, useRef, useEffect } from "react";
import { Icons } from "../utils/Icons";

export default function ChatInput({ onSend, isLoading, agent }) {
  const [text, setText] = useState("");
  const textareaRef = useRef(null);

  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = "24px"; // Reset to base height
      const scrollHeight = textarea.scrollHeight;
      textarea.style.height = Math.min(scrollHeight, 200) + "px";
    }
  }, [text]);

  useEffect(() => {
    textareaRef.current?.focus();
  }, [agent]);

  const handleSubmit = () => {
    if (text.trim() && !isLoading) {
      onSend(text);
      setText("");
      if (textareaRef.current) textareaRef.current.style.height = "24px";
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="max-w-4xl mx-auto w-full px-4">
      <div className="relative bg-bg-secondary rounded-3xl transition-all duration-300 focus-within:ring-1 focus-within:ring-border-light shadow-sm">
        <textarea
          ref={textareaRef}
          rows={1}
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask me anything..."
          disabled={isLoading}
          className="w-full bg-transparent text-text-primary placeholder-text-tertiary outline-none resize-none text-[15px] leading-relaxed px-6 py-4 pr-14 min-h-[56px] max-h-[200px]"
          style={{ overflowY: text.length > 200 ? "auto" : "hidden" }}
        />

        <button
          onClick={handleSubmit}
          disabled={!text.trim() || isLoading}
          className={`absolute right-3 bottom-3 p-2 rounded-full transition-all duration-200 flex items-center justify-center ${
            text.trim() && !isLoading
              ? "bg-text-primary text-bg-primary hover:bg-gray-300 scale-100"
              : "bg-transparent text-text-tertiary cursor-not-allowed scale-95"
          }`}
        >
          <Icons.Send />
        </button>
      </div>

      <p className="text-center text-[12px] text-text-tertiary mt-3 font-medium">
        AI can make mistakes. Consider verifying important information.
      </p>
    </div>
  );
}
