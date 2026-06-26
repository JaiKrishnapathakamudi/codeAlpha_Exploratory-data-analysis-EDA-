// dashboard.js - UI Controller for Netflix EDA Dashboard

// Wait for DOM content to load
document.addEventListener('DOMContentLoaded', () => {
  initializeStats();
  setupKeyboardClose();
});

// 1. Initialize stats from the generated data file
function initializeStats() {
  // Check if NETFLIX_STATS is available in the global window namespace
  if (typeof NETFLIX_STATS !== 'undefined') {
    console.log('Loading statistics from stats_data.js:', NETFLIX_STATS);
    
    // Update KPI Card values
    updateDOMText('kpi-total', formatNumber(NETFLIX_STATS.totalTitles));
    updateDOMText('kpi-movies-pct', NETFLIX_STATS.moviesPct + '%');
    updateDOMText('kpi-tvshows-pct', NETFLIX_STATS.tvShowsCount ? NETFLIX_STATS.tvShowsPct + '%' : '30.9%');
    updateDOMText('kpi-mature-pct', NETFLIX_STATS.maturePct + '%');
    updateDOMText('kpi-duration', NETFLIX_STATS.avgMovieDuration + ' min');

    // Update KPI Card subtexts (counts)
    const movieCard = document.querySelector('.stat-card:nth-child(2) .stat-desc');
    if (movieCard) movieCard.textContent = `${formatNumber(NETFLIX_STATS.moviesCount)} titles in catalog`;
    
    const tvCard = document.querySelector('.stat-card:nth-child(3) .stat-desc');
    if (tvCard) tvCard.textContent = `${formatNumber(NETFLIX_STATS.tvShowsCount)} titles in catalog`;

    const matureCard = document.querySelector('.stat-card:nth-child(4) .stat-desc');
    if (matureCard) matureCard.textContent = `${formatNumber(NETFLIX_STATS.matureCount)} mature-rated titles`;

    const durationCard = document.querySelector('.stat-card:nth-child(5) .stat-desc');
    if (durationCard) durationCard.textContent = `Median runtime: ${NETFLIX_STATS.medianMovieDuration} min`;

    // Update Schema Missing % values
    updateDOMText('null-director', NETFLIX_STATS.missingDirectorPct + '%');
    updateDOMText('null-cast', NETFLIX_STATS.missingCastPct + '%');
    updateDOMText('null-country', NETFLIX_STATS.missingCountryPct + '%');
  } else {
    console.warn('NETFLIX_STATS is not loaded. Utilizing static fallback values.');
  }
}

// Helper to safely update DOM text content
function updateDOMText(elementId, text) {
  const el = document.getElementById(elementId);
  if (el) {
    el.textContent = text;
  }
}

// Format numbers with commas (e.g., 7787 -> 7,787)
function formatNumber(num) {
  return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

// 2. Tab Navigation
function switchTab(tabName) {
  // Hide all panels
  const panels = document.querySelectorAll('.tab-panel');
  panels.forEach(panel => panel.classList.remove('active'));

  // Deactivate all nav buttons
  const navItems = document.querySelectorAll('.nav-item');
  navItems.forEach(item => item.classList.remove('active'));

  // Show selected panel
  const activePanel = document.getElementById(`panel-${tabName}`);
  if (activePanel) {
    activePanel.classList.add('active');
  }

  // Activate selected nav button
  const activeNavItem = document.querySelector(`.nav-item[data-tab="${tabName}"]`);
  if (activeNavItem) {
    activeNavItem.classList.add('active');
  }

  // Update header title
  const headerTitle = document.getElementById('dashboard-title');
  if (headerTitle) {
    // Capitalize first letter or use map
    const titleMap = {
      'overview': 'Overview',
      'charts': 'Visualizations Dashboard',
      'hypotheses': 'Hypothesis Verification',
      'details': 'Audited Data Issues'
    };
    headerTitle.textContent = titleMap[tabName] || tabName;
  }

  // Scroll to top
  window.scrollTo({ top: 0, behavior: 'smooth' });

  // Close mobile sidebar if open
  const sidebar = document.getElementById('sidebar');
  if (sidebar) {
    sidebar.classList.remove('mobile-active');
  }
}

// 3. Mobile Sidebar Toggle
function toggleMobileSidebar() {
  const sidebar = document.getElementById('sidebar');
  if (sidebar) {
    sidebar.classList.toggle('mobile-active');
  }
}

// 4. Zoomable Lightbox Modal for charts
function openLightbox(imgSrc, imgDesc) {
  const modal = document.getElementById('lightbox-modal');
  const modalImg = document.getElementById('lightbox-img');
  const modalDesc = document.getElementById('lightbox-desc');

  if (modal && modalImg && modalDesc) {
    modalImg.src = imgSrc;
    modalDesc.textContent = imgDesc;
    modal.classList.add('active');
    document.body.style.overflow = 'hidden'; // Lock background scrolling
  }
}

function closeLightbox() {
  const modal = document.getElementById('lightbox-modal');
  if (modal) {
    modal.classList.remove('active');
    document.body.style.overflow = ''; // Restore background scrolling
  }
}

// Close modal with ESC key
function setupKeyboardClose() {
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      closeLightbox();
    }
  });
}
