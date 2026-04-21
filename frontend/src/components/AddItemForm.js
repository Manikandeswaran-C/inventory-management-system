import React, { useState } from 'react';
import { addItem } from '../api';
import toast from 'react-hot-toast';

/**
 * AddItemForm
 * Controlled form to add a new inventory item.
 * Validates: name required, quantity >= 0.
 */
function AddItemForm({ onItemAdded }) {
  const [name, setName] = useState('');
  const [quantity, setQuantity] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();

    const trimmedName = name.trim();
    if (!trimmedName) {
      toast.error('Item name is required.');
      return;
    }

    const qty = parseInt(quantity, 10);
    if (isNaN(qty) || qty < 0) {
      toast.error('Quantity must be a non-negative number.');
      return;
    }

    setLoading(true);
    try {
      const created = await addItem(trimmedName, qty);
      toast.success(`"${created.name}" added to inventory!`);
      onItemAdded(created);
      setName('');
      setQuantity('');
    } catch (err) {
      toast.error(err.message || 'Failed to add item.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="form-card">
      <div className="section-header" style={{ marginBottom: '20px' }}>
        <h2 className="section-title">
          <span>➕</span> Add New Item
        </h2>
      </div>
      <form onSubmit={handleSubmit} id="add-item-form">
        <div className="form-row">
          <div className="form-group">
            <label htmlFor="item-name-input" className="form-label">
              Item Name
            </label>
            <input
              id="item-name-input"
              type="text"
              className="form-input"
              placeholder="e.g. Wireless Mouse"
              value={name}
              onChange={(e) => setName(e.target.value)}
              disabled={loading}
              required
              maxLength={255}
            />
          </div>

          <div className="form-group">
            <label htmlFor="item-quantity-input" className="form-label">
              Initial Quantity
            </label>
            <input
              id="item-quantity-input"
              type="number"
              className="form-input"
              placeholder="0"
              min="0"
              value={quantity}
              onChange={(e) => setQuantity(e.target.value)}
              disabled={loading}
              required
              style={{ width: '140px' }}
            />
          </div>

          <button
            type="submit"
            id="add-item-btn"
            className="btn btn-primary"
            disabled={loading}
            style={{ height: '42px' }}
          >
            {loading ? (
              <>
                <span className="spinner" style={{ width: '14px', height: '14px', borderWidth: '2px' }} />
                Adding…
              </>
            ) : (
              <>+ Add Item</>
            )}
          </button>
        </div>
      </form>
    </div>
  );
}

export default AddItemForm;
