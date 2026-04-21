import React, { useState, useCallback } from 'react';
import { updateStock, deleteItem } from '../api';
import toast from 'react-hot-toast';

/** Derive a consistent emoji avatar from item name */
const getAvatar = (name = '') => {
  const emojis = ['📦', '🔧', '💡', '🖥️', '⌨️', '🖱️', '📷', '🎧', '🔋', '💾'];
  const idx = name.charCodeAt(0) % emojis.length;
  return emojis[idx];
};

/** Stock status label & class */
const getStockStatus = (item) => {
  if (item.quantity === 0)            return { label: '● Out of Stock', cls: 'out' };
  if (item.low_stock)                 return { label: '▲ Low Stock',    cls: 'low' };
  return                               { label: '✔ In Stock',           cls: 'ok'  };
};

/**
 * InventoryTable
 * Displays items in a styled table with inline stock editing.
 */
function InventoryTable({ items, onStockUpdated, onItemDeleted }) {
  // Map of itemId -> editing quantity value
  const [editValues, setEditValues] = useState({});
  const [loadingIds, setLoadingIds] = useState(new Set());

  const setLoading = (id, val) =>
    setLoadingIds((prev) => {
      const next = new Set(prev);
      val ? next.add(id) : next.delete(id);
      return next;
    });

  const handleQuantityChange = (id, val) => {
    setEditValues((prev) => ({ ...prev, [id]: val }));
  };

  const handleStockUpdate = useCallback(
    async (item) => {
      const rawVal = editValues[item.id];
      if (rawVal === undefined || rawVal === '') {
        toast.error('Enter a quantity first.');
        return;
      }

      const qty = parseInt(rawVal, 10);
      if (isNaN(qty)) {
        toast.error('Quantity must be a number.');
        return;
      }
      // ⚠️ Trick Logic: block on client side too
      if (qty < 0) {
        toast.error('❌ Stock cannot be negative!');
        return;
      }

      setLoading(item.id, true);
      try {
        const updated = await updateStock(item.id, qty);
        onStockUpdated(updated);
        // Clear edit value after success
        setEditValues((prev) => {
          const next = { ...prev };
          delete next[item.id];
          return next;
        });
        if (updated.low_stock) {
          toast(`⚠️ "${updated.name}" is now low stock (${updated.quantity} units)!`, {
            icon: '🟡',
            style: { background: '#1c1c2e', color: '#f59e0b', border: '1px solid rgba(245,158,11,0.3)' },
          });
        } else {
          toast.success(`Stock updated to ${updated.quantity} units.`);
        }
      } catch (err) {
        toast.error(err.message || 'Failed to update stock.');
      } finally {
        setLoading(item.id, false);
      }
    },
    [editValues, onStockUpdated]
  );

  const handleDelete = useCallback(
    async (item) => {
      if (!window.confirm(`Delete "${item.name}" from inventory?`)) return;
      setLoading(item.id, true);
      try {
        await deleteItem(item.id);
        onItemDeleted(item.id);
        toast.success(`"${item.name}" deleted.`);
      } catch (err) {
        toast.error(err.message || 'Failed to delete item.');
      } finally {
        setLoading(item.id, false);
      }
    },
    [onItemDeleted]
  );

  if (items.length === 0) {
    return (
      <div className="table-wrapper">
        <div className="empty-state">
          <div className="empty-icon">📭</div>
          <div className="empty-title">No items found</div>
          <div className="empty-sub">Add your first inventory item using the form above.</div>
        </div>
      </div>
    );
  }

  return (
    <div className="table-wrapper">
      <table className="inventory-table" aria-label="Inventory items">
        <thead>
          <tr>
            <th>Item</th>
            <th>ID</th>
            <th>Status</th>
            <th>Current Stock</th>
            <th>Update Stock</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {items.map((item) => {
            const status = getStockStatus(item);
            const isLoading = loadingIds.has(item.id);
            const editVal = editValues[item.id] ?? '';

            return (
              <tr key={item.id}>
                {/* Name */}
                <td>
                  <div className="item-name">
                    <div className="item-avatar">{getAvatar(item.name)}</div>
                    <span>{item.name}</span>
                  </div>
                </td>

                {/* ID */}
                <td style={{ color: 'var(--text-muted)', fontFamily: 'monospace' }}>
                  #{item.id}
                </td>

                {/* Status badge */}
                <td>
                  <span className={`stock-badge ${status.cls}`}>{status.label}</span>
                </td>

                {/* Current qty */}
                <td>
                  <strong
                    style={{
                      color:
                        item.quantity === 0
                          ? 'var(--accent-danger)'
                          : item.low_stock
                          ? 'var(--accent-warning)'
                          : 'var(--accent-success)',
                      fontSize: '1.05rem',
                    }}
                  >
                    {item.quantity}
                  </strong>
                </td>

                {/* Inline stock editor */}
                <td>
                  <div className="stock-editor">
                    <input
                      id={`stock-input-${item.id}`}
                      type="number"
                      className="stock-input"
                      aria-label={`Update stock for ${item.name}`}
                      min="0"
                      placeholder={String(item.quantity)}
                      value={editVal}
                      onChange={(e) => handleQuantityChange(item.id, e.target.value)}
                      disabled={isLoading}
                    />
                    <button
                      id={`update-btn-${item.id}`}
                      className="btn btn-success btn-sm"
                      onClick={() => handleStockUpdate(item)}
                      disabled={isLoading || editVal === ''}
                      aria-label={`Save stock for ${item.name}`}
                    >
                      {isLoading ? '…' : '✓ Save'}
                    </button>
                  </div>
                </td>

                {/* Delete */}
                <td>
                  <button
                    id={`delete-btn-${item.id}`}
                    className="btn btn-danger btn-sm"
                    onClick={() => handleDelete(item)}
                    disabled={isLoading}
                    aria-label={`Delete ${item.name}`}
                  >
                    🗑 Delete
                  </button>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

export default InventoryTable;
