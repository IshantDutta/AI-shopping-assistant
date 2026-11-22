import { useEffect, useMemo, useState } from "react";
import { ShoppingBag, Search, SlidersHorizontal, Sparkles, LayoutGrid, Heart, GitCompareArrows, RefreshCw, X, Menu } from "lucide-react";
import { api } from "./services/api";
import ProductCard from "./components/ProductCard";
import ChatPanel from "./components/ChatPanel";

const money = (value) => value === null || value === undefined ? "Price unavailable" : `₹${Number(value).toLocaleString("en-IN")}`;


function renderAssistantText(text) {
  // Safe, dependency-free Markdown renderer for Gemini responses.
  const lines = String(text || "").split(/\r?\n/);
  const blocks = [];
  let listItems = [];
  let listType = null;

  const renderInline = (value) => {
    const tokens = value.split(/(\[[^\]]+\]\(https?:\/\/[^)\s]+\)|\*\*[^*]+\*\*|\*[^*]+\*)/g);
    return tokens.map((token, index) => {
      const link = token.match(/^\[([^\]]+)\]\((https?:\/\/[^)\s]+)\)$/);
      if (link) {
        return <a key={index} href={link[2]} target="_blank" rel="noopener noreferrer">{link[1]}</a>;
      }
      if (token.startsWith("**") && token.endsWith("**")) {
        return <strong key={index}>{token.slice(2, -2)}</strong>;
      }
      if (token.startsWith("*") && token.endsWith("*")) {
        return <em key={index}>{token.slice(1, -1)}</em>;
      }
      return token;
    });
  };

  const flushList = () => {
    if (!listItems.length) return;
    const Tag = listType === "ol" ? "ol" : "ul";
    blocks.push(
      <Tag className="answer-list" key={`list-${blocks.length}`}>
        {listItems.map((item, index) => <li key={index}>{renderInline(item)}</li>)}
      </Tag>
    );
    listItems = [];
    listType = null;
  };

  lines.forEach((rawLine, index) => {
    const line = rawLine.trim();
    if (!line || /^---+$/.test(line) || /^\*\*\*+$/.test(line)) {
      flushList();
      return;
    }

    const heading = line.match(/^(#{1,6})\s+(.+)$/);
    if (heading) {
      flushList();
      const Tag = heading[1].length <= 2 ? "h3" : "h4";
      blocks.push(
        <Tag className="answer-heading" key={`heading-${index}`}>
          {renderInline(heading[2])}
        </Tag>
      );
      return;
    }

    const ordered = line.match(/^\d+[.)]\s+(.+)$/);
    const unordered = line.match(/^[-*•]\s+(.+)$/);
    if (ordered || unordered) {
      const nextType = ordered ? "ol" : "ul";
      if (listType && listType !== nextType) flushList();
      listType = nextType;
      listItems.push((ordered || unordered)[1]);
      return;
    }

    flushList();
    blocks.push(
      <p className="answer-paragraph" key={`paragraph-${index}`}>
        {renderInline(line)}
      </p>
    );
  });

  flushList();
  return blocks;
}

function readSavedProducts() {
  try { return JSON.parse(localStorage.getItem("shopmate-saved") || "[]"); }
  catch { return []; }
}

