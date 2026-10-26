/**
 * app.js - Koraput Tourism Full Single-Page Portal Client
 * Features:
 * - Rich Multi-Section Homepage (Destinations, Coffee Trail, Culture, Stays, Handicrafts, Itineraries, Seasons)
 * - Multi-image Carousel Slider for every card
 * - Mascot "Kora - The Spirit of Koraput"
 * - "Ask Kora" AI Tour Guide grounded on SQLite database
 * - Dynamic filtering, live search, compare modal, trip planner, and offline audio soundscape
 */

const AppState = {
  places: [],
  hotels: [],
  itineraries: [],
  culture: [],
  stats: {},
  filterCategory: 'all',
  searchQuery: '',
  selectedItem: null,
  savedTrip: JSON.parse(localStorage.getItem('koraput_trip') || '[]'),
  cardSlideIndices: {},
  audioPlaying: false,
  audioContext: null,
  audioNodes: [],
  chatHistory: []
};

document.addEventListener('DOMContentLoaded', () => {
  initApp();
});

async function initApp() {
  setupEventListeners();
  await loadStats();
  await loadPlaces();
  await loadHotels();
  await loadItineraries();
  await loadCulture();
  updateTripBadge();
  renderApp();
}

/* =========================================================================
   Data Loaders
   ========================================================================= */

async function loadPlaces() {
  try {
    let url = '/api/places';
    const params = [];
    if (AppState.filterCategory && AppState.filterCategory !== 'all') {
      params.push(`category=${encodeURIComponent(AppState.filterCategory)}`);
    }
    if (AppState.searchQuery) {
      params.push(`search=${encodeURIComponent(AppState.searchQuery)}`);
    }
    if (params.length) url += '?' + params.join('&');

    const res = await fetch(url);
    const data = await res.json();
    if (data.success) AppState.places = data.places;
  } catch (err) {
    console.error('Error loading places:', err);
  }
}

async function loadHotels() {
  try {
    const res = await fetch('/api/hotels');
    const data = await res.json();
    if (data.success) AppState.hotels = data.hotels;
  } catch (err) {
    console.error('Error loading hotels:', err);
  }
}

async function loadItineraries() {
  try {
    const res = await fetch('/api/itineraries');
    const data = await res.json();
    if (data.success) AppState.itineraries = data.itineraries;
  } catch (err) {
    console.error('Error loading itineraries:', err);
  }
}

async function loadCulture() {
  try {
    const res = await fetch('/api/culture');
    const data = await res.json();
    if (data.success) AppState.culture = data.culture;
  } catch (err) {
    console.error('Error loading culture:', err);
  }
}

async function loadStats() {
  try {
    const res = await fetch('/api/stats');
    const data = await res.json();
    if (data.success) AppState.stats = data.stats;
  } catch (err) {
    console.error('Error loading stats:', err);
  }
}

/* =========================================================================
   Event Listeners & Navigation
   ========================================================================= */

function setupEventListeners() {
  // Category Filters on homepage
  document.querySelectorAll('[data-category]').forEach(btn => {
    btn.addEventListener('click', (e) => {
      document.querySelectorAll('[data-category]').forEach(b => b.classList.remove('active-cat', 'bg-white/30'));
      e.currentTarget.classList.add('active-cat', 'bg-white/30');
      AppState.filterCategory = e.currentTarget.getAttribute('data-category');
      loadPlaces().then(() => {
        renderPlacesList();
        // Smooth scroll to destinations section if clicked from hero
        const destSection = document.getElementById('destinations');
        if (destSection) {
          destSection.scrollIntoView({ behavior: 'smooth' });
        }
      });
    });
  });

  // Live Search
  const searchInput = document.getElementById('searchInput');
  if (searchInput) {
    let debounceTimer;
    searchInput.addEventListener('input', (e) => {
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(() => {
        AppState.searchQuery = e.target.value.trim();
        loadPlaces().then(() => {
          renderPlacesList();
          const destSection = document.getElementById('destinations');
          if (destSection && AppState.searchQuery) {
            destSection.scrollIntoView({ behavior: 'smooth' });
          }
        });
      }, 250);
    });
  }

  // Soundscape
  const audioBtn = document.getElementById('btnToggleAudio');
  if (audioBtn) audioBtn.addEventListener('click', toggleKoraputAmbience);

  // Trip Drawer
  const tripBtn = document.getElementById('btnTripDrawer');
  if (tripBtn) tripBtn.addEventListener('click', openTripDrawer);
  const closeTripBtn = document.getElementById('btnCloseTripDrawer');
  if (closeTripBtn) closeTripBtn.addEventListener('click', closeTripDrawer);

  // Detail Modal Close
  const modalClose = document.getElementById('modalCloseBtn');
  if (modalClose) modalClose.addEventListener('click', closeDetailsModal);

  // Ask Kora AI Chat Modal
  const btnCloseKoraAi = document.getElementById('btnCloseKoraAi');
  if (btnCloseKoraAi) btnCloseKoraAi.addEventListener('click', closeKoraChatModal);

  const koraChatForm = document.getElementById('koraChatForm');
  if (koraChatForm) {
    koraChatForm.addEventListener('submit', (e) => {
      e.preventDefault();
      sendKoraMessage();
    });
  }
}

function scrollToSection(sectionId) {
  const el = document.getElementById(sectionId);
  if (el) el.scrollIntoView({ behavior: 'smooth' });
}

/* =========================================================================
   Multi-Image Carousel Controller
   ========================================================================= */

function nextSlide(key, total, event) {
  if (event) event.stopPropagation();
  const current = AppState.cardSlideIndices[key] || 0;
  const next = (current + 1) % total;
  AppState.cardSlideIndices[key] = next;
  updateCarouselDOM(key, next, total);
}

function prevSlide(key, total, event) {
  if (event) event.stopPropagation();
  const current = AppState.cardSlideIndices[key] || 0;
  const prev = (current - 1 + total) % total;
  AppState.cardSlideIndices[key] = prev;
  updateCarouselDOM(key, prev, total);
}

function updateCarouselDOM(key, index, total) {
  const container = document.getElementById(`carousel-${key}`);
  if (!container) return;

  const track = container.querySelector('.carousel-track');
  if (track) {
    track.style.transform = `translateX(-${index * 100}%)`;
  }

  const dots = container.querySelectorAll('.carousel-dot');
  dots.forEach((d, i) => {
    if (i === index) {
      d.classList.add('bg-white', 'w-3.5');
      d.classList.remove('bg-white/50', 'w-1.5');
    } else {
      d.classList.remove('bg-white', 'w-3.5');
      d.classList.add('bg-white/50', 'w-1.5');
    }
  });
}

