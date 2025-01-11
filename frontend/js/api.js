class ApiService {
    constructor() {
        this.baseUrl = config.API_BASE_URL;
    }

    getAuthToken() {
        return localStorage.getItem(config.STORAGE_KEYS.AUTH_TOKEN);
    }

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
        try {
            const response = await this.request('/api/users/register/', {
                method: 'POST',
                body: JSON.stringify(userData),
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (response.error) {
                throw new Error(response.error);
            }

            return response;
        } catch (error) {
            if (error.message.includes('duplicate')) {
                throw new Error('Email already exists. Please use a different email.');
            }
            throw error;
        }
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

    async getFarmerProducts() {
        const response = await this.request('/api/products/my-products/');
        return response;
    }

    async addProduct(formData) {
        const response = await this.request('/api/products/', {
            method: 'POST',
            body: formData,
        });
        return response;
    }

    async updateProduct(productId, formData) {
        const response = await this.request(`/api/products/${productId}/`, {
            method: 'PATCH',
            body: formData,
        });
        return response;
    }

    async deleteProduct(productId) {
        await this.request(`/api/products/${productId}/`, {
            method: 'DELETE',
        });
    }

    async reportWaste(wasteData) {
        return await this.request(config.WASTE.REPORT, {
            method: 'POST',
            body: JSON.stringify(wasteData),
        });
    }

    async getWasteStats() {
        return await this.request(config.WASTE.STATS);
    }

    async createPayment(orderData) {
        return await this.request(config.PAYMENT.CREATE, {
            method: 'POST',
            body: JSON.stringify({
                amount: orderData.amount,
                payment_method: orderData.payment_method || 'razorpay',
                farmer_phone: orderData.farmer_phone
            })
        });
    }

    async verifyPayment(paymentData) {
        return await this.request(config.PAYMENT.VERIFY, {
            method: 'POST',
            body: JSON.stringify(paymentData),
        });
    }

    async subscribeToNotifications(subscription) {
        return await this.request(config.NOTIFICATIONS.SUBSCRIBE, {
            method: 'POST',
            body: JSON.stringify(subscription),
        });
    }
}

const api = new ApiService();
