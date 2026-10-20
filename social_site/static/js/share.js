console.log("share feature");

htmx.on("share", (evt) => {
    console.log("share", evt.detail);
});

document.addEventListener("share", (evt) => {
    console.log("Native share event:", evt.detail);
});