import React, { useState, useEffect, useCallback, useRef } from 'react';
import { Toaster } from 'react-hot-toast';
import { fetchItems } from './api';
import AddItemForm from './components/AddItemForm';
import InventoryTable from './components/InventoryTable';
import './index.css';

const POLL_INTERVAL_MS = 15000; // Real-time polling every 15 seconds

function App() {
  const [items, setItems] = useState([]);
  const [filteredItems, setFilteredItems] = useState([]);
  const [stats, setStats] = useState({ total: 0, low_stock_count: 0 });
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [filter, setFilter] = useState('all'); // 'all' | 'low' | 'ok'
  const [search, setSearch] = useState('');
  const [lastUpdated, setLastUpdated] = useState(null);
  const pollRef = useRef(null);

  // ── Fetch from API ─────────────────────────────────────────────────
  const loadItems = useCallback(async (silent = false) => {
    if (!silent) setRefreshing(true);
    try {
      const data = await fetchItems();
      setItems(data.items);
      setStats({ total: data.total, low_stock_count: data.low_stock_count });
      setLastUpdated(new Date());
    } catch (err) {
      // Silently ignore poll errors; notify on manual refresh
      if (!silent) console.error('Failed to fetch inventory:', err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  // Initial load
  useEffect(() => {
    loadItems(false);
  }, [loadItems]);

  // ── Real-time polling (bonus feature) ──────────────────────────────
  useEffect(() => {
    pollRef.current = setInterval(() => loadItems(true), POLL_INTERVAL_MS);
    return () => clearInterval(pollRef.current);
  }, [loadItems]);

  // ── Client-side filtering ──────────────────────────────────────────
  useEffect(() => {
    let result = [...items];

    // Text search
    if (search.trim()) {
      const q = search.toLowerCase();
      result = result.filter((i) => i.name.toLowerCase().includes(q));
    }

    // Stock filter
    if (filter === 'low') {
      result = result.filter((i) => i.low_stock);
    } else if (filter === 'ok') {
      result = result.filter((i) => !i.low_stock);
    }

    setFilteredItems(result);
  }, [items, filter, search]);

  // ── Item event handlers ────────────────────────────────────────────
  const handleItemAdded = (newItem) => {
    setItems((prev) => [newItem, ...prev]);
    setStats((s) => ({
      total: s.total + 1,
      low_stock_count: newItem.low_stock ? s.low_stock_count + 1 : s.low_stock_count,
    }));
  };

  const handleStockUpdated = (updatedItem) => {
    setItems((prev) =>
      prev.map((i) => (i.id === updatedItem.id ? updatedItem : i))
    );
    // Recompute low_stock_count
    setStats((s) => {
      const lowCount = items
        .map((i) => (i.id === updatedItem.id ? updatedItem : i))
        .filter((i) => i.low_stock).length;
      return { ...s, low_stock_count: lowCount };
    });
  };

  const handleItemDeleted = (deletedId) => {
    setItems((prev) => {
      const removed = prev.find((i) => i.id === deletedId);
      const next = prev.filter((i) => i.id !== deletedId);
      setStats((s) => ({
        total: s.total - 1,
        low_stock_count:
          removed?.low_stock ? s.low_stock_count - 1 : s.low_stock_count,
      }));
      return next;
    });
  };

  // ── Derived stats ──────────────────────────────────────────────────
  const inStockCount = items.filter((i) => !i.low_stock && i.quantity > 0).length;
  const outOfStockCount = items.filter((i) => i.quantity === 0).length;

  return (
    <div className="app">
      {/* Toast notifications */}
      <Toaster
        position="top-right"
        toastOptions={{
          style: {
            background: '#1e293b',
            color: '#f0f4ff',
            border: '1px solid rgba(255,255,255,0.08)',
            borderRadius: '10px',
            fontSize: '0.88rem',
          },
          success: { iconTheme: { primary: '#22c55e', secondary: '#fff' } },
          error:   { iconTheme: { primary: '#ef4444', secondary: '#fff' } },
        }}
      />

      {/* ── Header ── */}
      <header className="header">
        <div className="header-brand">
          <div className="header-icon">📦</div>
          <div>
            <div className="header-title">Inventory Management</div>
            <div className="header-subtitle">Warehouse Stock Control System</div>
          </div>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div className="rt-indicator">
            <div className="rt-dot" />
            Live · auto-refresh 15s
          </div>
          <div className="header-badge">
            <div className="badge-dot" />
            API Connected
          </div>
        </div>
      </header>

      {/* ── Stats ── */}
      <div className="stats-bar">
        <div className="stat-card">
          <div className="stat-label">Total Items</div>
          <div className="stat-value primary">{stats.total}</div>
          <div className="stat-sub">unique SKUs tracked</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">In Stock</div>
          <div className="stat-value success">{inStockCount}</div>
          <div className="stat-sub">healthy stock level</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">⚠ Low Stock Alerts</div>
          <div className="stat-value warning">{stats.low_stock_count}</div>
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

      {/* ── Add Item Form ── */}
      <AddItemForm onItemAdded={handleItemAdded} />

      {/* ── Inventory Table Section ── */}
      <div className="section-header">
        <h2 className="section-title">
          <span>🗂</span> Inventory ({filteredItems.length})
        </h2>

        <div className="filter-bar">
          {/* Search */}
          <input
            id="search-input"
            type="text"
            className="search-input"
            placeholder="Search items…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            aria-label="Search inventory items"
          />

          {/* Filter chips */}
          {['all', 'low', 'ok'].map((f) => (
            <button
              key={f}
              id={`filter-${f}`}
              className={`filter-chip ${filter === f ? 'active' : ''}`}
              onClick={() => setFilter(f)}
            >
              {f === 'all' ? 'All' : f === 'low' ? '⚠ Low Stock' : '✓ Healthy'}
            </button>
          ))}

          {/* Manual refresh */}
          <button
            id="refresh-btn"
            className={`refresh-btn ${refreshing ? 'spinning' : ''}`}
            onClick={() => loadItems(false)}
            disabled={refreshing}
            aria-label="Refresh inventory"
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
              <polyline points="23 4 23 10 17 10" />
              <polyline points="1 20 1 14 7 14" />
              <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15" />
            </svg>
            {refreshing ? 'Refreshing…' : 'Refresh'}
          </button>
        </div>
      </div>

      {loading ? (
        <div className="loading-wrap">
          <div className="spinner" />
          Loading inventory…
        </div>
      ) : (
        <InventoryTable
          items={filteredItems}
          onStockUpdated={handleStockUpdated}
          onItemDeleted={handleItemDeleted}
        />
      )}

      {/* Last updated timestamp */}
      {lastUpdated && (
        <div style={{ textAlign: 'right', marginTop: '16px', color: 'var(--text-muted)', fontSize: '0.75rem' }}>
          Last synced: {lastUpdated.toLocaleTimeString()}
        </div>
      )}
    </div>
  );
}

export default App;
