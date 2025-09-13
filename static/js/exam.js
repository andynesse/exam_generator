// No JS needed for exam creation: form submits as regular POST and is handled by Flask backend.

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('exam-form');
    if (!form) return;
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        // Display correct answers under each question as a bullet list
        document.querySelectorAll('.question-block').forEach(block => {
            const correct = block.getAttribute('data-correct');
            let answerDiv = block.querySelector('.user-answer');
            if (!answerDiv) {
                answerDiv = document.createElement('div');
                answerDiv.className = 'user-answer';
                block.appendChild(answerDiv);
            }
            if (correct) {
                const correctArr = JSON.parse(correct);
                if (Array.isArray(correctArr)) {
                    if (correctArr.length) {
                        answerDiv.innerHTML = `<strong>Correct answers:</strong><ul class='correct-list'>${correctArr.map(a => `<li>${a}</li>`).join('')}</ul>`;
                    } else {
                        answerDiv.innerHTML = `<strong>Correct answers:</strong> <em>None</em>`;
                    }
                } else {
                    answerDiv.innerHTML = `<strong>Correct answer:</strong> <ul class='correct-list'><li>${correctArr}</li></ul>`;
                }
            } else {
                answerDiv.innerHTML = `<strong>Correct answer:</strong> <em>None</em>`;
            }
        });
    });
});
