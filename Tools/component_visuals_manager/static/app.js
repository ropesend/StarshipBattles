let state = {
    components: [],
    metadata: { tags: [], assignments: {} },
    images: [],
    selectedComponentId: null,
    selectedSpriteIndex: null,
    filters: {}, // tag: 'include' | 'exclude' | 'ignore'
    searchTerm: ''
};

// --- Initialization ---
async function init() {
    try {
        const res = await fetch('/api/init');
        const data = await res.json();
        state.components = data.components;
        state.metadata = data.metadata;
        state.images = data.images;
        
        // Initialize filters as 'ignore'
        state.metadata.tags.forEach(tag => {
            state.filters[tag] = 'ignore';
        });

        renderAll();
    } catch (e) {
        console.error("Init failed:", e);
        showStatus("Error loading data", "error");
    }
}

// --- Rendering ---
function renderAll() {
    renderComponentList();
    renderTagFilters();
    renderImageGrid();
}

function renderComponentList() {
    const list = document.getElementById('componentList');
    const searchTerm = state.searchTerm.toLowerCase();
    
    const filtered = state.components.filter(c => 
        c.name.toLowerCase().includes(searchTerm) || 
        c.id.toLowerCase().includes(searchTerm)
    );

    document.getElementById('compCount').textContent = filtered.length;

    list.innerHTML = filtered.map(c => `
        <div class="comp-item ${state.selectedComponentId === c.id ? 'active' : ''}" onclick="selectComponent('${c.id}')">
            <img src="${getImageUrl(c.sprite_index)}" alt="${c.name}">
            <div class="comp-info">
                <div class="comp-name">${c.name}</div>
                <div class="comp-id">${c.id}</div>
                <div class="comp-sprite">Index: ${c.sprite_index}</div>
            </div>
        </div>
    `).join('');
}

function renderTagFilters() {
    const list = document.getElementById('tagFilterList');
    list.innerHTML = state.metadata.tags.map(tag => `
        <div class="tag-filter-item">
            <div class="tag-btn ${state.filters[tag]}" onclick="toggleFilter('${tag}')">${tag}</div>
        </div>
    `).join('');
}

function renderImageGrid() {
    const grid = document.getElementById('imageGrid');
    const filteredImages = getFilteredImages();
    
    document.getElementById('imageCount').textContent = filteredImages.length;
    
    grid.innerHTML = filteredImages.map(img => {
        const index = parseInt(img.match(/_(\d+)\./)[1]);
        const isAssigned = state.selectedComponentId && 
            state.components.find(c => c.id === state.selectedComponentId)?.sprite_index === index;
            
        return `
            <div class="image-card ${isAssigned ? 'assigned' : ''}" onclick="selectImage(${index})">
                <img src="/assets/${img}" loading="lazy">
                <div class="index-label">${img} (Index: ${index})</div>
            </div>
        `;
    }).join('');
}

function getFilteredImages() {
    const activeIncludes = Object.keys(state.filters).filter(t => state.filters[t] === 'include');
    const activeExcludes = Object.keys(state.filters).filter(t => state.filters[t] === 'exclude');

    return state.images.filter(imgName => {
        const index = parseInt(imgName.match(/_(\d+)\./)[1]);
        const imgTags = state.metadata.assignments[index.toString()] || [];
        
        // Exclude logic: Must NOT have any 'exclude' tags
        const hasExcluded = activeExcludes.some(t => imgTags.includes(t));
        if (hasExcluded) return false;

        // Include logic: Must have ALL 'include' tags (AND logic)
        const hasAllIncludes = activeIncludes.every(t => imgTags.includes(t));
        if (!hasAllIncludes) return false;

        return true;
    });
}

// --- Interaction ---
function selectComponent(id) {
    state.selectedComponentId = id;
    const comp = state.components.find(c => c.id === id);
    if (comp) {
        state.selectedSpriteIndex = comp.sprite_index;
    }
    renderAll();
    showDetailPanel();
}

async function selectImage(index) {
    state.selectedSpriteIndex = index;
    
    if (state.selectedComponentId) {
        showStatus("Saving Component...", "saving");
        try {
            const res = await fetch('/api/component/image', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ component_id: state.selectedComponentId, sprite_index: index })
            });
            if (res.ok) {
                // Update local state
                const comp = state.components.find(c => c.id === state.selectedComponentId);
                if (comp) comp.sprite_index = index;
                showStatus("Saved!", "success");
                renderAll();
            }
        } catch (e) {
            showStatus("Save Failed", "error");
        }
    }
    showDetailPanel();
}

