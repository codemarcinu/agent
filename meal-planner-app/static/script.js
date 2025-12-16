
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
let currentCalendarDate = new Date();
let receiptCache = {}; // Cache receipt dates for calendar

async function loadStatistics() {
    try {
        const res = await fetch(`${API_URL}/statistics`);
        const data = await res.json();

        // Update summary cards
        document.getElementById('totalSpend').textContent = (data.total_spend || 0).toFixed(2) + ' PLN';
        document.getElementById('totalItems').textContent = data.total_items;
        document.getElementById('itemsRatio').textContent = `${data.available_items} / ${(data.total_items - data.available_items)}`;
        document.getElementById('avgBasket').textContent = (data.avg_basket || 0).toFixed(2) + ' PLN';

        renderCharts(data);
        loadCalendarReceipts(); // Fetch receipts for calendar
    } catch (e) {
        console.error(e);
    }
}

// --- Calendar Logic ---
async function loadCalendarReceipts() {
    try {
        // Fetch all receipts to map them on calendar
        // Ideally we should fetch by month range, but for now fetch last 50
        const res = await fetch(`${API_URL}/receipts`);
        const receipts = await res.json();

        receiptCache = {};
        receipts.forEach(r => {
            const date = r.data_zakupu; // YYYY-MM-DD
            if (!receiptCache[date]) receiptCache[date] = [];
            receiptCache[date].push(r);
        });

        renderCalendar();
    } catch (e) {
        console.error("Calendar fetch error", e);
    }
}

