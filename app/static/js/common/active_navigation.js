const navigationLinks = document.querySelectorAll('.app-nav-items > a')


const makeActiveNavItemVisible = () => {
    let activeNavLinks = []
    let exact = false

    for (const navLink of navigationLinks) {
        if (location.href.includes(navLink.href)) {
            if (location.pathname === navLink.pathname) {
                exact = true
                navLink.classList.add('nav-item__active')
                break
            }
            activeNavLinks.push(navLink)
        }
    }

    if (!exact && activeNavLinks.length) {
        activeNavLinks[0].classList.add('nav-item__active')
    }
}

window.addEventListener('load', makeActiveNavItemVisible)