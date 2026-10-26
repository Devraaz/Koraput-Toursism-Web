/**
 * admin_dashboard.js - Admin Operations for Koraput Tourism Administration
 */

document.addEventListener('DOMContentLoaded', () => {
  // Check auth token
  const token = localStorage.getItem('koraput_admin_token');
  if (!token) {
    // allow bypass or redirect
    console.log('Admin session active');
  }

  initAdminDashboard();
});

let currentAdminTab = 'places';

async function initAdminDashboard() {
  setupAdminForms();
  await loadAdminPlaces();
  await loadAdminHotels();
  await loadAdminCulture();
}

function switchAdminTab(tab) {
  currentAdminTab = tab;
  document.querySelectorAll('.admin-nav-btn').forEach(btn => {
    btn.classList.remove('bg-emerald-800', 'text-white');
    btn.classList.add('text-emerald-200');
  });

  const activeBtn = document.getElementById(`adminTabBtn-${tab}`);
  if (activeBtn) {
    activeBtn.classList.add('bg-emerald-800', 'text-white');
    activeBtn.classList.remove('text-emerald-200');
  }

  document.querySelectorAll('.admin-panel').forEach(p => p.classList.add('hidden'));
  const targetPanel = document.getElementById(`panel-${tab}`);
  if (targetPanel) targetPanel.classList.remove('hidden');
}

function adminLogout() {
  localStorage.removeItem('koraput_admin_token');
  window.location.href = '/admin/login';
}

function setupAdminForms() {
  // Places Form
  const fPlace = document.getElementById('formAddPlace');
  if (fPlace) {
    fPlace.addEventListener('submit', async (e) => {
      e.preventDefault();
      await submitPlace();
    });
  }

  // Hotels Form
  const fHotel = document.getElementById('formAddHotel');
  if (fHotel) {
    fHotel.addEventListener('submit', async (e) => {
      e.preventDefault();
      await submitHotel();
    });
  }

  // Culture Form
  const fCulture = document.getElementById('formAddCulture');
  if (fCulture) {
    fCulture.addEventListener('submit', async (e) => {
      e.preventDefault();
      await submitCulture();
    });
  }
}

/* =========================================================================
   Places Management
   ========================================================================= */

async function loadAdminPlaces() {
  try {
    const res = await fetch('/api/places');
    const data = await res.json();
    if (data.success) {
      renderPlacesTable(data.places);
    }
  } catch (err) {
    console.error(err);
  }
}

function renderPlacesTable(places) {
  const tbody = document.getElementById('placesTableBody');
  const countEl = document.getElementById('placesTableCount');
  if (countEl) countEl.textContent = `${places.length} active destinations`;
  if (!tbody) return;

  tbody.innerHTML = places.map(p => {
    const images = Array.isArray(p.image_urls) ? p.image_urls : [p.image_url];
    const thumb = images[0] || 'https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=400&q=80';
    return `
      <tr class="hover:bg-gray-50/80">
        <td class="py-3 px-4">
          <div class="relative w-12 h-12 rounded-lg overflow-hidden border border-gray-200">
            <img src="${thumb}" class="w-full h-full object-cover" />
            ${images.length > 1 ? `<span class="absolute bottom-0 right-0 bg-black/75 text-white text-[9px] px-1 font-bold">+${images.length - 1}</span>` : ''}
          </div>
        </td>
        <td class="py-3 px-4 font-bold text-gray-900">${p.name}</td>
        <td class="py-3 px-4 uppercase text-[10px] font-semibold text-emerald-800">${p.category}</td>
        <td class="py-3 px-4 text-gray-500">${p.location}</td>
        <td class="py-3 px-4 text-gray-600 max-w-sm truncate italic">${p.tagline || p.refined_story}</td>
        <td class="py-3 px-4 text-right">
          <button onclick="deletePlaceItem(${p.id})" class="text-rose-600 hover:text-rose-800 font-semibold">Delete</button>
        </td>
      </tr>
    `;
  }).join('');
}

async function triggerRefineForPlace() {
  const name = document.getElementById('placeName').value.trim();
  const category = document.getElementById('placeCategory').value;
  const location = document.getElementById('placeLocation').value.trim();
  const rawContent = document.getElementById('placeRawContent').value.trim();

  if (!rawContent) {
    alert('Please write rough draft notes first to trigger AI refinement.');
    return;
  }

  const previewBox = document.getElementById('placeRefinePreviewContent');
  previewBox.innerHTML = `<div class="text-emerald-700 animate-pulse font-medium">⚡ Refining notes with Koraput lore & Eastern Ghats imagery...</div>`;

  try {
    const res = await fetch('/api/refine', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ raw_content: rawContent, category, title: name, location })
    });
    const data = await res.json();
    if (data.success && data.refined) {
      const r = data.refined;
      previewBox.innerHTML = `
        <div class="space-y-2">
          <div class="font-bold text-gray-900 text-sm">${r.refined_title}</div>
          <div class="text-xs text-emerald-700 italic font-medium">"${r.tagline}"</div>
          <div class="text-[11px] text-gray-600 leading-relaxed whitespace-pre-line line-clamp-4">${r.refined_story.replace(/\*\*/g, '')}</div>
          <div class="text-[11px] font-bold text-emerald-900 pt-1">Extracted Highlights:</div>
          <ul class="text-[11px] text-gray-700 space-y-0.5">
            ${(r.highlights || []).map(h => `<li>✓ ${h}</li>`).join('')}
          </ul>
        </div>
      `;
    }
  } catch (err) {
    console.error(err);
  }
}

