/**
 * GaonBazaar Customer App - API Service
 * Handles all backend communications with error handling and real authentication tokens.
 */
window.GB_API = {
  baseUrl: '',

  getHeaders: function() {
    const headers = {
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    };
    if (window.GB_STATE && window.GB_STATE.user && window.GB_STATE.user.token) {
      headers['Authorization'] = 'Bearer ' + window.GB_STATE.user.token;
    }
    return headers;
  },

  async request(endpoint, options = {}) {
    const url = this.baseUrl + endpoint;
    const config = {
      ...options,
      headers: {
        ...this.getHeaders(),
        ...(options.headers || {})
      }
    };
    try {
      const res = await fetch(url, config);
      if (!res.ok) {
        let errData = {};
        try {
          errData = await res.json();
        } catch (e) {
          errData = { detail: res.statusText || 'Request failed' };
        }
        throw new Error(errData.detail || errData.message || ('HTTP ' + res.status));
      }
      return await res.json();
    } catch (err) {
      console.warn(`[GB_API] ${endpoint} failed:`, err.message);
      throw err;
    }
  },

  // Stores
  async getStores(lat, lng) {
    let url = '/api/stores';
    const params = new URLSearchParams();
    if (lat !== undefined && lat !== null) params.append('lat', lat);
    if (lng !== undefined && lng !== null) params.append('lng', lng);
    const qs = params.toString();
    if (qs) url += '?' + qs;
    return await this.request(url);
  },

  async getStoreProfile(storeId, lat, lng) {
    let url = `/api/stores/${encodeURIComponent(storeId)}`;
    const params = new URLSearchParams();
    if (lat !== undefined && lat !== null) params.append('lat', lat);
    if (lng !== undefined && lng !== null) params.append('lng', lng);
    const qs = params.toString();
    if (qs) url += '?' + qs;
    return await this.request(url);
  },

  async getStoreProducts(storeId, category) {
    let url = `/api/stores/${encodeURIComponent(storeId)}/products`;
    if (category && category !== 'all') {
      url += `?category=${encodeURIComponent(category)}`;
    }
    return await this.request(url);
  },

  // Products
  async getProducts(category, storeId, limit = 50) {
    let url = '/api/products';
    const params = new URLSearchParams();
    if (category && category !== 'all') params.append('category', category);
    if (storeId) params.append('store_id', storeId);
    if (limit) params.append('limit', limit);
    const qs = params.toString();
    if (qs) url += '?' + qs;
    return await this.request(url);
  },

  // Authentication & OTP
  async sendOtp(phone) {
    return await this.request('/api/auth/send-otp', {
      method: 'POST',
      body: JSON.stringify({ phone })
    });
  },

  async verifyOtp(phone, otp) {
    return await this.request('/api/auth/verify', {
      method: 'POST',
      body: JSON.stringify({ phone, otp })
    });
  },

  // Address & Landmark
  async saveLandmark(data) {
    return await this.request('/api/customer/landmark', {
      method: 'POST',
      body: JSON.stringify(data)
    });
  },

  async checkServiceability(lat, lng) {
    return await this.request('/api/customer/location/serviceable', {
      method: 'POST',
      body: JSON.stringify({ lat, lng })
    });
  },

  // Checkout & Orders
  async checkout(orderData) {
    return await this.request('/api/checkout', {
      method: 'POST',
      body: JSON.stringify(orderData)
    });
  },

  async getOrders(phone) {
    const url = `/api/customer/orders?phone=${encodeURIComponent(phone)}`;
    return await this.request(url);
  },

  async getOrderDetails(orderId) {
    return await this.request(`/api/orders/${encodeURIComponent(orderId)}`);
  },

  async cancelOrder(orderId, phone, reason = 'Customer requested cancellation') {
    return await this.request(`/api/orders/${encodeURIComponent(orderId)}/cancel`, {
      method: 'POST',
      body: JSON.stringify({
        order_id: orderId,
        user_phone: phone,
        reason: reason
      })
    });
  },

  // Support
  async createSupportTicket(ticketData) {
    return await this.request('/api/support/ticket', {
      method: 'POST',
      body: JSON.stringify(ticketData)
    });
  },

  async getSupportTickets(phone) {
    return await this.request(`/api/support/tickets?phone=${encodeURIComponent(phone)}`);
  }
};
