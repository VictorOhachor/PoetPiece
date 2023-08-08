const stanzaCards = document.querySelectorAll('.poem-stanzas__container .poem-stanza__card')
const stanzaWhatNumber = document.querySelector('.what-stanza__number #what-number')
const slidePrevBtn = document.querySelector('#slide-backward__btn')
const slideNextBtn = document.querySelector('#slide-forward__btn')


const getPrevStanza = () => {
    const stanzaNumber = +stanzaWhatNumber.textContent
    // Note that stanzaWhatNumber is always 1 + the stanza index in stanzaCards
    let prevStanzaNumber = 0;

    console.log(stanzaCards);

    if (stanzaCards.length > 0) {
        prevStanzaNumber = stanzaNumber > 1 ? stanzaNumber - 1 : stanzaNumber;

        // hide the current stanzaCard
        stanzaCards[stanzaNumber - 1].classList.add('hidden');
    }

    // decrement stanzaWhatNumber by 1
    stanzaWhatNumber.textContent = `${prevStanzaNumber}`;

    return stanzaCards.length > 0 ? stanzaCards[prevStanzaNumber - 1] : null;
}

const getNextStanzaNo = () => {
    const stanzaNumber = +stanzaWhatNumber.textContent
    // stanzaWhatNumber textContent is always 1 more than the stanza index in stanzaCards
    let nextStanzaNumber = 0;

    if (stanzaCards.length > 0) {
        nextStanzaNumber = stanzaNumber != stanzaCards.length ? stanzaNumber + 1 : stanzaNumber
        
        // increment stanzaWhatNumber textContent by 1
        stanzaWhatNumber.textContent = `${nextStanzaNumber}`
        // hide the current stanzaCard
        stanzaCards[stanzaNumber - 1].classList.add('hidden')
    
        return stanzaCards[nextStanzaNumber - 1]
    }

    return null;
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

        if (stanzaCard) {
            stanzaCard.classList.remove('hidden')
        }
    }
}

window.addEventListener('load', () => showStanza('previous'))
slidePrevBtn.addEventListener('click', () => showStanza('previous'))
slideNextBtn.addEventListener('click', () => showStanza('next'))