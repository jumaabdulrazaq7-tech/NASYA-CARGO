/* ================================================================
   NASYA CARGO — script.js
   All interactive functionality: nav, tracking, forms, animations
   ================================================================ */

'use strict';

// ── SHIPMENT DATABASE ──────────────────────────────────────────
const SHIPMENTS = {
  'NSY-2024-001': {
    customer: 'Ahmed Al-Rashid',
    origin: 'Guangzhou, China',
    destination: 'Dar es Salaam, Tanzania',
    mode: 'Sea Freight (FCL)',
    weight: '2,400 kg',
    volume: '12 CBM',
    status: 'In Transit',
    eta: '18 Apr 2025',
    updated: '07 Apr 2025',
    progress: 60
  },
  'NSY-2024-002': {
    customer: 'Fatuma Ally',
    origin: 'Dubai, UAE',
    destination: 'Zanzibar, Tanzania',
    mode: 'Sea Freight (LCL)',
    weight: '850 kg',
    volume: '4.2 CBM',
    status: 'At Customs',
    eta: '10 Apr 2025',
    updated: '07 Apr 2025',
    progress: 80
  },
  'NSY-2024-003': {
    customer: 'James Mwangi',
    origin: 'Guangzhou, China',
    destination: 'Nairobi, Kenya',
    mode: 'Air Freight',
    weight: '320 kg',
    volume: '1.8 CBM',
    status: 'Delivered',
    eta: '03 Apr 2025',
    updated: '03 Apr 2025',
    progress: 100
  },
  'NSY-2024-004': {
    customer: 'Halima Juma',
    origin: 'Dubai, UAE',
    destination: 'Dar es Salaam, Tanzania',
    mode: 'Air Freight',
    weight: '175 kg',
    volume: '0.9 CBM',
    status: 'Pending',
    eta: '14 Apr 2025',
    updated: '07 Apr 2025',
    progress: 15
  },
  'NSY-2024-005': {
    customer: 'Omar Bin Said',
    origin: 'Guangzhou, China',
    destination: 'Zanzibar, Tanzania',
    mode: 'Sea Freight (FCL)',
    weight: '5,600 kg',
    volume: '28 CBM',
    status: 'In Transit',
    eta: '22 Apr 2025',
    updated: '06 Apr 2025',
    progress: 45
  }
};

// ── NAVIGATION ─────────────────────────────────────────────────
const navbar = document.querySelector('.navbar');
const hamburger = document.getElementById('hamburger');
const mobileMenu = document.getElementById('mobileMenu');

// Navbar scroll effect
window.addEventListener('scroll', () => {
  navbar?.classList.toggle('scrolled', window.scrollY > 20);
});

// Hamburger toggle
function toggleMenu() {
  const isOpen = mobileMenu?.classList.toggle('open');
  hamburger?.classList.toggle('open', isOpen);
}

function closeMenu() {
  mobileMenu?.classList.remove('open');
  hamburger?.classList.remove('open');
}

// Set active nav link based on current page
function setActiveNav() {
  const page = window.location.pathname.split('/').pop().replace('.html','') || 'index';
  document.querySelectorAll('.nav-link, .mobile-link').forEach(link => {
    const href = link.getAttribute('href')?.replace('.html','') || '';
    const isActive = href === page ||
      (page === 'index' && href === 'index') ||
      (page === '' && href === 'index');
    link.classList.toggle('active', isActive);
  });
}

// Close mobile menu on outside click
document.addEventListener('click', (e) => {
  if (mobileMenu?.classList.contains('open') &&
      !mobileMenu.contains(e.target) &&
      !hamburger?.contains(e.target)) {
    closeMenu();
  }
});

// ── CARGO TRACKING ─────────────────────────────────────────────
function trackCargo() {
  const input = document.getElementById('trackInput');
  if (!input) return;
  const id = input.value.trim().toUpperCase();
  renderTrackResult(id, 'trackResult');
}

function handleTrackKey(e) {
  if (e.key === 'Enter') trackCargo();
}

function renderTrackResult(id, containerId) {
  const container = document.getElementById(containerId);
  if (!container) return;

  if (!id) {
    container.innerHTML = '<div class="track-error">Please enter a tracking number.</div>';
    return;
  }

  const ship = SHIPMENTS[id];
  if (!ship) {
    container.innerHTML = `
      <div class="track-error">
        ❌ No shipment found for <strong>${id}</strong>.<br>
        Check your number and try again, or contact us on
        <a href="https://wa.me/971547417800" target="_blank" style="color:var(--gold)">WhatsApp</a>.
      </div>`;
    return;
  }

  const steps = ['Pending','In Transit','At Customs','Delivered'];
  const cur   = steps.indexOf(ship.status);

  const statusClass = {
    'Pending':    'status-pending',
    'In Transit': 'status-transit',
    'At Customs': 'status-customs',
    'Delivered':  'status-delivered'
  }[ship.status] || 'status-transit';

  const stepIcons = ['📦','🚢','🏛️','✅'];

  container.innerHTML = `
    <div class="track-result-inner">
      <div class="track-result-header">
        <div class="track-id">${id}</div>
        <div class="track-status-badge ${statusClass}">${ship.status}</div>
      </div>

      <div class="track-steps">
        ${steps.map((s, i) => `
          <div class="track-step ${i < cur ? 'done' : i === cur ? 'active' : ''}">
            <div class="step-dot">${i <= cur ? stepIcons[i] : ''}</div>
            <div class="step-label">${s}</div>
          </div>`).join('')}
      </div>

      <div class="track-grid" style="margin-top:20px;">
        <div class="track-field"><label>Consignee</label><span>${ship.customer}</span></div>
        <div class="track-field"><label>Shipping Mode</label><span>${ship.mode}</span></div>
        <div class="track-field"><label>Origin</label><span>${ship.origin}</span></div>
        <div class="track-field"><label>Destination</label><span>${ship.destination}</span></div>
        <div class="track-field"><label>Weight</label><span>${ship.weight}</span></div>
        <div class="track-field"><label>Volume</label><span>${ship.volume}</span></div>
        <div class="track-field"><label>ETA</label><span>${ship.eta}</span></div>
        <div class="track-field"><label>Last Updated</label><span>${ship.updated}</span></div>
      </div>

      <div style="margin-top:20px;">
        <div style="display:flex;justify-content:space-between;font-size:12px;color:rgba(255,255,255,0.4);margin-bottom:6px;">
          <span>Shipment Progress</span><span>${ship.progress}%</span>
        </div>
        <div class="hero-card-bar-bg">
          <div class="hero-card-bar" style="width:${ship.progress}%"></div>
        </div>
      </div>
    </div>`;
}

