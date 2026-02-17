/**
 * Main JavaScript for Performance Marketing System
 * Shared utilities used across all pages.
 */

// Escape HTML to prevent XSS when injecting into innerHTML
function escapeHtml(str) {
    if (str == null) return '';
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

// Format numbers with commas and optional decimal places
function formatNumber(n, decimals = 0) {
    if (n == null || isNaN(n)) return '0';
    return Number(n).toLocaleString('he-IL', { minimumFractionDigits: decimals, maximumFractionDigits: decimals });
}

// Format currency (NIS)
function formatCurrency(n) {
    if (n == null || isNaN(n)) return '₪0';
    return '₪' + formatNumber(n, 0);
}

// Format percentage
function formatPct(n) {
    if (n == null || isNaN(n)) return '0%';
    return Number(n).toFixed(1) + '%';
}

// Close any modal
function closeModal(id) {
    document.getElementById(id).style.display = 'none';
}

// Generic modal close on outside click
window.addEventListener('click', function(e) {
    document.querySelectorAll('.modal').forEach(m => {
        if (e.target === m) m.style.display = 'none';
    });
});

// Flash message helper
function showFlash(msg, type = 'success') {
    const el = document.createElement('div');
    el.className = `alert alert-${type}`;
    el.style.cssText = 'position:fixed;top:1rem;left:50%;transform:translateX(-50%);z-index:9999;max-width:500px;padding:.8rem 1.5rem;border-radius:6px;box-shadow:0 4px 12px rgba(0,0,0,.12);animation:fadeIn .3s;';
    el.textContent = msg;
    document.body.appendChild(el);
    setTimeout(() => el.remove(), 3500);
}
