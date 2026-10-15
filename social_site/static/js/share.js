document.addEventListener("click", async (event) => {
    const button = event.target.closest("#share-button");

    if (!button) return;

    if (!navigator.share) {
        return;
    }

    try {
        await navigator.share({
            title: button.dataset.title,
            url: button.dataset.url
        });
    } catch (error) {
        if (error.name !== "AbortError") {
            console.error("Sharing failed:", error);
        }
    }
});