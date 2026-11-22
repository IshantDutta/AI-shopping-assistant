import { useState } from "react";
import {
  Heart,
  ExternalLink,
  GitCompareArrows,
  Star,
  ShoppingCart,
} from "lucide-react";

const FALLBACK_BY_CATEGORY = {
  headphones: "/products/headphones.svg",
  earbuds: "/products/earbuds.svg",
  "gaming headset": "/products/gaming-headset.svg",
  laptops: "/products/laptop.svg",
  accessories: "/products/accessories.svg",
};

function getFallback(product) {
  const category = (product.category || "").toLowerCase();
  return FALLBACK_BY_CATEGORY[category] || "/products/accessories.svg";
}

function formatPrice(product) {
  if (product.price_label && !product.price_label.includes("�")) {
    return product.price_label;
  }
  if (product.price !== null && product.price !== undefined) {
    return `₹${Number(product.price).toLocaleString("en-IN")}`;
  }
  return "Price unavailable";
}

export default function ProductCard({
  product,
  saved,
  onSave,
  selected,
  onCompare,
}) {
  const [imageFailed, setImageFailed] = useState(false);
  const imageUrl = imageFailed || !product.image_url
    ? getFallback(product)
    : product.image_url;

  const isLive = product.source === "live";
  const merchant = product.brand || "Online marketplace";
  const hasPurchaseLink = Boolean(product.product_url);

  return (
    <article className="product-card">
      <div className="product-image">
        <img
          src={imageUrl}
          alt={`${merchant} ${product.name}`}
          loading="lazy"
          onError={() => setImageFailed(true)}
        />
        <span className={`source-tag ${isLive ? "live" : ""}`}>
          {isLive ? "LIVE PRICE" : "CATALOG"}
        </span>
        <button
          className={`icon-button save-button ${saved ? "active" : ""}`}
          onClick={() => onSave(product)}
          aria-label={saved ? "Remove from wishlist" : "Save product"}
          title={saved ? "Remove from wishlist" : "Save to wishlist"}
        >
          <Heart size={17} fill={saved ? "currentColor" : "none"} />
        </button>
      </div>

      <div className="product-content">
        <div className="eyebrow merchant-eyebrow">{merchant}</div>
        <h3 title={product.name}>{product.name}</h3>
        <div className="product-meta">
          <span className="price">{formatPrice(product)}</span>
          {product.rating
            ? <span className="rating"><Star size={14} fill="currentColor" /> {product.rating}</span>
            : <span className="muted">Rating unavailable</span>}
        </div>
        <p>{product.description || "Check the seller page for product details, stock and delivery."}</p>

        <div className="card-actions">
          <label className="compare-check">
            <input
              type="checkbox"
              checked={selected}
              onChange={() => onCompare(product)}
            />
            <GitCompareArrows size={15} /> Compare
          </label>
          {hasPurchaseLink ? (
            <a
              className="buy-now-link"
              href={product.product_url}
              target="_blank"
              rel="noopener noreferrer"
              aria-label={`Buy ${product.name} from ${merchant}`}
            >
              <ShoppingCart size={14} />
              Buy now
              <ExternalLink size={13} />
            </a>
          ) : (
            <span className="muted no-link">Link unavailable</span>
          )}
        </div>
      </div>
    </article>
  );
}