/* =========================================================================
   Rendering All Homepage Sections
   ========================================================================= */

function renderApp() {
  renderPlacesList();
  renderHotelsList();
  renderItinerariesList();
  renderCultureList();
  renderStatsBar();
  renderCompareShowcase();
}

function renderStatsBar() {
  const s = AppState.stats;
  if (!s) return;
  const statsContainer = document.getElementById('statsContainer');
  if (statsContainer) {
    statsContainer.innerHTML = `
      <div class="flex items-center space-x-3 text-xs text-emerald-900 font-medium overflow-x-auto py-1">
        <span class="inline-block w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse"></span>
        <span><strong>${s.total_places || 10}</strong> Must-Visit Spots</span>
        <span>•</span>
        <span><strong>${s.waterfalls || 2}</strong> Roaring Waterfalls</span>
        <span>•</span>
        <span><strong>${s.peaks || 2}</strong> Cloud Peaks</span>
        <span>•</span>
        <span><strong>${s.hotels || 4}</strong> Eco-Stays & Camps</span>
        <span>•</span>
        <span>Highest Peak: <strong>${s.elevation || '1672m'} (Deomali)</strong></span>
        <span>•</span>
        <span class="text-amber-800 font-semibold">☕ 100% Organic GI Arabica Coffee</span>
      </div>
    `;
  }
}

function renderPlacesList() {
  const container = document.getElementById('placesGrid');
  if (!container) return;

  if (AppState.places.length === 0) {
    container.innerHTML = `
      <div class="col-span-full py-16 text-center text-gray-500">
        <p class="text-lg font-medium">No destinations found matching your criteria.</p>
        <p class="text-sm">Try clearing filters or search for another landmark in Koraput.</p>
      </div>
    `;
    return;
  }

  container.innerHTML = AppState.places.map(place => {
    const isSaved = AppState.savedTrip.includes(place.id);
    const badgeClass = `badge-${place.category || 'peak'}`;
    const categoryIcon = getCategoryIcon(place.category);
    const images = Array.isArray(place.image_urls) && place.image_urls.length > 0 
      ? place.image_urls 
      : [place.image_url];
    const cardKey = `place-${place.id}`;
    const totalImages = images.length;

    return `
      <div class="tourism-card bg-white rounded-3xl overflow-hidden shadow-sm border border-gray-100 flex flex-col justify-between group">
        <div>
          <!-- Card Image Header with Multi-Image Scrolling -->
          <div id="carousel-${cardKey}" class="relative h-64 overflow-hidden bg-gray-900 select-none">
            <div class="carousel-track flex h-full transition-transform duration-500 ease-out">
              ${images.map(img => `
                <div class="w-full h-full shrink-0 relative">
                  <img src="${img}" alt="${place.name}" class="w-full h-full object-cover" loading="lazy" />
                  <div class="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-black/30"></div>
                </div>
              `).join('')}
            </div>

            <!-- Carousel Controls -->
            ${totalImages > 1 ? `
              <button onclick="prevSlide('${cardKey}', ${totalImages}, event)" title="Previous image" class="absolute left-2.5 top-1/2 -translate-y-1/2 w-8 h-8 rounded-full bg-black/40 hover:bg-black/70 text-white flex items-center justify-center backdrop-blur-xs transition z-10 text-sm font-bold">
                ‹
              </button>
              <button onclick="nextSlide('${cardKey}', ${totalImages}, event)" title="Next image" class="absolute right-2.5 top-1/2 -translate-y-1/2 w-8 h-8 rounded-full bg-black/40 hover:bg-black/70 text-white flex items-center justify-center backdrop-blur-xs transition z-10 text-sm font-bold">
                ›
              </button>
              <div class="absolute bottom-12 left-0 right-0 flex justify-center space-x-1.5 z-10">
                ${images.map((_, i) => `
                  <span class="carousel-dot h-1.5 rounded-full transition-all duration-300 ${i === 0 ? 'bg-white w-3.5' : 'bg-white/50 w-1.5'}"></span>
                `).join('')}
              </div>
            ` : ''}

            <!-- Badges -->
            <div class="absolute top-3 left-3 flex items-center space-x-1.5 z-10">
              <span class="px-3 py-1 rounded-full text-xs font-semibold uppercase tracking-wider ${badgeClass} shadow-sm backdrop-blur-sm">
                ${categoryIcon} ${place.category}
              </span>
              ${place.distance_koraput ? `
                <span class="px-2.5 py-1 rounded-full text-xs font-medium bg-black/50 text-white backdrop-blur-md">
                  📍 ${place.distance_koraput.split('(')[0]}
                </span>
              ` : ''}
            </div>

            <!-- Save to Bucket Button -->
            <button onclick="toggleSaveTrip(${place.id})" title="${isSaved ? 'Remove from My Trip' : 'Save to My Trip'}" class="absolute top-3 right-3 w-9 h-9 rounded-full bg-white/90 hover:bg-white text-gray-700 flex items-center justify-center shadow transition-all z-10 ${isSaved ? 'text-rose-500 font-bold' : ''}">
              ${isSaved ? '❤️' : '🤍'}
            </button>

            <!-- Bottom Title overlay -->
            <div class="absolute bottom-3 left-3 right-3 text-white z-10">
              <h3 class="text-xl font-bold leading-tight drop-shadow-md">${place.name}</h3>
              <p class="text-xs text-emerald-200 line-clamp-1 italic">${place.tagline || 'Scenic highlight of Koraput'}</p>
            </div>
          </div>

          <!-- Card Content -->
          <div class="p-6">
            <div class="mb-3 flex items-center justify-between">
              <span class="text-xs text-amber-600 font-medium flex items-center font-bold">
                ★ ${place.rating} / 5.0
              </span>
              <span class="text-[11px] bg-emerald-50 text-emerald-700 px-2.5 py-0.5 rounded-full font-mono font-medium">
                AI Refined Story
              </span>
            </div>

            <p class="text-xs text-gray-600 line-clamp-3 mb-4 leading-relaxed">
              ${place.refined_story ? place.refined_story.replace(/<[^>]+>/g, '').replace(/\*\*/g, '') : place.raw_content}
            </p>

            <div class="space-y-1.5 mb-2">
              ${(place.highlights || []).slice(0, 2).map(h => `
                <div class="flex items-start text-xs text-gray-700">
                  <span class="text-emerald-600 mr-2 font-bold">✓</span>
                  <span class="line-clamp-1">${h}</span>
                </div>
              `).join('')}
            </div>
          </div>
        </div>

        <!-- Footer Actions -->
        <div class="px-6 pb-6 pt-2 border-t border-gray-100 flex items-center justify-between gap-2">
          <button onclick="openPlaceModal(${place.id})" class="flex-1 bg-emerald-800 hover:bg-emerald-900 text-white font-medium py-2.5 px-3 rounded-xl text-xs flex items-center justify-center transition shadow-xs">
            <span>Explore Details</span>
            <svg class="w-3.5 h-3.5 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3"/></svg>
          </button>
          
          <button onclick="openCompareModal(${place.id})" title="Compare Admin Raw Note vs Refined Customer Story" class="bg-gray-100 hover:bg-amber-100 hover:text-amber-800 text-gray-600 p-2.5 rounded-xl text-xs font-mono flex items-center transition">
            <span class="mr-1">⚡</span>
            <span class="hidden sm:inline">Compare</span>
          </button>
        </div>
      </div>
    `;
  }).join('');
}

