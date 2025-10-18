document.addEventListener("DOMContentLoaded", () => {
  const softwareGrid = document.getElementById("softwareGrid");
  const paginationContainer = document.getElementById("paginationContainer");
  const searchInput = document.getElementById("searchInput");
  const clearSearchBtn = document.getElementById("clearSearchBtn");
  const categoryFilter = document.getElementById("categoryFilter");
  const tagFilter = document.getElementById("tagFilter");
  const columnSelector = document.getElementById("columnSelector");
  const gridViewBtn = document.getElementById("gridViewBtn");
  const listViewBtn = document.getElementById("listViewBtn");

  let currentPage = 1;
  let perPage = 6;
  let currentView = "grid";

  async function fetchSoftware() {
    const search = searchInput.value.trim();
    const category = categoryFilter.value;
    const tag = tagFilter ? tagFilter.value : "";
    const url = `/api/software?page=${currentPage}&per_page=${perPage}&search=${search}&category=${category}&tag=${tag}`;

    const res = await fetch(url);
    const data = await res.json();
    renderSoftware(data.items);
    renderPagination(data.pages);
  }

  function renderSoftware(items) {
    softwareGrid.innerHTML = "";

    if (!items.length) {
      softwareGrid.innerHTML = `<p class="text-center text-gray-500 col-span-full">Tidak ada data ditemukan.</p>`;
      return;
    }

    if (currentView === "grid") {
      softwareGrid.className = `grid grid-cols-${columnSelector.value} gap-6 transition-all duration-300`;
      items.forEach(item => {
        const div = document.createElement("div");
        div.className = "bg-white shadow-md rounded-xl p-4 hover:shadow-lg transition";
        div.innerHTML = `
          <img src="/images/${item.image}" alt="${item.name}" class="w-16 h-16 mx-auto mb-3 rounded-lg object-contain">
          <h3 class="text-lg font-semibold text-center text-gray-800">${item.name}</h3>
          <p class="text-sm text-center text-gray-500">${item.category} • ${item.version}</p>
          <div class="flex flex-wrap justify-center gap-1 mt-2">
            ${item.tag
              ? item.tag.split(",").map(t => `<span class="bg-blue-100 text-blue-700 text-xs px-2 py-0.5 rounded-full">${t.trim()}</span>`).join("")
              : ""}
          </div>
        `;
        softwareGrid.appendChild(div);
      });
    } else {
      softwareGrid.className = "flex flex-col gap-2 transition-all duration-300";
      items.forEach(item => {
        const div = document.createElement("div");
        div.className = "flex items-center justify-between bg-white border rounded-lg p-3 hover:bg-gray-50";
        div.innerHTML = `
          <div class="flex items-center space-x-4">
            <img src="/images/${item.image}" alt="${item.name}" class="w-10 h-10 rounded object-contain">
            <div>
              <h3 class="font-semibold text-gray-800">${item.name}</h3>
              <p class="text-sm text-gray-500">${item.category} • ${item.version}</p>
              <div class="flex flex-wrap gap-1 mt-1">
                ${item.tag
                  ? item.tag.split(",").map(t => `<span class="bg-blue-100 text-blue-700 text-xs px-2 py-0.5 rounded-full">${t.trim()}</span>`).join("")
                  : ""}
              </div>
            </div>
          </div>
        `;
        softwareGrid.appendChild(div);
      });
    }
  }

  function renderPagination(totalPages) {
    paginationContainer.innerHTML = "";
    for (let i = 1; i <= totalPages; i++) {
      const btn = document.createElement("button");
      btn.className = `px-3 py-1 rounded-md ${i === currentPage ? "bg-blue-600 text-white" : "bg-gray-200 hover:bg-gray-300"}`;
      btn.textContent = i;
      btn.addEventListener("click", () => {
        currentPage = i;
        fetchSoftware();
      });
      paginationContainer.appendChild(btn);
    }
  }

  // 🎯 Event handlers
  searchInput.addEventListener("input", () => {
    clearSearchBtn.classList.toggle("hidden", !searchInput.value);
    currentPage = 1;
    fetchSoftware();
  });

  clearSearchBtn.addEventListener("click", () => {
    searchInput.value = "";
    clearSearchBtn.classList.add("hidden");
    currentPage = 1;
    fetchSoftware();
  });

  categoryFilter.addEventListener("change", () => {
    currentPage = 1;
    fetchSoftware();
  });

  if (tagFilter) {
    tagFilter.addEventListener("change", () => {
      currentPage = 1;
      fetchSoftware();
    });
  }

  columnSelector.addEventListener("change", () => fetchSoftware());
  gridViewBtn.addEventListener("click", () => {
    currentView = "grid";
    gridViewBtn.classList.add("bg-blue-600", "text-white");
    listViewBtn.classList.remove("bg-blue-600", "text-white");
    fetchSoftware();
  });
  listViewBtn.addEventListener("click", () => {
    currentView = "list";
    listViewBtn.classList.add("bg-blue-600", "text-white");
    gridViewBtn.classList.remove("bg-blue-600", "text-white");
    fetchSoftware();
  });

  // 🚀 Load pertama kali
  fetchSoftware();
});
