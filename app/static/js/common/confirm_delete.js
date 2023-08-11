const actionLinksGroup = document.querySelectorAll('[class$="action__links"]')

/* [Temporary] Ensure that user confirms a delete operation when the delete button is clicked
    before performing the operation */
actionLinksGroup.forEach(actionLinks => {
    for (const actionLink of actionLinks.children) {
        console.log(actionLink.dataset?.action);
        actionLink.addEventListener('click', (e) => {
            if (actionLink.textContent?.toLowerCase().startsWith('delete') ||
                actionLink.dataset?.action?.startsWith('delete')) {
                e.preventDefault()

                const href = e.currentTarget.href
                const answer = prompt("Enter 'yes' to confirm action:", 'no')

                if (answer?.toLowerCase() === 'yes') {
                    location.href = href
                }
            }
        })
    }
})

// TODO: A function that generate a form for the user to confirm deletion
// Form must be positioned fixed and must request that user enters 'yes' to confirm delete
const generateConfirmForm = (href) => { }