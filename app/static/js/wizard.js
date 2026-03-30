/**
 * Multi-step form wizard with smooth transitions and validation.
 */
document.addEventListener('DOMContentLoaded', function () {
    const steps = document.querySelectorAll('.wizard-step');
    const progressItems = document.querySelectorAll('.wizard-progress-item');
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    const submitBtn = document.getElementById('submitBtn');
    let currentStep = 0;

    function showStep(n) {
        // Hide all steps
        steps.forEach(step => {
            step.classList.remove('active');
            step.style.display = 'none';
        });

        // Show current step with animation
        steps[n].style.display = 'block';
        requestAnimationFrame(() => {
            steps[n].classList.add('active');
        });

        // Update progress indicators
        progressItems.forEach((item, index) => {
            item.classList.remove('active', 'completed');
            if (index < n) {
                item.classList.add('completed');
            } else if (index === n) {
                item.classList.add('active');
            }
        });

        // Show/hide buttons
        prevBtn.style.display = n === 0 ? 'none' : 'inline-block';
        if (n === steps.length - 1) {
            nextBtn.style.display = 'none';
            submitBtn.style.display = 'inline-block';
        } else {
            nextBtn.style.display = 'inline-block';
            submitBtn.style.display = 'none';
        }

        currentStep = n;

        // Scroll to top of form
        document.querySelector('.wizard-container').scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    }

    function validateStep(n) {
        const currentFields = steps[n].querySelectorAll('select[required], input[required]');
        let valid = true;

        currentFields.forEach(field => {
            // Remove previous error state
            field.classList.remove('is-invalid');

            if (!field.value || field.value === '') {
                field.classList.add('is-invalid');
                valid = false;
            }

            // Validate number inputs
            if (field.type === 'number') {
                const val = parseFloat(field.value);
                const min = parseFloat(field.min);
                const max = parseFloat(field.max);
                if (isNaN(val) || val < min || val > max) {
                    field.classList.add('is-invalid');
                    valid = false;
                }
            }
        });

        if (!valid) {
            // Shake the step card
            const card = steps[n].closest('.card-custom') || steps[n];
            card.classList.add('shake');
            setTimeout(() => card.classList.remove('shake'), 500);
        }

        return valid;
    }

    // Next button
    if (nextBtn) {
        nextBtn.addEventListener('click', function () {
            if (validateStep(currentStep)) {
                showStep(currentStep + 1);
            }
        });
    }

    // Previous button
    if (prevBtn) {
        prevBtn.addEventListener('click', function () {
            showStep(currentStep - 1);
        });
    }

    // Submit button - validate last step before submit
    if (submitBtn) {
        submitBtn.addEventListener('click', function (e) {
            if (!validateStep(currentStep)) {
                e.preventDefault();
            }
        });
    }

    // Remove invalid class on input change
    document.querySelectorAll('.wizard-step select, .wizard-step input').forEach(field => {
        field.addEventListener('change', function () {
            this.classList.remove('is-invalid');
        });
        field.addEventListener('input', function () {
            this.classList.remove('is-invalid');
        });
    });

    // Initialize
    showStep(0);

    // Auto-dismiss flash messages
    document.querySelectorAll('.alert-dismissible').forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-10px)';
            setTimeout(() => alert.remove(), 300);
        }, 5000);
    });
});
