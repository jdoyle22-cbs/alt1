import { showToast } from "./toast.js";

htmx.on("share", async (evt) => {
    const shareData = {
        title: evt.detail.title ?? "Post on Wave",
        text: evt.detail.description ?? "You've been shared a post on Wave - come check it out!",
        url: evt.detail.url,
    };

    if (!navigator.canShare) {
        if (!navigator.clipboard) {
            showToast("Your device doesn't support sharing.", "error");
            return;
        }

        navigator.clipboard.writeText(text_to_copy).then(
            () => {
                showToast("Copied link to post.", "success");
                return;
            },
            () => {
                showToast("Your device doesn't support sharing.", "error");
                return;
            },
        );

        return;
    }

    try {
        await navigator.share(shareData);
        showToast("Shared successfully.", "success");
        return;
    } catch (err) {
        console.log(`[ERR] ${err}`)
        showToast("Something went wrong while sharing.", "error");
        return;
    }
});