function renderCalendar() {
    const grid = document.getElementById('calendar');
    grid.innerHTML = '';

    const year = currentCalendarDate.getFullYear();
    const month = currentCalendarDate.getMonth();

    // Update Header
    const monthNames = ["Styczeń", "Luty", "Marzec", "Kwiecień", "Maj", "Czerwiec", "Lipiec", "Sierpień", "Wrzesień", "Październik", "Listopad", "Grudzień"];
    document.getElementById('calendarMonth').textContent = `${monthNames[month]} ${year}`;

    // Logic for days
    const firstDay = new Date(year, month, 1).getDay(); // 0 = Sun, 1 = Mon...
    const daysInMonth = new Date(year, month + 1, 0).getDate();

    // Adjust for Monday start (0=Mon, 6=Sun)
    let startOffset = firstDay === 0 ? 6 : firstDay - 1;

    // Headers (Mon-Sun)
    const days = ['Pn', 'Wt', 'Śr', 'Cz', 'Pt', 'Sb', 'Nd'];
    days.forEach(d => {
        const dh = document.createElement('div');
        dh.className = 'cal-day-header';
        dh.textContent = d;
        grid.appendChild(dh);
    });

    // Empty slots
    for (let i = 0; i < startOffset; i++) {
        const empty = document.createElement('div');
        empty.className = 'cal-day empty';
        grid.appendChild(empty);
    }

    // Days
    for (let d = 1; d <= daysInMonth; d++) {
        const dayCell = document.createElement('div');
        dayCell.className = 'cal-day';
        dayCell.textContent = d;

        // Check for receipts
        const dateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(d).padStart(2, '0')}`;
        if (receiptCache[dateStr]) {
            dayCell.classList.add('has-receipt');
            const receipts = receiptCache[dateStr];

            // Indicator
            // Show up to 3 receipts as labels
            receipts.slice(0, 3).forEach(r => {
                const label = document.createElement('div');
                label.className = 'receipt-label';
                label.textContent = r.sklep;
                label.title = `${r.sklep}: ${r.suma_total.toFixed(2)} PLN`;
                dayCell.appendChild(label);
            });

            // If more than 3, show count
            if (receipts.length > 3) {
                const more = document.createElement('div');
                more.className = 'receipt-more';
                more.textContent = `+${receipts.length - 3} więcej`;
                dayCell.appendChild(more);
            }

            // Total amount hint for the whole day
            const total = receipts.reduce((sum, r) => sum + r.suma_total, 0);
            dayCell.setAttribute('title', `Suma dnia: ${total.toFixed(2)} PLN`);

            dayCell.onclick = () => openReceiptListModal(dateStr, receipts);
        }

        grid.appendChild(dayCell);
    }
}

function changeMonth(delta) {
    currentCalendarDate.setMonth(currentCalendarDate.getMonth() + delta);
    renderCalendar();
}

// --- Receipt Modal ---
function openReceiptListModal(date, receipts) {
    const modal = document.getElementById('receiptModal');
    const details = document.getElementById('receiptDetails');
    modal.classList.remove('hidden');

    if (receipts.length === 1) {
        // Show detail directly
        loadReceiptDetail(receipts[0].id);
    } else {
        // Show list to choose
        let html = `<h3>Paragony z dnia ${date}:</h3><ul>`;
        receipts.forEach(r => {
            html += `<li><button class="btn-text" onclick="loadReceiptDetail(${r.id})">${r.sklep} - ${r.suma_total} PLN</button></li>`;
        });
        html += '</ul>';
        details.innerHTML = html;
    }
}

async function loadReceiptDetail(id) {
    const details = document.getElementById('receiptDetails');
    details.innerHTML = '<p>Ładowanie szczegółów...</p>';

    try {
        const res = await fetch(`${API_URL}/receipts/${id}`);
        const data = await res.json();
        const r = data.receipt;

        let html = `
            <div class="receipt-view">
                <div class="r-header">
                    <h3>${r.sklep}</h3>
                    <span>${r.data_zakupu}</span>
                </div>
                <hr>
                <table class="r-table">
                    <thead><tr><th>Produkt</th><th>Ilość</th><th>Cena</th><th>Suma</th></tr></thead>
                    <tbody>
        `;

        data.items.forEach(item => {
            html += `
                <tr>
                    <td>${item.product_name || item.category || 'Produkt'}</td> 
                    <td>${item.quantity}</td>
                    <td>${item.price.toFixed(2)}</td>
                    <td>${(item.quantity * item.price).toFixed(2)}</td>
                </tr>
            `;
        });

        html += `
                    </tbody>
                    <tfoot>
                        <tr>
                            <td colspan="3"><strong>SUMA</strong></td>
                            <td><strong>${r.suma_total.toFixed(2)} PLN</strong></td>
                        </tr>
                    </tfoot>
                </table>
            </div>
            <button class="btn-secondary" onclick="document.getElementById('receiptModal').classList.add('hidden')">Zamknij</button>
        `;

        details.innerHTML = html;
    } catch (e) {
        details.innerHTML = '<p class="error">Błąd ładowania paragonu.</p>';
    }
}

function closeReceiptModal(e) {
    if (e) e.stopPropagation();
    document.getElementById('receiptModal').classList.add('hidden');
}

function renderCharts(data) {
    // Categories Chart
    // Ensure the canvas exists in current DOM
    const ctxCatCanvas = document.getElementById('categoriesChart');
    if (ctxCatCanvas) {
        if (charts.categories) charts.categories.destroy();
        charts.categories = new Chart(ctxCatCanvas.getContext('2d'), {
            type: 'doughnut',
            data: {
                labels: data.top_categories.map(c => c.name),
                datasets: [{
                    data: data.top_categories.map(c => c.count),
                    backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF']
                }]
            }
        });
    }

    // Trends Chart (Monthly Spend)
    const ctxTrendCanvas = document.getElementById('trendsChart');
    if (ctxTrendCanvas) {
        if (charts.trends) charts.trends.destroy();
        charts.trends = new Chart(ctxTrendCanvas.getContext('2d'), {
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
}

// Sub-tabs logic
function switchStatTab(tabName) {
    // Hide all contents
    ['dashboard', 'trends', 'calendar'].forEach(t => {
        document.getElementById(`stat-${t}`).classList.add('hidden');
        document.getElementById(`stat-${t}`).classList.remove('active');
    });

    // Show selected
    document.getElementById(`stat-${tabName}`).classList.remove('hidden');
    document.getElementById(`stat-${tabName}`).classList.add('active');

    // Update buttons
    const btns = document.querySelectorAll('.sub-tab-btn');
    btns.forEach(b => b.classList.remove('active'));
    // Find button with matching onclick
    // Simple way: iterate and check text or add ID. 
    // Let's assume order matches or click event finds target.
    // Better: pass event or select by index. 
    // Since we used onclick="switchStatTab('xxx')", we can just manually set active class on click target 
    // But here we don't have event. Let's fix in HTML or query selectors.

    // Hacky but simple: Select button by onclick attribute text
    const targetBtn = document.querySelector(`.sub-tab-btn[onclick="switchStatTab('${tabName}')"]`);
    if (targetBtn) targetBtn.classList.add('active');

    // Re-render charts if hidden canvas causes issues (Chart.js sometimes needs visible canvas)
    // No, we loaded data already. We might need to resize.
}

// Ensure first tab is active on load
// Called by openTab('statistics') ? 
// We should probably init sub-tab when main tab opens.


function exportReport() {
    window.print();
}

// Init
document.addEventListener('DOMContentLoaded', () => {
    openTab('products'); // Default tab
});
