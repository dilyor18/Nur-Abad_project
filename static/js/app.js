const API_BASE = '/api';
const AUTH_KEY = 'market_auth';

const qs = (selector) => document.querySelector(selector);

function getAuth() {
    try {
        return JSON.parse(localStorage.getItem(AUTH_KEY)) || null;
    } catch (error) {
        return null;
    }
}

function saveAuth(payload) {
    localStorage.setItem(AUTH_KEY, JSON.stringify(payload));
    updateAuthUI();
}

function clearAuth() {
    localStorage.removeItem(AUTH_KEY);
    updateAuthUI();
}

async function refreshAuthProfile() {
    const auth = getAuth();
    if (!auth?.access) return;

    try {
        const me = await api('/me/');
        const nextAuth = { ...auth, user: me.username || auth.user, is_staff: !!me.is_staff };
        localStorage.setItem(AUTH_KEY, JSON.stringify(nextAuth));
        updateAuthUI();
    } catch (error) {
        console.warn('Could not refresh auth profile:', error.message);
    }
}

function api(path, options = {}) {
    const token = getAuth()?.access;
    const isFormData = options.body instanceof FormData;
    const headers = {
        ...(isFormData ? {} : { 'Content-Type': 'application/json' }),
        ...(options.headers || {}),
    };

    if (token) {
        headers.Authorization = `Bearer ${token}`;
    }

    return fetch(`${API_BASE}${path}`, {
        ...options,
        headers,
    }).then(async response => {
        const text = await response.text();
        let payload = null;
        try {
            payload = text ? JSON.parse(text) : null;
        } catch (error) {
            payload = text;
        }

        if (!response.ok) {
            const message = payload?.detail || payload?.message || 'Ошибка запроса';
            throw new Error(message);
        }

        return payload;
    });
}

function updateAuthUI() {
    const auth = getAuth();
    const greeting = qs('#user-greeting');
    const logoutBtn = qs('#logout-btn');
    const navCreateAd = qs('#nav-create-ad');
    const profileLink = qs('#profile-link');
    const favoritesLink = qs('#favorites-link');
    const chatsLink = qs('#chats-link');
    const adminLink = qs('#admin-link');

    if (greeting) {
        greeting.textContent = auth ? `Привет, ${auth.user || 'пользователь'}` : '';
        greeting.classList.toggle('hidden', !auth);
    }

    if (logoutBtn) {
        logoutBtn.classList.toggle('hidden', !auth);
    }

    if (navCreateAd) {
        navCreateAd.style.display = auth ? 'inline' : 'none';
    }

    if (profileLink) {
        profileLink.style.display = auth ? 'inline' : 'none';
    }

    if (favoritesLink) {
        favoritesLink.style.display = auth ? 'inline' : 'none';
    }

    if (chatsLink) {
        chatsLink.style.display = auth ? 'inline' : 'none';
    }

    if (adminLink) {
        adminLink.style.display = auth?.is_staff ? 'inline' : 'none';
    }
}

async function loadCategories(targetSelector = '#category-filter', createSelector = '#create-category') {
    try {
        const data = await api('/categories/');
        const target = qs(targetSelector);
        const createTarget = qs(createSelector);

        const options = data.map(item => `<option value="${item.id}">${item.name}</option>`).join('');

        if (target) {
            target.innerHTML = targetSelector === '#category-filter'
                ? '<option value="">Все категории</option>' + options
                : options || '<option value="">Категория не найдена</option>';
        }
        if (createTarget) {
            createTarget.innerHTML = options || '<option value="">Категория не найдена</option>';
        }
    } catch (error) {
        console.error('Categories load failed:', error.message);
    }
}

