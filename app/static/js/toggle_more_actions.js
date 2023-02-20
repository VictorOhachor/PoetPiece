const moreActionToggler = document.querySelector('#more-action__toggler')
const generateBtn = document.querySelector('#generate-btn')
const copyBtn = document.querySelector('#copy-btn')

moreActionToggler.addEventListener('click', (e) => {
    const moreActionsBox = e.currentTarget.nextElementSibling
    // toggle the hidden class
    moreActionsBox.classList.toggle('hidden')
})

const generatePDF = () => {
    const poemTitle = document.querySelector('.main-content__title')
    const poemDesc = document.querySelector('.poem-desc')
    const poemStanzas = document.querySelector('.poem-stanzas')

    // create a new div element
    const poemPage = document.createElement('div')

    // append the title, desc, and stanzas to div
    poemPage.appendChild(poemTitle.cloneNode(deep=true))
    poemPage.appendChild(poemDesc.cloneNode(deep=true))
    poemPage.appendChild(poemStanzas.cloneNode(deep=true))

    const opt = {
        filename: poemTitle.textContent + '.pdf',
        html2canvas: {scale: 1}
    }
    // toggle the toggler
    moreActionToggler.click()
    // save to pdf and download
    html2pdf().set(opt).from(poemPage).toPdf().save()
}

const copyPoemLink = (e) => {
    const poemLink = location.href
    const btn = e.currentTarget
    const btnText = btn.textContent

    // copy text to clipboard
    navigator.clipboard.writeText(poemLink)
    // change button text to 'copied'
    e.currentTarget.textContent = 'Copied!'
    // return button text to former
    setTimeout(() => {
        console.log(btnText)
        btn.innerText = btnText
    }, 2000)
}

generateBtn && generateBtn.addEventListener('click', generatePDF)
copyBtn && copyBtn.addEventListener('click', copyPoemLink)