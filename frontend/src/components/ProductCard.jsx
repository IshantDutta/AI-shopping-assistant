import { useState } from "react";
import { Heart, ExternalLink, GitCompareArrows, Star, ImageOff } from "lucide-react";

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

function getImageUrl(url) {
  if (!url) return "";
  if (url.startsWith("/")) return url;
  return url;
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
    : getImageUrl(product.image_url);

  const price = product.price_label ||
    (product.price !== null && product.price !== undefined
      ? `₹${Number(product.price).toLocaleString("en-IN")}`
      : "Price unavailable");

  return (
    <article className="product-card">
      <div className="product-image">
        <img
          src={imageUrl}
          alt={`${product.brand || ""} ${product.name}`}
          loading="lazy"
          onError={() => {
            if (!imageFailed) setImageFailed(true);
          }}
        />
        <span className={`source-tag ${product.source === "live" ? "live" : ""}`}>
          {product.source === "live" ? "LIVE RESULT" : "CATALOG"}
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
        <div className="eyebrow">
          {product.brand || "Marketplace"} · {product.category || "Product"}
        </div>
        <h3>{product.name}</h3>
        <div className="product-meta">
          <span className="price">{price}</span>
          {product.rating
            ? <span className="rating"><Star size={14} fill="currentColor" /> {product.rating}</span>
            : <span className="muted">No rating</span>}
        </div>
        <p>{product.description || "Product details may vary by seller."}</p>
        <div className="card-actions">
          <label className="compare-check">
            <input
              type="checkbox"
              checked={selected}
              onChange={() => onCompare(product)}
            />
            <GitCompareArrows size={15} /> Compare
          </label>
          {product.product_url && (
            <a
              className="merchant-link"
              href={product.product_url}
              target="_blank"
              rel="noreferrer"
            >
              View deal <ExternalLink size={14} />
            </a>
          )}
        </div>
      </div>
    </article>
  );
}