async function loadCities(targetSelector = '#city-filter', createSelector = '#create-city') {
    try {
        const data = await api('/cities/');
        const target = qs(targetSelector);
        const createTarget = qs(createSelector);

        const options = data.map(item => `<option value="${item.id}">${item.name}</option>`).join('');

        if (target) {
            target.innerHTML = targetSelector === '#city-filter'
                ? '<option value="">Все города</option>' + options
                : options || '<option value="">Город не найден</option>';
        }
        if (createTarget) {
            createTarget.innerHTML = options || '<option value="">Город не найден</option>';
        }
    } catch (error) {
        console.error('Cities load failed:', error.message);
    }
}

async function loadDistricts(cityId = '', targetSelector = '#district-filter', createSelector = '#create-district') {
    try {
        const params = cityId ? `?city=${cityId}` : '';
        const data = await api(`/districts/${params}`);
        const target = qs(targetSelector);
        const createTarget = qs(createSelector);

        const options = data.map(item => `<option value="${item.id}">${item.name}</option>`).join('');

        if (target) {
            target.innerHTML = targetSelector === '#district-filter'
                ? '<option value="">Все районы</option>' + options
                : options || '<option value="">Район не найден</option>';
        }
        if (createTarget) {
            createTarget.innerHTML = options || '<option value="">Район не найден</option>';
        }
    } catch (error) {
        console.error('Districts load failed:', error.message);
    }
}

async function loadNews() {
    const widget = qs('#news-widget');
    if (!widget) return;

    try {
        const data = await api('/news/');
        if (!data.results || !data.results.length) {
            widget.innerHTML = '<p class="muted">Новости пока отсутствуют.</p>';
            return;
        }

        widget.innerHTML = data.results.slice(0, 4).map(item => `
            <article class="news-item">
                <h4>${item.title}</h4>
                <p>${item.content.slice(0, 100)}${item.content.length > 100 ? '...' : ''}</p>
            </article>
        `).join('');
    } catch (error) {
        widget.innerHTML = '<p class="muted">Не удалось загрузить новости.</p>';
    }
}

function makeAdCard(item) {
    const image = item.images && item.images.length ? item.images[0].image : 'https://placehold.co/600x400/EEF2FF/1F2937?text=Market';
    const price = Number(item.price || 0).toLocaleString('ru-RU');
    return `
        <article class="ad-card">
            <img src="${image.startsWith('http') ? image : '/media/' + image}" alt="${item.title}">
            <div class="ad-body">
                <div class="ad-meta">
                    <span>${item.category_name || 'Категория'}</span>
                    <span>${item.condition || 'Не указано'}</span>
                </div>
                <h3>${item.title}</h3>
                <div class="ad-price">${price} ₽</div>
                <div class="ad-meta">
                    <span>${item.city_name || 'Город'}</span>
                    <span>${item.district_name || 'Район'}</span>
                </div>
                <span class="badge">${item.author || 'Автор'}</span>
            </div>
        </article>
    `;
}

async function loadAds() {
    const grid = qs('#ads-grid');
    if (!grid) return;

    const params = new URLSearchParams();
    const search = qs('#search-input')?.value || '';

    if (search) params.set('search', search);

    grid.innerHTML = '<p class="muted">Загрузка объявлений...</p>';

    try {
        const data = await api(`/ads/?${params.toString()}`);
        if (!data || !data.length) {
            grid.innerHTML = '<p class="muted">Объявлений не найдено.</p>';
            return;
        }

        const mapped = data.map(item => ({
            ...item,
            category_name: item.category_name || 'Категория',
            city_name: item.city_name || 'Город',
            district_name: item.district_name || 'Район',
        }));

        grid.innerHTML = mapped.map(item => `
            <a href="/ad/${item.id}/" class="ad-card-link">
                ${makeAdCard(item)}
            </a>
        `).join('');
    } catch (error) {
        grid.innerHTML = `<p class="muted">${error.message}</p>`;
    }
}

