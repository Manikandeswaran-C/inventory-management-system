import React from 'react';

/**
 * StatsBar — shows summary statistics at a glance.
 * Props: total, lowStockCount, inStockCount, outOfStockCount
 */
function StatsBar({ total = 0, lowStockCount = 0, inStockCount = 0, outOfStockCount = 0 }) {
  return (
    <div className="stats-bar">
      <div className="stat-card">
        <div className="stat-label">Total Items</div>
        <div className="stat-value primary">{total}</div>
        <div className="stat-sub">unique SKUs tracked</div>
      </div>

      <div className="stat-card">
        <div className="stat-label">In Stock</div>
        <div className="stat-value success">{inStockCount}</div>
        <div className="stat-sub">healthy stock level</div>
      </div>

      <div className="stat-card">
        <div className="stat-label">⚠ Low Stock Alerts</div>
        <div className="stat-value warning">{lowStockCount}</div>
        <div className="stat-sub">≤ 10 units — needs restock</div>
      </div>

      <div className="stat-card">
        <div className="stat-label">Out of Stock</div>
        <div className="stat-value" style={{ color: 'var(--accent-danger)' }}>
          {outOfStockCount}
        </div>
        <div className="stat-sub">zero quantity items</div>
      </div>
    </div>
  );
}

export default StatsBar;
