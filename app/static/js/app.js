const grid = document.getElementById('softwareGrid');
const gridBtn = document.getElementById('gridViewBtn');
const listBtn = document.getElementById('listViewBtn');
const colSelect = document.getElementById('columnSelector');
const categoryFilter = document.getElementById('categoryFilter');
const searchInput = document.getElementById('searchInput');
const clearBtn = document.getElementById('clearSearchBtn');
const paginationContainer = document.getElementById('paginationContainer');

let isListView = false;
let currentPage = 1;
let perPage = 9;
let slideDirection = 'right';

// Dropdown jumlah item per halaman
const perPageSelect = document.createElement('select');
perPageSelect.className = "border px-2 py-1 rounded text-sm";
perPageSelect.innerHTML = `
  <option value="6">6</option>
  <option value="9" selected>9</option>
  <option value="12">12</option>
  <option value="24">24</option>
`;
paginationContainer.appendChild(perPageSelect);
perPageSelect.addEventListener("change", () => {
  perPage = parseInt(perPageSelect.value);
  currentPage = 1;
  animateReload('right');
});

// 🔹 Transisi animasi slide + fade
function animateReload(direction = 'right') {
  slideDirection = direction;
  grid.classList.add("opacity-0", direction === 'right' ? "translate-x-10" : "-translate-x-10", "transition-all", "duration-150");

  setTimeout(() => {
    loadSoftwares().then(() => {
      grid.classList.remove("opacity-0", "translate-x-10", "-translate-x-10");
      grid.classList.add("opacity-100", "translate-x-0");
    });
  }, 250);
}

// 🔹 Fetch data dari API backend
async function loadSoftwares() {
  const search = searchInput.value;
  const category = categoryFilter.value;
  const res = await fetch(`/api/softwares?page=${currentPage}&per_page=${perPage}&search=${encodeURIComponent(search)}&category=${encodeURIComponent(category)}`);
  const data = await res.json();
  renderSoftwares(data.softwares);
  renderPagination(data.total, data.page, data.per_page);
}

// 🔹 Render konten software cards
function renderSoftwares(list) {
  grid.innerHTML = "";
  const cols = colSelect.value;
  grid.className = isListView
    ? "flex flex-col space-y-4 transition-all duration-150"
    : `grid grid-cols-${cols} gap-6 transition-all duration-150`;

  list.forEach((sw, idx) => {
    const card = document.createElement("div");
    card.className = isListView
      ? "flex items-center justify-between bg-white rounded-2xl shadow-md p-4 hover:shadow-lg transform opacity-0 translate-y-3 transition-all duration-150"
      : "bg-white rounded-2xl shadow-md p-6 hover:shadow-lg transform opacity-0 translate-y-3 transition-all duration-150";

    card.innerHTML = isListView ? `
      <div class="flex items-center gap-4">
        <img src="../static/default.png" class="w-12 h-12 sm:w-16 sm:h-16 rounded">
        <div>
          <h2 class="text-base sm:text-lg font-semibold text-gray-800">${sw.name}</h2>
          <p class="text-xs sm:text-sm text-gray-500">v ${sw.version} | ${sw.category}</p>
          <p class="hidden sm:block text-gray-600 text-sm">${sw.size}</p>
        </div>
      </div>
      <a href="/download/${sw.relative_path}" class="bg-blue-600 text-white px-3 py-2 rounded-lg text-sm font-medium hover:bg-blue-700">Download</a>
    ` : `
      <img src="../static/default.png" class="w-16 h-16 mb-4 mx-auto" alt="icon">
      <h2 class="text-xl font-semibold text-gray-800 text-center">${sw.name}</h2>
      <p class="text-sm text-gray-500 text-center mb-2">v ${sw.version} | ${sw.category}</p>
      <p class="text-gray-600 text-sm mb-4 text-center">${sw.size}</p>
      <div class="flex justify-center">
        <a href="/download/${sw.relative_path}" class="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-700">Download</a>
      </div>
    `;

    grid.appendChild(card);

    // Efek muncul bertahap (staggered)
    setTimeout(() => {
      card.classList.remove("opacity-0", "translate-y-3");
      card.classList.add("opacity-100", "translate-y-0");
    }, 80 * idx);
  });
}

// 🔹 Pagination dengan animasi arah slide
function renderPagination(total, page, perPage) {
  const totalPages = Math.ceil(total / perPage);
  paginationContainer.querySelectorAll("button.page-btn").forEach(btn => btn.remove());

  for (let i = 1; i <= totalPages; i++) {
    const btn = document.createElement("button");
    btn.textContent = i;
    btn.className = `page-btn px-3 py-1 rounded border ${i === page ? "bg-blue-600 text-white" : "bg-white text-gray-700 hover:bg-gray-100"}`;
    btn.addEventListener("click", () => {
      slideDirection = i > currentPage ? 'right' : 'left';
      currentPage = i;
      animateReload(slideDirection);
    });
    paginationContainer.insertBefore(btn, perPageSelect);
  }
}

// 🔹 Event listeners
categoryFilter.addEventListener("change", () => { currentPage = 1; animateReload('right'); });
searchInput.addEventListener("input", () => { currentPage = 1; animateReload('right'); clearBtn.classList.toggle('hidden', searchInput.value === ''); });
clearBtn.addEventListener("click", () => { searchInput.value = ''; clearBtn.classList.add('hidden'); animateReload('left'); });
gridBtn.addEventListener("click", () => { isListView = false; animateReload('left'); });
listBtn.addEventListener("click", () => { isListView = true; animateReload('right'); });
colSelect.addEventListener("change", () => { if (!isListView) animateReload('right'); });

// 🔹 Initial load
loadSoftwares();
