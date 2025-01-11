// Configuration settings for the application
const config = {
    // API endpoints
    API_BASE_URL: 'http://localhost:8000/api',
    
    // Authentication endpoints
    AUTH: {
        LOGIN: '/users/login/',
        REGISTER: '/users/register/',
        LOGOUT: '/users/logout/',
        REFRESH: '/users/token/refresh/',
        PROFILE: '/users/profile/',
        TOKEN: '/users/token/'
    },
    
    // Product endpoints
    PRODUCTS: {
        LIST: '/products/',
        DETAIL: (id) => `/products/${id}/`,
        CREATE: '/products/',
        UPDATE: (id) => `/products/${id}/`,
        DELETE: (id) => `/products/${id}/`,
        MY_PRODUCTS: '/products/my_products/',
        MANAGE_STOCK: (id) => `/products/${id}/manage_stock/`,
        REVIEWS: (id) => `/products/${id}/reviews/`,
        CATEGORIES: '/products/categories/'
    },
    
    // Waste Management endpoints
    WASTE: {
        REPORTS: '/waste/reports/',
        CATEGORIES: '/waste/categories/',
        DETAIL: (id) => `/waste/reports/${id}/`,
        CLASSIFY: '/waste/reports/classify/',
        UPLOAD: '/waste/reports/upload/'
    },

    // Leaderboard endpoints
    LEADERBOARD: {
        OVERALL: '/users/leaderboard/',
        WEEKLY: '/users/leaderboard/weekly/',
        IMPACT: '/users/leaderboard/impact/'
    },

    // Storage keys
    STORAGE_KEYS: {
        AUTH_TOKEN: 'auth_token',
        REFRESH_TOKEN: 'refresh_token',
        USER_DATA: 'user_data'
    },

    // Notification settings
    NOTIFICATIONS: {
        DURATION: 5000,
        POSITION: 'top-right'
    },
    
    // Feature flags
    FEATURES: {
        ENABLE_NOTIFICATIONS: true,
        ENABLE_OFFLINE_MODE: true,
        ENABLE_DARK_MODE: true
    },
    
    // Theme colors
    THEME: {
        PRIMARY: '#2c7a7b',
        SECONDARY: '#38a169',
        BACKGROUND: '#f7fafc',
        TEXT: '#2d3748',
        TEXT_LIGHT: '#718096'
    },
    
    // Validation rules
    VALIDATION: {
        PASSWORD_MIN_LENGTH: 8,
        USERNAME_MIN_LENGTH: 3,
        USERNAME_MAX_LENGTH: 30,
        PRODUCT: {
            NAME_MIN_LENGTH: 3,
            NAME_MAX_LENGTH: 100,
            DESCRIPTION_MIN_LENGTH: 10,
            MIN_PRICE: 0,
            MIN_STOCK: 0,
            MAX_FILE_SIZE: 5 * 1024 * 1024, // 5MB
            ALLOWED_IMAGE_TYPES: ['image/jpeg', 'image/png', 'image/webp']
        }
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

export default config;
