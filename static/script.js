document.addEventListener('DOMContentLoaded', () => {
    const fileInputs = document.querySelectorAll('input[type="file"]');
    const form = document.getElementById('generatorForm');
    const submitBtn = document.getElementById('submitBtn');
    const btnText = submitBtn.querySelector('.btn-text');
    const spinner = submitBtn.querySelector('.spinner');
    const statusMessage = document.getElementById('statusMessage');

    // Handle drag and drop and file selection UI
    fileInputs.forEach(input => {
        const zone = input.closest('.upload-zone');
        const fileNameDisplay = zone.querySelector('.file-name');

        // Click to upload
        input.addEventListener('change', (e) => {
            if (input.files.length > 0) {
                fileNameDisplay.textContent = input.files[0].name;
                fileNameDisplay.style.color = 'var(--text-main)';
                zone.style.borderColor = 'var(--accent)';
            } else {
                fileNameDisplay.textContent = 'No file selected';
                fileNameDisplay.style.color = 'var(--text-muted)';
                zone.style.borderColor = 'var(--glass-border)';
            }
        });

        // Drag events
        zone.addEventListener('dragover', (e) => {
            e.preventDefault();
            zone.classList.add('dragover');
        });

        zone.addEventListener('dragleave', () => {
            zone.classList.remove('dragover');
        });

        zone.addEventListener('drop', (e) => {
            e.preventDefault();
            zone.classList.remove('dragover');
            
            if (e.dataTransfer.files.length > 0) {
                input.files = e.dataTransfer.files;
                // Trigger change event to update UI
                const event = new Event('change');
                input.dispatchEvent(event);
            }
        });
    });

    // Handle Form Submission
    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        // Check if all files are provided
        const csvFile = document.getElementById('csvFile').files[0];
        const templateImage = document.getElementById('templateImage').files[0];
        const fontFile = document.getElementById('fontFile').files[0];

        if (!csvFile || !templateImage || !fontFile) {
            showStatus('Please select all required files.', 'error');
            return;
        }

        // Prepare FormData
        const formData = new FormData(form);

        // UI Loading State
        submitBtn.disabled = true;
        btnText.textContent = 'Generating...';
        spinner.classList.remove('hidden');
        statusMessage.classList.remove('show');

        try {
            const response = await fetch('/generate', {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                // Handle ZIP file download
                const blob = await response.blob();
                const downloadUrl = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = downloadUrl;
                a.download = 'certificates.zip';
                document.body.appendChild(a);
                a.click();
                a.remove();
                window.URL.revokeObjectURL(downloadUrl);
                
                showStatus('Certificates generated successfully!', 'success');
            } else {
                // Handle Error
                const errorData = await response.json();
                showStatus(errorData.error || 'An error occurred during generation.', 'error');
            }
        } catch (error) {
            showStatus('Network error. Please try again.', 'error');
        } finally {
            // Reset UI Loading State
            submitBtn.disabled = false;
            btnText.textContent = 'Generate Certificates';
            spinner.classList.add('hidden');
        }
    });

    function showStatus(message, type) {
        statusMessage.textContent = message;
        statusMessage.className = `status-message ${type === 'success' ? 'status-success' : 'status-error'} show`;
    }
});