function renderHotelsList() {
  const container = document.getElementById('hotelsGrid');
  if (!container) return;

  container.innerHTML = AppState.hotels.map(h => {
    const images = Array.isArray(h.image_urls) && h.image_urls.length > 0 ? h.image_urls : [h.image_url];
    const hotelKey = `hotel-${h.id}`;
    const totalImages = images.length;

    return `
      <div class="tourism-card bg-white rounded-3xl overflow-hidden shadow-sm border border-gray-100 flex flex-col justify-between hover:shadow-md transition">
        <div>
          <!-- Hotel Multi-Image Carousel -->
          <div id="carousel-${hotelKey}" class="relative h-56 overflow-hidden bg-gray-900 select-none">
            <div class="carousel-track flex h-full transition-transform duration-500 ease-out">
              ${images.map(img => `
                <div class="w-full h-full shrink-0 relative">
                  <img src="${img}" alt="${h.name}" class="w-full h-full object-cover" />
                  <div class="absolute inset-0 bg-gradient-to-t from-black/70 to-transparent"></div>
                </div>
              `).join('')}
            </div>

            ${totalImages > 1 ? `
              <button onclick="prevSlide('${hotelKey}', ${totalImages}, event)" class="absolute left-2.5 top-1/2 -translate-y-1/2 w-7 h-7 rounded-full bg-black/40 hover:bg-black/70 text-white flex items-center justify-center transition z-10">‹</button>
              <button onclick="nextSlide('${hotelKey}', ${totalImages}, event)" class="absolute right-2.5 top-1/2 -translate-y-1/2 w-7 h-7 rounded-full bg-black/40 hover:bg-black/70 text-white flex items-center justify-center transition z-10">›</button>
              <div class="absolute bottom-3 left-0 right-0 flex justify-center space-x-1 z-10">
                ${images.map((_, i) => `
                  <span class="carousel-dot h-1.5 rounded-full ${i === 0 ? 'bg-white w-3' : 'bg-white/50 w-1.5'}"></span>
                `).join('')}
              </div>
            ` : ''}

            <span class="absolute top-3 left-3 bg-purple-900/80 text-white text-xs px-2.5 py-1 rounded-full backdrop-blur-sm z-10 font-medium">
              🏨 ${h.category.replace('_', ' ').toUpperCase()}
            </span>
            <span class="absolute bottom-3 right-3 bg-white/95 text-emerald-900 text-xs px-3 py-1 rounded-xl font-bold shadow-sm z-10">
              ${h.price_range}
            </span>
          </div>

          <div class="p-6">
            <h3 class="text-lg font-bold text-gray-900 mb-1">${h.name}</h3>
            <p class="text-xs text-gray-500 mb-3 flex items-center">
              📍 ${h.location} • ${h.distance_koraput}
            </p>
            <p class="text-xs text-gray-600 line-clamp-3 mb-4 leading-relaxed italic">
              "${h.tagline || h.refined_story.substring(0, 140) + '...'}"
            </p>
            <div class="flex flex-wrap gap-1.5 mb-2">
              ${(h.amenities || []).slice(0, 4).map(a => `
                <span class="text-[11px] bg-purple-50 text-purple-900 px-2.5 py-0.5 rounded-full border border-purple-100">${a}</span>
              `).join('')}
            </div>
          </div>
        </div>

        <div class="p-6 pt-0 border-t border-gray-50 flex items-center justify-between text-xs">
          <span class="text-gray-500 font-mono">📞 ${h.contact}</span>
          <button onclick="alert('Enquiry booking for: ${h.name}\\nContact: ${h.contact}\\nBooking Portal: ${h.booking_url || 'https://www.ecotourodisha.com'}')" class="bg-emerald-800 hover:bg-emerald-900 text-white font-medium px-4 py-2 rounded-xl transition shadow-xs">
            Book Stay
          </button>
        </div>
      </div>
    `;
  }).join('');
}

function renderCultureList() {
  const container = document.getElementById('cultureGrid');
  if (!container) return;

  container.innerHTML = AppState.culture.map(c => `
    <div class="tourism-card bg-white rounded-3xl overflow-hidden shadow-sm border border-gray-100 group flex flex-col justify-between">
      <div>
        <div class="relative h-60 overflow-hidden">
          <img src="${c.image_url}" alt="${c.title}" class="w-full h-full object-cover group-hover:scale-105 transition duration-700" />
          <div class="absolute inset-0 bg-gradient-to-t from-black/85 via-black/30 to-transparent"></div>
          <div class="absolute bottom-4 left-4 right-4 text-white">
            <span class="text-[11px] font-bold uppercase tracking-wider text-amber-300 bg-black/40 px-2 py-0.5 rounded">
              ${c.category.replace('_', ' ')}
            </span>
            <h3 class="text-xl font-bold leading-tight mt-1.5">${c.title}</h3>
          </div>
        </div>
        <div class="p-6">
          <div class="text-xs text-gray-700 leading-relaxed mb-4 whitespace-pre-line line-clamp-4">
            ${c.refined_article}
          </div>
          <h4 class="text-xs font-bold text-emerald-900 uppercase tracking-wider mb-2">Heritage Highlights:</h4>
          <ul class="space-y-1.5 text-xs text-gray-600">
            ${(c.highlights || []).slice(0, 3).map(h => `
              <li class="flex items-start">
                <span class="text-amber-500 mr-2 font-bold">✦</span>
                <span class="line-clamp-1">${h}</span>
              </li>
            `).join('')}
          </ul>
        </div>
      </div>
      <div class="p-6 pt-0">
        <button onclick="openCultureDetail('${encodeURIComponent(c.title)}', '${encodeURIComponent(c.refined_article)}', '${encodeURIComponent(JSON.stringify(c.highlights))}', '${c.image_url}')" class="w-full bg-amber-50 hover:bg-amber-100 text-amber-900 font-semibold py-2 rounded-xl text-xs transition border border-amber-200">
          Read Full Heritage Chronicle →
        </button>
      </div>
    </div>
  `).join('');
}

