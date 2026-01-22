document.addEventListener('DOMContentLoaded', () => {
    // Current Page Detection
    const path = window.location.pathname;
    const page = path.split('/').pop() || 'index.html';

    // Navbar HTML
    const navbarHTML = `
    <nav class="main-nav">
        <div class="nav-container">
            <a href="index.html" class="nav-logo">
                <span class="logo-icon">🩺</span>
                <span class="logo-text">Bharat Health Policy</span>
            </a>
            <button class="mobile-toggle" aria-label="Toggle Menu">
                <ion-icon name="menu-outline"></ion-icon>
            </button>
            <div class="nav-links">
                <a href="index.html" class="${page === 'index.html' ? 'active' : ''}">Home</a>
                <a href="schemes.html" class="${page === 'schemes.html' ? 'active' : ''}">Schemes</a>
                <a href="videos.html" class="${page === 'videos.html' ? 'active' : ''}">Video Hub</a>
                <a href="chat.html" class="${page === 'chat.html' ? 'active' : ''} chat-highlight">AI Assistant</a>
                <a href="admin.html" class="${page === 'admin.html' ? 'active' : ''} admin-link">Admin</a>
            </div>
        </div>
    </nav>
    `;

    // Footer HTML
    const footerHTML = `
    <footer class="main-footer">
        <div class="footer-content">
            <div class="footer-section">
                <h4>Bharat Health Policy Genius</h4>
                <p>AI-Powered Assistant for PM-JAY & NHM</p>
            </div>
            <div class="footer-section">
                <h4>Quick Links</h4>
                <a href="sitemap.html">Sitemap</a>
                <a href="disclaimer.html">Disclaimer</a>
                <a href="privacy.html">Privacy Policy</a>
            </div>
            <div class="footer-section">
                <p class="disclaimer">Note: This is an educational tool, not an official government website.</p>
                <p>&copy; 2024 Aryan IT Solutions</p>
            </div>
        </div>
    </footer>
    `;

    // Inject Navbar
    const appContainer = document.querySelector('.app-container') || document.body;
    // We insert navbar at the top of body usually
    document.body.insertAdjacentHTML('afterbegin', navbarHTML);

    // Inject Footer (only if not chat page, usually)
    if (page !== 'chat.html') {
        document.body.insertAdjacentHTML('beforeend', footerHTML);
    }

    // Mobile Menu Toggle
    const toggleBtn = document.querySelector('.mobile-toggle');
    const navLinks = document.querySelector('.nav-links');

    if (toggleBtn) {
        toggleBtn.addEventListener('click', () => {
            navLinks.classList.toggle('show');
        });
    }
});
