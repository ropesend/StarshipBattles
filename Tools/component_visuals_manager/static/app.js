let state = {
    components: [],
    metadata: { tags: [], assignments: {} },
    images: [],
    selectedComponentIds: [], // Multi-select
    selectedImageIndices: [],   // Multi-select
    pendingSpriteIndex: null,   // Highlighted image (last clicked or hovered)
    filters: {}, // tag: 'include' | 'exclude' | 'ignore'
    searchTerm: '',
    tagToDelete: null
};

// --- Initialization ---
async function init() {
    try {
        const res = await fetch('/api/init');
        const data = await res.json();
        state.components = data.components;
        state.metadata = data.metadata;
        state.images = data.images;
        
        state.metadata.tags.forEach(tag => {
            if (!state.filters[tag]) state.filters[tag] = 'ignore';
        });

        initRectangleSelection();
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
        <div class="comp-item ${state.selectedComponentIds.includes(c.id) ? 'active' : ''}" 
             onclick="selectComponent('${c.id}', event)">
            <img src="${getImageUrl(c.sprite_index, 64)}" alt="${c.name}">
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
            <button class="tag-control-btn assign" onclick="bulkTagImages('${tag}', 'add')" title="Assign to selected">+</button>
            <button class="tag-control-btn remove" onclick="bulkTagImages('${tag}', 'remove')" title="Remove from selected">-</button>
            <button class="tag-control-btn delete" onclick="confirmDeleteTag('${tag}')" title="Delete tag globally">×</button>
        </div>
    `).join('');
}

function renderImageGrid() {
    const grid = document.getElementById('imageGrid');
    const filteredImages = getFilteredImages();
    
    document.getElementById('imageCount').textContent = filteredImages.length;
    
    // Calculate which component IDs match which indices
    const assignedIndices = new Set(
        state.components
            .filter(c => state.selectedComponentIds.includes(c.id))
            .map(c => c.sprite_index)
    );

    grid.innerHTML = filteredImages.map(img => {
        const index = parseInt(img.match(/_(\d+)\./)[1]);
        const isAssigned = assignedIndices.has(index);
        const isSelected = state.selectedImageIndices.includes(index);
        const isPending = state.pendingSpriteIndex === index;
            
        return `
            <div class="image-card ${isAssigned ? 'assigned' : ''} ${isSelected ? 'selected' : ''} ${isPending ? 'pending' : ''}" 
                 data-index="${index}"
                 onclick="selectImage(${index}, event)">
                <img src="${getImageUrl(index, 128)}" loading="lazy">
                <div class="index-label">${img} [${index}]</div>
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
        if (activeExcludes.some(t => imgTags.includes(t))) return false;
        if (!activeIncludes.every(t => imgTags.includes(t))) return false;
        return true;
    });
}

// --- Interaction ---
function selectComponent(id, event) {
    if (event && event.ctrlKey) {
        if (state.selectedComponentIds.includes(id)) {
            state.selectedComponentIds = state.selectedComponentIds.filter(cid => cid !== id);
        } else {
            state.selectedComponentIds.push(id);
        }
    } else {
        state.selectedComponentIds = [id];
    }
    renderAll();
}

function selectImage(index, event) {
    state.pendingSpriteIndex = index;
    if (event && event.ctrlKey) {
        if (state.selectedImageIndices.includes(index)) {
            state.selectedImageIndices = state.selectedImageIndices.filter(i => i !== index);
        } else {
            state.selectedImageIndices.push(index);
        }
    } else {
        state.selectedImageIndices = [index];
    }
    renderAll();
    showDetailPanel();
}

async function assignImageToComponents() {
    if (state.pendingSpriteIndex === null || state.selectedComponentIds.length === 0) return;

    const index = state.pendingSpriteIndex;
    showStatus("Assigning...", "saving");
    
    try {
        // We'll update components one by one or batch if the API allowed it
        // For simplicity, sequential for now (API currently takes one at a time)
        for (const cid of state.selectedComponentIds) {
            await fetch('/api/component/image', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ component_id: cid, sprite_index: index })
            });
            const comp = state.components.find(c => c.id === cid);
            if (comp) comp.sprite_index = index;
        }
        showStatus("Assigned!", "success");
        renderAll();
        showDetailPanel();
    } catch (e) {
        showStatus("Assignment Failed", "error");
    }
}

