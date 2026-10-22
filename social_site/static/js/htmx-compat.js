// hx-history-cache compat
document.addEventListener("click", (event) => {
    const button = event.target.closest('[data-action="history-back"]');
    if (!button) return;

    history.back();
})

document.addEventListener("click", (event) => {
    const button = event.target.closest('[data-action="page-reload"]');
    if (!button) return;

    window.location.reload();
})