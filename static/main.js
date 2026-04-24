/* =========================================================
   NRCan Article Monitor — main.js
   Handles: client-side filtering, Run Now polling, run selector
   ========================================================= */

'use strict';

// ---------------------------------------------------------------------------
// State from the server-rendered page
// ---------------------------------------------------------------------------
const pageData = JSON.parse(document.getElementById('page-data')?.textContent || '{}');
let pollInterval = null;

// ---------------------------------------------------------------------------
// DOM refs (may be null on first-run empty state)
// ---------------------------------------------------------------------------
const searchEl    = document.getElementById('search');
const catFilter   = document.getElementById('cat-filter');
const srcFilter   = document.getElementById('src-filter');
const clearBtn    = document.getElementById('clear-btn');
const runBtn      = document.getElementById('run-btn');
const runBtnEmpty = document.getElementById('run-btn-empty');
const runSelect   = document.getElementById('run-select');
const tbody       = document.getElementById('articles-tbody');
const countEl     = document.getElementById('article-count');
const noResults   = document.getElementById('no-results');

// ---------------------------------------------------------------------------
// Init
// ---------------------------------------------------------------------------
document.addEventListener('DOMContentLoaded', () => {
  setupFilters();
  setupRunButton();
  setupRunSelect();

  // If a scrape is already running when the page loads, resume polling
  if (pageData.isRunning && pageData.currentRun) {
    startPolling(pageData.currentRun, /* resuming */ true);
  }
});

// ---------------------------------------------------------------------------
// Client-side filtering
// ---------------------------------------------------------------------------
function setupFilters() {
  if (!searchEl) return;

  searchEl.addEventListener('input', debounce(applyFilters, 150));
  catFilter?.addEventListener('change', applyFilters);
  srcFilter?.addEventListener('change', applyFilters);

  clearBtn?.addEventListener('click', () => {
    searchEl.value     = '';
    if (catFilter) catFilter.value = '';
    if (srcFilter) srcFilter.value = '';
    applyFilters();
  });
}

function applyFilters() {
  if (!tbody) return;

  const q   = searchEl?.value.trim().toLowerCase() || '';
  const cat = catFilter?.value || '';
  const src = srcFilter?.value || '';

  let visible = 0;

  tbody.querySelectorAll('tr').forEach(row => {
    const title    = row.querySelector('.article-link')?.textContent.toLowerCase() || '';
    const summary  = row.querySelector('.summary-text')?.textContent.toLowerCase() || '';
    const rowCat   = row.dataset.category || '';
    const rowSrc   = row.dataset.source   || '';

    const matchQ   = !q   || title.includes(q) || summary.includes(q);
    const matchCat = !cat || rowCat === cat;
    const matchSrc = !src || rowSrc === src;

    const show = matchQ && matchCat && matchSrc;
    row.classList.toggle('hidden', !show);
    if (show) visible++;
  });

  if (countEl) countEl.textContent = visible;
  if (noResults) noResults.classList.toggle('d-none', visible > 0);
}

// Called from source-pill onclick in the template
function filterBySource(sourceName) {
  if (srcFilter) {
    srcFilter.value = sourceName;
    applyFilters();
    srcFilter.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }
}
window.filterBySource = filterBySource;  // expose to inline onclick

// ---------------------------------------------------------------------------
// Run Now button
// ---------------------------------------------------------------------------
function setupRunButton() {
  [runBtn, runBtnEmpty].forEach(btn => {
    btn?.addEventListener('click', startRun);
  });
}

async function startRun() {
  if (runBtn) {
    runBtn.disabled = true;
    runBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status"></span>Starting…';
  }

  const dedup = document.getElementById('dedup-toggle')?.checked ?? true;

  let resp, data;
  try {
    resp = await fetch('/api/run', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ dedup }),
    });
    data = await resp.json();
  } catch (err) {
    showAlert('Network error: ' + err.message, 'danger');
    resetRunBtn();
    return;
  }

  if (resp.status === 409) {
    showAlert(data.error || 'A scrape is already running.', 'warning');
    resetRunBtn();
    return;
  }
  if (!resp.ok) {
    showAlert(data.error || 'Failed to start run.', 'danger');
    resetRunBtn();
    return;
  }

  startPolling(data.run_id, false);
}

function startPolling(runId, resuming) {
  showProgressBanner(resuming ? 'Resuming scrape…' : 'Scrape started…', 0);

  if (pollInterval) clearInterval(pollInterval);

  pollInterval = setInterval(async () => {
    let status;
    try {
      status = await fetch(`/api/run/${runId}`).then(r => r.json());
    } catch (_) {
      return; // transient error, keep polling
    }

    const done  = status.sources_done  || 0;
    const total = status.total_sources || 1;
    const pct   = Math.round((done / total) * 100);
    const label = total
      ? `Scanning source ${done} of ${total}…`
      : 'Scanning…';

    updateProgressBanner(label, pct);

    if (status.status === 'done') {
      clearInterval(pollInterval);
      pollInterval = null;
      hideProgressBanner();
      resetRunBtn();
      showAlert(`Done! Found ${status.articles_found} article(s).`, 'success');
      // Reload the page so the new run appears in the selector and table
      window.location.href = `/?run_id=${runId}`;
    } else if (status.status === 'error') {
      clearInterval(pollInterval);
      pollInterval = null;
      hideProgressBanner();
      resetRunBtn();
      showAlert('Scrape failed: ' + (status.error_msg || 'Unknown error'), 'danger');
    }
  }, 3000);
}

function resetRunBtn() {
  if (runBtn) {
    runBtn.disabled = false;
    runBtn.innerHTML = '<i class="bi bi-play-circle-fill me-1"></i>Run Now';
  }
}

// ---------------------------------------------------------------------------
// Run selector
// ---------------------------------------------------------------------------
function setupRunSelect() {
  runSelect?.addEventListener('change', () => {
    const rid = runSelect.value;
    if (rid) window.location.href = `/?run_id=${rid}`;
  });
}

// ---------------------------------------------------------------------------
// Progress banner
// ---------------------------------------------------------------------------
function showProgressBanner(text, pct) {
  const banner = document.getElementById('progress-banner');
  const textEl = document.getElementById('progress-text');
  const bar    = document.getElementById('progress-bar');
  if (!banner) return;
  banner.classList.remove('d-none');
  if (textEl) textEl.textContent = text;
  if (bar) bar.style.width = pct + '%';
}

function updateProgressBanner(text, pct) {
  const textEl = document.getElementById('progress-text');
  const bar    = document.getElementById('progress-bar');
  if (textEl) textEl.textContent = text;
  if (bar) bar.style.width = pct + '%';
}

function hideProgressBanner() {
  document.getElementById('progress-banner')?.classList.add('d-none');
}

// ---------------------------------------------------------------------------
// Alert helper
// ---------------------------------------------------------------------------
function showAlert(message, type = 'info') {
  const container = document.getElementById('alert-container');
  if (!container) return;
  const id  = 'alert-' + Date.now();
  const div = document.createElement('div');
  div.id        = id;
  div.className = `alert alert-${type} alert-dismissible fade show`;
  div.innerHTML = `${escHtml(message)}
    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>`;
  container.appendChild(div);
  setTimeout(() => {
    const el = document.getElementById(id);
    if (el) el.remove();
  }, 8000);
}

// ---------------------------------------------------------------------------
// Utilities
// ---------------------------------------------------------------------------
function debounce(fn, delay) {
  let timer;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), delay);
  };
}

function escHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}
