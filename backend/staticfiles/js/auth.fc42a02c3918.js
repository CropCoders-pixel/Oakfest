// Authentication Service
class AuthService {
    constructor() {
        this.isAuthenticated = !!localStorage.getItem(config.STORAGE_KEYS.AUTH_TOKEN);
        this.currentUser = JSON.parse(localStorage.getItem(config.STORAGE_KEYS.USER_DATA) || 'null');
        this.authStateListeners = [];
    }

    // Add listener for auth state changes
    addAuthStateListener(listener) {
        this.authStateListeners.push(listener);
    }

    // Notify all listeners of auth state change
    notifyAuthStateChange() {
        this.authStateListeners.forEach(listener => listener(this.isAuthenticated, this.currentUser));
    }

    // Login user
    async login(email, password) {
        try {
            const response = await api.login(email, password);
            this.isAuthenticated = true;
            this.currentUser = response.user;
            localStorage.setItem(config.STORAGE_KEYS.USER_DATA, JSON.stringify(response.user));
            this.notifyAuthStateChange();
            return response;
        } catch (error) {
            console.error('Login error:', error);
            throw error;
        }
    }

    // Register user
    async register(userData) {
        try {
            const response = await api.register(userData);
            return response;
        } catch (error) {
            console.error('Registration error:', error);
            throw error;
        }
    }

    // Logout user
    logout() {
        localStorage.removeItem(config.STORAGE_KEYS.AUTH_TOKEN);
        localStorage.removeItem(config.STORAGE_KEYS.REFRESH_TOKEN);
        localStorage.removeItem(config.STORAGE_KEYS.USER_DATA);
        this.isAuthenticated = false;
        this.currentUser = null;
        this.notifyAuthStateChange();
    }

    // Google OAuth login
    async googleLogin() {
        const popup = window.open(
            `${config.API_BASE_URL}${config.AUTH.GOOGLE}`,
            'Google Login',
            'width=500,height=600'
        );

        return new Promise((resolve, reject) => {
            window.addEventListener('message', async (event) => {
                if (event.origin !== window.location.origin) return;

                if (event.data.type === 'oauth_success') {
                    const { token, user } = event.data;
                    localStorage.setItem(config.STORAGE_KEYS.AUTH_TOKEN, token);
                    this.isAuthenticated = true;
                    this.currentUser = user;
                    localStorage.setItem(config.STORAGE_KEYS.USER_DATA, JSON.stringify(user));
                    this.notifyAuthStateChange();
                    popup.close();
                    resolve(user);
                } else if (event.data.type === 'oauth_error') {
                    popup.close();
                    reject(new Error(event.data.error));
                }
            });
        });
    }

    // Facebook OAuth login
    async facebookLogin() {
        const popup = window.open(
            `${config.API_BASE_URL}${config.AUTH.FACEBOOK}`,
            'Facebook Login',
            'width=500,height=600'
        );

        return new Promise((resolve, reject) => {
            window.addEventListener('message', async (event) => {
                if (event.origin !== window.location.origin) return;

                if (event.data.type === 'oauth_success') {
                    const { token, user } = event.data;
                    localStorage.setItem(config.STORAGE_KEYS.AUTH_TOKEN, token);
                    this.isAuthenticated = true;
                    this.currentUser = user;
                    localStorage.setItem(config.STORAGE_KEYS.USER_DATA, JSON.stringify(user));
                    this.notifyAuthStateChange();
                    popup.close();
                    resolve(user);
                } else if (event.data.type === 'oauth_error') {
                    popup.close();
                    reject(new Error(event.data.error));
                }
            });
        });
    }

    // Check if user is authenticated
    isUserAuthenticated() {
        return this.isAuthenticated;
    }

    // Get current user
    getCurrentUser() {
        return this.currentUser;
    }

    // Update user profile
    async updateProfile(userData) {
        try {
            const response = await api.request('/user/profile', {
                method: 'PUT',
                body: JSON.stringify(userData),
            });
            this.currentUser = { ...this.currentUser, ...response.user };
            localStorage.setItem(config.STORAGE_KEYS.USER_DATA, JSON.stringify(this.currentUser));
            this.notifyAuthStateChange();
            return response;
        } catch (error) {
            console.error('Profile update error:', error);
            throw error;
        }
    }

    // Check if user has required role
    hasRole(role) {
        return this.currentUser && this.currentUser.roles.includes(role);
    }
}

// Create a singleton instance
const auth = new AuthService();
