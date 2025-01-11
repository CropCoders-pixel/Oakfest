// UI Service for handling UI components and interactions
class UiService {
    constructor() {
        this.currentPage = 'home';
        this.modals = {};
        this.templates = {};
        this.initializeTemplates();
        this.initializeModals();
        this.setupEventListeners();
    }

    // Initialize page templates
    initializeTemplates() {
        ['home', 'products', 'waste'].forEach(page => {
            const template = document.getElementById(`${page}-template`);
            if (template) {
                this.templates[page] = template.content.cloneNode(true);
            }
        });
    }

    // Initialize modal components
    initializeModals() {
        // Get modal elements
        this.modals.login = document.getElementById('loginModal');
        this.modals.register = document.getElementById('registerModal');

        // Add close button handlers
        document.querySelectorAll('.modal .close').forEach(closeBtn => {
            closeBtn.addEventListener('click', () => {
                this.closeAllModals();
            });
        });

        // Close modal when clicking outside
        window.addEventListener('click', (event) => {
            if (event.target.classList.contains('modal')) {
                this.closeAllModals();
            }
        });
    }

    // Setup event listeners
    setupEventListeners() {
        // Navigation links
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const page = e.target.closest('.nav-link').dataset.page;
                this.navigateTo(page);
            });
        });

        // Auth buttons
        document.getElementById('loginBtn').addEventListener('click', () => this.showModal('login'));
        document.getElementById('registerBtn').addEventListener('click', () => this.showModal('register'));

        // Form submissions
        document.getElementById('loginForm').addEventListener('submit', this.handleLogin.bind(this));
        document.getElementById('registerForm').addEventListener('submit', this.handleRegister.bind(this));
    }

    // Navigation
    navigateTo(page) {
        this.currentPage = page;
        const mainContent = document.getElementById('mainContent');
        mainContent.innerHTML = '';

        if (this.templates[page]) {
            mainContent.appendChild(this.templates[page].cloneNode(true));
            this.initializePageSpecificFeatures(page);
        }

        // Update active nav link
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.toggle('active', link.dataset.page === page);
        });
    }

    // Initialize page-specific features
    initializePageSpecificFeatures(page) {
        switch (page) {
            case 'products':
                this.initializeProductsPage();
                break;
            case 'waste':
                this.initializeWastePage();
                break;
        }
    }

    // Products page initialization
    async initializeProductsPage() {
        const productsGrid = document.getElementById('productsGrid');
        if (!productsGrid) return;

        try {
            const products = await api.getProducts();
            this.renderProducts(products);

            // Initialize filters
            document.getElementById('categoryFilter').addEventListener('change', this.handleProductFilter.bind(this));
            document.getElementById('priceRange').addEventListener('input', this.handleProductFilter.bind(this));
            document.getElementById('sortBy').addEventListener('change', this.handleProductFilter.bind(this));
        } catch (error) {
            this.showError('Failed to load products');
        }
    }

    // Waste management page initialization
    initializeWastePage() {
        const wasteForm = document.getElementById('wasteForm');
        if (!wasteForm) return;

        wasteForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(wasteForm);
            const wasteData = Object.fromEntries(formData.entries());

            try {
                await api.reportWaste(wasteData);
                this.showSuccess('Waste report submitted successfully!');
                wasteForm.reset();
                this.updateWasteStats();
            } catch (error) {
                this.showError('Failed to submit waste report');
            }
        });

        this.updateWasteStats();
    }

    // Modal handling
    showModal(modalName) {
        this.closeAllModals();
        if (this.modals[modalName]) {
            this.modals[modalName].style.display = 'block';
        }
    }

    closeAllModals() {
        Object.values(this.modals).forEach(modal => {
            if (modal) modal.style.display = 'none';
        });
    }

    // Form handling
    async handleLogin(e) {
        e.preventDefault();
        const email = document.getElementById('loginEmail').value;
        const password = document.getElementById('loginPassword').value;

        try {
            await auth.login(email, password);
            this.closeAllModals();
            this.updateAuthUI();
            this.showSuccess('Login successful!');
        } catch (error) {
            this.showError('Login failed. Please check your credentials.');
        }
    }

    async handleRegister(e) {
        e.preventDefault();
        const formData = new FormData(e.target);
        const userData = Object.fromEntries(formData.entries());

        try {
            await auth.register(userData);
            this.closeAllModals();
            this.showSuccess('Registration successful! Please login.');
            this.showModal('login');
        } catch (error) {
            this.showError('Registration failed. Please try again.');
        }
    }

    // UI Updates
    updateAuthUI() {
        const isAuthenticated = auth.isUserAuthenticated();
        const user = auth.getCurrentUser();

        document.querySelectorAll('.auth-dependent').forEach(el => {
            el.style.display = isAuthenticated ? 'block' : 'none';
        });

        document.querySelectorAll('.guest-only').forEach(el => {
            el.style.display = isAuthenticated ? 'none' : 'block';
        });

        if (isAuthenticated && user) {
            document.getElementById('userProfile').textContent = user.name;
        }
    }

    // Notifications
    showSuccess(message) {
        this.showNotification(message, 'success');
    }

    showError(message) {
        this.showNotification(message, 'error');
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;

        // Add to document
        document.body.appendChild(notification);

        // Remove after delay
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }

    // Product rendering
    renderProducts(products) {
        const productsGrid = document.getElementById('productsGrid');
        if (!productsGrid) return;

        productsGrid.innerHTML = products.map(product => `
            <div class="product-card soft-ui-card">
                <img src="${product.image}" alt="${product.name}">
                <h3>${product.name}</h3>
                <p>${product.description}</p>
                <div class="product-price">₹${product.price}</div>
                <button class="btn-primary" onclick="ui.addToCart(${product.id})">
                    Add to Cart
                </button>
            </div>
        `).join('');
    }

    // Cart handling
    addToCart(productId) {
        if (!auth.isUserAuthenticated()) {
            this.showModal('login');
            return;
        }

        // Add to cart logic here
        this.showSuccess('Product added to cart!');
    }

    // Waste statistics update
    async updateWasteStats() {
        try {
            const stats = await api.getWasteStats();
            document.querySelectorAll('.stat-value').forEach(el => {
                const statType = el.dataset.stat;
                if (stats[statType]) {
                    el.textContent = stats[statType];
                }
            });
        } catch (error) {
            console.error('Failed to update waste stats:', error);
        }
    }
}

// Create a singleton instance
const ui = new UiService();
