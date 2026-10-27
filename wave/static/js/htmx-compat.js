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

document.body.addEventListener('change', function (event) {
    const fileInput = event.target;

    if (fileInput.type === 'file') {
        const statusId = fileInput.getAttribute('aria-describedby');

        if (statusId) {
            const statusText = document.getElementById(statusId);

            if (statusText) {
                if (fileInput.files && fileInput.files[0]) {
                    statusText.textContent = fileInput.files[0].name;
                } else {
                    statusText.textContent = 'No file selected';
                }
            }
        }
    }
});

htmx.on("share", async (evt) => {
    try {
        const { handleShare } = await import('/static/js/share.js');
        handleShare(evt.detail);
    } catch (error) {
        console.error("Failed to load the sharing script:", error);
    }
});