function toggleFilter(tag) {
    const current = state.filters[tag];
    if (current === 'ignore') state.filters[tag] = 'include';
    else if (current === 'include') state.filters[tag] = 'exclude';
    else state.filters[tag] = 'ignore';
    renderAll();
}

async function toggleImageTag(tag) {
    if (state.selectedSpriteIndex === null) return;
    
    let imgTags = state.metadata.assignments[state.selectedSpriteIndex.toString()] || [];
    if (imgTags.includes(tag)) {
        imgTags = imgTags.filter(t => t !== tag);
    } else {
        imgTags.push(tag);
    }
    
    state.metadata.assignments[state.selectedSpriteIndex.toString()] = imgTags;
    
    showStatus("Saving tags...", "saving");
    try {
        const res = await fetch('/api/image/tags', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ sprite_index: state.selectedSpriteIndex, tags: imgTags })
        });
        if (res.ok) {
            showStatus("Tags Saved", "success");
            renderAll();
            showDetailPanel();
        }
    } catch (e) {
        showStatus("Tags Failed", "error");
    }
}

// --- Detail Panel ---
function showDetailPanel() {
    const panel = document.getElementById('selectionDetail');
    if (state.selectedSpriteIndex === null) {
        panel.classList.add('hidden');
        return;
    }
    
    panel.classList.remove('hidden');
    const indexStr = state.selectedSpriteIndex.toString().padStart(3, '0');
    const imgName = state.images.find(i => i.includes(`Comp_${indexStr}`));
    
    document.getElementById('detailImg').src = `/assets/${imgName}`;
    document.getElementById('detailIndex').textContent = `Index: ${state.selectedSpriteIndex}`;
    
    const imgTags = state.metadata.assignments[state.selectedSpriteIndex.toString()] || [];
    const tagCloud = document.getElementById('detailTags');
    tagCloud.innerHTML = state.metadata.tags.map(tag => `
        <div class="tag-chip ${imgTags.includes(tag) ? 'active' : ''}" onclick="toggleImageTag('${tag}')">
            ${tag}
        </div>
    `).join('');
    
    const usage = state.components.filter(c => c.sprite_index === state.selectedSpriteIndex);
    const usageList = document.getElementById('detailUsage');
    usageList.innerHTML = usage.length > 0 
        ? usage.map(c => `<div>${c.name} (${c.id})</div>`).join('')
        : '<div style="color: grey">Not assigned to any component</div>';
}

// --- Utils ---
function getImageUrl(index) {
    if (index === undefined || index === null) return '';
    const indexStr = index.toString().padStart(3, '0');
    const imgName = state.images.find(i => i.includes(`Comp_${indexStr}`));
    return imgName ? `/assets/${imgName}` : '';
}

function showStatus(text, type) {
    const status = document.getElementById('saveStatus');
    status.textContent = text;
    status.className = 'status-' + type;
    if (type === 'success') {
        setTimeout(() => {
            if (status.textContent === 'Saved!' || status.textContent === 'Tags Saved') {
                status.textContent = 'Idle';
                status.className = 'status-idle';
            }
        }, 3000);
    }
}

function openNewTagDialog() {
    document.getElementById('modalOverlay').classList.remove('hidden');
    document.getElementById('newTagName').focus();
}

function closeNewTagDialog() {
    document.getElementById('modalOverlay').classList.add('hidden');
}

async function addNewTag() {
    const input = document.getElementById('newTagName');
    const tag = input.value.trim();
    if (!tag) return;
    
    try {
        const res = await fetch('/api/tags/create', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ tag })
        });
        const data = await res.json();
        state.metadata.tags = data.tags;
        if (!state.filters[tag]) state.filters[tag] = 'ignore';
        
        closeNewTagDialog();
        renderAll();
        showDetailPanel();
        showStatus("Tag Created", "success");
    } catch (e) {
        showStatus("Create Failed", "error");
    }
}

// Events
document.getElementById('componentSearch').addEventListener('input', (e) => {
    state.searchTerm = e.target.value;
    renderComponentList();
});

init();
