

async function sendMessage() {
    const userInput = document.getElementById("userInput");
    const sendButton = document.getElementById("sendButton");
    const sendIcon = document.getElementById("sendIcon");

    const message = userInput.innerText.trim(); 

    if (message === "") return;

    userInput.setAttribute("contenteditable", "false");
    sendButton.disabled = true;
    sendIcon.src = "static/images/stop.png";

    appendMessage(message, "user-message");
    userInput.innerText = "";

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
            streamBotResponse("Error: " + responseAgent.statusText);
            return;
        }

        // Stream the response
        streamBotResponse("");
        const reader = responseAgent.body.getReader();
        const decoder = new TextDecoder("utf-8");
        const messageContainers = document.querySelectorAll(".bot-message-container");
        const messageContainer = messageContainers[messageContainers.length - 1];
        let resultText = messageContainer.querySelector(".bot-message");

        let done = false;

        while (!done) {
            const { value, done: readerDone } = await reader.read();
            done = readerDone;

            if (value) {
                const chunk = decoder.decode(value);
                const lines = chunk.split("\n");
                const parsedLines = lines
                    .map((line) => line.replace(/^data: /, ""))
                    .filter((line) => line !== "[DONE]");
                
                for (const parsedLine of parsedLines) {
                    resultText.innerHTML += parsedLine; 
                }
            }
        }

        const loadingExtractRelevantSchemaConst = document.getElementById("loading-extract-relevant-schema");
        if (loadingExtractRelevantSchemaConst) {
            loadingExtractRelevantSchemaConst.remove(); 
        }

        // Now call the markdown_to_html endpoint
        const responseMarkdown = await fetch("/markdown_to_html", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ user_input: message}),
        });

        if (!responseMarkdown.ok) {
            console.error("Error:", responseMarkdown.statusText);
            streamBotResponse("Error: " + responseMarkdown.statusText);
            return;
        }

        const dataMarkdown = await responseMarkdown.json();
        const htmlOutput = dataMarkdown.agent_output;

        // Replace the content of resultText with the new HTML
        resultText.innerHTML = htmlOutput;

    } catch (error) {
        console.error("Error during message sending:", error);
        streamBotResponse("Error: Something went wrong.");
    } finally {
        userInput.setAttribute("contenteditable", "true");
        sendButton.disabled = false;
        sendIcon.src = "static/images/icons8-arrow-100.png";
        const loadingExtractRelevantSchemaConst = document.getElementById("loading-extract-relevant-schema");
        if (loadingExtractRelevantSchemaConst) {
            loadingExtractRelevantSchemaConst.remove(); 
        }
    }
}


