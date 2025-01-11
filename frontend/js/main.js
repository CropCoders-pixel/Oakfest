document.addEventListener('DOMContentLoaded', () => {
    ui.navigateTo('home');
    ui.updateAuthUI();

    auth.addAuthStateListener((isAuthenticated, user) => {
        ui.updateAuthUI();
    });

    if ('serviceWorker' in navigator && config.FEATURES.ENABLE_NOTIFICATIONS) {
        initializeNotifications();
    }

    if (config.FEATURES.ENABLE_OFFLINE_MODE) {
        initializeOfflineSupport();
    }
});

async function initializeNotifications() {
    try {
        const registration = await navigator.serviceWorker.register('/service-worker.js');
        const subscription = await registration.pushManager.subscribe({
            userVisibleOnly: true,
            applicationServerKey: config.NOTIFICATIONS.VAPID_PUBLIC_KEY
        });

        await api.subscribeToNotifications(subscription);
    } catch (error) {
        console.error('Failed to initialize notifications:', error);
    }
}

async function initializeOfflineSupport() {
    try {
        const registration = await navigator.serviceWorker.register('/service-worker.js');
        console.log('Service Worker registered:', registration);
    } catch (error) {
        console.error('Service Worker registration failed:', error);
    }
}

window.onPaymentSuccess = (response) => {
    api.verifyPayment(response)
        .then(() => {
            ui.showSuccess('Payment successful!');
        })
        .catch(error => {
            ui.showError('Payment verification failed');
            console.error('Payment verification error:', error);
        });
};

window.onPaymentError = (error) => {
    ui.showError('Payment failed. Please try again.');
    console.error('Payment error:', error);
};

function initializeRazorpay(orderData) {
    const options = {
        key: config.PAYMENT.RAZORPAY_KEY,
        amount: orderData.amount,
        currency: orderData.currency,
        name: 'Farm to Table',
        description: 'Purchase from Farm to Table Marketplace',
        order_id: orderData.id,
        handler: function (response) {
            window.onPaymentSuccess(response);
        },
        prefill: {
            name: auth.currentUser?.name,
            email: auth.currentUser?.email,
        },
        theme: {
            color: config.THEME.PRIMARY
        }
    };

    const rzp = new Razorpay(options);
    rzp.on('payment.failed', function (response) {
        window.onPaymentError(response.error);
    });
    
    return rzp;
}

window.initializeRazorpay = initializeRazorpay;