// ── QUOTE FORM ─────────────────────────────────────────────────
function submitQuote() {
  const name   = document.getElementById('qName')?.value.trim();
  const email  = document.getElementById('qEmail')?.value.trim();
  const phone  = document.getElementById('qPhone')?.value.trim();
  const cargo  = document.getElementById('qCargo')?.value;
  const origin = document.getElementById('qOrigin')?.value.trim();
  const dest   = document.getElementById('qDest')?.value.trim();

  if (!name || !email || !phone || !cargo || !origin || !dest) {
    showNotif('Please fill in all required fields.', 'error');
    return;
  }
  if (!email.includes('@')) {
    showNotif('Please enter a valid email address.', 'error');
    return;
  }

  const btn = document.querySelector('#quoteForm .btn-submit');
  if (btn) { btn.textContent = 'Submitting...'; btn.disabled = true; }

  setTimeout(() => {
    const success = document.getElementById('quoteSuccess');
    if (success) {
      success.classList.add('show');
      success.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
    if (btn) { btn.textContent = 'Submit Quote Request →'; btn.disabled = false; }
    showNotif('✅ Quote submitted! We\'ll reply within 2 hours.', 'success');
  }, 900);
}

// ── CONTACT FORM ───────────────────────────────────────────────
function submitContact() {
  const name = document.getElementById('cName')?.value.trim();
  const email = document.getElementById('cEmail')?.value.trim();
  const msg  = document.getElementById('cMsg')?.value.trim();

  if (!name || !email || !msg) {
    showNotif('Please fill in all required fields.', 'error');
    return;
  }

  const btn = document.querySelector('#contactForm .btn-submit');
  if (btn) { btn.textContent = 'Sending...'; btn.disabled = true; }

  setTimeout(() => {
    const success = document.getElementById('contactSuccess');
    if (success) {
      success.classList.add('show');
      success.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
    if (btn) { btn.textContent = 'Send Message'; btn.disabled = false; }
    showNotif('✅ Message sent! We\'ll reply within 4 hours.', 'success');
  }, 900);
}

// ── FAQ ACCORDION ──────────────────────────────────────────────
function initFaq() {
  document.querySelectorAll('.faq-q').forEach(q => {
    q.addEventListener('click', () => {
      const item = q.closest('.faq-item');
      const isOpen = item.classList.contains('open');
      document.querySelectorAll('.faq-item.open').forEach(i => i.classList.remove('open'));
      if (!isOpen) item.classList.add('open');
    });
  });
}

// ── NOTIFICATION TOAST ─────────────────────────────────────────
function showNotif(msg, type = 'info') {
  let notif = document.getElementById('notif');
  if (!notif) {
    notif = document.createElement('div');
    notif.id = 'notif';
    notif.className = 'notif';
    document.body.appendChild(notif);
  }
  const colors = { success: '#10b981', error: '#ef4444', warning: '#f59e0b', info: '#00B4D2' };
  notif.style.borderLeftColor = colors[type] || colors.info;
  notif.textContent = msg;
  notif.classList.add('show');
  clearTimeout(notif._timer);
  notif._timer = setTimeout(() => notif.classList.remove('show'), 3500);
}

// ── SCROLL REVEAL ──────────────────────────────────────────────
function initReveal() {
  const obs = new IntersectionObserver((entries) => {
    entries.forEach((e, i) => {
      if (e.isIntersecting) {
        setTimeout(() => e.target.classList.add('visible'), i * 80);
        obs.unobserve(e.target);
      }
    });
  }, { threshold: 0.1 });
  document.querySelectorAll('.reveal').forEach(el => obs.observe(el));
}

// ── HERO CARD ANIMATION ─────────────────────────────────────── 
function animateHeroCards() {
  const bars = document.querySelectorAll('.hero-card-bar');
  bars.forEach(bar => {
    const w = bar.dataset.width || bar.style.width;
    bar.style.width = '0';
    setTimeout(() => { bar.style.width = w; }, 600);
  });
}

// ── INIT ───────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  setActiveNav();
  initFaq();
  initReveal();
  animateHeroCards();
});
