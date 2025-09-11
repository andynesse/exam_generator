function showPopup(status, message) {
    var popup = document.getElementById('popup-message');
    var popupText = document.getElementById('popup-text');
    popupText.textContent = message;
    popup.classList.remove('popup-success', 'popup-fail');
    if (status === 'success') {
        popup.classList.add('popup-success');
    } else {
        popup.classList.add('popup-fail');
    }
    popup.style.display = 'block';
    sessionStorage.setItem('popupStatus', status);
    sessionStorage.setItem('popupMessage', message);
    setTimeout(function() {
        popup.style.display = 'none';
        sessionStorage.removeItem('popupStatus');
        sessionStorage.removeItem('popupMessage');
    }, 3500);
}

document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('popup-close').onclick = function() {
        var popup = document.getElementById('popup-message');
        popup.style.display = 'none';
        sessionStorage.removeItem('popupStatus');
        sessionStorage.removeItem('popupMessage');
    };
    document.getElementById('pdf-upload-form').onsubmit = function(e) {
        e.preventDefault();
        var formData = new FormData(this);
        fetch('/upload_pdf', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            showPopup(data.status, data.message);
            if (data.status === 'success' && data.filename) {
                // Add new PDF to the select list
                var pdfSelect = document.getElementById('pdf-select');
                if (pdfSelect) {
                    var option = document.createElement('option');
                    option.value = data.pdf_id || '';
                    option.textContent = data.filename;
                    pdfSelect.appendChild(option);
                }
            }
        })
        .catch(() => {
            showPopup('fail', 'An error occurred during upload.');
        });
    };
    var status = sessionStorage.getItem('popupStatus');
    var message = sessionStorage.getItem('popupMessage');
    if (status && message) {
        showPopup(status, message);
    }
});
