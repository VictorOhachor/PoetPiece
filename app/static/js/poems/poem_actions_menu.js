const moreActionToggler = document.querySelector('#more-action__toggler')
const generateBtn = document.querySelector('#generate-btn')
const copyBtn = document.querySelector('#copy-btn')

moreActionToggler.addEventListener('click', (e) => {
    const moreActionsBox = e.currentTarget.nextElementSibling
    // toggle the hidden class
    moreActionsBox.classList.toggle('hidden')
})

const css = (element, style) => {
    for (const property in style) {
        element.style[property] = style[property];
    }
}

const generatePDF = () => {
    // create a new div element
    const poemPage = document.createElement('div')

    css(poemPage, {
      fontFamily: "'Quicksand', sans-serif",
      color: '#222',
      position: 'relative',
      minHeight: '100vh',
      padding: '2rem 1rem'
    })

    const poemTitle = document.querySelector('.main-content__title')
    const poemDesc = document.querySelector('.poem-desc__content')
    const poemStanzas = document.querySelectorAll('.poem-stanzas__container .poem-stanza__card')
    const appLogo = document.querySelector('.app-logo')

    // append the title and desc to div
    const clonedLogo = appLogo.cloneNode(deep=true)
    const clonedPoemDesc = poemDesc.cloneNode(deep = true)

    // add css styling to them
    css(clonedLogo, {
        color: '#222',
        fontFamily: '"Monoton", cursive',
        fontSize: 'calc(1.5rem + 1.5vmin)',
        padding: '1rem',
        fontWeight: 700
    })

    css(clonedPoemDesc, {
      color: '#222',
      padding: '1rem',
      whiteSpace: 'pre-line',
      fontSize: '1.5rem'
    })

    poemPage.appendChild(clonedLogo)
    poemPage.appendChild(poemTitle.cloneNode(deep = true))
    poemPage.appendChild(clonedPoemDesc)
    poemPage.appendChild(document.createElement('hr'))

    // extract the stanza content from poemStanzas
    const stanzaContainer = document.createElement('div')
    const stanzaContainerStyle = {
        display: 'flex',
        flexDirection: 'column',
        gap: '1rem',
        margin: '1rem .3rem',
        fontSize: '1.5rem',
        color: '#222',
    }

    css(stanzaContainer, stanzaContainerStyle)

    for (const stanza of poemStanzas) {
        const clonedStanza = stanza.cloneNode(deep=true)

        if (clonedStanza.classList.contains('hidden')) {
            clonedStanza.classList.remove('hidden')
        }
        const stanzaContent = clonedStanza.querySelector('.stanza-content')
        // set stanza content style
        css(stanzaContent, {
            whiteSpace: 'pre-line',
            border: '1px solid #3b8ea5',
            padding: '1rem',
            marginTop: '1rem',
            borderRadius: '5px'
        })
        // append to stanza container
        stanzaContainer.appendChild(stanzaContent)
    }

    poemPage.appendChild(stanzaContainer)

    const opt = {
        filename: poemTitle.textContent + '.pdf',
    }
    // toggle the toggler
    moreActionToggler.click()
    // save to pdf and download
    html2pdf().set(opt).from(poemPage).save()
}

const copyPoemLink = (e) => {
    const poemURL = document.querySelector('input[name="poem_url"]')
    const poemLink = window.location.host + poemURL.value

    // const poemLink = location.href
    const btn = e.currentTarget
    const btnText = btn.textContent

    // copy text to clipboard
    navigator.clipboard.writeText(poemLink)
    // change button text to 'copied'
    e.currentTarget.textContent = 'Copied!'
    // return button text to former
    setTimeout(() => {
        btn.innerText = btnText
        // toggle the toggler
        moreActionToggler.click()
    }, 2000)
}

generateBtn && generateBtn.addEventListener('click', generatePDF)
copyBtn && copyBtn.addEventListener('click', copyPoemLink)