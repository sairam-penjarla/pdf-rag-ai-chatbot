////////////////////////////////////////////////////////////////////////////////////////////////////
// GLOBAL VARIABLES & INITIAL SETUP
////////////////////////////////////////////////////////////////////////////////////////////////////

let uploadedFile = null;
let isPdfContainerExpanded = true;

////////////////////////////////////////////////////////////////////////////////////////////////////
// UTILITY FUNCTIONS
////////////////////////////////////////////////////////////////////////////////////////////////////

async function invokeLLM(event) {
    if (event.key === "Enter") {
        event.preventDefault();
        const chatAttachIcon = document.getElementById("chat-input-box");
    const chatSendBtn = document.getElementById("chat-send-btn");
    const chatSendIcon = document.getElementById("chat-send-icon");

    const message = chatAttachIcon.innerText.trim();

    if (message === "") return;

    chatAttachIcon.setAttribute("contenteditable", "false");
    chatSendBtn.disabled = true;
    chatSendIcon.src = "static/images/stop.png";

    showQuestion(message, "user-message");
    chatAttachIcon.innerText = "";

    loadingExtractRelevantSchema(); // loading animation while extract_relavant_schema method returns the results

    try {
        // send request to /invoke_agent (streaming response) # change here
        const responseAgent = await fetch("/invoke_agent", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ user_input: message, file_is_attached: uploadedFile !== null }),
        });

        if (!responseAgent.ok) {
            console.error("Error:", responseAgent.statusText);
            showAnswer("Error: " + responseAgent.statusText);
            return;
        }

        // Stream the response
        showAnswer("");
        const reader = responseAgent.body.getReader();
        const decoder = new TextDecoder("utf-8");
        const messageContainers = document.querySelectorAll(".bot-message-container");
        const messageContainer = messageContainers[messageContainers.length - 1];
        let resultText = messageContainer.querySelector(".bot-message");

        let done = false;
        let llm_output = "";

        while (!done) {
            const { value, done: readerDone } = await reader.read();
            done = readerDone;

            if (value) {
                llm_output += decoder.decode(value);
                resultText.innerHTML = marked.parse(llm_output);

                const chatContainer = document.getElementById("chat-message-wrapper");
                chatContainer.scrollTop = chatContainer.scrollHeight;
            }
        }

        const loadingExtractRelevantSchemaConst = document.getElementById("loading-extract-relevant-schema");
        if (loadingExtractRelevantSchemaConst) {
            loadingExtractRelevantSchemaConst.remove();
        }

        // Now call the update_conversation endpoint
        const responseMarkdown = await fetch("/update_conversation", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                user_input: message,
                llm_output: llm_output,
                flow_index: 0,
                conversation_index: 0,
            }),
        });
    } catch (error) {
        console.error("Error during message sending:", error);
        showAnswer("Error: Something went wrong.");
    } finally {
        chatAttachIcon.setAttribute("contenteditable", "true");
        chatSendBtn.disabled = false;
        chatSendIcon.src = "static/images/icons8-arrow-100.png";
        const loadingExtractRelevantSchemaConst = document.getElementById("loading-extract-relevant-schema");
        if (loadingExtractRelevantSchemaConst) {
            loadingExtractRelevantSchemaConst.remove();
        }
    }
    }
}

function clearFormatting(event) {
    event.preventDefault();
    const text = event.clipboardData.getData("text/plain");
    document.execCommand("insertText", false, text);
}


////////////////////////////////////////////////////////////////////////////////////////////////////
// LOADING ANIMATIONS
////////////////////////////////////////////////////////////////////////////////////////////////////
function loadingExtractRelevantSchema() {
    const chatContainer = document.getElementById("chat-message-wrapper");
    const loadingMessageContainer = document.createElement("div");
    loadingMessageContainer.classList.add("bot-loading-message-container");
    loadingMessageContainer.textContent = "Analysing data";
    loadingMessageContainer.id = "loading-extract-relevant-schema";
    chatContainer.appendChild(loadingMessageContainer);
}

