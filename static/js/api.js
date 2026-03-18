const API = {
    async post(url, data) {
        const response = await fetch(url, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data),
        });
        if (!response.ok) {
            const err = await response.json().catch(() => ({}));
            throw new Error(err.message || `Request failed (${response.status})`);
        }
        return response.json();
    },

    async get(url) {
        const response = await fetch(url);
        if (!response.ok) {
            const err = await response.json().catch(() => ({}));
            throw new Error(err.message || `Request failed (${response.status})`);
        }
        return response.json();
    },

    showError(message) {
        this._showAlert(message, 'danger');
    },

    showSuccess(message) {
        this._showAlert(message, 'success', 3000);
    },

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    },

    _showAlert(message, type, autoDismissMs) {
        const container = document.querySelector('main .container');
        if (!container) return;

        const alert = document.createElement('div');
        alert.className = `alert alert-${type} alert-dismissible fade show`;
        alert.innerHTML = `
            ${this.escapeHtml(message)}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        container.prepend(alert);

        if (autoDismissMs) {
            setTimeout(() => alert.remove(), autoDismissMs);
        }
    },
};