function openCultureDetail(titleEnc, textEnc, highsEnc, imgUrl) {
  const title = decodeURIComponent(titleEnc);
  const text = decodeURIComponent(textEnc);
  const highlights = JSON.parse(decodeURIComponent(highsEnc));

  const modal = document.getElementById('detailsModal');
  const modalContent = document.getElementById('modalDynamicContent');

  modalContent.innerHTML = `
    <div class="relative h-64 overflow-hidden">
      <img src="${imgUrl}" class="w-full h-full object-cover" />
      <div class="absolute inset-0 bg-gradient-to-t from-black/85 to-transparent"></div>
      <div class="absolute bottom-4 left-6 right-6 text-white">
        <span class="text-xs text-amber-300 font-bold uppercase">Koraput Living Heritage</span>
        <h2 class="text-2xl font-extrabold mt-1">${title}</h2>
      </div>
    </div>
    <div class="p-6 space-y-4">
      <p class="text-xs sm:text-sm text-gray-700 leading-relaxed whitespace-pre-line">${text.replace(/\*\*/g, '')}</p>
      <div class="bg-amber-50 p-4 rounded-2xl border border-amber-200">
        <h4 class="text-xs font-bold text-amber-900 uppercase mb-2">Key Heritage Insights:</h4>
        <ul class="space-y-1 text-xs text-gray-700">
          ${highlights.map(h => `<li>✦ ${h}</li>`).join('')}
        </ul>
      </div>
      <button onclick="closeDetailsModal()" class="w-full bg-emerald-800 text-white font-bold py-2.5 rounded-xl text-xs">
        Close Chronicle
      </button>
    </div>
  `;
  modal.classList.remove('hidden');
}

function renderItinerariesList() {
  const container = document.getElementById('itinerariesList');
  if (!container) return;

  container.innerHTML = AppState.itineraries.map((it, idx) => `
    <div class="bg-white rounded-3xl p-6 sm:p-8 shadow-sm border border-gray-100 mb-8 hover:shadow-md transition">
      <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-gray-100">
        <div>
          <div class="flex items-center space-x-2 mb-1.5">
            <span class="px-3 py-1 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800">
              ⏱️ ${it.duration}
            </span>
            <span class="px-3 py-1 rounded-full text-xs font-medium bg-amber-100 text-amber-800">
              ${it.theme}
            </span>
            <span class="text-xs text-gray-400">Budget: ${it.budget}</span>
          </div>
          <h3 class="text-2xl font-bold text-gray-900">${it.title}</h3>
          <p class="text-xs text-gray-500 mt-0.5">${it.subtitle || 'Carefully tailored Koraput exploration'}</p>
        </div>
        <button onclick="toggleItineraryDetails('itinerary-days-${idx}')" class="self-start md:self-auto bg-emerald-50 hover:bg-emerald-100 text-emerald-800 font-semibold px-4 py-2.5 rounded-xl text-xs transition flex items-center border border-emerald-200">
          <span>View Day-by-Day Schedule</span>
          <svg class="w-3.5 h-3.5 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
        </button>
      </div>

      <div class="mt-4 text-xs text-gray-700 leading-relaxed">
        <p class="italic text-gray-600 mb-3">${it.refined_story || it.raw_content}</p>
      </div>

      <div id="itinerary-days-${idx}" class="mt-4 pt-4 border-t border-gray-100 space-y-4">
        ${(it.days || []).map(d => `
          <div class="bg-gray-50/70 rounded-2xl p-5 border border-gray-200/60">
            <h4 class="font-bold text-emerald-900 text-sm mb-3 flex items-center">
              <span class="w-6 h-6 rounded-full bg-emerald-700 text-white flex items-center justify-center text-xs mr-2 font-mono">D${d.day}</span>
              ${d.title}
            </h4>
            <div class="space-y-2 pl-6 border-l-2 border-emerald-300 ml-3">
              ${(d.schedule || []).map(s => `
                <div class="text-xs">
                  <span class="font-semibold text-gray-900 bg-white px-2 py-0.5 rounded border border-gray-200">${s.time}</span>
                  <span class="text-gray-700 ml-2">${s.activity}</span>
                </div>
              `).join('')}
            </div>
          </div>
        `).join('')}
      </div>
    </div>
  `).join('');
}

function toggleItineraryDetails(elementId) {
  const el = document.getElementById(elementId);
  if (el) el.classList.toggle('hidden');
}

/* =========================================================================
   Compare Showcase (Admin Raw vs Refined Story)
   ========================================================================= */

