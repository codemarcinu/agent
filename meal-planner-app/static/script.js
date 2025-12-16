
const API_URL = '/api';

// --- Data ---
let allProducts = [];
const CATEGORIES = {
    'napoje': '🥤',
    'przyprawy': '🧂',
    'nabiał': '🧀',
    'mięso': '🥩',
    'wędliny': '🥓',
    'warzywa': '🥦',
    'owoce': '🍎',
    'pieczywo': '🍞',
    'makarony': '🍝',
    'ryż': '🍚',
    'słodycze': '🍬',
    'inne': '📦'
};

function getIcon(catName) {
    if (!catName) return '📦';
    const lower = catName.toLowerCase();
    for (const [key, icon] of Object.entries(CATEGORIES)) {
        if (lower.includes(key)) return icon;
    }
    return '📦';
}

// --- Tab Management ---
function openTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });

    // Show selected tab
    document.getElementById(tabName).classList.add('active');
    document.querySelector(`button[onclick = "openTab('${tabName}')"]`).classList.add('active');

    // Load data if needed
    if (tabName === 'products') {
        loadProducts();
    } else if (tabName === 'settings') {
        loadSettings();
        loadPreferences();
    } else if (tabName === 'statistics') {
        loadStatistics();
    }
}

// --- Product Management ---
function toggleAddProductForm() {
    const form = document.getElementById('addProductForm');
    form.classList.toggle('hidden');
}

async function loadProducts() {
    const grid = document.getElementById('categoryGrid');
    grid.innerHTML = '<p class="loading-text">Ładowanie...</p>';

    try {
        const res = await fetch(`${API_URL}/products`);
        allProducts = await res.json();
        renderCategories();
    } catch (e) {
        console.error(e);
        grid.innerHTML = '<p class="error">Błąd pobierania danych :(</p>';
    }
}

function renderCategories() {
    const grid = document.getElementById('categoryGrid');
    grid.innerHTML = '';

    if (allProducts.length === 0) {
        grid.innerHTML = '<p>Brak produktów.</p>';
        return;
    }

    // Group by category
    const grouped = {};
    allProducts.forEach(p => {
        // Normalize category
        let cat = p.category ? p.category.trim() : 'Inne';
        // Capitalize first letter
        cat = cat.charAt(0).toUpperCase() + cat.slice(1);

        if (!grouped[cat]) grouped[cat] = [];
        grouped[cat].push(p);
    });

    // Render tiles
    Object.keys(grouped).sort().forEach(catName => {
        const products = grouped[catName];
        const icon = getIcon(catName);

        const tile = document.createElement('div');
        tile.className = 'category-tile';
        tile.onclick = () => openCategoryModal(catName, products);

        tile.innerHTML = `
            <span class="cat-icon">${icon}</span>
            <span class="cat-name">${catName}</span>
            <span class="cat-count">${products.length} szt.</span>
        `;
        grid.appendChild(tile);
    });
}

function openCategoryModal(catName, products) {
    const modal = document.getElementById('categoryModal');
    document.getElementById('modalTitle').textContent = `${getIcon(catName)} ${catName}`;
    const list = document.getElementById('modalList');
    list.innerHTML = '';

    products.forEach(p => {
        const row = document.createElement('div');
        row.className = `product-row ${p.is_frozen ? 'frozen' : ''}`;
        row.id = `row-${p.id}`;

        row.innerHTML = `
            <div class="p-info">
                <span class="p-name">${p.name}</span>
                <span class="p-qty">${p.quantity} ${p.unit} &bull; ${p.shop || ''}</span>
            </div>
            <div class="p-actions">
                <input type="number" class="qty-input-small" placeholder="Użyj..." id="use-qty-${p.id}" style="width: 60px;">
                <button class="btn-use" onclick="useProduct(${p.id})">Zużyj</button>
                <div class="separator">|</div>
                <input type="date" class="date-input" value="${p.expiry_date || ''}" 
                       onchange="markModified(${p.id})">
                <label class="frozen-toggle">
                    <input type="checkbox" ${p.is_frozen ? 'checked' : ''} 
                           onchange="toggleFrozenStyle(this, ${p.id}); markModified(${p.id})">
                    ❄️ Zamrożone
                </label>
                <button class="btn-save-row" onclick="saveProduct(${p.id})">Zapisz</button>
            </div>
        `;
        list.appendChild(row);
    });

    modal.classList.remove('hidden');
}

