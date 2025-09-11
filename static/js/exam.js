document.addEventListener('DOMContentLoaded', function() {
    var createExamForm = document.getElementById('create-exam-form');
    if (createExamForm) {
        createExamForm.onsubmit = function(e) {
            e.preventDefault();
            var examName = document.getElementById('exam-name').value;
            var pdfSelect = document.getElementById('pdf-select');
            var selected = Array.from(pdfSelect.selectedOptions).map(opt => opt.value);
            fetch('/create_exam', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({exam_name: examName, pdf_ids: selected})
            })
            .then(response => response.json())
            .then(data => {
                if (typeof showPopup === 'function') {
                    showPopup(data.status, data.message);
                }
                if (data.status === 'success') {
                    setTimeout(() => window.location.reload(), 1500);
                }
            })
            .catch(() => {
                if (typeof showPopup === 'function') {
                    showPopup('fail', 'An error occurred while creating the exam.');
                }
            });
        };
    }
});