function renderCompareShowcase() {
  const container = document.getElementById('compareShowcaseContainer');
  if (!container) return;

  container.innerHTML = AppState.places.slice(0, 3).map(place => `
    <div class="bg-white rounded-3xl p-6 shadow-sm border border-gray-200 mb-6">
      <div class="flex items-center justify-between pb-3 mb-4 border-b border-gray-100">
        <div>
          <span class="px-2.5 py-0.5 rounded-full text-xs font-semibold badge-${place.category}">
            ${place.category.toUpperCase()}
          </span>
          <h3 class="text-xl font-bold text-gray-900 mt-1">${place.name}</h3>
          <p class="text-xs text-gray-500">${place.location} • ${place.distance_koraput}</p>
        </div>
        <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800">
          Refined for Tourists
        </span>
      </div>

      <div class="compare-container">
        <!-- Left: Raw Admin Notes -->
        <div class="raw-admin-box">
          <div class="flex items-center justify-between pb-2 mb-2 border-b border-gray-200 text-xs font-semibold text-gray-500 uppercase">
            <span>Admin's Raw Notes (Input)</span>
            <span class="text-[10px] bg-gray-200 text-gray-700 px-1.5 py-0.5 rounded">Unformatted</span>
          </div>
          <p class="leading-relaxed whitespace-pre-wrap">${place.raw_content}</p>
        </div>

        <!-- Right: Refined Tourist Story -->
        <div class="refined-tourist-box">
          <div class="flex items-center justify-between pb-2 mb-2 border-b border-emerald-200 text-xs font-semibold text-emerald-800 uppercase">
            <span>✨ Customer View (AI Refined Story)</span>
            <span class="text-[10px] bg-emerald-600 text-white px-2 py-0.5 rounded-full font-bold">Tourist-Ready</span>
          </div>
          <h4 class="font-bold text-gray-900 text-sm mb-1">${place.refined_title || place.name}</h4>
          <p class="text-xs text-emerald-700 italic mb-2 font-medium">"${place.tagline || ''}"</p>
          <p class="text-xs text-gray-700 leading-relaxed mb-3 line-clamp-4">
            ${place.refined_story ? place.refined_story.replace(/\*\*/g, '') : ''}
          </p>
        </div>
      </div>
    </div>
  `).join('');
}

/* =========================================================================
   Detail Modal View
   ========================================================================= */

function openPlaceModal(placeId) {
  const place = AppState.places.find(p => p.id === placeId);
  if (!place) return;

  AppState.selectedItem = place;
  const modal = document.getElementById('detailsModal');
  const modalContent = document.getElementById('modalDynamicContent');
  const images = Array.isArray(place.image_urls) && place.image_urls.length > 0 ? place.image_urls : [place.image_url];
  const modalKey = `modal-${place.id}`;

  modalContent.innerHTML = `
    <!-- Modal Carousel Header -->
    <div id="carousel-${modalKey}" class="relative h-72 sm:h-80 overflow-hidden bg-gray-900">
      <div class="carousel-track flex h-full transition-transform duration-500 ease-out">
        ${images.map(img => `
          <div class="w-full h-full shrink-0 relative">
            <img src="${img}" alt="${place.name}" class="w-full h-full object-cover" />
            <div class="absolute inset-0 bg-gradient-to-t from-gray-950/90 via-gray-900/30 to-transparent"></div>
          </div>
        `).join('')}
      </div>

      ${images.length > 1 ? `
        <button onclick="prevSlide('${modalKey}', ${images.length}, event)" class="absolute left-3 top-1/2 -translate-y-1/2 w-8 h-8 rounded-full bg-black/50 text-white flex items-center justify-center z-10">‹</button>
        <button onclick="nextSlide('${modalKey}', ${images.length}, event)" class="absolute right-3 top-1/2 -translate-y-1/2 w-8 h-8 rounded-full bg-black/50 text-white flex items-center justify-center z-10">›</button>
      ` : ''}

      <div class="absolute top-4 left-4 flex gap-2 z-10">
        <span class="px-3 py-1 rounded-full text-xs font-semibold badge-${place.category}">
          ${getCategoryIcon(place.category)} ${place.category.toUpperCase()}
        </span>
        <span class="px-3 py-1 rounded-full text-xs font-medium bg-black/60 text-white backdrop-blur-md">
          ⭐ ${place.rating} / 5.0
        </span>
      </div>

      <div class="absolute bottom-4 left-4 right-4 text-white z-10">
        <h2 class="text-2xl sm:text-3xl font-extrabold tracking-tight">${place.refined_title || place.name}</h2>
        <p class="text-sm text-emerald-300 italic font-medium mt-0.5">${place.tagline || ''}</p>
        <p class="text-xs text-gray-300 mt-1">📍 ${place.location} (${place.distance_koraput})</p>
      </div>
    </div>

    <!-- Modal Body -->
    <div class="p-6">
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 p-4 bg-emerald-50/60 rounded-xl border border-emerald-100 text-xs mb-6">
        <div>
          <span class="text-gray-500 block">Best Season</span>
          <span class="font-semibold text-emerald-900">${place.best_season || 'Oct to March'}</span>
        </div>
        <div>
          <span class="text-gray-500 block">Ideal Duration</span>
          <span class="font-semibold text-emerald-900">${place.ideal_duration || '2 to 3 Hours'}</span>
        </div>
        <div>
          <span class="text-gray-500 block">Entry Fee</span>
          <span class="font-semibold text-emerald-900">${place.entry_fee || 'Free'}</span>
        </div>
        <div>
          <span class="text-gray-500 block">Timings</span>
          <span class="font-semibold text-emerald-900">${place.timing || '06:00 AM - 06:00 PM'}</span>
        </div>
      </div>

      <!-- Tab Buttons Inside Modal -->
      <div class="flex border-b border-gray-200 mb-4 text-sm font-medium">
        <button id="modalTabRefined" onclick="switchModalSubTab('refined')" class="py-2 px-4 border-b-2 border-emerald-600 text-emerald-700 font-semibold">
          ✨ Refined Tourist Experience
        </button>
        <button id="modalTabRaw" onclick="switchModalSubTab('raw')" class="py-2 px-4 text-gray-500 hover:text-gray-700">
          📝 Raw Admin Draft Note
        </button>
      </div>

      <!-- Tab 1: Refined Story -->
      <div id="modalSubTabRefined" class="space-y-5">
        <div>
          <h4 class="text-sm font-bold text-gray-900 uppercase tracking-wider mb-2 text-emerald-800">The Story & Landscape</h4>
          <div class="text-xs sm:text-sm text-gray-700 leading-relaxed whitespace-pre-line">
            ${place.refined_story ? place.refined_story.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>') : place.raw_content}
          </div>
        </div>

        <div>
          <h4 class="text-sm font-bold text-gray-900 uppercase tracking-wider mb-2 text-emerald-800">Key Highlights & Photo Spots</h4>
          <ul class="space-y-2 text-xs text-gray-700">
            ${(place.highlights || []).map(h => `
              <li class="flex items-start bg-gray-50 p-2.5 rounded-lg border border-gray-100">
                <span class="text-emerald-500 mr-2 font-bold text-sm">✓</span>
                <span>${h}</span>
              </li>
            `).join('')}
          </ul>
        </div>

        <div>
          <h4 class="text-sm font-bold text-gray-900 uppercase tracking-wider mb-2 text-emerald-800">Local Travel Tips & Guidance</h4>
          <ul class="space-y-2 text-xs text-gray-700">
            ${(place.travel_tips || []).map(t => `
              <li class="flex items-start bg-amber-50/60 p-2.5 rounded-lg border border-amber-200/60">
                <span class="text-amber-600 mr-2 font-bold">💡</span>
                <span>${t}</span>
              </li>
            `).join('')}
          </ul>
        </div>
      </div>

      <!-- Tab 2: Raw Admin Notes -->
      <div id="modalSubTabRaw" class="hidden">
        <div class="bg-gray-50 rounded-xl p-5 border border-dashed border-gray-300 font-mono text-xs text-gray-700">
          <div class="text-gray-400 font-semibold mb-2">RAW_ADMIN_INPUT_DRAFT:</div>
          <div class="leading-relaxed whitespace-pre-wrap">${place.raw_content}</div>
        </div>
      </div>

      <!-- Modal Footer -->
      <div class="mt-8 pt-4 border-t border-gray-100 flex items-center justify-between">
        <button onclick="toggleSaveTrip(${place.id})" class="px-4 py-2 rounded-xl text-xs font-semibold border border-gray-200 hover:bg-gray-50 flex items-center transition">
          ${AppState.savedTrip.includes(place.id) ? '❤️ In Your Trip Bucket' : '➕ Add to My Trip Bucket'}
        </button>
        <button onclick="closeDetailsModal()" class="px-5 py-2 bg-emerald-800 hover:bg-emerald-900 text-white rounded-xl text-xs font-semibold transition">
          Close Explorer
        </button>
      </div>
    </div>
  `;

  modal.classList.remove('hidden');
}

