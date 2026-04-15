// Toggle button groups for match scouting
document.querySelectorAll('.btn-group-toggle').forEach(group => {
    group.querySelectorAll('.btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const colorClass = btn.dataset.color || 'primary';
            // Deselect all in group
            group.querySelectorAll('.btn').forEach(b => {
                const bColor = b.dataset.color || 'primary';
                b.classList.remove('btn-' + bColor);
                b.classList.add('btn-outline-' + bColor);
            });
            // Select clicked
            btn.classList.remove('btn-outline-' + colorClass);
            btn.classList.add('btn-' + colorClass);
            // Update hidden input
            const input = group.querySelector('input[type="hidden"]');
            if (input) {
                input.value = btn.dataset.value;
            }
        });
    });
});

// Fuel scored — two-stage input (Shot/Didn't Shoot → 1-5 selector)
const FUEL_EXPLAINERS = {
    '1': 'Very few balls scored',
    '2': 'Scored some, but not impressive',
    '3': 'Decent — maybe around 100',
    '4': 'Really good shooting',
    '5': 'Overwhelming scoring volume'
};

document.querySelectorAll('.fuel-scored').forEach(card => {
    const input = card.querySelector('input[type="hidden"]');
    const levels = card.querySelector('.fuel-levels');
    const explainer = card.querySelector('.fuel-explainer');
    const shotBtn = card.querySelector('.fuel-mode-btn[data-mode="shot"]');
    const noneBtn = card.querySelector('.fuel-mode-btn[data-mode="none"]');
    const levelBtns = card.querySelectorAll('.fuel-level-btn');

    function clearLevels() {
        levelBtns.forEach(b => {
            b.classList.remove('btn-warning');
            b.classList.add('btn-outline-warning');
        });
        explainer.textContent = '';
    }

    shotBtn.addEventListener('click', () => {
        shotBtn.classList.remove('btn-outline-warning');
        shotBtn.classList.add('btn-warning');
        noneBtn.classList.remove('btn-danger');
        noneBtn.classList.add('btn-outline-danger');
        levels.style.display = '';
        if (!['1','2','3','4','5'].includes(input.value)) {
            input.value = '';
        }
    });

    noneBtn.addEventListener('click', () => {
        noneBtn.classList.remove('btn-outline-danger');
        noneBtn.classList.add('btn-danger');
        shotBtn.classList.remove('btn-warning');
        shotBtn.classList.add('btn-outline-warning');
        levels.style.display = 'none';
        clearLevels();
        input.value = '0';
    });

    levelBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const n = btn.dataset.level;
            levelBtns.forEach(b => {
                if (b.dataset.level === n) {
                    b.classList.remove('btn-outline-warning');
                    b.classList.add('btn-warning');
                } else {
                    b.classList.remove('btn-warning');
                    b.classList.add('btn-outline-warning');
                }
            });
            explainer.textContent = FUEL_EXPLAINERS[n] || '';
            input.value = n;
        });
    });
});

// Save confirmation modal
function confirmMatchSave(teamNumber, matchNumber) {
    const modal = document.getElementById('confirmModal');
    document.getElementById('confirmTeamNumber').textContent = teamNumber;
    document.getElementById('confirmMatchNumber').textContent = matchNumber;
    new bootstrap.Modal(modal).show();
}
