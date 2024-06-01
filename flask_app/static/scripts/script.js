document.addEventListener("DOMContentLoaded", function() {
    const uploadForm = document.getElementById('uploadForm');
    uploadForm.addEventListener('submit', function(event) {
        event.preventDefault();

        const formData = new FormData(uploadForm);
        const checkboxes = document.querySelectorAll('input[type="checkbox"]');
        const params = document.querySelectorAll('input[type="text"]')
        const inputBoxSelector = document.querySelector('select[id="sex"]');
        const checkboxData = {};
        const paramsData = {}

        checkboxes.forEach((checkbox) => {
            checkboxData[checkbox.name] = checkbox.checked;
        });

        params.forEach((parameter) => {
            paramsData[parameter.name] = parameter.value
        })
        paramsData["sex"] = inputBoxSelector.value;

        formData.append('checkboxData', JSON.stringify(checkboxData));
        formData.append('paramsData', JSON.stringify(paramsData));
        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (response.redirected) {
                window.location.href = response.url;
            }
            else{
                return response.text();
            }
        })
        .then(data => {
            console.log(data);
        })
        .catch(error => {
            console.error('Error:', error);
        });
    });
});
