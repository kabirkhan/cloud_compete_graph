document.addEventListener('prodigyupdate', event => {
    console.log('WINDOW LOADED', event)
    
    var entityMarkPrevText = document.querySelector('mark').previousSibling.innerText.toLowerCase().trim()
    console.log(entityMarkPrevText)
    if (entityMarkPrevText.endsWith('azure')) {
        console.log('PREVIOUS ENDS WITH AZURE')
        var rejectBtn = document.querySelector('button[aria-label="reject (x)"]')
        rejectBtn.click()
    }
});
