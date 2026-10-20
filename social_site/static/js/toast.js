export function showToast(text, timeout = 5000) {
    const toast = document.getElementById("toast");
    toast.innerText = text;
    toast.classList.add("show");

    setTimeout(() => {
        toast.classList.remove("show");
    }, timeout);

    return;
}