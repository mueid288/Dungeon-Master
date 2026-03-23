const API_BASE = "http://127.0.0.1:8000";

// Global State
let token = localStorage.getItem("token") || null;
let currentCharacter = null;
let currentCampaignId = null;

// --- DOM Layout Handlers ---
const screens = {
    auth: document.getElementById('auth-screen'),
    lobby: document.getElementById('lobby-screen'),
    game: document.getElementById('game-screen')
};

function showScreen(screenName) {
    Object.values(screens).forEach(s => s.classList.remove('active'));
    screens[screenName].classList.add('active');
}

function showToast(msg, isError = false) {
    const toast = document.getElementById('toast');
    toast.textContent = msg;
    toast.style.background = isError ? "var(--crimson)" : "var(--gold)";
    toast.classList.remove('hidden');
    setTimeout(() => { toast.classList.add('hidden'); }, 3000);
}

// --- Init & Check Auth ---
async function init() {
    if (token) {
        if (await fetchLobbyData()) {
            showScreen('lobby');
        } else {
            logout();
        }
    } else {
        showScreen('auth');
    }
}

function logout() {
    token = null;
    localStorage.removeItem("token");
    showScreen('auth');
}

// --- Fetch Wrapper ---
async function apiCall(endpoint, method = "GET", body = null) {
    const headers = { "Content-Type": "application/json" };
    if (token) headers["Authorization"] = `Bearer ${token}`;

    const config = { method, headers };
    if (body) config.body = JSON.stringify(body);

    const res = await fetch(`${API_BASE}${endpoint}`, config);
    const data = await res.json();
    
    if (!res.ok) {
        throw new Error(data.detail || data.message || "API Error");
    }
    return data;
}

// --- Authentication ---
document.getElementById('auth-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const errorDiv = document.getElementById('auth-error');

    try {
        const res = await apiCall("/auth/login", "POST", { email, password });
        token = res.token;
        localStorage.setItem("token", token);
        errorDiv.textContent = "";
        init();
    } catch (err) {
        errorDiv.textContent = err.message;
    }
});

document.getElementById('signup-btn').addEventListener('click', async () => {
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const errorDiv = document.getElementById('auth-error');

    try {
        await apiCall("/auth/register", "POST", { email, password });
        showToast("Account forged! You may now login.");
    } catch (err) {
        errorDiv.textContent = err.message;
    }
});

document.getElementById('logout-btn').addEventListener('click', logout);


// --- Lobby Logic ---
async function fetchLobbyData() {
    try {
        // Fetch Character
        const chars = await apiCall("/character/all");
        if (chars && chars.length > 0) {
            currentCharacter = chars[0];
            document.getElementById('create-char-form').classList.add('hidden');
            document.getElementById('char-details').classList.remove('hidden');
            
            document.getElementById('char-name').textContent = currentCharacter.name;
            document.getElementById('char-class').textContent = currentCharacter.char_class;
            document.getElementById('char-level').textContent = currentCharacter.level;
            document.getElementById('char-hp').textContent = `${currentCharacter.health}/${currentCharacter.max_health}`;
            document.getElementById('char-xp').textContent = currentCharacter.xp;
        } else {
            document.getElementById('char-details').classList.add('hidden');
            document.getElementById('create-char-form').classList.remove('hidden');
        }

        // Fetch Campaigns
        const campaigns = await apiCall("/campaign/my");
        const list = document.getElementById('campaign-list');
        list.innerHTML = "";
        
        if(campaigns && campaigns.length > 0) {
            campaigns.forEach(camp => {
                const li = document.createElement('li');
                li.innerHTML = `<strong>${camp.name}</strong> <span class="text-sm">ID: ${camp.id}</span>`;
                li.addEventListener('click', () => enterCampaign(camp));
                list.appendChild(li);
            });
        } else {
            list.innerHTML = `<li class="text-dim italic text-center">No campaigns found.</li>`;
        }
        return true;
    } catch (err) {
        console.error(err);
        return false;
    }
}

// Character Creation
document.getElementById('create-char-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const name = document.getElementById('new-char-name').value;
    const char_class = document.getElementById('new-char-class').value;
    try {
        await apiCall("/character/create", "POST", { name, char_class });
        showToast("Character created!");
        fetchLobbyData();
    } catch (err) {
        showToast(err.message, true);
    }
});

// Campaign Controls
document.getElementById('show-create-campaign').addEventListener('click', () => {
    document.getElementById('create-campaign-form').classList.toggle('hidden');
    document.getElementById('join-campaign-form').classList.add('hidden');
});

document.getElementById('show-join-campaign').addEventListener('click', () => {
    document.getElementById('join-campaign-form').classList.toggle('hidden');
    document.getElementById('create-campaign-form').classList.add('hidden');
});

document.getElementById('create-campaign-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const name = document.getElementById('camp-name').value;
    const theme = document.getElementById('camp-theme').value;
    try {
        await apiCall("/campaign/create", "POST", { name, theme });
        showToast("Campaign forged!");
        fetchLobbyData();
    } catch (err) {
        showToast(err.message, true);
    }
});

document.getElementById('join-campaign-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const campaign_id = parseInt(document.getElementById('join-camp-id').value);
    try {
        await apiCall("/campaign/join", "POST", { campaign_id });
        showToast("Joined campaign!");
        fetchLobbyData();
    } catch (err) {
        showToast(err.message, true);
    }
});


