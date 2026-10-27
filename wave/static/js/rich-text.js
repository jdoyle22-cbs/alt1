document.addEventListener("click", (event) => {
    const button = event.target.closest('[data-rich-input]');
    if (!button) return;

    const command = button.dataset.inputCommand;
    if (!command) return;

    const input_id = button.dataset.richInput;
    if (!input_id) {
        console.error("[ERR] No input_id was assigned to button");
        return;
    }

    const input = document.getElementById(`${input_id}`);
    if (!input) return;

    const start = input.selectionStart;
    const end = input.selectionEnd;
    const text = input.value;

    const selectedText = text.substring(start, end);
    let wrappedText = ``;
    let data = {
        "link": {
            "text": "",
            "url": ""
        },
        "codeblock": {
            "language": "",
            "code": ""
        }
    };

    if (command === "link") {
        const link_text_input = document.getElementById(`link-text-${input_id}`);
        const link_text_url = document.getElementById(`link-url-${input_id}`);

        data.link.text = link_text_input.value;
        data.link.url = link_text_url.value;
    }

    if (command === "codeblock") {
        const codeblock_language_input = document.getElementById(`codeblock-language-${input_id}`);
        const codeblock_code_input = document.getElementById(`codeblock-content-${input_id}`);

        data.codeblock.language = codeblock_language_input.value;
        data.codeblock.code = codeblock_code_input.value;
    }

    wrappedText = interpretCommand(command, wrappedText, selectedText, data)

    input.value = text.substring(0, start) + wrappedText + text.substring(end);
    input.focus();
})

function interpretCommand(command, wrappedText, selectedText, data) {
    switch (command) {
        case "bold":
            wrappedText = `**${selectedText}**`;
            break;
        case "italic":
            wrappedText = `*${selectedText}*`;
            break;
        case "underline":
            wrappedText = `<span style="text-decoration: underline;">${selectedText}</span>`;
            break;
        case "strikethrough":
            wrappedText = `~~${selectedText}~~`;
            break;

        case "heading-1":
            wrappedText = `# ${selectedText}\n\n`;
            break;
        case "heading-2":
            wrappedText = `## ${selectedText}\n\n`;
            break;
        case "heading-3":
            wrappedText = `### ${selectedText}\n\n`;
            break;

        case "list-unordered":
            wrappedText = `\n- ${selectedText}\n\n`;
            break;
        case "list-ordered":
            wrappedText = `\n1. ${selectedText}\n\n`;
            break;
        case "list-task":
            wrappedText = `\n- [ ] ${selectedText}\n\n`;
            break;

        case "blockquote":
            wrappedText = `> ${selectedText}`;
            break;
        case "subscript":
            wrappedText = `<sub>${selectedText}</sub>`;
            break;
        case "superscript":
            wrappedText = `<sup>${selectedText}</sup>`;
            break;

        case "link":
            wrappedText = `[${data.link.text}](${data.link.url})`;
            break;
        case "codeblock":
            wrappedText = `\n\`\`\`${data.codeblock.language}\n${data.codeblock.code}\n`;
            break;
    }

    return wrappedText;
}