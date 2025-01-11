import { ApiService } from './api.js';
const api = new ApiService();

class AuthService {
    constructor() {
        this.isAuthenticated = !!localStorage.getItem(config.STORAGE_KEYS.AUTH_TOKEN);
        this.currentUser = JSON.parse(localStorage.getItem(config.STORAGE_KEYS.USER_DATA) || 'null');
        this.authStateListeners = [];
    }

    addAuthStateListener(listener) {
        this.authStateListeners.push(listener);
    }

    notifyAuthStateChange() {
        this.authStateListeners.forEach(listener => listener(this.isAuthenticated, this.currentUser));
    }

    async login(email, password) {
        try {
            const response = await api.login(email, password);
            if (response.token) {
                localStorage.setItem(config.STORAGE_KEYS.AUTH_TOKEN, response.token);
                localStorage.setItem(config.STORAGE_KEYS.REFRESH_TOKEN, response.refresh_token);
                this.isAuthenticated = true;
                this.currentUser = response.user;
                this.notifyAuthStateChange();
            }
            return response;
        } catch (error) {
            throw error;
        }
    }

    logout() {
        localStorage.removeItem(config.STORAGE_KEYS.AUTH_TOKEN);
        localStorage.removeItem(config.STORAGE_KEYS.REFRESH_TOKEN);
        localStorage.removeItem(config.STORAGE_KEYS.USER_DATA);
        this.isAuthenticated = false;
        this.currentUser = null;
        this.notifyAuthStateChange();
    }

    async googleLogin() {
        try {
            const popup = window.open(
                `${config.API_BASE_URL}${config.AUTH.GOOGLE}`,
                'Google Login',
                'width=500,height=600'
            );

            const messageHandler = async (event) => {
                if (event.origin !== window.location.origin) return;

                if (event.data.type === 'oauth_success') {
                    const { token, user } = event.data;
                    localStorage.setItem(config.STORAGE_KEYS.AUTH_TOKEN, token);
                    this.isAuthenticated = true;
                    this.currentUser = user;
                    this.notifyAuthStateChange();
                    window.removeEventListener('message', messageHandler);
                    popup.close();
                }
            };

            window.addEventListener('message', messageHandler);
        } catch (error) {
            throw error;
        }
    }

    async facebookLogin() {
        try {
            const popup = window.open(
                `${config.API_BASE_URL}${config.AUTH.FACEBOOK}`,
                'Facebook Login',
                'width=500,height=600'
            );

            const messageHandler = async (event) => {
                if (event.origin !== window.location.origin) return;

                if (event.data.type === 'oauth_success') {
                    const { token, user } = event.data;
                    localStorage.setItem(config.STORAGE_KEYS.AUTH_TOKEN, token);
                    this.isAuthenticated = true;
                    this.currentUser = user;
                    this.notifyAuthStateChange();
                    window.removeEventListener('message', messageHandler);
                    popup.close();
                }
            };

            window.addEventListener('message', messageHandler);
        } catch (error) {
            throw error;
        }
    }

    isUserAuthenticated() {
        return this.isAuthenticated;
    }

    getCurrentUser() {
        return this.currentUser;
    }

    async updateProfile(userData) {
        try {
            const response = await api.updateProfile(userData);
            if (response.user) {
                this.currentUser = response.user;
                localStorage.setItem(config.STORAGE_KEYS.USER_DATA, JSON.stringify(response.user));
                this.notifyAuthStateChange();
            }
            return response;
        } catch (error) {
            throw error;
        }
    }

    hasRole(role) {
        return this.currentUser && this.currentUser.roles.includes(role);
    }
}

const auth = new AuthService();
export default auth;
