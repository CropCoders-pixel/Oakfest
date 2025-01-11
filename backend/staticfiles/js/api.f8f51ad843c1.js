// API Service for handling all API calls
class ApiService {
    constructor() {
        this.baseUrl = config.API_BASE_URL;
    }

    // Helper method to get auth token
    getAuthToken() {
        return localStorage.getItem(config.STORAGE_KEYS.AUTH_TOKEN);
    }

    // Helper method to build headers
    getHeaders() {
        const headers = {
            'Content-Type': 'application/json',
        };
        const token = this.getAuthToken();
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }
        return headers;
    }

    // Generic request method
    async request(endpoint, options = {}) {
        try {
            const url = this.baseUrl + endpoint;
            const response = await fetch(url, {
                ...options,
                headers: this.getHeaders(),
            });

            if (!response.ok) {
                if (response.status === 401) {
                    // Token expired, try to refresh
                    await this.refreshToken();
                    // Retry the request
                    return this.request(endpoint, options);
                }
                throw new Error(response.statusText);
            }

            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }

    // Authentication methods
    async login(email, password) {
        const response = await this.request(config.AUTH.LOGIN, {
            method: 'POST',
            body: JSON.stringify({ email, password }),
        });
        if (response.token) {
            localStorage.setItem(config.STORAGE_KEYS.AUTH_TOKEN, response.token);
            localStorage.setItem(config.STORAGE_KEYS.REFRESH_TOKEN, response.refresh_token);
        }
        return response;
    }

    async register(userData) {
        return await this.request(config.AUTH.REGISTER, {
            method: 'POST',
            body: JSON.stringify(userData),
        });
    }

    async refreshToken() {
        const refresh_token = localStorage.getItem(config.STORAGE_KEYS.REFRESH_TOKEN);
        if (!refresh_token) {
            throw new Error('No refresh token available');
        }

        const response = await this.request(config.AUTH.REFRESH, {
            method: 'POST',
            body: JSON.stringify({ refresh_token }),
        });

        if (response.token) {
            localStorage.setItem(config.STORAGE_KEYS.AUTH_TOKEN, response.token);
        }
        return response;
    }

    // Product methods
    async getProducts(filters = {}) {
        const queryParams = new URLSearchParams(filters).toString();
        return await this.request(`${config.PRODUCTS.LIST}?${queryParams}`);
    }

    async getProductDetails(productId) {
        return await this.request(config.PRODUCTS.DETAIL(productId));
    }

    async searchProducts(query) {
        return await this.request(`${config.PRODUCTS.SEARCH}?q=${query}`);
    }

    // Waste management methods
    async reportWaste(wasteData) {
        return await this.request(config.WASTE.REPORT, {
            method: 'POST',
            body: JSON.stringify(wasteData),
        });
    }

    async getWasteStats() {
        return await this.request(config.WASTE.STATS);
    }

    // Payment methods
    async createPayment(orderData) {
        return await this.request(config.PAYMENT.CREATE, {
            method: 'POST',
            body: JSON.stringify(orderData),
        });
    }

    async verifyPayment(paymentData) {
        return await this.request(config.PAYMENT.VERIFY, {
            method: 'POST',
            body: JSON.stringify(paymentData),
        });
    }

    // Notification methods
    async subscribeToNotifications(subscription) {
        return await this.request(config.NOTIFICATIONS.SUBSCRIBE, {
            method: 'POST',
            body: JSON.stringify(subscription),
        });
    }
}

// Create a singleton instance
const api = new ApiService();
