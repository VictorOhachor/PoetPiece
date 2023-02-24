const navigationLinks = document.querySelectorAll('.app-nav-items > a')


const makeActiveNavItemVisible = () => {
    navigationLinks.forEach(navLink => {
        if (location.href.includes(navLink.href)) {
            if (location.pathname == navLink.pathname) {
                navLink.classList.add('nav-item__active')
            } else {
                const lastChild = navLink.children[1]
                lastChild.classList.add('nav-item__active-parent')
            }
        }
    })
}

const disableUnactiveNavItems = () => {
    navigationLinks.forEach(navLink => {
        if (!navLink.classList.contains('nav-item__active')) {
            navLink.disabled = true
            navLink.style.opacity = 0.6
        }
    })
}

window.addEventListener('load', makeActiveNavItemVisible)
window.addEventListener('load', disableUnactiveNavItems)