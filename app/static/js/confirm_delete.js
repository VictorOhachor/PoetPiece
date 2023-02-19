const actionLinksGroup = document.querySelectorAll('[class$="action__links"]')

/* Ensure that user confirms a delete operation when the delete button is clicked
    before performing the operation */
actionLinksGroup.forEach(actionLinks => {
    for (const actionLink of actionLinks.children) {
        actionLink.addEventListener('click', (e) => {
            e.preventDefault()

            if (actionLink.textContent.toLowerCase().startsWith('delete')) {
                const href = e.currentTarget.href
                const answer = prompt("Enter 'yes' to confirm action:", 'no')
                
                if (answer.toLowerCase() === 'yes') {
                    location.href = href
                }
            }
        })
    }
})

// TODO: A function that generate a form for the user to confirm deletion
const generateConfirmForm = (href) => {}