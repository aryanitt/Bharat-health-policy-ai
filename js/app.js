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
        <div class="video-card feature-card" style="text-align: left; padding: 0; overflow: hidden;">
            <div class="video-thumbnail" style="height: 180px; background: #000; position: relative;">
                <img src="https://img.youtube.com/vi/${v.youtube_id}/hqdefault.jpg" style="width: 100%; height: 100%; object-fit: cover;">
                <a href="https://www.youtube.com/watch?v=${v.youtube_id}" target="_blank" class="play-btn" style="position: absolute; top:50%; left:50%; transform:translate(-50%, -50%); color: white; font-size: 48px;"><ion-icon name="play-circle"></ion-icon></a>
            </div>
            <div class="video-info" style="padding: 20px;">
                <span class="tag" style="background: #eff6ff; color: var(--primary); padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: 600;">${v.lang}</span>
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
        <div class="scheme-card feature-card" style="text-align: left; margin-bottom: 20px;">
            <div style="display: flex; justify-content: space-between; align-items: start;">
                <h3 style="color: var(--primary); font-size: 20px;">${s.name}</h3>
                <span style="background: #ecfdf5; color: #059669; padding: 6px 12px; border-radius: 20px; font-size: 12px; font-weight: 600;">Active</span>
            </div>
            <p style="margin: 12px 0;">${s.description}</p>
            
            <div class="scheme-meta" style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-top: 20px; border-top: 1px solid var(--border); padding-top: 20px;">
                <div>
                    <strong style="display: block; font-size: 12px; color: var(--text-muted);">COVERAGE</strong>
                    <span>${s.coverage}</span>
                </div>
                <div>
                    <strong style="display: block; font-size: 12px; color: var(--text-muted);">BENEFICIARIES</strong>
                    <span>${s.beneficiaries}</span>
                </div>
            </div>
            
            <div style="margin-top: 20px;">
                <a href="chat.html" class="btn btn-primary" style="width: 100%; justify-content: center;">Check Eligibility</a>
            </div>
        </div>
    `).join('');
}
