document.addEventListener('DOMContentLoaded', async () => {
    // Determine Page
    const page = window.location.pathname.split('/').pop();
    if (page !== 'admin.html') return;

    // Simple Auth (Session based)
    const isAuth = sessionStorage.getItem('cms_auth');
    if (!isAuth) {
        const password = prompt("Enter Admin Password (default: admin):");
        if (password === 'admin') {
            sessionStorage.setItem('cms_auth', 'true');
        } else {
            alert("Incorrect Password");
            window.location.href = 'index.html';
            return;
        }
    }

    // Load Data
    let data = {};
    if (window.cmsData) {
        data = window.cmsData; // Use in-memory if already loaded/modified
    } else {
        try {
            const response = await fetch('data/content.json');
            data = await response.json();
            window.cmsData = data; // Store global
        } catch (e) {
            console.error(e);
        }
    }

    renderDashboard();
});

function renderDashboard() {
    const data = window.cmsData;
    const container = document.getElementById('admin-content');

    // Calculate Stats
    const stats = {
        videos: data.videos ? data.videos.length : 0,
        schemes: data.schemes ? data.schemes.length : 0,
        faqs: data.faqs ? data.faqs.length : 0
    };

    let html = `
        <!-- Stats Row -->
        <div style="display: flex; gap: 20px; margin-bottom: 40px;">
            <div class="stat-card feature-card" style="flex: 1; padding: 20px;">
                <h3 style="color: var(--primary); font-size: 32px;">${stats.videos}</h3>
                <p>Videos</p>
            </div>
            <div class="stat-card feature-card" style="flex: 1; padding: 20px;">
                <h3 style="color: var(--accent); font-size: 32px;">${stats.schemes}</h3>
                <p>Schemes</p>
            </div>
            <div class="stat-card feature-card" style="flex: 1; padding: 20px;">
                <h3 style="color: #10b981; font-size: 32px;">${stats.faqs}</h3>
                <p>FAQs</p>
            </div>
        </div>

        <!-- Manager Sections -->
        ${renderSection('Videos', 'videos', data.videos, 'title')}
        ${renderSection('Schemes', 'schemes', data.schemes, 'name')}
        ${renderSection('FAQs', 'faqs', data.faqs, 'question')}
        
        <!-- Actions -->
        <div class="cms-actions" style="margin-top: 40px; border-top: 1px solid var(--border); padding-top: 20px; text-align: center;">
            <p style="color: var(--text-muted); font-size: 14px; margin-bottom: 10px;">
                Changes are saved in your browser memory. Download the file and commit to GitHub to go live.
            </p>
            <button class="btn btn-primary" onclick="downloadJSON()">
                <ion-icon name="cloud-download"></ion-icon> Download content.json
            </button>
        </div>
    `;

    container.innerHTML = html;
}

function renderSection(title, key, items, labelField) {
    return `
        <div class="cms-section" style="margin-top: 40px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                <h2>Manage ${title}</h2>
                <button class="btn btn-secondary" onclick="addItem('${key}')" style="font-size: 12px; padding: 6px 12px;">+ Add New</button>
            </div>
            <div class="cms-list">
                ${items.map((item, index) => `
                    <div class="cms-item">
                        <span>${item[labelField] || 'Untitled'}</span>
                        <div class="actions">
                            <button class="danger" onclick="deleteItem('${key}', ${index})">Delete</button>
                        </div>
                    </div>
                `).join('')}
                ${items.length === 0 ? '<p style="color: var(--text-muted); font-style: italic;">No items found.</p>' : ''}
            </div>
        </div>
    `;
}

// Actions
window.deleteItem = function (key, index) {
    if (!confirm("Are you sure?")) return;
    window.cmsData[key].splice(index, 1);
    renderDashboard();
}

window.addItem = function (key) {
    let newItem = {};
    if (key === 'videos') {
        const title = prompt("Video Title:");
        const id = prompt("YouTube Video ID (e.g. SToefGBjhbM):");
        if (!title || !id) return;
        newItem = { id: Date.now().toString(), title, youtube_id: id, category: "New", lang: "English", description: "Added via CMS" };
    } else if (key === 'schemes') {
        const name = prompt("Scheme Name:");
        if (!name) return;
        newItem = { id: Date.now().toString(), name, description: "Description here", coverage: "TBD", beneficiaries: "All" };
    } else if (key === 'faqs') {
        const q = prompt("Question:");
        const a = prompt("Answer:");
        if (!q || !a) return;
        newItem = { question: q, answer: a };
    }

    window.cmsData[key].push(newItem);
    renderDashboard();
}

window.downloadJSON = function () {
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(window.cmsData, null, 2));
    const downloadAnchorNode = document.createElement('a');
    downloadAnchorNode.setAttribute("href", dataStr);
    downloadAnchorNode.setAttribute("download", "content.json");
    document.body.appendChild(downloadAnchorNode);
    downloadAnchorNode.click();
    downloadAnchorNode.remove();
}
