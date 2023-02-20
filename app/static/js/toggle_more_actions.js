const moreActionToggler = document.querySelector('#more-action__toggler')
const generateBtn = document.querySelector('.generate-pdf')

moreActionToggler.addEventListener('click', (e) => {
    const moreActionsBox = e.currentTarget.nextElementSibling
    // toggle the hidden class
    moreActionsBox.classList.toggle('hidden')
})

const generatePDF = () => {
    const poemPage = document.querySelector('.app-main__content')
    const opt = {
        filename: document.querySelector('.main-content__title')
            .textContent + '.pdf',
        html2canvas: {scale: 1}
    }
    // toggle the toggler
    moreActionToggler.click()

    if (poemPage) {
        html2pdf().set(opt).from(poemPage).toPdf().save()
    } else {
        alert('Something went wrong!')
    }
}

generateBtn && generateBtn.addEventListener('click', generatePDF)