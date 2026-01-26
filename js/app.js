document.addEventListener('DOMContentLoaded', async () => {
    // Determine which page we are on
    const page = window.location.pathname.split('/').pop();

    // Fetch Data
    let data = {};
    try {
        const response = await fetch('data/content.json');
        data = await response.json();
    } catch (e) {
        console.error("Failed to load content:", e);
        return;
    }

    // Logic for Videos Page
    if (page === 'videos.html') {
        renderVideos(data.videos);
    }

    // Logic for Schemes Page
    if (page === 'schemes.html') {
        renderSchemes(data.schemes);
    }

    // Logic for Home Page (Features Stats? Or just static)
    // Home is static for now.
});

function renderVideos(videos) {
    const container = document.getElementById('video-grid');
    if (!container) return;

    container.innerHTML = videos.map(v => `
        <div class="video-card feature-card">
            <div class="video-thumbnail">
                <img src="https://img.youtube.com/vi/${v.youtube_id}/hqdefault.jpg" alt="${v.title}">
                <a href="https://www.youtube.com/watch?v=${v.youtube_id}" target="_blank" class="play-btn">
                    <ion-icon name="play-circle"></ion-icon>
                </a>
            </div>
            <div class="video-info">
                <span class="tag">${v.lang}</span>
                <h3 style="margin: 12px 0; font-size: 16px;">${v.title}</h3>
                <p style="font-size: 13px; color: var(--text-muted);">${v.description}</p>
            </div>
        </div>
    `).join('');
}

function renderSchemes(schemes) {
    const container = document.getElementById('schemes-list');
    if (!container) return;

    container.innerHTML = schemes.map(s => `
        <div class="scheme-card feature-card">
            <div class="scheme-header">
                <h3>${s.name}</h3>
                <span class="status-badge">Active</span>
            </div>
            <p style="margin: 12px 0;">${s.description}</p>
            
            <div class="scheme-meta">
                <div>
                    <span class="meta-label">COVERAGE</span>
                    <span>${s.coverage}</span>
                </div>
                <div>
                    <span class="meta-label">BENEFICIARIES</span>
                    <span>${s.beneficiaries}</span>
                </div>
            </div>
            
            <div style="margin-top: 20px;">
                <a href="chat.html" class="btn btn-primary" style="width: 100%; justify-content: center;">Check Eligibility</a>
            </div>
        </div>
    `).join('');
}