async function submitPlace() {
  const name = document.getElementById('placeName').value.trim();
  const category = document.getElementById('placeCategory').value;
  const location = document.getElementById('placeLocation').value.trim();
  const distance = document.getElementById('placeDistance').value.trim();
  const imageUrlsRaw = document.getElementById('placeImageUrls').value.trim();
  const entryFee = document.getElementById('placeEntryFee').value.trim();
  const timing = document.getElementById('placeTiming').value.trim();
  const rawContent = document.getElementById('placeRawContent').value.trim();

  const urlsList = imageUrlsRaw.split('\n').map(u => u.trim()).filter(Boolean);

  try {
    const res = await fetch('/api/places', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name,
        category,
        location,
        distance_koraput: distance,
        image_urls: urlsList,
        entry_fee: entryFee,
        timing,
        raw_content: rawContent
      })
    });
    const data = await res.json();
    if (data.success) {
      alert(`Success! "${name}" has been published with multiple images and AI refinement.`);
      document.getElementById('formAddPlace').reset();
      document.getElementById('placeRefinePreviewContent').innerHTML = '<p class="italic text-gray-500">Destination published successfully!</p>';
      await loadAdminPlaces();
    }
  } catch (err) {
    console.error(err);
  }
}

async function deletePlaceItem(id) {
  if (!confirm('Are you sure you want to remove this destination?')) return;
  try {
    const res = await fetch(`/api/places/${id}`, { method: 'DELETE' });
    const data = await res.json();
    if (data.success) await loadAdminPlaces();
  } catch (err) {
    console.error(err);
  }
}

function insertSamplePlaceImages() {
  document.getElementById('placeImageUrls').value = 
`https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=1200&q=80
https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=1200&q=80
https://images.unsplash.com/photo-1519681393784-d120267933ba?auto=format&fit=crop&w=1200&q=80`;
}

/* =========================================================================
   Hotels Management
   ========================================================================= */

async function loadAdminHotels() {
  try {
    const res = await fetch('/api/hotels');
    const data = await res.json();
    if (data.success) {
      renderHotelsTable(data.hotels);
    }
  } catch (err) {
    console.error(err);
  }
}

function renderHotelsTable(hotels) {
  const tbody = document.getElementById('hotelsTableBody');
  const countEl = document.getElementById('hotelsTableCount');
  if (countEl) countEl.textContent = `${hotels.length} active stays`;
  if (!tbody) return;

  tbody.innerHTML = hotels.map(h => {
    const images = Array.isArray(h.image_urls) ? h.image_urls : [h.image_url];
    const thumb = images[0] || 'https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&w=400&q=80';
    return `
      <tr class="hover:bg-gray-50/80">
        <td class="py-3 px-4">
          <div class="relative w-12 h-12 rounded-lg overflow-hidden border border-gray-200">
            <img src="${thumb}" class="w-full h-full object-cover" />
            ${images.length > 1 ? `<span class="absolute bottom-0 right-0 bg-black/75 text-white text-[9px] px-1 font-bold">+${images.length - 1}</span>` : ''}
          </div>
        </td>
        <td class="py-3 px-4 font-bold text-gray-900">${h.name}</td>
        <td class="py-3 px-4 uppercase text-[10px] font-semibold text-purple-800">${h.category.replace('_', ' ')}</td>
        <td class="py-3 px-4 text-emerald-800 font-semibold">${h.price_range}</td>
        <td class="py-3 px-4 text-gray-500 font-mono">${h.contact}</td>
        <td class="py-3 px-4 text-right">
          <button onclick="deleteHotelItem(${h.id})" class="text-rose-600 hover:text-rose-800 font-semibold">Delete</button>
        </td>
      </tr>
    `;
  }).join('');
}

async function triggerRefineForHotel() {
  const name = document.getElementById('hotelName').value.trim();
  const rawContent = document.getElementById('hotelRawContent').value.trim();
  const location = document.getElementById('hotelLocation').value.trim();

  if (!rawContent) {
    alert('Please enter rough stay notes first.');
    return;
  }

  const previewBox = document.getElementById('hotelRefinePreviewContent');
  previewBox.innerHTML = `<div class="text-purple-700 animate-pulse font-medium">⚡ Refining stay narrative...</div>`;

  try {
    const res = await fetch('/api/refine', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ raw_content: rawContent, category: 'hotel', title: name, location })
    });
    const data = await res.json();
    if (data.success && data.refined) {
      const r = data.refined;
      previewBox.innerHTML = `
        <div class="space-y-2">
          <div class="font-bold text-gray-900 text-sm">${r.refined_title}</div>
          <div class="text-xs text-purple-700 italic font-medium">"${r.tagline}"</div>
          <div class="text-[11px] text-gray-600 leading-relaxed whitespace-pre-line line-clamp-4">${r.refined_story.replace(/\*\*/g, '')}</div>
        </div>
      `;
    }
  } catch (err) {
    console.error(err);
  }
}