function closeModal(e) {
    if (e) e.stopPropagation();
    document.getElementById('categoryModal').classList.add('hidden');
}

function toggleFrozenStyle(checkbox, id) {
    const row = document.getElementById(`row-${id}`);
    if (checkbox.checked) row.classList.add('frozen');
    else row.classList.remove('frozen');
}

function markModified(id) {
    document.getElementById(`row-${id}`).classList.add('modified');
}

async function saveProduct(id) {
    const row = document.getElementById(`row-${id}`);
    const dateInput = row.querySelector('.date-input');
    const frozenInput = row.querySelector('.frozen-toggle input');

    const payload = {
        expiry_date: dateInput.value || null,
        is_frozen: frozenInput.checked
    };

    try {
        const res = await fetch(`${API_URL}/products/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (res.ok) {
            // Update local state (optional but good for UX)
            const pIndex = allProducts.findIndex(p => p.id === id);
            if (pIndex !== -1) {
                allProducts[pIndex].expiry_date = payload.expiry_date;
                allProducts[pIndex].is_frozen = payload.is_frozen;
            }

            row.classList.remove('modified');
            // Re-render categories in background to update counts if we were filtering...
            // But here we just update UI style
        } else {
            alert('Błąd zapisu');
        }
    } catch (e) {
        alert('Błąd połączenia');
    }
}

async function handleAddProduct(event) {
    event.preventDefault();
    const formData = new FormData(event.target);
    const data = Object.fromEntries(formData.entries());

    try {
        const res = await fetch(`${API_URL}/products`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        if (res.ok) {
            event.target.reset();
            toggleAddProductForm();
            loadProducts();
        } else {
            alert('Błąd dodawania produktu');
        }
    } catch (e) {
        console.error(e);
        alert('Błąd sieci');
    }
}

async function deleteProduct(id) {
    if (!confirm('Usunąć ten produkt?')) return;

    try {
        await fetch(`${API_URL}/products/${id}`, { method: 'DELETE' });
        loadProducts();
    } catch (e) {
        console.error(e);
    }
}

// --- Usage Tracking ---
async function useProduct(id) {
    const input = document.getElementById(`use-qty-${id}`);
    const amount = parseFloat(input.value);

    if (!amount || amount <= 0) {
        alert('Podaj ilość do zużycia!');
        return;
    }

    if (!confirm(`Zużyć ${amount} jednostek produktu?`)) return;

    try {
        const res = await fetch(`${API_URL}/products/${id}/usage`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ amount: amount })
        });

        if (res.ok) {
            const data = await res.json();
            alert(`Zużyto! Nowa ilość: ${data.new_quantity}`);
            // Refresh
            closeModal();
            loadProducts();
        } else {
            alert('Błąd aktualizacji');
        }
    } catch (e) {
        console.error(e);
        alert('Błąd sieci');
    }
}

// --- AI Suggestions ---
async function getSuggestion(type) {
    const resultDiv = document.getElementById('aiResult');
    const textDiv = document.getElementById('aiText');

    resultDiv.classList.remove('hidden');
    textDiv.innerHTML = '<p>🤖 Model myśli... to może chwilę potrwać...</p>';

    let endpoint = 'suggest-meal';
    if (type === 'menu') endpoint = 'suggest-weekly-menu';
    if (type === 'shopping') endpoint = 'suggest-shopping-list';

    try {
        const res = await fetch(`${API_URL}/${endpoint}`, { method: 'POST' });
        const data = await res.json();

        if (data.is_json && typeof data.suggestion === 'object') {
            const s = data.suggestion;
            let html = '';

            if (s.meal_name) {
                // Meal Suggestion
                html += `<h4>🥘 ${s.meal_name}</h4>`;
                if (s.ingredients) {
                    html += `<h5>Składniki:</h5><ul>${s.ingredients.map(i => `<li>${i}</li>`).join('')}</ul>`;
                }
                if (s.steps) {
                    html += `<h5>Przygotowanie:</h5><ol>${s.steps.map((step, i) => `<li>${step}</li>`).join('')}</ol>`;
                }
            } else if (Array.isArray(s)) {
                // List (Shopping)
                html += `<ul>${s.map(i => `<li>${i}</li>`).join('')}</ul>`;
            } else {
                // Fallback
                html += `<pre>${JSON.stringify(s, null, 2)}</pre>`;
            }
            textDiv.innerHTML = html;
        } else {
            // Simple markdown to HTML conversion
            let content = typeof data.suggestion === 'string' ? data.suggestion : JSON.stringify(data.suggestion);
            let formatted = content
                .replace(/\n/g, '<br>')
                .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                .replace(/### (.*?)(<br>|$)/g, '<h3>$1</h3>')
                .replace(/- (.*?)(<br>|$)/g, '<li>$1</li>');

            textDiv.innerHTML = formatted;
        }
    } catch (e) {
        textDiv.innerHTML = '<p class="error">Błąd generowania sugestii. Sprawdź czy Ollama działa.</p>';
    }
}

// --- Settings & Configuration ---
async function loadSettings() {
    try {
        // Load config from backend
        const res = await fetch(`${API_URL}/config`);
        const config = await res.json();

        document.getElementById('dbHost').value = config.database_host || '';
        document.getElementById('dbPort').value = config.database_port || '';
        document.getElementById('dbName').value = config.database_name || '';
        document.getElementById('dbUser').value = config.database_user || '';

        document.getElementById('ollamaHost').value = config.ollama_host || 'http://localhost:11434';

        // Load models separately to populate dropdown
        await loadOllamaModels(config.ollama_model);

    } catch (e) {
        console.error('Cant load settings', e);
    }
}

async function loadOllamaModels(preselectedModel) {
    const select = document.getElementById('ollamaModel');
    select.innerHTML = '<option>Ładowanie...</option>';

    try {
        const res = await fetch(`${API_URL}/ollama-models`);
        const data = await res.json();

        select.innerHTML = '';
        if (data.status === 'OK') {
            data.models.forEach(m => {
                const opt = document.createElement('option');
                opt.value = m.name;
                opt.textContent = `${m.name} (${formatSize(m.size)})`;
                select.appendChild(opt);
            });

            // Select current model if exists
            if (preselectedModel) {
                select.value = preselectedModel;
            } else if (data.models.find(m => m.name.includes('bielik'))) {
                // Auto-select bielik if available and no preselection
                select.value = data.models.find(m => m.name.includes('bielik')).name;
            }
        } else {
            select.innerHTML = '<option>Błąd pobierania modeli</option>';
        }
    } catch (e) {
        select.innerHTML = '<option>Błąd połączenia z Ollama</option>';
    }
}

function formatSize(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

async function testDB() {
    const status = document.getElementById('dbStatus');
    status.textContent = 'Testowanie...';
    try {
        const res = await fetch(`${API_URL}/test-db`, { method: 'POST' });
        const data = await res.json();
        status.textContent = data.message;
        status.style.color = data.status === 'OK' ? 'var(--primary)' : 'var(--danger)';
    } catch (e) {
        status.textContent = 'Błąd połączenia';
    }
}

async function testOllama() {
    const status = document.getElementById('ollamaStatus');
    status.textContent = 'Testowanie modelu...';

    // Update config first potentially? Or mostly we rely on what's in text inputs for "test"
    // Ideally we should temporarily switch to check inputs
    // But for simplicity, we assume we want to test "currently saved" or "update first"
    // Let's rely on saving first or implement a way to pass params to test endpoint.
    // For now, let's just hit the endpoint which uses env vars.
    // User should save first.
    // OPTIONALLY: We could send current form values to update config before testing.

    await saveSettings(); // Auto-save before test to ensure consistency

    try {
        const res = await fetch(`${API_URL}/test-ollama`, { method: 'POST' });
        const data = await res.json();
        status.textContent = data.message;
        status.style.color = data.status === 'OK' ? 'var(--primary)' : 'var(--danger)';
    } catch (e) {
        status.textContent = 'Błąd połączenia';
    }
}

async function saveSettings() {
    const data = {
        database_host: document.getElementById('dbHost').value,
        database_port: document.getElementById('dbPort').value,
        database_name: document.getElementById('dbName').value,
        database_user: document.getElementById('dbUser').value,
        ollama_host: document.getElementById('ollamaHost').value,
        ollama_model: document.getElementById('ollamaModel').value
    };

    const pass = document.getElementById('dbPass').value;
    if (pass) data.database_password = pass;

    try {
        const res = await fetch(`${API_URL}/config/update`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        const result = await res.json();
        if (result.status === 'OK') {
            alert('Ustawienia zapisane (sesja)!');
        } else {
            alert('Błąd zapisu: ' + result.message);
        }
    } catch (e) {
        alert('Błąd zapisu ustawień');
    }

    // Save Preferences
    const prefData = {
        diet_type: document.getElementById('dietType').value,
        allergen: document.getElementById('allergens').value,
        disliked_products: document.getElementById('disliked').value,
        liked_products: document.getElementById('liked').value
    };

    try {
        await fetch(`${API_URL}/preferences`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(prefData)
        });
    } catch (e) {
        console.error("Error saving preferences", e);
    }
}

async function loadPreferences() {
    try {
        const res = await fetch(`${API_URL}/preferences`);
        const data = await res.json();

        if (data) {
            document.getElementById('dietType').value = data.diet_type || '';
            document.getElementById('allergens').value = data.allergen || '';
            document.getElementById('disliked').value = data.disliked_products || '';
            document.getElementById('liked').value = data.liked_products || '';
        }
    } catch (e) {
        console.error(e);
    }
}

// --- Statistics ---
let charts = {};

async function loadStatistics() {
    try {
        const res = await fetch(`${API_URL}/statistics`);
        const data = await res.json();

        // Update summary cards
        document.getElementById('totalSpend').textContent = (data.total_spend || 0).toFixed(2) + ' PLN';
        document.getElementById('totalItems').textContent = data.total_items;
        document.getElementById('itemsRatio').textContent = `${data.available_items} / ${(data.total_items - data.available_items)}`;

        renderCharts(data);
    } catch (e) {
        console.error(e);
    }
}

function renderCharts(data) {
    // Categories Chart
    const ctxCat = document.getElementById('categoriesChart').getContext('2d');

    if (charts.categories) charts.categories.destroy();

    charts.categories = new Chart(ctxCat, {
        type: 'doughnut',
        data: {
            labels: data.top_categories.map(c => c.name),
            datasets: [{
                data: data.top_categories.map(c => c.count),
                backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF']
            }]
        }
    });

    // Trends Chart (Monthly Spend)
    const ctxTrend = document.getElementById('trendsChart').getContext('2d');

    if (charts.trends) charts.trends.destroy();

    charts.trends = new Chart(ctxTrend, {
        type: 'bar',
        data: {
            labels: data.monthly_spend.map(m => m.month),
            datasets: [{
                label: 'Wydatki (PLN)',
                data: data.monthly_spend.map(m => m.total),
                backgroundColor: '#36A2EB'
            }]
        },
        options: {
            scales: {
                y: { beginAtZero: true }
            }
        }
    });
}

function exportReport() {
    window.print();
}

// Init
document.addEventListener('DOMContentLoaded', () => {
    openTab('products'); // Default tab
});