async function loadFavoritesPage() {
    const grid = qs('#favorites-grid');
    const empty = qs('#favorites-empty');
    if (!grid) return;

    const auth = getAuth();
    if (!auth) {
        window.location.href = '/auth/';
        return;
    }

    try {
        const favorites = await api('/favorites/');
        const allAds = await api('/ads/');
        const ids = new Set(favorites.map(item => item.ad));
        const items = allAds.filter(ad => ids.has(ad.id));

        if (!items.length) {
            grid.innerHTML = '';
            if (empty) empty.classList.remove('hidden');
            return;
        }

        if (empty) empty.classList.add('hidden');
        grid.innerHTML = items.map(item => `
            <a href="/ad/${item.id}/" class="ad-card-link">
                ${makeAdCard(item)}
            </a>
        `).join('');
    } catch (error) {
        if (empty) {
            empty.textContent = error.message || 'Не удалось загрузить избранное.';
            empty.classList.remove('hidden');
        }
        grid.innerHTML = '';
    }
}

async function loadConversationsPage() {
    const list = qs('#conversations-list');
    const thread = qs('#chat-thread');
    const form = qs('#message-form');
    const header = qs('#chat-header');
    if (!list) return;

    const auth = getAuth();
    if (!auth) {
        window.location.href = '/auth/';
        return;
    }

    try {
        const data = await api('/conversations/');
        if (!data.length) {
            list.innerHTML = '<p class="muted">У вас пока нет диалогов.</p>';
            if (thread) thread.innerHTML = '<p class="muted">Выберите диалог слева.</p>';
            if (form) form.classList.add('hidden');
            return;
        }

        list.innerHTML = data.map(item => `
            <button class="conversation-item" data-conversation-id="${item.id}">
                <strong>${item.seller || 'Продавец'}</strong>
                <small>Объявление #${item.ad}</small>
            </button>
        `).join('');

        list.querySelectorAll('.conversation-item').forEach(button => {
            button.addEventListener('click', () => {
                const id = Number(button.dataset.conversationId);
                if (!Number.isNaN(id)) {
                    openConversation(id);
                }
            });
        });

        if (header) header.textContent = `Диалог с ${data[0].seller || 'продавцом'}`;
        openConversation(data[0].id);
    } catch (error) {
        list.innerHTML = `<p class="muted">${error.message}</p>`;
    }
}

async function openConversation(id) {
    const thread = qs('#chat-thread');
    const form = qs('#message-form');
    const header = qs('#chat-header');
    if (!thread) return;

    try {
        const data = await api(`/conversations/${id}/messages/`);
        const label = qs('.conversation-item[data-conversation-id="' + id + '"] strong');
        if (header) {
            header.textContent = label ? label.textContent : 'Диалог';
        }

        if (!data.length) {
            thread.innerHTML = '<p class="muted">Сообщений пока нет.</p>';
        } else {
            thread.innerHTML = data.map(message => `
                <div class="message-bubble">
                    <strong>${message.author}</strong>
                    <p>${message.text}</p>
                    <small>${new Date(message.created_at).toLocaleString('ru-RU')}</small>
                </div>
            `).join('');
        }

        if (form) {
            form.classList.remove('hidden');
            form.dataset.conversationId = String(id);
        }
    } catch (error) {
        thread.innerHTML = `<p class="muted">${error.message}</p>`;
    }
}

async function handleMessageSubmit(event) {
    event.preventDefault();
    const form = event.currentTarget;
    const conversationId = form.dataset.conversationId;
    const input = qs('#message-input');
    if (!conversationId || !input || !input.value.trim()) return;

    try {
        await api(`/conversations/${conversationId}/messages/`, {
            method: 'POST',
            body: JSON.stringify({ text: input.value.trim() }),
        });
        input.value = '';
        await openConversation(Number(conversationId));
    } catch (error) {
        alert(error.message);
    }
}

