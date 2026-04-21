/**
 * api.js — Axios client for Inventory Management API
 * All backend calls go through this module (frontend never touches DB).
 */
import axios from 'axios';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const client = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
  timeout: 10000,
});

// ── Response interceptor: shape errors consistently ───────────────
client.interceptors.response.use(
  (res) => res,
  (err) => {
    const detail =
      err.response?.data?.detail ||
      (Array.isArray(err.response?.data?.detail)
        ? err.response.data.detail.map((d) => d.msg).join('; ')
        : null) ||
      err.message ||
      'Unknown error';
    return Promise.reject(new Error(detail));
  }
);

// ── Items API ─────────────────────────────────────────────────────

/** Fetch all items with optional pagination */
export const fetchItems = async (skip = 0, limit = 100) => {
  const { data } = await client.get('/items/', { params: { skip, limit } });
  return data; // { items, total, low_stock_count }
};

/** Add a new inventory item */
export const addItem = async (name, quantity) => {
  const { data } = await client.post('/items/', { name, quantity });
  return data;
};

/** Update stock quantity for an existing item */
export const updateStock = async (itemId, quantity) => {
  const { data } = await client.patch(`/items/${itemId}/stock`, { quantity });
  return data;
};

/** Delete an item by ID */
export const deleteItem = async (itemId) => {
  const { data } = await client.delete(`/items/${itemId}`);
  return data;
};
