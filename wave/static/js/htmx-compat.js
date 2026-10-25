// hx-history-cache compat
import { showToast } from "./toast.js";

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

document.addEventListener("click", (event) => {
    const button = event.target.closest('[data-action="copy-content"]');
    if (!button) return;

    const text_to_copy = button.querySelector("[data-copy]").innerText;
    if (!text_to_copy) return;

    if (!navigator.clipboard) return;

    navigator.clipboard.writeText(text_to_copy).then(
        () => {
            showToast("Copied text.", "success");
            return;
        },
        () => {
            showToast("Failed to copy text.", "error");
            return;
        },
    );
})