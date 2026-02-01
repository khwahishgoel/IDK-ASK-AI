const fileInput = document.getElementById('fileInput');
const fileInfo = document.getElementById('fileInfo');
const fileName = document.getElementById('fileName');
const removeFile = document.getElementById('removeFile');
const convertBtn = document.getElementById('convertBtn');
const loading = document.getElementById('loading');
const results = document.getElementById('results');
const convertedText = document.getElementById('convertedText');
const copyBtn = document.getElementById('copyBtn');
const errorMsg = document.getElementById('errorMsg');

let selectedFile = null;

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleFile(e.target.files[0]);
    }
});

function handleFile(file) {
    selectedFile = file;
    fileName.textContent = file.name;
    fileInfo.style.display = 'flex';
    convertBtn.disabled = false;
    hideError();
    results.style.display = 'none';
}

if (removeFile) {
    removeFile.addEventListener('click', () => {
        selectedFile = null;
        fileInput.value = '';
        fileInfo.style.display = 'none';
        convertBtn.disabled = true;
        results.style.display = 'none';
    });
}

if (convertBtn) {
    convertBtn.addEventListener('click', async () => {
        if (!selectedFile) return;

        convertBtn.disabled = true;
        loading.style.display = 'block';
        results.style.display = 'none';
        hideError();

        const formData = new FormData();
        formData.append('file', selectedFile);

        try {
            const response = await fetch('/convert', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (data.success) {
                convertedText.textContent = data.converted;
                results.style.display = 'block';
            } else {
                showError(data.error || 'something went wrong fr');
            }
        } catch (err) {
            showError('network error bestie, try again');
        } finally {
            loading.style.display = 'none';
            convertBtn.disabled = false;
        }
    });
}

if (copyBtn) {
    copyBtn.addEventListener('click', () => {
        navigator.clipboard.writeText(convertedText.textContent).then(() => {
            const originalText = copyBtn.textContent;
            copyBtn.textContent = 'copied! ';
            setTimeout(() => {
                copyBtn.textContent = originalText;
            }, 2000);
        });
    });
}

function showError(message) {
    if (errorMsg) {
        errorMsg.textContent = message;
        errorMsg.style.display = 'block';
    }
}

function hideError() {
    if (errorMsg) {
        errorMsg.style.display = 'none';
    }
}