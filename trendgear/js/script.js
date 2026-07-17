/* =========================================================
   TrendGear Dashboard — Lógica (Fase III)
   ---------------------------------------------------------
   En producción, FIREBASE_URL apunta al nodo REST de Firebase
   Realtime Database, p. ej.:
     https://trendgear-XXXX-default-rtdb.firebaseio.com/customers.json
   Firebase Realtime Database expone cada nodo como JSON vía
   HTTPS, por lo que un simple fetch(FIREBASE_URL) funciona
   igual apuntando a la nube o, como aquí, a un archivo local
   que reproduce esa misma estructura para el taller.
   ========================================================= */

const FIREBASE_URL = "data/dataset.json";

let customers = [];

async function fetchCustomers() {
  try {
    const response = await fetch(FIREBASE_URL);
    if (!response.ok) {
      throw new Error(`Respuesta HTTP ${response.status}`);
    }
    const data = await response.json();
    // Firebase entrega un objeto { "TG-0001": {...}, "TG-0002": {...} };
    // lo convertimos a arreglo para poder iterarlo con forEach.
    customers = Object.values(data);
    renderKPIs(customers);
    applyFiltersAndRender();
  } catch (error) {
    // Protocolo de depuración asistida: copiar este mensaje y el
    // fragmento relevante para instruir a la IA sobre el error.
    console.error("Error al conectar con Firebase:", error);
    const tbody = document.getElementById("customerTableBody");
    tbody.innerHTML = `
      <tr><td colspan="9" class="empty-state">
        No se pudieron cargar los datos. Revisa la consola para más detalle.
      </td></tr>`;
  }
}

function formatCurrency(value) {
  return new Intl.NumberFormat("es-CO", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 2,
  }).format(value);
}

function renderKPIs(list) {
  const total = list.length;
  const revenue = list.reduce((sum, c) => sum + c["Amount Spent ($)"], 0);
  const avg = total ? revenue / total : 0;
  const goldCount = list.filter((c) => c["Membership Status"] === "Gold").length;

  document.getElementById("kpiTotal").textContent = total;
  document.getElementById("kpiRevenue").textContent = formatCurrency(revenue);
  document.getElementById("kpiAvg").textContent = formatCurrency(avg);
  document.getElementById("kpiGold").textContent = goldCount;
}

function membershipBadgeClass(status) {
  return status.toLowerCase();
}

function renderTable(list) {
  const tbody = document.getElementById("customerTableBody");
  const resultCount = document.getElementById("resultCount");

  resultCount.textContent = `${list.length} de ${customers.length} clientes`;

  if (list.length === 0) {
    tbody.innerHTML = `<tr><td colspan="9" class="empty-state">Sin resultados para este filtro.</td></tr>`;
    return;
  }

  // Renderizado dinámico: recorremos el dataset con forEach y
  // generamos un template literal por registro (fila de tabla).
  let rowsHtml = "";
  list.forEach((c) => {
    rowsHtml += `
      <tr>
        <td class="id">${c["Customer ID"]}</td>
        <td>${c["Name"]}</td>
        <td>${c["Product Purchased"]}</td>
        <td class="date">${c["Purchase Date"]}</td>
        <td class="amount">${formatCurrency(c["Amount Spent ($)"])}</td>
        <td>${c["Age"]}</td>
        <td>${c["City"]}</td>
        <td>${c["Payment Method"]}</td>
        <td><span class="badge ${membershipBadgeClass(c["Membership Status"])}">${c["Membership Status"]}</span></td>
      </tr>`;
  });

  tbody.innerHTML = rowsHtml;
}

function applyFiltersAndRender() {
  const query = document.getElementById("searchInput").value.trim().toLowerCase();
  const membership = document.getElementById("membershipFilter").value;
  const sortBy = document.getElementById("sortSelect").value;

  let filtered = customers.filter((c) => {
    const matchesQuery =
      !query ||
      c["Name"].toLowerCase().includes(query) ||
      c["City"].toLowerCase().includes(query);
    const matchesMembership = !membership || c["Membership Status"] === membership;
    return matchesQuery && matchesMembership;
  });

  if (sortBy === "amount-desc") {
    filtered = filtered.slice().sort((a, b) => b["Amount Spent ($)"] - a["Amount Spent ($)"]);
  } else if (sortBy === "amount-asc") {
    filtered = filtered.slice().sort((a, b) => a["Amount Spent ($)"] - b["Amount Spent ($)"]);
  } else if (sortBy === "age-asc") {
    filtered = filtered.slice().sort((a, b) => a["Age"] - b["Age"]);
  }

  renderTable(filtered);
}

function setupNav() {
  const hamburgerBtn = document.getElementById("hamburgerBtn");
  const mainNav = document.getElementById("mainNav");

  hamburgerBtn.addEventListener("click", () => {
    const isOpen = mainNav.classList.toggle("open");
    hamburgerBtn.setAttribute("aria-expanded", String(isOpen));
  });

  mainNav.querySelectorAll("a").forEach((link) => {
    link.addEventListener("click", () => {
      mainNav.classList.remove("open");
      hamburgerBtn.setAttribute("aria-expanded", "false");
    });
  });
}

function setupFilters() {
  document.getElementById("searchInput").addEventListener("input", applyFiltersAndRender);
  document.getElementById("membershipFilter").addEventListener("change", applyFiltersAndRender);
  document.getElementById("sortSelect").addEventListener("change", applyFiltersAndRender);
}

document.addEventListener("DOMContentLoaded", () => {
  setupNav();
  setupFilters();
  fetchCustomers();
});