// --- Game Loop ---
async function enterCampaign(campaign) {
    if (!currentCharacter) {
        showToast("You must mold a character first!", true);
        return;
    }
    currentCampaignId = campaign.id;
    document.getElementById('active-camp-name').textContent = campaign.name;
    updateSidebarStats();
    
    // Attempt Start Game
    showScreen('game');
    const logs = document.getElementById('story-log');
    logs.innerHTML = `<div class="system-msg">Connecting to the realm...</div>`;
    
    try {
        // Warning: Start game may throw 409 if already started, which is fine
        const startRes = await apiCall(`/game/start`, "POST", { campaign_id: campaign.id });
        appendStory("DM", startRes.opening, null, true);
        renderOptions(startRes.next_options);
        
        // Fetch to update latest campaign details
        const campData = await apiCall(`/campaign/${campaign.id}`);
        updateCampaignSidebar(campData);
    } catch (err) {
        if(err.message === "Game Already Started") {
            // Already started! Let's show the real data summary so far
            try {
                const campData = await apiCall(`/campaign/${campaign.id}`);
                const history = campData.summary ? campData.summary : "Welcome back to the shadows...";
                appendStory("DM", `[RECAP] ${history}`, null, true);
                updateCampaignSidebar(campData);
            } catch (e) {
                appendStory("DM", "Welcome back to the table.", null, true);
            }
        } else {
            showToast(err.message, true);
            showScreen('lobby');
        }
    }
}

document.getElementById('leave-game-btn').addEventListener('click', () => {
    showScreen('lobby');
    fetchLobbyData();
});

document.getElementById('action-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const input = document.getElementById('player-action');
    const  actionText = input.value.trim();
    if(!actionText) return;

    input.value = "";
    appendStory("Player", actionText);

    // Disable input while thinking
    const btn = document.getElementById('send-action-btn');
    btn.disabled = true;
    btn.textContent = "Rolling...";

    try {
        const payload = {
            character_id: currentCharacter.id,
            campaign_id: currentCampaignId,
            player_action: actionText
        };
        const result = await apiCall("/game/action", "POST", payload);
        
        // Emulate dice roll
        const diceEl = document.getElementById('dice-result');
        const rollEl = document.getElementById('roll-value');
        rollEl.textContent = result.dice_roll;
        
        if(result.dice_roll === 20) diceEl.style.color = "var(--gold)";
        else if (result.dice_roll === 1) diceEl.style.color = "var(--crimson)";
        else diceEl.style.color = "var(--text-main)";

        diceEl.classList.remove('hidden');
        setTimeout(() => { diceEl.classList.add('hidden'); }, 4000);

        // Update stats
        if(result.damage_taken) currentCharacter.health = Math.max(0, currentCharacter.health - result.damage_taken);
        if(result.xp_gained) currentCharacter.xp += result.xp_gained;
        
        updateSidebarStats();
        
        // Refresh campaign to get new action count / status
        const campData = await apiCall(`/campaign/${currentCampaignId}`);
        updateCampaignSidebar(campData);
        
        const isCritical = result.importance === "critical" || result.importance === "high";
        appendStory("DM", result.narrative, result.dice_roll, isCritical);
        
        renderOptions(result.next_options);

    } catch (err) {
        showToast(err.message, true);
    } finally {
        btn.disabled = false;
        btn.textContent = "ACT";
    }
});

function renderOptions(options) {
    const container = document.getElementById('quick-options');
    container.innerHTML = "";
    if(!options || options.length === 0) {
        container.classList.add('hidden');
        return;
    }
    
    options.forEach(opt => {
        const btn = document.createElement('button');
        btn.className = 'opt-btn';
        btn.textContent = opt;
        btn.onclick = () => {
            document.getElementById('player-action').value = opt;
            document.getElementById('action-form').dispatchEvent(new Event('submit'));
            container.classList.add('hidden');
        };
        container.appendChild(btn);
    });
    
    container.classList.remove('hidden');
}

function appendStory(speaker, text, roll = null, critical = false) {
    const logs = document.getElementById('story-log');
    const div = document.createElement('div');
    
    if (speaker === "Player") {
        div.className = "msg-player";
        div.textContent = text;
    } else {
        div.className = "msg-dm";
        if(critical) div.classList.add('critical');
        div.innerHTML = text.replace(/\n/g, "<br>");
    }
    
    logs.appendChild(div);
    logs.scrollTop = logs.scrollHeight;
}

function updateSidebarStats() {
    if(!currentCharacter) return;
    
    document.getElementById('game-char-name').textContent = currentCharacter.name;
    document.getElementById('game-char-level').textContent = currentCharacter.level || "1";
    document.getElementById('game-char-hp').textContent = `${currentCharacter.health}/${currentCharacter.max_health}`;
    
    // HP Bar Fill
    const hpPct = Math.max(0, Math.min(100, (currentCharacter.health / currentCharacter.max_health) * 100));
    document.getElementById('health-bar-fill').style.width = hpPct + "%";

    // XP Bar Fill (Assumes 100 xp per level as per backend)
    const needed = (currentCharacter.level || 1) * 100;
    const xpPct = Math.min(100, ((currentCharacter.xp || 0) / needed) * 100);
    document.getElementById('game-char-xp').textContent = `${currentCharacter.xp || 0}/${needed}`;
    document.getElementById('xp-bar-fill').style.width = xpPct + "%";
}

function updateCampaignSidebar(campData) {
    if(!campData) return;
    document.getElementById('campaign-extra-info').classList.remove('hidden');
    document.getElementById('camp-main-quest').textContent = campData.main_quest || "Unknown";
    document.getElementById('camp-villain').textContent = campData.villain || "Unknown";
    document.getElementById('camp-status').textContent = campData.status || "active";
    document.getElementById('camp-action-count').textContent = campData.action_count || 0;
    
    if (campData.status !== "active") {
        document.getElementById('camp-status').style.color = (campData.status === "Failed") ? "var(--crimson)" : "var(--gold)";
    } else {
        document.getElementById('camp-status').style.color = "var(--text-main)";
    }
}

// Boot
init();