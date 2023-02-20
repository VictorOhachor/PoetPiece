const moreActionToggler = document.querySelector('#more-action__toggler')

moreActionToggler.addEventListener('click', (e) => {
    const moreActionsBox = e.currentTarget.nextElementSibling
    // toggle the hidden class
    moreActionsBox.classList.toggle('hidden')
})