async function loadNewsPage() {
    const grid = qs('#news-page-grid');
    const form = qs('#news-form');
    if (!grid) return;

    const auth = getAuth();
    if (!auth) {
        grid.innerHTML = '<p class="muted">Войдите в аккаунт, чтобы читать и публиковать новости.</p>';
        if (form) form.classList.add('hidden');
        return;
    }

    try {
        const data = await api('/news/');
        const items = Array.isArray(data) ? data : data.results || [];
        if (!items.length) {
            grid.innerHTML = '<p class="muted">Пока нет новостей.</p>';
            return;
        }

        grid.innerHTML = items.map(item => `
            <article class="news-card">
                <div class="news-card-header">
                    <span class="badge">${item.status || 'PUBLISHED'}</span>
                    <span class="muted">${item.author || 'Администратор'}</span>
                </div>
                <h3>${item.title}</h3>
                <p>${item.content}</p>
            </article>
        `).join('');
    } catch (error) {
        grid.innerHTML = `<p class="muted">${error.message}</p>`;
    }
}

async function loadAdminPage() {
    const newsList = qs('#admin-news-list');
    const reportList = qs('#admin-reports-list');
    if (!newsList || !reportList) return;

    const auth = getAuth();
    if (!auth || !auth.is_staff) {
        newsList.innerHTML = '<p class="muted">Доступ только для администратора.</p>';
        reportList.innerHTML = '';
        return;
    }

    try {
        const [newsData, reportsData] = await Promise.all([
            api('/news/'),
            api('/reports/'),
        ]);

        const news = Array.isArray(newsData) ? newsData : newsData.results || [];
        const reports = Array.isArray(reportsData) ? reportsData : reportsData.results || [];

        newsList.innerHTML = news.length
            ? news.map(item => `
                <div class="admin-list-item">
                    <div>
                        <strong>${item.title}</strong>
                        <small>${item.status}</small>
                    </div>
                    <div class="admin-actions">
                        <button class="btn btn-secondary" data-moderate-news="${item.id}" data-status="PUBLISHED">Опубликовать</button>
                        <button class="btn btn-light" data-moderate-news="${item.id}" data-status="REJECTED">Отклонить</button>
                    </div>
                </div>
            `).join('')
            : '<p class="muted">Нет новостей на модерацию.</p>';

        reportList.innerHTML = reports.length
            ? reports.map(item => `
                <div class="admin-list-item">
                    <div>
                        <strong>${item.target_type}</strong>
                        <small>${item.reason}</small>
                    </div>
                    <div class="admin-actions">
                        <button class="btn btn-secondary" data-moderate-report="${item.id}" data-status="RESOLVED">Решено</button>
                        <button class="btn btn-light" data-moderate-report="${item.id}" data-status="REJECTED">Отклонить</button>
                    </div>
                </div>
            `).join('')
            : '<p class="muted">Жалоб нет.</p>';

        document.querySelectorAll('[data-moderate-news]').forEach(button => {
            button.addEventListener('click', async () => {
                try {
                    await api(`/news/${button.dataset.moderateNews}/moderate/`, {
                        method: 'PATCH',
                        body: JSON.stringify({ status: button.dataset.status }),
                    });
                    await loadAdminPage();
                } catch (error) {
                    alert(error.message);
                }
            });
        });

        document.querySelectorAll('[data-moderate-report]').forEach(button => {
            button.addEventListener('click', async () => {
                try {
                    await api(`/reports/${button.dataset.moderateReport}/`, {
                        method: 'PATCH',
                        body: JSON.stringify({ status: button.dataset.status, admin_note: 'Обработано через админку сайта' }),
                    });
                    await loadAdminPage();
                } catch (error) {
                    alert(error.message);
                }
            });
        });
    } catch (error) {
        newsList.innerHTML = `<p class="muted">${error.message}</p>`;
        reportList.innerHTML = '';
    }
}

async function handleNewsSubmit(event) {
    event.preventDefault();
    const form = event.currentTarget;
    const auth = getAuth();
    if (!auth) {
        window.location.href = '/auth/';
        return;
    }

    const payload = {
        title: form.title.value,
        slug: form.slug.value || undefined,
        content: form.content.value,
        category: Number(form.category.value),
        city: Number(form.city.value),
        district: Number(form.district.value),
    };

    try {
        await api('/news/', {
            method: 'POST',
            body: JSON.stringify(payload),
        });
        form.reset();
        await loadNewsPage();
        alert('Новость отправлена на модерацию.');
    } catch (error) {
        alert(error.message);
    }
}