function switchModalSubTab(tab) {
  const tabRefined = document.getElementById('modalTabRefined');
  const tabRaw = document.getElementById('modalTabRaw');
  const subRefined = document.getElementById('modalSubTabRefined');
  const subRaw = document.getElementById('modalSubTabRaw');

  if (tab === 'refined') {
    tabRefined.classList.add('border-b-2', 'border-emerald-600', 'text-emerald-700', 'font-semibold');
    tabRefined.classList.remove('text-gray-500');
    tabRaw.classList.remove('border-b-2', 'border-emerald-600', 'text-emerald-700', 'font-semibold');
    tabRaw.classList.add('text-gray-500');
    subRefined.classList.remove('hidden');
    subRaw.classList.add('hidden');
  } else {
    tabRaw.classList.add('border-b-2', 'border-emerald-600', 'text-emerald-700', 'font-semibold');
    tabRaw.classList.remove('text-gray-500');
    tabRefined.classList.remove('border-b-2', 'border-emerald-600', 'text-emerald-700', 'font-semibold');
    tabRefined.classList.add('text-gray-500');
    subRefined.classList.add('hidden');
    subRaw.classList.remove('hidden');
  }
}

function closeDetailsModal() {
  const modal = document.getElementById('detailsModal');
  if (modal) modal.classList.add('hidden');
}

function openCompareModal(placeId) {
  openPlaceModal(placeId);
  switchModalSubTab('raw');
}

/* =========================================================================
   "Ask Kora" AI Tour Guide Mode (With Typewriter Streaming Effect)
   ========================================================================= */

let activeTypewriterTimer = null;

function openKoraChatModal() {
  const modal = document.getElementById('koraChatModal');
  if (modal) {
    modal.classList.remove('hidden');
    if (AppState.chatHistory.length === 0) {
      appendKoraMessage({
        sender: 'kora',
        text: "**Johar!** 🙏 I am **Kora, the Spirit of Koraput** - your friendly local guide to Nature, Culture & Adventure in the *Heaven of Odisha*!\n\nAsk me anything specific about our misty peaks, waterfalls, caves, GI coffee trails, eco-stays, or tribal culture!",
        suggestions: [
          "What is the height of Deomali?",
          "How many steps at Duduma Waterfalls?",
          "Where to stay: Eco cottages & camps?",
          "Why is Koraput Coffee so famous?",
          "Which day is Kunduli tribal haat?"
        ]
      }, true);
    }
    const input = document.getElementById('koraChatInput');
    if (input) input.focus();
  }
}

function closeKoraChatModal() {
  if (activeTypewriterTimer) {
    clearInterval(activeTypewriterTimer);
    activeTypewriterTimer = null;
  }
  const modal = document.getElementById('koraChatModal');
  if (modal) modal.classList.add('hidden');
}

function appendKoraMessage(msg, animateTypewriter = false) {
  AppState.chatHistory.push(msg);
  const container = document.getElementById('koraChatMessages');
  if (!container) return;

  const isUser = msg.sender === 'user';
  const msgEl = document.createElement('div');
  msgEl.className = `flex items-start space-x-2.5 mb-4 ${isUser ? 'justify-end' : 'justify-start'}`;

  if (!isUser) {
    const textContainerId = `kora-text-${Date.now()}-${Math.floor(Math.random() * 1000)}`;
    const suggestionsId = `kora-sug-${Date.now()}-${Math.floor(Math.random() * 1000)}`;

    msgEl.innerHTML = `
      <img src="/static/images/kora_avatar.jpg" alt="Kora" class="w-8 h-8 rounded-full border-2 border-emerald-500 object-cover shadow-xs shrink-0 mt-0.5" />
      <div class="max-w-[85%] bg-white rounded-2xl rounded-tl-none p-4 shadow-sm border border-emerald-100 text-xs text-gray-800">
        <div class="font-extrabold text-emerald-800 text-[11px] mb-1 flex items-center">
          <span>Kora • Spirit of Koraput</span>
          <span class="ml-1.5 px-1.5 py-0.2 rounded bg-emerald-50 text-[9px] font-mono text-emerald-700">AI Guide</span>
        </div>
        <div id="${textContainerId}" class="leading-relaxed font-sans text-xs sm:text-[13px] text-gray-700"></div>
        ${msg.suggestions && msg.suggestions.length > 0 ? `
          <div id="${suggestionsId}" class="mt-3 pt-2.5 border-t border-gray-100 flex flex-wrap gap-1.5 transition-opacity duration-500 ${animateTypewriter ? 'opacity-0' : 'opacity-100'}">
            ${msg.suggestions.map(s => `
              <button onclick="askKoraPrompt('${s}')" class="text-[10px] sm:text-[11px] bg-emerald-50 hover:bg-emerald-100 text-emerald-800 px-3 py-1 rounded-full border border-emerald-200 transition font-medium">
                ${s}
              </button>
            `).join('')}
          </div>
        ` : ''}
      </div>
    `;

    container.appendChild(msgEl);
    const textEl = document.getElementById(textContainerId);
    const sugEl = document.getElementById(suggestionsId);

    if (animateTypewriter && textEl) {
      streamTypewriterEffect(textEl, msg.text, sugEl, container);
    } else if (textEl) {
      textEl.innerHTML = formatKoraMarkdown(msg.text);
      container.scrollTop = container.scrollHeight;
    }
  } else {
    // User message
    msgEl.innerHTML = `
      <div class="max-w-[85%] bg-emerald-800 text-white rounded-2xl rounded-tr-none px-4 py-2.5 text-xs sm:text-[13px] leading-relaxed shadow-sm">
        ${msg.text}
      </div>
      <div class="w-7 h-7 rounded-full bg-emerald-950 text-white flex items-center justify-center text-[10px] font-bold shrink-0 mt-0.5">
        You
      </div>
    `;
    container.appendChild(msgEl);
    container.scrollTop = container.scrollHeight;
  }
}