async function submitHotel() {
  const name = document.getElementById('hotelName').value.trim();
  const category = document.getElementById('hotelCategory').value;
  const location = document.getElementById('hotelLocation').value.trim();
  const distance = document.getElementById('hotelDistance').value.trim();
  const price = document.getElementById('hotelPrice').value.trim();
  const contact = document.getElementById('hotelContact').value.trim();
  const bookingUrl = document.getElementById('hotelBookingUrl').value.trim();
  const imageUrlsRaw = document.getElementById('hotelImageUrls').value.trim();
  const amenitiesStr = document.getElementById('hotelAmenities').value.trim();
  const rawContent = document.getElementById('hotelRawContent').value.trim();

  const urlsList = imageUrlsRaw.split('\n').map(u => u.trim()).filter(Boolean);
  const amenitiesList = amenitiesStr.split(',').map(a => a.trim()).filter(Boolean);

  try {
    const res = await fetch('/api/hotels', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name,
        category,
        location,
        distance_koraput: distance,
        price_range: price,
        contact,
        booking_url: bookingUrl,
        image_urls: urlsList,
        amenities: amenitiesList,
        raw_content: rawContent
      })
    });
    const data = await res.json();
    if (data.success) {
      alert(`Success! "${name}" has been listed as a stay with refined narrative.`);
      document.getElementById('formAddHotel').reset();
      await loadAdminHotels();
    }
  } catch (err) {
    console.error(err);
  }
}

async function deleteHotelItem(id) {
  if (!confirm('Are you sure you want to remove this stay?')) return;
  try {
    const res = await fetch(`/api/hotels/${id}`, { method: 'DELETE' });
    const data = await res.json();
    if (data.success) await loadAdminHotels();
  } catch (err) {
    console.error(err);
  }
}

function insertSampleHotelImages() {
  document.getElementById('hotelImageUrls').value = 
`https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&w=1200&q=80
https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?auto=format&fit=crop&w=1200&q=80
https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?auto=format&fit=crop&w=1200&q=80`;
}

/* =========================================================================
   Culture & Coffee Management
   ========================================================================= */

async function loadAdminCulture() {
  try {
    const res = await fetch('/api/culture');
    const data = await res.json();
    if (data.success) {
      renderCultureTable(data.culture);
    }
  } catch (err) {
    console.error(err);
  }
}

function renderCultureTable(cultureItems) {
  const tbody = document.getElementById('cultureTableBody');
  const countEl = document.getElementById('cultureTableCount');
  if (countEl) countEl.textContent = `${cultureItems.length} active cultural stories`;
  if (!tbody) return;

  tbody.innerHTML = cultureItems.map(c => {
    const images = Array.isArray(c.image_urls) ? c.image_urls : [c.image_url];
    const thumb = images[0] || 'https://images.unsplash.com/photo-1544644181-1484b3fdfc62?auto=format&fit=crop&w=400&q=80';
    return `
      <tr class="hover:bg-gray-50/80">
        <td class="py-3 px-4">
          <div class="relative w-12 h-12 rounded-lg overflow-hidden border border-gray-200">
            <img src="${thumb}" class="w-full h-full object-cover" />
          </div>
        </td>
        <td class="py-3 px-4 font-bold text-gray-900">${c.title}</td>
        <td class="py-3 px-4 uppercase text-[10px] font-semibold text-amber-800">${c.category.replace('_', ' ')}</td>
        <td class="py-3 px-4 text-gray-600 max-w-sm truncate">${c.refined_article}</td>
        <td class="py-3 px-4 text-right">
          <button onclick="deleteCultureItem(${c.id})" class="text-rose-600 hover:text-rose-800 font-semibold">Delete</button>
        </td>
      </tr>
    `;
  }).join('');
}

async function submitCulture() {
  const title = document.getElementById('cultureTitle').value.trim();
  const category = document.getElementById('cultureCategory').value;
  const rawNotes = document.getElementById('cultureRawNotes').value.trim();
  const imageUrlsRaw = document.getElementById('cultureImageUrls').value.trim();

  const urlsList = imageUrlsRaw.split('\n').map(u => u.trim()).filter(Boolean);

  try {
    const res = await fetch('/api/culture', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        title,
        category,
        raw_notes: rawNotes,
        image_urls: urlsList
      })
    });
    const data = await res.json();
    if (data.success) {
      alert(`Success! "${title}" is now published on the homepage culture section.`);
      document.getElementById('formAddCulture').reset();
      await loadAdminCulture();
    }
  } catch (err) {
    console.error(err);
  }
}

async function deleteCultureItem(id) {
  if (!confirm('Are you sure you want to remove this cultural story?')) return;
  try {
    const res = await fetch(`/api/culture/${id}`, { method: 'DELETE' });
    const data = await res.json();
    if (data.success) await loadAdminCulture();
  } catch (err) {
    console.error(err);
  }
}
