// ============================================================
//  JARVIS — Gumanoid Robot & Web Control Script
// ============================================================
const socket = io();
const cardsFeed = document.getElementById('cards-feed');
const statusTxt = document.getElementById('status-text');
const circle    = document.getElementById('pulse-circle');
const connEl    = document.getElementById('conn-status');
const cmdCount  = document.getElementById('cmd-count');

let commands = 0;

// ------------------------------------------------------------
//  Web Audio API Mechanical Keyboard SFX Synthesizer ("tq-tq-tq")
// ------------------------------------------------------------
const AudioContext = window.AudioContext || window.webkitAudioContext;
let audioCtx = null;

function getAudioContext() {
    if (!audioCtx) {
        audioCtx = new AudioContext();
    }
    if (audioCtx.state === 'suspended') {
        audioCtx.resume();
    }
    return audioCtx;
}

function playClickSound() {
    try {
        const ctx = getAudioContext();
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();

        // Realistic mechanical key press click frequency
        const freq = 1200 + Math.random() * 800;
        osc.type = 'sine';
        osc.frequency.setValueAtTime(freq, ctx.currentTime);
        osc.frequency.exponentialRampToValueAtTime(100, ctx.currentTime + 0.03);

        gain.gain.setValueAtTime(0.08, ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.03);

        osc.connect(gain);
        gain.connect(ctx.destination);

        osc.start();
        osc.stop(ctx.currentTime + 0.035);
    } catch (e) {
        // Audio context handling
    }
}

function triggerTypingSequence(durationSec) {
    const totalClicks = Math.floor((durationSec || 1.5) * 12);
    let count = 0;
    const interval = setInterval(() => {
        playClickSound();
        count++;
        if (count >= totalClicks) {
            clearInterval(interval);
        }
    }, 70 + Math.random() * 40);
}

// ------------------------------------------------------------
//  Socket Event Handlers
// ------------------------------------------------------------
socket.on('connect', () => {
    connEl.textContent = '● Robot Server Ulandi';
    connEl.className = 'conn-online';
});

socket.on('disconnect', () => {
    connEl.textContent = '● Server Uzildi';
    connEl.className = 'conn-offline';
    setStatus('idle');
});

socket.on('typing_sfx', (data) => {
    triggerTypingSequence(data.duration || 1.5);
});

socket.on('card', (data) => {
    addVisualCard(data);
    if (data.type === 'task' || data.type === 'cmd') {
        commands++;
        cmdCount.textContent = commands;
    }
});

socket.on('status', (data) => {
    setStatus(data.status);
});

// ------------------------------------------------------------
//  Status Indicator
// ------------------------------------------------------------
function setStatus(status) {
    circle.className = 'circle';
    if (status === 'listening') {
        circle.classList.add('listening');
        statusTxt.textContent = 'Eshityapman...';
    } else if (status === 'processing') {
        circle.classList.add('processing');
        statusTxt.textContent = 'O\'ylayapman...';
    } else {
        circle.classList.add('idle');
        statusTxt.textContent = 'Kutmoqda...';
    }
}

// ------------------------------------------------------------
//  Clean Visual Cards Renderer (Not plaintext logs!)
// ------------------------------------------------------------
function addVisualCard(data) {
    const emptyFeed = document.getElementById('empty-feed');
    if (emptyFeed) emptyFeed.remove();

    const card = document.createElement('div');
    const cardType = data.type || 'info';
    card.className = `card card-${cardType}`;

    const iconMap = {
        task: '📌',
        ai: '💡',
        cmd: '⚙️',
        ui: '🎨',
        success: '🟢',
        error: '❌',
        info: 'ℹ️'
    };

    const icon = iconMap[cardType] || '⚡';
    const timestamp = data.timestamp || new Date().toLocaleTimeString('uz-UZ', { hour: '2-digit', minute: '2-digit', second: '2-digit' });

    let extraHTML = '';
    if (data.details && data.details.url) {
        extraHTML = `<a href="${data.details.url}" target="_blank" class="card-btn">🌐 UI Sahifasini Ochish</a>`;
    } else if (data.details && data.details.cmd) {
        extraHTML = `<div class="card-code"><code>${data.details.cmd}</code></div>`;
    }

    card.innerHTML = `
        <div class="card-header">
            <span class="card-icon">${icon}</span>
            <span class="card-title">${data.title || 'Xabar'}</span>
            <span class="card-time">${timestamp}</span>
        </div>
        <div class="card-body">
            <p>${data.message || ''}</p>
            ${extraHTML}
        </div>
    `;

    cardsFeed.appendChild(card);
    cardsFeed.scrollTop = cardsFeed.scrollHeight;

    // Trigger subtle click sound for visual feedback
    playClickSound();

    // Maintain max 100 visual cards
    while (cardsFeed.children.length > 100) {
        cardsFeed.removeChild(cardsFeed.firstChild);
    }
}

function clearCards() {
    cardsFeed.innerHTML = '<div class="empty-feed" id="empty-feed"><div class="empty-icon">🧹</div><h3>Kartalar Tozalandi</h3></div>';
}