////////////////////////////////////////////////////////////////////////////////////////////////////
// CHATBOT FUNCTIONS
////////////////////////////////////////////////////////////////////////////////////////////////////
function showQuestion(content) {
    const chatContainer = document.getElementById("chat-message-wrapper");

    const messageContainer = document.createElement("div");
    messageContainer.classList.add(`user-message-container`);

    const messageElement = document.createElement("div");
    messageElement.classList.add("message", "user-message");
    messageElement.textContent = content;

    messageContainer.appendChild(messageElement);

    chatContainer.appendChild(messageContainer);

    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function showAnswer(chunk) {
    const chatContainer = document.getElementById("chat-message-wrapper");

    let messageContainer = document.createElement("div");
    messageContainer.classList.add("bot-message-container");

    const botIconContainer = document.createElement("div");
    botIconContainer.classList.add("bot-icon-container");

    const messageElement = document.createElement("div");
    messageElement.classList.add("message", "bot-message");

    messageContainer.appendChild(messageElement);

    chatContainer.appendChild(messageContainer);

    messageElement.innerHTML = marked.parse(chunk);

    chatContainer.scrollTop = chatContainer.scrollHeight;
}

////////////////////////////////////////////////////////////////////////////////////////////////////
// FILE UPLOAD & PDF DISPLAY FUNCTIONS
////////////////////////////////////////////////////////////////////////////////////////////////////

function displayPDFInIframe(pdfURL) {
    const displayContainer = document.getElementById("displayContainer");

    // Clear any previous content in the container
    displayContainer.innerHTML = "";

    // Create an iframe element
    const iframe = document.createElement("iframe");
    iframe.src = pdfURL;
    iframe.width = "100%"; // Set to full width
    iframe.height = "500px"; // Adjust the height as needed
    iframe.style.border = "none"; // Remove border for clean look

    // Append the iframe to the file container
    displayContainer.appendChild(iframe);

    // Apply expanded styles
    expandPdfContainer();
}

function togglePdfContainer() {
    if (isPdfContainerExpanded) {
        collapsePdfContainer();
    } else {
        expandPdfContainer();
    }
}

function expandPdfContainer() {
    const displayContainer = document.getElementById("displayContainer");
    const fileContainer = document.getElementById("fileContainer");
    const pdf_thumbnail_container = document.getElementById("pdf-thumbnail-container");
    displayContainer.style.width = "100%";
    fileContainer.style.width = "50%";
    displayContainer.style.padding = "2%";
    pdf_thumbnail_container.style.display = "block";

    const container = document.querySelector(".chat-main-container");
    container.style.maxWidth = "900px";
    container.style.width = "50%";
    container.style.padding = "0px 2% 30px 2%";

    // Change icon to collapse icon
    document.getElementById("pdf-collapse-expand-icon").src = "static/images/icons8-collapse-100.png";
    isPdfContainerExpanded = true;
}

function collapsePdfContainer() {
    const displayContainer = document.getElementById("displayContainer");
    const pdf_thumbnail_container = document.getElementById("pdf-thumbnail-container");
    const fileContainer = document.getElementById("fileContainer");
    fileContainer.style.width = "0px";
    displayContainer.style.width = "0px";
    displayContainer.style.padding = "0px";
    pdf_thumbnail_container.style.display = "none";

    const container = document.querySelector(".chat-main-container");
    container.style.maxWidth = "900px";
    container.style.width = "100%";
    container.style.padding = "0px";

    // Change icon to expand icon
    document.getElementById("pdf-collapse-expand-icon").src = "static/images/icons8-expand-100.png";
    isPdfContainerExpanded = false;
}

function handlePDFUpload(event) {
    // Ensure event.target is the input element and has 'files'
    const file = event.target.files ? event.target.files[0] : null;
    if (!file) {
        alert("No file selected.");
        return;
    }

    uploadedFile = file; // Store the file reference

    if (file && file.type === "application/pdf") {
        const formData = new FormData();
        formData.append("pdf", file);

        loadingExtractRelevantSchema(); // Show loading indicator

        // Send the POST request with the PDF file
        fetch("/create_vector_index", {
            method: "POST",
            body: formData,
        })
            .then((response) => response.json())
            .then((data) => {
                if (data.success) {
                    const fileURL = URL.createObjectURL(file);
                    location.reload();
                } else {
                    alert("Failed to process the PDF.");
                }
            })
            .catch((error) => {
                console.error("Error uploading the PDF:", error);
                alert("An error occurred while uploading the PDF.");
            });
    } else {
        alert("Please upload a valid PDF file.");
        uploadedFile = null; // Reset the file reference if not valid
    }

    const loadingExtractRelevantSchemaConst = document.getElementById("loading-extract-relevant-schema");
    if (loadingExtractRelevantSchemaConst) {
        loadingExtractRelevantSchemaConst.remove();
    }
}

document.getElementById("chat-clear-btn").addEventListener("click", function () {
    // Confirm if the user wants to delete all conversations
    if (confirm("Are you sure you want to delete all conversations?")) {
        // Call the DELETE endpoint to delete all conversations
        fetch("/delete_conversations", {
            method: "DELETE",
        })
            .then((response) => response.json())
            .then((data) => {
                // Handle the success or failure
                if (data.success) {
                    alert("All conversations have been deleted.");
                } else {
                    alert("Failed to delete conversations.");
                }
            })
            .catch((error) => {
                console.error("Error:", error);
                alert("An error occurred while deleting conversations.");
            });
    }
});

document.getElementById("chat-attach-btn").addEventListener("click", function () {
    const input = document.createElement("input");
    input.type = "file";
    input.accept = "application/pdf";
    input.style.display = "none";

    input.addEventListener("change", handlePDFUpload); // Make sure event listener is attached correctly
    document.body.appendChild(input); // Temporarily add input to the DOM
    input.click(); // Programmatically click the input to open file dialog
    document.body.removeChild(input); // Remove input after use
});