function streamBotResponse(chunk) {
    const chatContainer = document.getElementById("chat-container");

    let messageContainer = document.createElement("div");
    messageContainer.classList.add("bot-message-container");

    const botIconContainer = document.createElement("div");
    botIconContainer.classList.add("bot-icon-container");

    const messageElement = document.createElement("div");
    messageElement.classList.add("message", "bot-message");

    messageContainer.appendChild(messageElement);

    const actionButtonContainer = document.createElement("div");
    actionButtonContainer.classList.add("action-button-container");
    actionButtonContainer.style.opacity = "0"; 

    const copyButton = createCopyButton(messageElement);

    actionButtonContainer.appendChild(copyButton);

    messageContainer.appendChild(actionButtonContainer);

    messageContainer.onmouseover = () => {
          actionButtonContainer.style.opacity = "1";
    };
    messageContainer.onmouseout = () => {
          actionButtonContainer.style.opacity = "0";
    };

    chatContainer.appendChild(messageContainer);

    messageElement.innerHTML += chunk;

    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function cleanInput() {
    const userInput = document.getElementById("userInput");
    userInput.innerHTML = userInput.innerHTML.replace(/<span[^>]*>(.*?)<\/span>/g, "$1");
}

function appendMessage(content, className) {
    const chatContainer = document.getElementById("chat-container");

    const messageContainer = document.createElement("div");
    messageContainer.classList.add(`${className}-container`); 

    const messageElement = document.createElement("div");
    messageElement.classList.add("message", className);
    messageElement.textContent = content;

    messageContainer.appendChild(messageElement);

    chatContainer.appendChild(messageContainer);

    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function loadingExtractRelevantSchema() {
    const chatContainer = document.getElementById("chat-container");
    const loadingMessageContainer = document.createElement("div");
    loadingMessageContainer.classList.add("bot-loading-message-container");
    loadingMessageContainer.textContent = "Analysing data";
    loadingMessageContainer.id = "loading-extract-relevant-schema";
    chatContainer.appendChild(loadingMessageContainer);
}
function loadingGatherSqlContent() {
    const chatContainer = document.getElementById("chat-container");
    const loadingMessageContainer = document.createElement("div");
    loadingMessageContainer.classList.add("bot-loading-message-container");
    loadingMessageContainer.textContent = "Gathering required data";
    loadingMessageContainer.id = "loading-gather-sql-content";
    chatContainer.appendChild(loadingMessageContainer);
}

function createCopyButton(messageElement) {
    const copyButton = document.createElement("button");
    copyButton.classList.add("copy-button");

    const copyIcon = document.createElement("img");
    copyIcon.src = "static/images/copy.png"; 
    copyIcon.classList.add("action-icon");
    copyButton.appendChild(copyIcon);
    copyButton.onclick = () => {
          copyToClipboard(messageElement.textContent);
          changeIconTemporary(copyIcon, "static/images/copy-checked.png", 3000); 
    };

    return copyButton;
}

function copyToClipboard(text) {
    navigator.clipboard
          .writeText(text)
          .then(() => {})
          .catch((err) => {
                console.error("Failed to copy: ", err);
          });
}

function handleKeyPress(event) {
    const sendButton = document.getElementById("sendButton");

    if (event.key === "Enter" && !sendButton.disabled) {
          event.preventDefault(); 
          sendMessage(); 
    }
}

function checkInput() {
    const userInput = document.getElementById("userInput").textContent.trim();
    const sendButton = document.getElementById("sendButton");

    if (userInput.length > 0) {
          sendButton.style.backgroundImage = "linear-gradient(111.8deg, rgb(0, 104, 155) 19.8%, rgb(0, 173, 239) 92.1%)"; 
    } else {
          sendButton.style.backgroundImage = "linear-gradient(45deg, rgb(91 153 207), rgb(144 222 255))"; 
    }
}

function handlePaste(event) {
    event.preventDefault();

    const text = event.clipboardData.getData("text/plain");

    document.execCommand("insertText", false, text);
}

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

let uploadedFile = null;
let isPdfContainerExpanded = true; // To track expand/collapse state


// Function to handle file input for PDF upload
function handlePDFUpload(event) {
    const file = event.target.files[0];
    uploadedFile = file;  // Store the file reference

    if (file && file.type === 'application/pdf') {
        const formData = new FormData();
        formData.append('pdf', file);

        loadingExtractRelevantSchema()

        // Send the POST request with the PDF file
        fetch('/create_vector_index', {
            method: 'POST',
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const fileURL = URL.createObjectURL(file);
                displayPDFInIframe(fileURL);

                // Show the collapse/expand icon after PDF upload
                document.getElementById('collapseExpandIcon').style.display = 'block';
            } else {
                alert("Failed to process the PDF.");
            }
        })
        .catch(error => {
            console.error("Error uploading the PDF:", error);
            alert("An error occurred while uploading the PDF.");
        });
       
    } else {
        alert("Please upload a valid PDF file.");
        uploadedFile = null;  // Reset the file reference if not valid
    }
    const loadingExtractRelevantSchemaConst = document.getElementById("loading-extract-relevant-schema");
    if (loadingExtractRelevantSchemaConst) {
        loadingExtractRelevantSchemaConst.remove(); 
    }
}


// Function to display the PDF in an iframe
function displayPDFInIframe(pdfURL) {
    const fileContainer = document.querySelector('.file-container');
    
    // Clear any previous content in the container
    fileContainer.innerHTML = '';

    // Create an iframe element
    const iframe = document.createElement('iframe');
    iframe.src = pdfURL;
    iframe.width = '100%';  // Set to full width
    iframe.height = '500px';  // Adjust the height as needed
    iframe.style.border = 'none';  // Remove border for clean look

    // Append the iframe to the file container
    fileContainer.appendChild(iframe);
    
    // Apply expanded styles
    expandPdfContainer();
}

// Function to toggle the PDF container between expanded and collapsed state
function togglePdfContainer() {
    if (isPdfContainerExpanded) {
        collapsePdfContainer();
    } else {
        expandPdfContainer();
    }
}

// Function to expand the PDF container
function expandPdfContainer() {
    const fileContainer = document.getElementById('fileContainer');
    fileContainer.style.width = '50%';
    fileContainer.style.padding = '2%';

    const container = document.querySelector('.container');
    container.style.maxWidth = '900px';
    container.style.width = '50%';
    container.style.padding = '0px 2% 30px 2%';

    // Change icon to collapse icon
    document.getElementById('iconImage').src = "static/images/icons8-collapse-100.png";
    isPdfContainerExpanded = true;
}

// Function to collapse the PDF container
function collapsePdfContainer() {
    const fileContainer = document.getElementById('fileContainer');
    fileContainer.style.width = '0px';
    fileContainer.style.padding = '0px';

    const container = document.querySelector('.container');
    container.style.maxWidth = '900px';
    container.style.width = '100%';
    container.style.padding = '0px';

    // Change icon to expand icon
    document.getElementById('iconImage').src = "static/images/icons8-expand-100.png";
    isPdfContainerExpanded = false;
}

// Attach file input event listener
document.getElementById('attachButton').addEventListener('click', function() {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'application/pdf';
    input.style.display = 'none';

    input.addEventListener('change', handlePDFUpload);
    document.body.appendChild(input); // Temporarily add input to the DOM
    input.click(); // Programmatically click the input to open file dialog
    document.body.removeChild(input); // Remove input after use
});