async function bulkTagImages(tag, action) {
    // Collect all indices to tag: Gallery selection + Selected Components' images
    const targetIndices = new Set(state.selectedImageIndices);
    state.components.filter(c => state.selectedComponentIds.includes(c.id)).forEach(c => {
        if (c.sprite_index !== undefined) targetIndices.add(c.sprite_index);
    });

    if (targetIndices.size === 0) {
        showStatus("No images selected", "error");
        return;
    }

    showStatus("Tagging...", "saving");
    try {
        const res = await fetch('/api/image/bulk-tags', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                sprite_indices: Array.from(targetIndices),
                tag: tag,
                action: action
            })
        });
        if (res.ok) {
            // Update local state
            targetIndices.forEach(idx => {
                const idxStr = idx.toString();
                if (!state.metadata.assignments[idxStr]) state.metadata.assignments[idxStr] = [];
                const tags = state.metadata.assignments[idxStr];
                if (action === 'add') {
                    if (!tags.includes(tag)) tags.push(tag);
                } else {
                    state.metadata.assignments[idxStr] = tags.filter(t => t !== tag);
                }
            });
            showStatus("Bulk Updated", "success");
            renderAll();
            showDetailPanel();
        }
    } catch (e) {
        showStatus("Bulk Tag Failed", "error");
    }
}

// --- Tag Lifecycle ---
function confirmDeleteTag(tag) {
    state.tagToDelete = tag;
    // Count usage
    let count = 0;
    Object.values(state.metadata.assignments).forEach(tags => {
        if (tags.includes(tag)) count++;
    });

    if (count > 0) {
        document.getElementById('deleteTagWarning').textContent = `Warning: This tag is currently applied to ${count} images.`;
        document.getElementById('deleteModal').classList.remove('hidden');
    } else {
        performDeleteTag(tag);
    }
}

async function performDeleteTag(tag) {
    try {
        const res = await fetch('/api/tags/delete', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ tag })
        });
        if (res.ok) {
            state.metadata.tags = state.metadata.tags.filter(t => t !== tag);
            delete state.filters[tag];
            showStatus("Tag Deleted", "success");
            closeDeleteModal();
            renderAll();
        }
    } catch (e) {
        showStatus("Delete Failed", "error");
    }
}

function closeDeleteModal() {
    document.getElementById('deleteModal').classList.add('hidden');
    state.tagToDelete = null;
}

// --- Rectangle Selection ---
function initRectangleSelection() {
    const grid = document.getElementById('imageGrid');
    let isDragging = false;
    let dragThreshold = 5; // px before starting drag
    let startX, startY;
    let selectionBox = null;

    grid.addEventListener('mousedown', (e) => {
        if (e.target !== grid && !e.target.parentElement?.classList.contains('image-card') && !e.target.classList.contains('image-card')) return;
        if (e.ctrlKey) return;

        startX = e.pageX;
        startY = e.pageY;
        isDragging = false; // Will set to true on move
    });

    window.addEventListener('mousemove', (e) => {
        if (!startX || (Math.abs(e.pageX - startX) < dragThreshold && Math.abs(e.pageY - startY) < dragThreshold && !isDragging)) return;
        
        if (!isDragging) {
            isDragging = true;
            state.selectedImageIndices = []; // Clear only when real drag starts
            selectionBox = document.createElement('div');
            selectionBox.className = 'selection-box';
            document.body.appendChild(selectionBox);
        }

        const currentX = e.pageX;
        const currentY = e.pageY;

        const left = Math.min(startX, currentX);
        const top = Math.min(startY, currentY);
        const width = Math.abs(startX - currentX);
        const height = Math.abs(startY - currentY);

        selectionBox.style.left = left + 'px';
        selectionBox.style.top = top + 'px';
        selectionBox.style.width = width + 'px';
        selectionBox.style.height = height + 'px';

        const boxRect = selectionBox.getBoundingClientRect();
        const cards = grid.querySelectorAll('.image-card');
        const selected = [];

        cards.forEach(card => {
            const cardRect = card.getBoundingClientRect();
            const intersect = !(
                cardRect.left > boxRect.right ||
                cardRect.right < boxRect.left ||
                cardRect.top > boxRect.bottom ||
                cardRect.bottom < boxRect.top
            );
            if (intersect) {
                selected.push(parseInt(card.dataset.index));
                card.classList.add('selected');
            } else {
                card.classList.remove('selected');
            }
        });
        state.selectedImageIndices = selected;
    });

    window.addEventListener('mouseup', () => {
        startX = null;
        startY = null;
        if (!isDragging) return;
        isDragging = false;
        if (selectionBox) selectionBox.remove();
        renderAll();
    });
}

