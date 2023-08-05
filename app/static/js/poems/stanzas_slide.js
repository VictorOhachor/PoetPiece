const stanzaCards = document.querySelectorAll('.poem-stanzas__container .poem-stanza__card')
const stanzaWhatNumber = document.querySelector('.what-stanza__number #what-number')
const slidePrevBtn = document.querySelector('#slide-backward__btn')
const slideNextBtn = document.querySelector('#slide-forward__btn')


const getPrevStanza = () => {
    const stanzaNumber = +stanzaWhatNumber.textContent
    // Note that stanzaWhatNumber is always 1 + the stanza index
    // in stanzaCards
    const prevStanzaNumber = stanzaNumber > 1 ? stanzaNumber - 1 : stanzaNumber
    // decrement stanzaWhatNumber by 1
    stanzaWhatNumber.textContent = `${prevStanzaNumber}`
    // hide the current stanzaCard
    stanzaCards[stanzaNumber - 1].classList.add('hidden')

    return stanzaCards[prevStanzaNumber - 1]
}

const getNextStanzaNo = () => {
    const stanzaNumber = +stanzaWhatNumber.textContent
    // stanzaWhatNumber textContent is always 1 more than the stanza
    // index in stanzaCards
    const nextStanzaNumber = stanzaNumber != stanzaCards.length ?
        stanzaNumber + 1 : stanzaNumber
    // increment stanzaWhatNumber textContent by 1
    stanzaWhatNumber.textContent = `${nextStanzaNumber}`
    // hide the current stanzaCard
    stanzaCards[stanzaNumber - 1].classList.add('hidden')

    return stanzaCards[nextStanzaNumber - 1]
}

const showStanza = (slideAction) => {
    const allowedSlideActions = new Set(['previous', 'next'])
    // slider commands
    const slideCommands = {
        'previous': getPrevStanza,
        'next': getNextStanzaNo
    }

    const actionFound = allowedSlideActions.has(slideAction)
    
    if (actionFound) {
        const stanzaCard = slideCommands[slideAction]()
        stanzaCard.classList.remove('hidden')
    }
}

window.addEventListener('load', () => showStanza('previous'))
slidePrevBtn.addEventListener('click', () => showStanza('previous'))
slideNextBtn.addEventListener('click', () => showStanza('next'))