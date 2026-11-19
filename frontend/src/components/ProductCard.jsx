import { Heart, ExternalLink, GitCompareArrows, Star } from "lucide-react";

export default function ProductCard({ product, saved, onSave, selected, onCompare }) {
  const price = product.price_label || (product.price ? `₹${Number(product.price).toLocaleString("en-IN")}` : "Check price");
  return (
    <article className="product-card">
      <div className="product-image">
        {product.image_url
          ? <img src={product.image_url} alt={product.name} loading="lazy" />
          : <div className="image-placeholder">{(product.brand || product.name || "S").slice(0, 1).toUpperCase()}</div>}
        <span className={`source-tag ${product.source === "live" ? "live" : ""}`}>
          {product.source === "live" ? "LIVE RESULT" : "CATALOG"}
        </span>
        <button className={`icon-button save-button ${saved ? "active" : ""}`} onClick={() => onSave(product)} aria-label="Save product">
          <Heart size={17} fill={saved ? "currentColor" : "none"} />
        </button>
      </div>
      <div className="product-content">
        <div className="eyebrow">{product.brand || "Marketplace"} · {product.category}</div>
        <h3>{product.name}</h3>
        <div className="product-meta">
          <span className="price">{price}</span>
          {product.rating ? <span className="rating"><Star size={14} fill="currentColor" /> {product.rating}</span> : <span className="muted">No rating</span>}
        </div>
        <p>{product.description || "Product details may vary by seller."}</p>
        <div className="card-actions">
          <label className="compare-check">
            <input type="checkbox" checked={selected} onChange={() => onCompare(product)} />
            <GitCompareArrows size={15} /> Compare
          </label>
          {product.product_url && <a className="merchant-link" href={product.product_url} target="_blank" rel="noreferrer">View deal <ExternalLink size={14} /></a>}
        </div>
      </div>
    </article>
  );
}