/**
 * Typewriter Streaming Effect:
 * Streams words with variable natural typing speed, blinking cursor, and auto-scroll.
 */
function streamTypewriterEffect(targetEl, fullText, suggestionsEl, scrollContainer) {
  if (activeTypewriterTimer) {
    clearInterval(activeTypewriterTimer);
  }

  // Split text by whitespace into words while preserving newlines
  const words = fullText.split(/(\s+)/);
  let currentIndex = 0;
  let accumulatedText = "";

  const cursorSpan = document.createElement('span');
  cursorSpan.className = 'inline-block w-1.5 h-3.5 bg-emerald-600 animate-pulse ml-0.5 align-middle';

  // Fast forward if user clicks the message
  targetEl.parentElement.style.cursor = 'pointer';
  const fastForwardHandler = () => {
    if (activeTypewriterTimer) {
      clearInterval(activeTypewriterTimer);
      activeTypewriterTimer = null;
      targetEl.innerHTML = formatKoraMarkdown(fullText);
      if (suggestionsEl) suggestionsEl.classList.remove('opacity-0');
      scrollContainer.scrollTop = scrollContainer.scrollHeight;
      targetEl.parentElement.style.cursor = 'default';
      targetEl.parentElement.removeEventListener('click', fastForwardHandler);
    }
  };
  targetEl.parentElement.addEventListener('click', fastForwardHandler);

  activeTypewriterTimer = setInterval(() => {
    if (currentIndex < words.length) {
      accumulatedText += words[currentIndex];
      currentIndex++;
      targetEl.innerHTML = formatKoraMarkdown(accumulatedText);
      targetEl.appendChild(cursorSpan);
      scrollContainer.scrollTop = scrollContainer.scrollHeight;
    } else {
      // Stream finished
      clearInterval(activeTypewriterTimer);
      activeTypewriterTimer = null;
      targetEl.innerHTML = formatKoraMarkdown(fullText);
      if (suggestionsEl) {
        suggestionsEl.classList.remove('opacity-0');
        suggestionsEl.classList.add('opacity-100');
      }
      scrollContainer.scrollTop = scrollContainer.scrollHeight;
      targetEl.parentElement.style.cursor = 'default';
      targetEl.parentElement.removeEventListener('click', fastForwardHandler);
    }
  }, 22); // natural ~22ms per word stream
}

function formatKoraMarkdown(text) {
  if (!text) return "";
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong class="text-emerald-950 font-bold">$1</strong>')
    .replace(/\*(.*?)\*/g, '<em class="text-emerald-800">$1</em>')
    .replace(/\n•/g, '<br/>•')
    .replace(/\n\n/g, '<br/><br/>')
    .replace(/\n/g, '<br/>');
}

function askKoraPrompt(promptText) {
  const input = document.getElementById('koraChatInput');
  if (input) input.value = promptText;
  sendKoraMessage();
}

async function sendKoraMessage() {
  const input = document.getElementById('koraChatInput');
  const query = input.value.trim();
  if (!query) return;

  // Append user message immediately
  appendKoraMessage({ sender: 'user', text: query }, false);
  input.value = '';

  // Show realistic animated "Thinking & Exploring Database" bubble
  const container = document.getElementById('koraChatMessages');
  const typingEl = document.createElement('div');
  typingEl.id = 'koraTypingIndicator';
  typingEl.className = 'flex items-start space-x-2.5 mb-4 animate-fade-in';
  typingEl.innerHTML = `
    <img src="/static/images/kora_avatar.jpg" class="w-8 h-8 rounded-full border-2 border-emerald-500 object-cover shrink-0 mt-0.5" />
    <div class="bg-white rounded-2xl rounded-tl-none p-3 shadow-xs border border-emerald-100 flex items-center space-x-2.5">
      <div class="flex space-x-1">
        <span class="w-2 h-2 rounded-full bg-emerald-500 animate-bounce"></span>
        <span class="w-2 h-2 rounded-full bg-emerald-500 animate-bounce [animation-delay:0.15s]"></span>
        <span class="w-2 h-2 rounded-full bg-emerald-500 animate-bounce [animation-delay:0.3s]"></span>
      </div>
      <span class="text-[11px] text-emerald-800 font-medium">Kora is consulting Koraput records...</span>
    </div>
  `;
  container.appendChild(typingEl);
  container.scrollTop = container.scrollHeight;

  try {
    const res = await fetch('/api/ai/ask', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query })
    });
    const data = await res.json();
    typingEl.remove();

    if (data.success) {
      appendKoraMessage({
        sender: 'kora',
        text: data.answer,
        suggestions: data.suggestions
      }, true); // activate typewriter streaming effect!
    } else {
      appendKoraMessage({
        sender: 'kora',
        text: "Johar! I had trouble accessing our tourism database right now. Please try asking again in a moment."
      }, true);
    }
  } catch (err) {
    if (document.getElementById('koraTypingIndicator')) {
      document.getElementById('koraTypingIndicator').remove();
    }
    appendKoraMessage({
      sender: 'kora',
      text: "Johar! Could not connect to the Koraput knowledge base. Please ensure the app server is running."
    }, false);
  }
}

/* =========================================================================
   Trip Planner Bucket
   ========================================================================= */

