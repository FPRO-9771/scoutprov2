// Toggle button groups — only one active per group
document.querySelectorAll('.btn-group-toggle').forEach(group => {
    group.querySelectorAll('.btn').forEach(btn => {
        btn.addEventListener('click', () => {
            // Deselect all in group
            group.querySelectorAll('.btn').forEach(b => {
                b.classList.remove('btn-primary');
                b.classList.add('btn-outline-primary');
            });
            // Select clicked
            btn.classList.remove('btn-outline-primary');
            btn.classList.add('btn-primary');
            // Update hidden input
            const input = group.querySelector('input[type="hidden"]');
            if (input) {
                input.value = btn.dataset.value;
            }
        });
    });
});

// Save confirmation modal
function confirmSave(teamNumber) {
    const modal = document.getElementById('confirmModal');
    document.getElementById('confirmTeamNumber').textContent = teamNumber;
    new bootstrap.Modal(modal).show();
}