export default function App() {
  const [products, setProducts] = useState([]);
  const [query, setQuery] = useState("");
  const [category, setCategory] = useState("");
  const [budget, setBudget] = useState("");
  const [loading, setLoading] = useState(false);
  const [chatLoading, setChatLoading] = useState(false);
  const [error, setError] = useState("");
  const [answer, setAnswer] = useState("");
  const [sources, setSources] = useState(null);
  const [saved, setSaved] = useState(readSavedProducts);
  const [selected, setSelected] = useState([]);
  const [compareItems, setCompareItems] = useState(null);
  const [activeTab, setActiveTab] = useState("discover");
  const [mobileMenu, setMobileMenu] = useState(false);
  const [systemStatus, setSystemStatus] = useState(null);

  const categories = useMemo(() => ["Headphones", "Earbuds", "Gaming Headset", "Laptops", "Accessories"], []);

  async function loadProducts() {
    setLoading(true); setError("");
    try {
      const rows = await api.products({ query, category, max_price: budget });
      setProducts(rows);
      setSources(null);
    } catch (e) { setError(`${e.message}. Is the FastAPI backend running?`); }
    finally { setLoading(false); }
  }

  useEffect(() => {
    loadProducts();
    api.status().then(setSystemStatus).catch(() => setSystemStatus(null));
  }, []); // Initial catalog and provider status.

  function toggleSaved(product) {
    const key = product.product_url || `${product.name}-${product.brand}`;
    const exists = saved.some((p) => (p.product_url || `${p.name}-${p.brand}`) === key);
    const next = exists ? saved.filter((p) => (p.product_url || `${p.name}-${p.brand}`) !== key) : [...saved, product];
    setSaved(next); localStorage.setItem("shopmate-saved", JSON.stringify(next));
  }

  function toggleCompare(product) {
    const key = product.id ?? product.product_url ?? product.name;
    setSelected((current) => current.includes(key) ? current.filter((x) => x !== key) : current.length < 4 ? [...current, key] : current);
  }

  async function askAssistant(message) {
    setChatLoading(true); setError(""); setAnswer("");
    try {
      const result = await api.chat({ message, max_price: budget ? Number(budget) : null, category: category || null, use_live_search: true });
      setProducts(result.products || []);
      setAnswer(result.message || "");
      setSources(result.sources || null);
      setActiveTab("discover");
    } catch (e) { setError(e.message); }
    finally { setChatLoading(false); }
  }

  async function compareSelected() {
    const ids = selected.filter((id) => typeof id === "number");
    if (ids.length < 2) { setError("Choose at least two catalog products to compare. Live results cannot be compared in this version."); return; }
    try {
      const result = await api.compare(ids);
      setCompareItems(result.products);
    } catch (e) { setError(e.message); }
  }

  const visibleProducts = activeTab === "saved" ? saved : products;

  return (
    <div className="app-shell">
      <aside className={`sidebar ${mobileMenu ? "open" : ""}`}>
        <div className="brand"><div className="brand-icon"><ShoppingBag size={21} /></div><span>shopmate<span className="brand-ai">.ai</span></span></div>
        <div className="workspace-label">WORKSPACE</div>
        <nav>
          <button className={activeTab === "discover" ? "nav-item active" : "nav-item"} onClick={() => {setActiveTab("discover");setMobileMenu(false);}}><LayoutGrid size={18}/> Discover <span className="nav-count">{products.length}</span></button>
          <button className={activeTab === "saved" ? "nav-item active" : "nav-item"} onClick={() => {setActiveTab("saved");setMobileMenu(false);}}><Heart size={18}/> Wishlist <span className="nav-count">{saved.length}</span></button>
        </nav>
        <div className="sidebar-bottom">
          <div className="status-card"><span className="status-pulse" /><div><b>ShopMate is ready</b><small>{systemStatus?.ai_configured ? "Gemini AI connected" : "Catalog search enabled"}</small></div></div>
          <div className="profile"><div className="profile-avatar">S</div><div><b>Shopper</b><small>Personal workspace</small></div><span className="profile-dots">•••</span></div>
        </div>
      </aside>

      <main className="main-area">
        <header className="topbar">
          <button className="mobile-menu icon-button" onClick={() => setMobileMenu(!mobileMenu)}><Menu size={19}/></button>
          <div className="breadcrumb">Workspace <span>/</span> <b>{activeTab === "saved" ? "Wishlist" : "Discover products"}</b></div>
          <div className="top-actions"><span className="top-status"><i className="online-dot"/> Systems operational</span><div className="top-avatar">S</div></div>
        </header>

        <div className="content-wrap">
          <section className="hero">
            <div className="hero-copy"><div className="hero-kicker"><Sparkles size={14}/> YOUR PERSONAL SHOPPING INTELLIGENCE</div>
              <h1>Find your next<br/><span>great purchase.</span></h1>
              <p>Search smarter. Compare confidently. Shop with clarity.</p>
            </div>
            <div className="hero-art"><div className="orb orb-one"/><div className="orb orb-two"/><div className="hero-bag"><ShoppingBag size={54}/><Sparkles className="hero-spark" size={23}/></div><div className="floating-chip chip-top">✦ Smart picks</div><div className="floating-chip chip-bottom">₹ Budget aware</div></div>
          </section>

          <div className="dashboard-grid">
            <div className="left-column">
              <ChatPanel onAsk={askAssistant} loading={chatLoading}/>
              {answer && <div className="answer-card"><div className="answer-title"><Sparkles size={16}/> ShopMate's take</div><div className="assistant-markdown">{renderAssistantText(answer)}</div>{sources && <small>Catalog: {sources.catalog_count} · Live results: {sources.live_count} · AI: {sources.ai_provider || "Gemini"}{!sources.live_search_configured ? " · SerpApi key not configured" : ""}</small>}</div>}
              <section className="catalog-section">
                <div className="section-heading"><div><div className="section-kicker">CURATED FOR YOU</div><h2>{activeTab === "saved" ? "Your wishlist" : "Explore products"}</h2></div><button className="refresh-button" onClick={loadProducts}><RefreshCw size={15}/> Refresh</button></div>
                <div className="filter-bar">
                  <div className="search-field"><Search size={17}/><input value={query} onChange={(e)=>setQuery(e.target.value)} onKeyDown={(e)=>e.key==="Enter"&&loadProducts()} placeholder="Search products, brands..."/></div>
                  <select value={category} onChange={(e)=>setCategory(e.target.value)}><option value="">All categories</option>{categories.map(c=><option key={c}>{c}</option>)}</select>
                  <div className="budget-field"><span>₹</span><input type="number" min="0" value={budget} onChange={(e)=>setBudget(e.target.value)} onKeyDown={(e)=>e.key==="Enter"&&loadProducts()} placeholder="Max budget"/></div>
                  <button className="filter-button" onClick={loadProducts}><SlidersHorizontal size={16}/> Apply</button>
                </div>
                {selected.length > 0 && <div className="compare-strip"><span><GitCompareArrows size={16}/> {selected.length} selected (max 4)</span><button onClick={compareSelected}>Compare selected</button><button className="clear-button" onClick={()=>setSelected([])}>Clear</button></div>}
                {error && <div className="error-banner"><span>{error}</span><button onClick={()=>setError("")}><X size={16}/></button></div>}
                {loading ? <div className="loading-state"><span className="spinner large"/> Loading products...</div> :
                  visibleProducts.length ? <div className="product-grid">{visibleProducts.map((p,i)=><ProductCard key={p.id ?? p.product_url ?? `${p.name}-${i}`} product={p} saved={saved.some(x=>(x.product_url||`${x.name}-${x.brand}`)===(p.product_url||`${p.name}-${p.brand}`))} onSave={toggleSaved} selected={selected.includes(p.id ?? p.product_url ?? p.name)} onCompare={toggleCompare}/>)}</div> :
                  <div className="empty-state"><ShoppingBag size={28}/><h3>{activeTab==="saved"?"No saved products yet":"No matching products"}</h3><p>Try another search or ask ShopMate for a recommendation.</p></div>}
              </section>
            </div>
            <aside className="right-column">
              <div className="insight-card"><div className="insight-icon"><Sparkles size={18}/></div><div className="section-kicker">SHOPPING, SIMPLIFIED</div><h3>Less scrolling.<br/><span>Better decisions.</span></h3><p>Let your requirements guide the search. ShopMate brings product options into one place.</p><div className="insight-line"><span>01</span> Describe what you need</div><div className="insight-line"><span>02</span> Review matched products</div><div className="insight-line"><span>03</span> Compare before you buy</div></div>
              <div className="source-card"><div className="source-card-head"><span className="source-indicator"/> DATA SOURCES</div><div className="source-row"><span>Local product catalog</span><b className="enabled">Connected</b></div><div className="source-row"><span>Google Shopping</span><b className={sources?.live_search_configured ? "enabled" : "optional"}>{sources?.live_search_configured ? "Enabled" : "API key optional"}</b></div><div className="source-row"><span>Gemini AI</span><b className={systemStatus?.ai_configured ? "enabled" : "optional"}>{systemStatus?.ai_configured ? "Key detected" : "API key needed"}</b></div><small>Gemini and live shopping require provider API keys in backend/.env.</small></div>
            </aside>
          </div>
          <footer>© 2026 ShopMate AI <span>Built for smarter shopping decisions.</span></footer>
        </div>
      </main>

      {compareItems && <div className="modal-backdrop" onClick={()=>setCompareItems(null)}><div className="compare-modal" onClick={e=>e.stopPropagation()}><div className="modal-heading"><div><span className="section-kicker">SIDE-BY-SIDE</span><h2>Product comparison</h2></div><button className="icon-button" onClick={()=>setCompareItems(null)}><X size={19}/></button></div><div className="compare-table"><div className="compare-row compare-header"><b>Product</b>{compareItems.map(p=><b key={p.id}>{p.name}</b>)}</div>{[["Brand",p=>p.brand],["Category",p=>p.category],["Price",p=>money(p.price)],["Rating",p=>p.rating?`${p.rating} / 5`:"Not listed"],["Description",p=>p.description]].map(([label,get])=><div className="compare-row" key={label}><b>{label}</b>{compareItems.map(p=><span key={p.id}>{get(p)}</span>)}</div>)}</div></div></div>}
    </div>
  );
}
