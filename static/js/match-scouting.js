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

// Save confirmation modal
function confirmMatchSave(teamNumber, matchNumber) {
    const modal = document.getElementById('confirmModal');
    document.getElementById('confirmTeamNumber').textContent = teamNumber;
    document.getElementById('confirmMatchNumber').textContent = matchNumber;
    new bootstrap.Modal(modal).show();
}
