import { showToast } from "./toast.js";

htmx.on("share", (evt) => {
    showToast(evt.detail);
});