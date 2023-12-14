function appendMessage(sender, message) {
    const conversationDiv = document.getElementById('conversation');
    const messageDiv = document.createElement('div');
    messageDiv.className = sender;
    messageDiv.innerHTML = message;
    conversationDiv.appendChild(messageDiv);
    conversationDiv.scrollTop = conversationDiv.scrollHeight;
}

function submitUserInput() {
    const userInputField = document.getElementById('user-input-field');
    const userMessage = userInputField.value.trim();

    if (userMessage !== '') {
        appendMessage('user', userMessage);

        // Make an AJAX request to the Flask server
        $.ajax({
            type: 'POST',
            url: '/results',
            data: { 'user_input': userMessage },
            success: function(data) {
                appendMessage('bot', data.bot_response);

                // Display enhanced summary
                appendMessage('bot', 'Enhanced Summary: ' + data.enhanced_summary);

                // Display the table (you need to adjust this based on your actual HTML structure)
                appendMessage('bot', 'Publication Information:');
                const tableRows = data.publication_info.map(entry =>
                    `<tr><td>${entry['Publication Year']}</td><td>${entry['Publication Link']}</td></tr>`
                );
                const tableHtml = `<table>${tableRows.join('')}</table>`;
                appendMessage('bot', tableHtml);

                // Optionally, you can check if the conversation should continue
                if (!data.continue_conversation) {
                    appendMessage('bot', 'Goodbye!');
                    document.getElementById('user-input-form').style.display = 'none';
                }

                // Clear user input field
                userInputField.value = '';
            },
            error: function(error) {
                console.error('Error:', error);
            }
        });
    }
}
