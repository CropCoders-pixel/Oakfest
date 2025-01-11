// Configuration settings for the application
const config = {
    // API endpoints
    API_BASE_URL: 'http://localhost:8000/api',
    
    // Authentication endpoints
    AUTH: {
        LOGIN: '/auth/login',
        REGISTER: '/auth/register',
        LOGOUT: '/auth/logout',
        REFRESH: '/auth/refresh',
        GOOGLE: '/auth/google',
        FACEBOOK: '/auth/facebook',
    },
    
    // Product endpoints
    PRODUCTS: {
        LIST: '/products',
        DETAIL: (id) => `/products/${id}`,
        CATEGORIES: '/products/categories',
        SEARCH: '/products/search',
    },
    
    // Waste management endpoints
    WASTE: {
        REPORT: '/waste/report',
        STATS: '/waste/stats',
        HISTORY: '/waste/history',
    },
    
    // Payment endpoints
    PAYMENT: {
        CREATE: '/payment/create',
        VERIFY: '/payment/verify',
        HISTORY: '/payment/history',
    },
    
    // Notification settings
    NOTIFICATIONS: {
        VAPID_PUBLIC_KEY: 'YOUR_VAPID_PUBLIC_KEY',
        SUBSCRIBE: '/notifications/subscribe',
    },
    
    // Local storage keys
    STORAGE_KEYS: {
        AUTH_TOKEN: 'auth_token',
        REFRESH_TOKEN: 'refresh_token',
        USER_DATA: 'user_data',
        CART: 'shopping_cart',
        THEME: 'app_theme',
    },
    
    // Feature flags
    FEATURES: {
        ENABLE_NOTIFICATIONS: true,
        ENABLE_OFFLINE_MODE: true,
        ENABLE_DARK_MODE: true,
    },
    
    // Theme colors (matching CSS variables)
    THEME: {
        PRIMARY: '#2c7a7b',
        SECONDARY: '#38a169',
        BACKGROUND: '#f7fafc',
        TEXT: '#2d3748',
        TEXT_LIGHT: '#718096',
    },
    
    // Validation rules
    VALIDATION: {
        PASSWORD_MIN_LENGTH: 8,
        NAME_MIN_LENGTH: 2,
        PHONE_REGEX: /^\+?[\d\s-]{10,}$/,
    },
    
    // Error messages
    ERRORS: {
        NETWORK: 'Network error. Please check your connection.',
        AUTH: {
            INVALID_CREDENTIALS: 'Invalid email or password',
            REGISTRATION_FAILED: 'Registration failed. Please try again.',
            TOKEN_EXPIRED: 'Session expired. Please login again.',
        },
        PAYMENT: {
            FAILED: 'Payment failed. Please try again.',
            INVALID: 'Invalid payment details.',
        },
    },
    
    // Success messages
    SUCCESS: {
        REGISTRATION: 'Registration successful! Please login.',
        PAYMENT: 'Payment successful!',
        WASTE_REPORT: 'Waste report submitted successfully!',
    },
};

// Freeze the config object to prevent modifications
Object.freeze(config);