async function handleReportSubmit(event) {
    event.preventDefault();
    const form = event.currentTarget;
    const auth = getAuth();
    if (!auth) {
        window.location.href = '/auth/';
        return;
    }

    const adId = form.dataset.adId;
    if (!adId) return;

    try {
        await api('/reports/', {
            method: 'POST',
            body: JSON.stringify({
                target_type: 'AD',
                ad: Number(adId),
                reason: form.reason.value,
            }),
        });
        form.reset();
        form.classList.add('hidden');
        alert('Жалоба отправлена модераторам.');
    } catch (error) {
        alert(error.message);
    }
}

async function handleLogin(event) {
    event.preventDefault();
    const form = event.currentTarget;
    const username = form.querySelector('[name="username"]')?.value.trim() || '';
    const password = form.querySelector('[name="password"]')?.value || '';

    if (!username || !password) {
        alert('Введите логин и пароль.');
        return;
    }

    const payload = {
        username,
        password,
    };

    try {
        const result = await api('/login/', {
            method: 'POST',
            body: JSON.stringify(payload),
        });

        saveAuth({
            access: result.access,
            refresh: result.refresh,
            user: result.user || payload.username,
        });

        window.location.href = '/';
    } catch (error) {
        alert(error.message);
    }
}

async function handleRegister(event) {
    event.preventDefault();
    const form = event.currentTarget;
    const username = form.querySelector('[name="username"]')?.value.trim() || '';
    const email = form.querySelector('[name="email"]')?.value.trim() || '';
    const password = form.querySelector('[name="password"]')?.value || '';
    const passwordConfirmation = form.querySelector('[name="password_confirm"]')?.value || '';

    if (!username || !email || !password || !passwordConfirmation) {
        alert('Заполните все поля регистрации.');
        return;
    }

    const payload = {
        username,
        email,
        password,
        password_confirmation: passwordConfirmation,
    };

    try {
        await api('/register/', {
            method: 'POST',
            body: JSON.stringify(payload),
        });

        alert('Регистрация успешна. Теперь войдите в аккаунт.');
        document.querySelector('[data-target="login-form"]').click();
        form.reset();
    } catch (error) {
        alert(error.message);
    }
}

async function ensureCreateAdDefaults() {
    const categoryHidden = qs('#create-category-hidden');
    const cityHidden = qs('#create-city-hidden');
    const districtHidden = qs('#create-district-hidden');
    const conditionHidden = qs('#create-condition-hidden');

    if (!categoryHidden || !cityHidden || !districtHidden || !conditionHidden) {
        return;
    }

    try {
        const categories = await api('/categories/');
        const cities = await api('/cities/');

        if (categories.length) {
            categoryHidden.value = String(categories[0].id);
        }
        if (cities.length) {
            cityHidden.value = String(cities[0].id);
            const districts = await api(`/districts/?city=${cities[0].id}`);
            if (districts.length) {
                districtHidden.value = String(districts[0].id);
            }
        }

        conditionHidden.value = 'NEW';
    } catch (error) {
        console.error('Default ad data setup failed:', error.message);
    }
}

