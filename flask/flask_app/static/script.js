document.addEventListener("DOMContentLoaded", function() {
    const uploadForm = document.getElementById('uploadForm');
    uploadForm.addEventListener('submit', function(event) {
        event.preventDefault();

        const formData = new FormData(uploadForm);
        const checkboxes = document.querySelectorAll('input[type="checkbox"]');
        const checkboxData = {};

        checkboxes.forEach((checkbox) => {
            checkboxData[checkbox.name] = checkbox.checked;
        });

        formData.append('checkboxData', JSON.stringify(checkboxData));

        fetch('/upload', {
            method: 'POST',
            body: formData
        });
    });
});