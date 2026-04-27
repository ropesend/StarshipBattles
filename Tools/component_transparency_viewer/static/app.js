let images = [];
let filtered = [];
let currentIndex = 0;
let activeFilter = "all";

const els = {
  list: document.getElementById("imageList"),
  counter: document.getElementById("counter"),
  filename: document.getElementById("filename"),
  stats: document.getElementById("stats"),
  notes: document.getElementById("notes"),
  original: document.getElementById("originalImage"),
  checker: document.getElementById("processedChecker"),
  black: document.getElementById("processedBlack"),
  white: document.getElementById("processedWhite"),
};

function statusLabel(status) {
  return (status || "unreviewed").replace("_", " ");
}

function applyFilter() {
  filtered = images.filter((image) => activeFilter === "all" || image.review_status === activeFilter);
  if (currentIndex >= filtered.length) currentIndex = Math.max(0, filtered.length - 1);
  renderList();
  renderCurrent();
}

function refreshFiltered() {
  filtered = images.filter((image) => activeFilter === "all" || image.review_status === activeFilter);
}

function renderList() {
  els.list.innerHTML = "";
  filtered.forEach((image, index) => {
    const button = document.createElement("button");
    button.className = `image-row ${index === currentIndex ? "selected" : ""} ${image.review_status}`;
    button.innerHTML = `<span>${image.filename}</span><small>${statusLabel(image.review_status)}</small>`;
    button.addEventListener("click", () => {
      currentIndex = index;
      renderList();
      renderCurrent();
    });
    els.list.appendChild(button);
  });
}

function renderCurrent() {
  const image = filtered[currentIndex];
  els.counter.textContent = `${filtered.length ? currentIndex + 1 : 0} / ${filtered.length}`;
  if (!image) {
    els.filename.textContent = "No image loaded";
    els.stats.textContent = "";
    els.notes.value = "";
    return;
  }

  els.filename.textContent = image.filename;
  els.stats.textContent = `${statusLabel(image.review_status)} | ${image.processor_status} | removed ${image.removed_pixels} px`;
  els.notes.value = image.notes || "";
  const cacheKey = encodeURIComponent(`${image.filename}:${image.review_status}:${image.removed_pixels}`);
  els.original.src = `${image.original_url}?v=${cacheKey}`;
  els.checker.src = `${image.processed_url}?v=${cacheKey}`;
  els.black.src = `${image.processed_url}?v=${cacheKey}`;
  els.white.src = `${image.processed_url}?v=${cacheKey}`;

  document.querySelectorAll(".status-buttons button").forEach((button) => {
    button.classList.toggle("active", button.dataset.status === image.review_status);
  });
}

async function saveStatus(status, advance = true) {
  const image = filtered[currentIndex];
  if (!image) return;
  const startingIndex = currentIndex;
  const reviewedFilename = image.filename;
  const nextFilename = filtered[startingIndex + 1]?.filename || null;

  const response = await fetch("/api/review", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      filename: image.filename,
      review_status: status,
      notes: els.notes.value,
    }),
  });
  if (!response.ok) {
    alert(await response.text());
    return;
  }

  image.review_status = status;
  image.notes = els.notes.value;
  const original = images.find((item) => item.filename === image.filename);
  if (original) {
    original.review_status = status;
    original.notes = image.notes;
  }

  refreshFiltered();
  if (advance) {
    const nextIndex = nextFilename
      ? filtered.findIndex((item) => item.filename === nextFilename)
      : -1;
    if (nextIndex >= 0) {
      currentIndex = nextIndex;
    } else {
      currentIndex = Math.min(startingIndex, Math.max(0, filtered.length - 1));
    }
  } else {
    const nextIndex = filtered.findIndex((item) => item.filename === reviewedFilename);
    if (nextIndex >= 0) currentIndex = nextIndex;
  }
  renderList();
  renderCurrent();
}

async function init() {
  const response = await fetch("/api/init");
  if (!response.ok) {
    document.body.innerHTML = `<pre>${await response.text()}</pre>`;
    return;
  }
  const data = await response.json();
  images = data.images;
  applyFilter();
}

document.getElementById("filters").addEventListener("click", (event) => {
  const button = event.target.closest("button[data-filter]");
  if (!button) return;
  activeFilter = button.dataset.filter;
  currentIndex = 0;
  document.querySelectorAll("#filters button").forEach((item) => item.classList.toggle("active", item === button));
  applyFilter();
});

document.querySelector(".status-buttons").addEventListener("click", (event) => {
  const button = event.target.closest("button[data-status]");
  if (button) saveStatus(button.dataset.status, true);
});

els.notes.addEventListener("change", () => {
  const image = filtered[currentIndex];
  if (image) saveStatus(image.review_status, false);
});

document.getElementById("prevBtn").addEventListener("click", () => {
  currentIndex = Math.max(0, currentIndex - 1);
  renderList();
  renderCurrent();
});

document.getElementById("nextBtn").addEventListener("click", () => {
  currentIndex = Math.min(filtered.length - 1, currentIndex + 1);
  renderList();
  renderCurrent();
});

document.getElementById("exportBtn").addEventListener("click", async () => {
  const response = await fetch("/api/export/recreate");
  const data = await response.json();
  alert(`Exported ${data.count} recreate item(s) to ${data.path}`);
});

document.addEventListener("keydown", (event) => {
  if (event.target === els.notes) return;
  if (event.key === "ArrowLeft") document.getElementById("prevBtn").click();
  if (event.key === "ArrowRight") document.getElementById("nextBtn").click();
  if (event.key.toLowerCase() === "a") saveStatus("accepted", true);
  if (event.key.toLowerCase() === "r") saveStatus("rejected", true);
  if (event.key.toLowerCase() === "m") saveStatus("manual_cleanup", true);
  if (event.key.toLowerCase() === "c") saveStatus("recreate", true);
});

init();

document.querySelectorAll(".image-frame img").forEach((img) => {
  img.addEventListener("load", () => {
    img.closest(".image-frame").classList.remove("load-error");
  });
  img.addEventListener("error", () => {
    img.closest(".image-frame").classList.add("load-error");
  });
});