async function handleCreateAd(event) {
    event.preventDefault();
    const form = event.currentTarget;

    await ensureCreateAdDefaults();

    const payload = {
        title: form.title.value,
        description: form.description.value,
        price: Number(form.price.value),
        category: Number(form.category.value || qs('#create-category-hidden')?.value || 0),
        city: Number(form.city.value || qs('#create-city-hidden')?.value || 0),
        district: Number(form.district.value || qs('#create-district-hidden')?.value || 0),
        condition: form.condition.value || qs('#create-condition-hidden')?.value || 'NEW',
        status: form.status.value,
    };

    try {
        const created = await api('/ads/', {
            method: 'POST',
            body: JSON.stringify(payload),
        });

        const file = form.image?.files?.[0];
        if (file) {
            const formData = new FormData();
            formData.append('image', file);
            formData.append('is_main', 'true');
            await api(`/ads/${created.id}/images/`, {
                method: 'POST',
                body: formData,
            });
        }

        form.reset();
        document.getElementById('create-ad-modal').classList.add('hidden');
        await ensureCreateAdDefaults();
        loadAds();
    } catch (error) {
        alert(error.message);
    }
}

function bindEvents() {
    const loginForm = qs('#login-form');
    const registerForm = qs('#register-form');
    const createForm = qs('#create-ad-form');
    const newsForm = qs('#news-form');
    const reportForm = qs('#report-form');
    const logoutBtn = qs('#logout-btn');
    const openCreateModalBtn = qs('#open-create-ad');
    const navCreateAd = qs('#nav-create-ad');
    const messageForm = qs('#message-form');
    const toggleNewsFormBtn = qs('#toggle-news-form');

    if (loginForm) loginForm.addEventListener('submit', handleLogin);
    if (registerForm) registerForm.addEventListener('submit', handleRegister);
    if (createForm) createForm.addEventListener('submit', handleCreateAd);
    if (newsForm) newsForm.addEventListener('submit', handleNewsSubmit);
    if (reportForm) reportForm.addEventListener('submit', handleReportSubmit);
    if (messageForm) messageForm.addEventListener('submit', handleMessageSubmit);

    if (toggleNewsFormBtn && newsForm) {
        toggleNewsFormBtn.addEventListener('click', () => {
            const auth = getAuth();
            if (!auth) {
                window.location.href = '/auth/';
                return;
            }
            newsForm.classList.toggle('hidden');
            const isHidden = newsForm.classList.contains('hidden');
            toggleNewsFormBtn.textContent = isHidden ? 'Добавить новость' : 'Скрыть форму';
        });
    }

    if (logoutBtn) {
        logoutBtn.addEventListener('click', () => {
            clearAuth();
            window.location.href = '/';
        });
    }

    if (openCreateModalBtn) {
        openCreateModalBtn.addEventListener('click', async () => {
            qs('#create-ad-modal')?.classList.remove('hidden');
            await ensureCreateAdDefaults();
        });
    }

    if (navCreateAd) {
        navCreateAd.addEventListener('click', (event) => {
            event.preventDefault();
            qs('#create-ad-modal')?.classList.remove('hidden');
        });
    }

    document.querySelectorAll('[data-close]').forEach(button => {
        button.addEventListener('click', () => {
            const id = button.getAttribute('data-close');
            const modal = document.getElementById(id);
            if (modal) modal.classList.add('hidden');
        });
    });

    const searchInput = qs('#search-input');
    const searchButton = qs('#search-button');

    if (searchInput) {
        searchInput.addEventListener('keydown', (event) => {
            if (event.key === 'Enter') {
                event.preventDefault();
                loadAds();
            }
        });
        searchInput.addEventListener('input', () => {
            if (!searchInput.value.trim()) {
                loadAds();
            }
        });
    }

    if (searchButton) {
        searchButton.addEventListener('click', loadAds);
    }
}

async function init() {
    updateAuthUI();
    bindEvents();
    await refreshAuthProfile();

    if (qs('#favorites-grid')) {
        await loadFavoritesPage();
    }

    if (qs('#conversations-list')) {
        await loadConversationsPage();
    }

    if (qs('#news-page-grid')) {
        await loadNewsPage();
    }

    if (qs('#admin-news-list')) {
        await loadAdminPage();
    }

    await Promise.all([loadCategories(), loadCities(), loadNews(), loadAds()]);
    await loadDistricts();
}

document.addEventListener('DOMContentLoaded', init);
