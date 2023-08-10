// Select all resource cards
const resourceCards = document.querySelectorAll('.resources-container .resource-card');

// Define the function to handle selecting a resource
const selectResource = (card) => {
    // Find the selected resource box
    const selectedResourceBox = document.querySelector('#selected-resource');

    // Ensure the selectedResourceBox and card are available
    if (!selectedResourceBox || !card) {
        return;
    }

    // Clone the card and add the 'expanded' class
    const clonedCard = card.cloneNode(true);
    clonedCard.classList.add('expanded');

    // Clear the selected resource box content
    selectedResourceBox.innerHTML = '';

    // Append a horizontal line and the cloned card to the selected resource box
    selectedResourceBox.appendChild(document.createElement('hr'));
    selectedResourceBox.appendChild(clonedCard);

    // Scroll the selected resource box into view
    selectedResourceBox.scrollIntoView({
        behavior: 'smooth',
        block: 'center',
        inline: 'nearest'
    });
};

// Attach event listener to each resource card
resourceCards.forEach((card) => {
    // Only allow image resource cards to be clickable
    // Make cursor a pointer on desktop-based screens
    card.style.cursor = 'pointer';

    // Create an event handler for the click event
    const handleClick = (event) => {
        // Check if the click target is the card itself
        if (event.currentTarget === card) {
            selectResource(card);
        }
    };

    // Attach the event listener to the card
    card.addEventListener('click', handleClick);
});
