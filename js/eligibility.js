document.addEventListener('DOMContentLoaded', () => {
    const checkBtn = document.getElementById('check-eligibility-btn');
    const form = document.getElementById('eligibility-form');
    const resultSection = document.getElementById('result-section');
    const resultContent = document.getElementById('result-content');

    if (checkBtn) {
        checkBtn.addEventListener('click', (e) => {
            e.preventDefault();
            checkEligibility();
        });
    }

    function checkEligibility() {
        // Exclusion Questions IDs
        const exclusions = [
            'vehicle',
            'equipment',
            'kcc',
            'gov-job',
            'income',
            'tax',
            'assets'
        ];

        let isExcluded = false;
        let reasons = [];

        // Check all inputs
        exclusions.forEach(id => {
            const yesOption = document.querySelector(`input[name="${id}"][value="yes"]`);
            if (yesOption && yesOption.checked) {
                isExcluded = true;
                // Get the label text for the reason
                const questionText = yesOption.closest('.question-group').querySelector('label').textContent;
                reasons.push(questionText);
            }
        });

        // Display Result
        displayResult(isExcluded, reasons);
    }

    function displayResult(isExcluded, reasons) {
        // Hide Form
        form.classList.add('hidden');
        resultSection.classList.remove('hidden');

        if (isExcluded) {
            // Not Eligible Result
            resultContent.innerHTML = `
                <div class="result-card warning">
                    <div class="icon-box"><ion-icon name="alert-circle"></ion-icon></div>
                    <h3>Likely Not Eligible</h3>
                    <p>Based on the PM-JAY exclusion criteria, you may not qualify for the scheme because:</p>
                    <ul class="reason-list">
                        ${reasons.map(r => `<li>${r}</li>`).join('')}
                    </ul>
                    <div class="actions">
                        <button onclick="location.reload()" class="btn btn-secondary">Check Another</button>
                        <a href="chat.html" class="btn btn-primary">Ask AI for Help</a>
                    </div>
                </div>
            `;
        } else {
            // Likely Eligible Result
            resultContent.innerHTML = `
                <div class="result-card success">
                    <div class="icon-box"><ion-icon name="checkmark-circle"></ion-icon></div>
                    <h3>You May Be Eligible!</h3>
                    <p>You do not meet any of the standard exclusion criteria. Your family might be listed in the SECC 2011 database.</p>
                    
                    <div class="next-steps">
                        <h4>Next Steps:</h4>
                        <ol>
                            <li>Visit your nearest <strong>Common Service Center (CSC)</strong>.</li>
                            <li>Carry your <strong>Ration Card</strong> and <strong>Aadhar Card</strong>.</li>
                            <li>Ask the operator to check your name in the <strong>PM-JAY list</strong>.</li>
                        </ol>
                    </div>

                    <div class="actions">
                        <a href="hospitals.html" class="btn btn-primary">Find Hospital</a>
                        <button onclick="location.reload()" class="btn btn-secondary">Check Again</button>
                    </div>
                </div>
            `;
        }
    }
});
