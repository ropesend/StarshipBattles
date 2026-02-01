const state = {
    planets: {},
    filter: 'ALL'
};

const CATEGORIES = [
    "CONTINENTAL", "ARID", "PELAGIC", "MAGMA", "CRYOPLANET",
    "BARREN", "JOVIAN", "ICE_GIANT", "CHTHONIAN", "ICE_DWARF", "PLANETOID"
];

// DOM Elements
const feedContainer = document.getElementById('feed');
const typeFilter = document.getElementById('typeFilter');
const statsContainer = document.getElementById('stats');

async function init() {
    await fetchPlanets();

    typeFilter.addEventListener('change', (e) => {
        state.filter = e.target.value;
        renderFeed();
    });

    renderFeed();
}

async function fetchPlanets() {
    try {
        const response = await fetch('/api/planets');
        state.planets = await response.json();
    } catch (err) {
        console.error('Failed to fetch planets:', err);
        feedContainer.innerHTML = '<div class="loading-state">Error connecting to server.</div>';
    }
}

function renderFeed() {
    feedContainer.innerHTML = '';
    const entries = Object.entries(state.planets);

    const filtered = state.filter === 'ALL'
        ? entries
        : entries.filter(([_, type]) => type === state.filter);

    if (filtered.length === 0) {
        feedContainer.innerHTML = `<div class="loading-state">No planets found for "${state.filter}"</div>`;
        return;
    }

    // Optimization: Create a fragment for faster DOM injection
    const fragment = document.createDocumentFragment();

    filtered.forEach(([filename, type]) => {
        const card = createPlanetCard(filename, type);
        fragment.appendChild(card);
    });

    feedContainer.appendChild(fragment);
    updateStats(filtered.length);
}

function createPlanetCard(filename, currentType) {
    const card = document.createElement('div');
    card.className = 'planet-card';
    card.id = `card-${filename.replace(/\./g, '-')}`;

    // HTML Structure
    card.innerHTML = `
        <div class="image-box">
            <img src="/images/${filename}" loading="lazy" alt="${filename}">
        </div>
        <div class="card-info">
            <div class="card-header">
                <h2>${filename}</h2>
                <div class="current-type-badge">${formatCategoryName(currentType)}</div>
            </div>
            <div class="reassign-section">
                <div class="reassign-title">Reassign Type</div>
                <div class="btn-grid">
                    ${CATEGORIES.map(cat => `
                        <button class="class-btn ${cat === currentType ? 'active' : ''}" 
                                onclick="updateClassification('${filename}', '${cat}')"
                                data-type="${cat}">
                            ${formatCategoryName(cat)}
                        </button>
                    `).join('')}
                </div>
            </div>
        </div>
    `;

    return card;
}

async function updateClassification(filename, newType) {
    const card = document.getElementById(`card-${filename.replace(/\./g, '-')}`);
    const badge = card.querySelector('.current-type-badge');
    const buttons = card.querySelectorAll('.class-btn');

    try {
        const response = await fetch('/api/update', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                filename: filename,
                new_type: newType
            })
        });

        if (response.ok) {
            // Update local state
            state.planets[filename] = newType;

            // UI Feedback
            badge.textContent = formatCategoryName(newType);
            buttons.forEach(btn => {
                btn.classList.toggle('active', btn.dataset.type === newType);
            });

            // If we are filtering, we might need to remove this card if it no longer matches
            if (state.filter !== 'ALL' && state.filter !== newType) {
                card.style.opacity = '0';
                card.style.transform = 'scale(0.95)';
                setTimeout(() => card.remove(), 300);
            }
        }
    } catch (err) {
        console.error('Update failed:', err);
    }
}

function updateStats(count) {
    statsContainer.textContent = `Showing ${count} planets`;
}

function formatCategoryName(cat) {
    return cat.replace('_', ' ').toLowerCase().split(' ').map(s => s.charAt(0).toUpperCase() + s.substring(1)).join(' ');
}

init();
