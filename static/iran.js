'use strict';

/* ==========================================================
   Iran Monitor — news feed with topic + lookback filtering
   ========================================================== */

let _allNews = [];   // all articles from last fetch (no date filter)

document.addEventListener('DOMContentLoaded', () => {
  loadNews();

  // Re-filter (no refetch) when lookback changes
  document.querySelectorAll('input[name="lookback"]').forEach(r =>
    r.addEventListener('change', applyFilters));

  document.getElementById('news-search')
    ?.addEventListener('input', debounce(applyFilters, 150));
  document.getElementById('topic-filter')
    ?.addEventListener('change', applyFilters);
  document.getElementById('news-source-filter')
    ?.addEventListener('change', applyFilters);

  document.getElementById('refresh-news-btn')
    ?.addEventListener('click', () => loadNews(true));

  document.getElementById('clear-filters-btn')
    ?.addEventListener('click', () => {
      document.getElementById('news-search').value        = '';
      document.getElementById('topic-filter').value       = '';
      document.getElementById('news-source-filter').value = '';
      // Reset lookback to 14 days
      document.getElementById('lb14').checked = true;
      applyFilters();
    });
});

/* ----------------------------------------------------------
   Fetch all available articles from server (cached 30 min)
   ---------------------------------------------------------- */
async function loadNews(forceRefresh = false) {
  const tbody = document.getElementById('news-tbody');
  tbody.innerHTML = `<tr><td colspan="3" class="text-center text-muted py-4">
    <span class="spinner-border spinner-border-sm me-2"></span>Fetching articles…
  </td></tr>`;

  const btn = document.getElementById('refresh-news-btn');
  if (btn) {
    btn.disabled = true;
    btn.innerHTML =
      '<span class="spinner-border spinner-border-sm me-1"></span>Fetching…';
  }

  try {
    const url  = '/api/iran/news' + (forceRefresh ? '?force=1' : '');
    const resp = await fetch(url);
    if (!resp.ok) throw new Error(`Server error ${resp.status}`);
    const data = await resp.json();

    _allNews = data.articles || [];

    // Show "cached" indicator
    const cachedEl = document.getElementById('news-cached');
    if (cachedEl) cachedEl.classList.toggle('d-none', !data.cached);

    applyFilters();
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="3" class="text-danger p-3">
      <i class="bi bi-exclamation-circle me-1"></i>${escHtml(err.message)}
    </td></tr>`;
  } finally {
    if (btn) {
      btn.disabled = false;
      btn.innerHTML = '<i class="bi bi-arrow-clockwise me-1"></i>Refresh News';
    }
  }
}

/* ----------------------------------------------------------
   Filter + render  (runs client-side on every control change)
   ---------------------------------------------------------- */
function applyFilters() {
  const q      = (document.getElementById('news-search')?.value || '').toLowerCase().trim();
  const topic  = document.getElementById('topic-filter')?.value  || '';
  const src    = document.getElementById('news-source-filter')?.value || '';
  const cutoff = getLookbackCutoff();   // YYYY-MM-DD string

  const filtered = _allNews.filter(a => {
    // Lookback: articles with no date always shown (unknown date)
    if (cutoff && a.published && a.published < cutoff)     return false;
    if (q && !a.title.toLowerCase().includes(q)
          && !(a.summary || '').toLowerCase().includes(q)) return false;
    if (topic && !(a.topics || []).includes(topic))        return false;
    if (src   && a.source !== src)                         return false;
    return true;
  });

  const countEl = document.getElementById('news-count');
  if (countEl) countEl.textContent = filtered.length;

  const noResults = document.getElementById('news-no-results');
  if (noResults) noResults.classList.toggle('d-none', filtered.length > 0);

  renderTable(filtered);
}

function getLookbackCutoff() {
  const days = parseInt(
    document.querySelector('input[name="lookback"]:checked')?.value || '14'
  );
  const d = new Date();
  d.setDate(d.getDate() - days);
  return d.toISOString().slice(0, 10);   // YYYY-MM-DD
}

function renderTable(articles) {
  const tbody = document.getElementById('news-tbody');
  if (!articles.length) { tbody.innerHTML = ''; return; }

  tbody.innerHTML = articles.map(a => `
    <tr>
      <td class="date-cell">${escHtml(a.published || '—')}</td>
      <td>
        <div class="source-pill mb-1" style="cursor:default;">
          ${escHtml(a.source)}
        </div>
        <div class="d-flex flex-wrap gap-1">
          ${(a.topics || []).map(t =>
            `<span class="topic-badge topic-${slugify(t)}">${escHtml(t)}</span>`
          ).join('')}
        </div>
      </td>
      <td>
        <a href="${escHtml(a.url)}" target="_blank" rel="noopener"
           class="article-link">
          ${escHtml(a.title)}
        </a>
        ${a.summary
          ? `<div class="summary-text">${escHtml(a.summary.slice(0, 200))}${
              a.summary.length > 200 ? '…' : ''}</div>`
          : ''}
      </td>
    </tr>`).join('');
}

/* ----------------------------------------------------------
   Utilities
   ---------------------------------------------------------- */
function slugify(str) {
  return str.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');
}

function escHtml(str) {
  return String(str ?? '')
    .replace(/&/g, '&amp;').replace(/</g, '&lt;')
    .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

function debounce(fn, ms) {
  let t;
  return (...args) => { clearTimeout(t); t = setTimeout(() => fn(...args), ms); };
}
