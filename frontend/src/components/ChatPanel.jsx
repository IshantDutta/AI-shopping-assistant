import { useState } from "react";
import { Send, Sparkles, Bot, UserRound } from "lucide-react";

export default function ChatPanel({ onAsk, loading }) {
  const [message, setMessage] = useState("");
  const prompts = ["Best headphones under ₹5,000", "Suggest a laptop for college", "Compare gaming headsets"];
  const submit = async (event) => {
    event.preventDefault();
    if (!message.trim() || loading) return;
    await onAsk(message.trim());
    setMessage("");
  };
  return (
    <section className="chat-panel">
      <div className="chat-heading"><div className="bot-avatar"><Bot size={20} /></div><div><h2>Ask ShopMate</h2><span><i className="online-dot" /> Shopping intelligence</span></div><Sparkles className="sparkle" size={19} /></div>
      <div className="chat-intro">
        <div className="assistant-mark"><Sparkles size={22} /></div>
        <h3>What are you shopping for?</h3>
        <p>Tell me your budget, use case and must-have features. I'll search your catalog and live shopping results when configured.</p>
      </div>
      <div className="prompt-list">
        {prompts.map((prompt) => <button key={prompt} onClick={() => setMessage(prompt)}>{prompt}</button>)}
      </div>
      <form className="chat-input" onSubmit={submit}>
        <input value={message} onChange={(e) => setMessage(e.target.value)} placeholder="e.g. Wireless headphones under ₹5,000..." />
        <button disabled={loading || !message.trim()} aria-label="Send message">{loading ? <span className="spinner" /> : <Send size={17} />}</button>
      </form>
      <div className="privacy-note"><Bot size={13} /> Results are informational. Verify price and seller details before buying.</div>
    </section>
  );
}
