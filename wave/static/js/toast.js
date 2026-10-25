export function showToast(text, type = "info", timeout = 5000) {
    const toast_container = document.getElementById("toast-container");
    if (!toast_container) return;

    const toast = document.createElement("div");
    toast.classList.add("toast");
    toast.offsetHeight; // Needed for animation for some reason
    toast.setAttribute("role", type === "error" ? "alert" : "status");
    toast.setAttribute("aria-live", type === "error" ? "assertive" : "polite");
    toast.innerText = text;

    toast_container.append(toast)
    requestAnimationFrame(() => toast.classList.add("show"));

    setTimeout(() => {
        toast.classList.remove("show");
        setTimeout(() => {
            toast.remove();
        }, 500);
    }, timeout);

    return;
}

htmx.on("toast", (event) => {
    const { text, type = "info", timeout = 5000 } = event.detail ?? {};

    if (typeof text !== "string") return;

    showToast(text, type, timeout);
});