// --- Utils ---
function getImageUrl(index, res = 128) {
    if (index === undefined || index === null) return '';
    const indexStr = index.toString().padStart(3, '0');
    return `/assets/${res}/${res}Portrait_Comp_${indexStr}.png`;
}

function showStatus(text, type) {
    const status = document.getElementById('saveStatus');
    status.textContent = text;
    status.className = 'status-' + type;
}

function showDetailPanel() {
    const panel = document.getElementById('selectionDetail');
    const displayIndex = state.pendingSpriteIndex !== null ? state.pendingSpriteIndex : (state.selectedImageIndices[0] || null);
    
    if (displayIndex === null) {
        panel.classList.add('hidden');
        return;
    }
    
    panel.classList.remove('hidden');
    const indexStr = displayIndex.toString().padStart(3, '0');
    
    document.getElementById('detailImg').src = getImageUrl(displayIndex, 128);
    document.getElementById('detailIndex').textContent = `Index: ${displayIndex} ${state.pendingSpriteIndex === displayIndex ? '(FOCUS)' : ''}`;
    
    const imgTags = state.metadata.assignments[displayIndex.toString()] || [];
    const tagCloud = document.getElementById('detailTags');
    tagCloud.innerHTML = state.metadata.tags.map(tag => `
        <div class="tag-chip ${imgTags.includes(tag) ? 'active' : ''}" onclick="toggleImageTag_Single(${displayIndex}, '${tag}')">
            ${tag}
        </div>
    `).join('');
    
    const usage = state.components.filter(c => c.sprite_index === displayIndex);
    const usageList = document.getElementById('detailUsage');
    usageList.innerHTML = usage.length > 0 
        ? usage.map(c => `<div>${c.name} (${c.id})</div>`).join('')
        : '<div style="color: grey">Not assigned</div>';
}

async function toggleImageTag_Single(idx, tag) {
    const tags = state.metadata.assignments[idx.toString()] || [];
    const action = tags.includes(tag) ? 'remove' : 'add';
    
    try {
        const res = await fetch('/api/image/bulk-tags', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ sprite_indices: [idx], tag, action })
        });
        if (res.ok) {
            if (action === 'add') tags.push(tag);
            else state.metadata.assignments[idx.toString()] = tags.filter(t => t !== tag);
            renderAll();
            showDetailPanel();
        }
    } catch (e) {}
}

function toggleFilter(tag) {
    const current = state.filters[tag];
    if (current === 'ignore') state.filters[tag] = 'include';
    else if (current === 'include') state.filters[tag] = 'exclude';
    else state.filters[tag] = 'ignore';
    renderAll();
}

function openNewTagDialog() {
    document.getElementById('modalOverlay').classList.remove('hidden');
    document.getElementById('newTagName').focus();
}

function closeNewTagDialog() {
    document.getElementById('modalOverlay').classList.add('hidden');
}

async function addNewTag() {
    const tag = document.getElementById('newTagName').value.trim();
    if (!tag) return;
    try {
        const res = await fetch('/api/tags/create', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ tag })
        });
        const data = await res.json();
        state.metadata.tags = data.tags;
        closeNewTagDialog();
        renderAll();
    } catch (e) {}
}

// Events
document.getElementById('componentSearch').addEventListener('input', (e) => {
    state.searchTerm = e.target.value;
    renderComponentList();
});

window.addEventListener('keydown', (e) => {
    if (e.key === ' ' && document.activeElement.tagName !== 'INPUT') {
        e.preventDefault();
        assignImageToComponents();
    }
});

init();
