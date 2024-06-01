document.addEventListener("DOMContentLoaded", function() {
    const uploadForm = document.getElementById('uploadData');
    uploadForm.addEventListener('submit', function(event) {
        event.preventDefault();

        const formData = new FormData(uploadForm);
        const inputBoxSelector = document.querySelector('select[id="sex"]')
        const inputBoxes = document.querySelectorAll('input[type="text"]');
        const inputBoxDatas = {};

        inputBoxes.forEach((inputBox) => {
            inputBoxDatas[inputBox.name] = inputBox.value;
        });
        inputBoxDatas[inputBoxSelector.name] = inputBoxSelector.value
        formData.append('inputBoxDatas', JSON.stringify(inputBoxDatas));

        fetch('/input-data', {
            method: 'POST',
            body: formData
        });
    });
});