function toggleSaveTrip(placeId) {
  const idx = AppState.savedTrip.indexOf(placeId);
  if (idx > -1) {
    AppState.savedTrip.splice(idx, 1);
  } else {
    AppState.savedTrip.push(placeId);
  }
  localStorage.setItem('koraput_trip', JSON.stringify(AppState.savedTrip));
  updateTripBadge();
  renderPlacesList();
  renderTripDrawerContent();
}

function updateTripBadge() {
  const badge = document.getElementById('tripBadgeCount');
  if (badge) {
    badge.textContent = AppState.savedTrip.length;
    if (AppState.savedTrip.length > 0) {
      badge.classList.remove('hidden');
    } else {
      badge.classList.add('hidden');
    }
  }
}

function openTripDrawer() {
  renderTripDrawerContent();
  const drawer = document.getElementById('tripDrawer');
  if (drawer) drawer.classList.remove('translate-x-full');
}

function closeTripDrawer() {
  const drawer = document.getElementById('tripDrawer');
  if (drawer) drawer.classList.add('translate-x-full');
}

function renderTripDrawerContent() {
  const container = document.getElementById('tripDrawerItems');
  if (!container) return;

  const savedPlaces = AppState.places.filter(p => AppState.savedTrip.includes(p.id));

  if (savedPlaces.length === 0) {
    container.innerHTML = `
      <div class="py-12 text-center text-gray-500">
        <p class="text-sm">Your Koraput trip bucket is empty.</p>
        <p class="text-xs text-gray-400 mt-1">Click the heart 🤍 on any destination card to plan your custom route!</p>
      </div>
    `;
    return;
  }

  container.innerHTML = `
    <div class="space-y-3">
      ${savedPlaces.map((p, i) => `
        <div class="flex items-center justify-between p-3 bg-gray-50 rounded-2xl border border-gray-100">
          <div class="flex items-center space-x-3">
            <span class="w-6 h-6 rounded-full bg-emerald-700 text-white flex items-center justify-center text-xs font-mono font-bold">${i + 1}</span>
            <div>
              <h4 class="text-xs font-bold text-gray-900">${p.name}</h4>
              <p class="text-[10px] text-gray-500">${p.location} • ${p.category}</p>
            </div>
          </div>
          <button onclick="toggleSaveTrip(${p.id})" class="text-rose-500 hover:text-rose-700 text-xs font-bold p-1">✕</button>
        </div>
      `).join('')}

      <div class="mt-6 p-4 bg-emerald-50 rounded-2xl border border-emerald-100 text-xs text-emerald-900 space-y-1">
        <div class="font-bold">Trip Summary:</div>
        <div>Total Destinations: <strong>${savedPlaces.length}</strong></div>
        <div>Estimated Exploration: <strong>${savedPlaces.length * 2.5} Hours</strong></div>
      </div>

      <button onclick="alert('Trip route generated! Pack your bags for the Heaven of Odisha.');" class="w-full mt-4 bg-emerald-800 hover:bg-emerald-900 text-white font-medium py-2.5 rounded-xl text-xs transition">
        Download / Print Travel Route
      </button>
    </div>
  `;
}

/* =========================================================================
   Soundscape Audio
   ========================================================================= */

function toggleKoraputAmbience() {
  if (AppState.audioPlaying) {
    stopKoraputAmbience();
  } else {
    startKoraputAmbience();
  }
}

function startKoraputAmbience() {
  try {
    const AudioContext = window.AudioContext || window.webkitAudioContext;
    if (!AudioContext) return;
    const ctx = new AudioContext();
    AppState.audioContext = ctx;

    const bufferSize = ctx.sampleRate * 2;
    const noiseBuffer = ctx.createBuffer(1, bufferSize, ctx.sampleRate);
    const output = noiseBuffer.getChannelData(0);
    let b0 = 0, b1 = 0, b2 = 0, b3 = 0, b4 = 0, b5 = 0, b6 = 0;
    for (let i = 0; i < bufferSize; i++) {
      const white = Math.random() * 2 - 1;
      b0 = 0.99886 * b0 + white * 0.0555179;
      b1 = 0.99332 * b1 + white * 0.0750759;
      b2 = 0.96900 * b2 + white * 0.1538520;
      b3 = 0.86650 * b3 + white * 0.3104856;
      b4 = 0.55000 * b4 + white * 0.5329522;
      b5 = -0.7616 * b5 - white * 0.0168980;
      output[i] = b0 + b1 + b2 + b3 + b4 + b5 + b6 + white * 0.5362;
      output[i] *= 0.05;
      b6 = white * 0.115926;
    }

    const whiteNoise = ctx.createBufferSource();
    whiteNoise.buffer = noiseBuffer;
    whiteNoise.loop = true;

    const filter = ctx.createBiquadFilter();
    filter.type = 'lowpass';
    filter.frequency.value = 800;

    const gainNode = ctx.createGain();
    gainNode.gain.setValueAtTime(0.12, ctx.currentTime);

    whiteNoise.connect(filter);
    filter.connect(gainNode);
    gainNode.connect(ctx.destination);
    whiteNoise.start();

    AppState.audioNodes = [whiteNoise, filter, gainNode];
    AppState.audioPlaying = true;

    const audioIndicator = document.getElementById('audioWaves');
    const audioLabel = document.getElementById('audioLabel');
    if (audioIndicator) audioIndicator.classList.add('audio-playing');
    if (audioLabel) audioLabel.textContent = 'Misty Ambiance (Playing)';
  } catch (err) {
    console.warn('Audio not allowed without gesture', err);
  }
}

function stopKoraputAmbience() {
  if (AppState.audioNodes) {
    AppState.audioNodes.forEach(node => {
      try { node.stop(); } catch(e){}
    });
  }
  if (AppState.audioContext) {
    try { AppState.audioContext.close(); } catch(e){}
  }
  AppState.audioPlaying = false;
  const audioIndicator = document.getElementById('audioWaves');
  const audioLabel = document.getElementById('audioLabel');
  if (audioIndicator) audioIndicator.classList.remove('audio-playing');
  if (audioLabel) audioLabel.textContent = 'Misty Ambiance';
}

function getCategoryIcon(cat) {
  const map = {
    'peak': '🏔️',
    'waterfall': '🌊',
    'temple': '🛕',
    'waterbody': '🚣',
    'coffee': '☕',
    'culture': '🥁',
    'hotel': '🏨'
  };
  return map[cat] || '📍';
}
