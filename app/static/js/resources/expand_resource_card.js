const resourceCards = document.querySelectorAll('.resources-container .resource-card')

resourceCards.forEach(card => {
//   // only allow image resource to be clickable
//   if (card.dataset.rtype != 'IMAGE') {
//     return
//   }
  // make cursor a pointer on desktop based screens
  card.style.cursor = 'zoom-in';

  // create an event handler
  card.addEventListener('click', (event) => {
    // Check if the clicked element is a child of the card
    if (!card.contains(event.target)) {
        return; // Do nothing if the click is on a child element
    }

    const selectedResourceBox = document.querySelector('#selected-resource')
    const clonedCard = card.cloneNode(true)

    // add the expanded class
    clonedCard.classList.add('expanded')
    // clear selecred resource box before appending card
    if (selectedResourceBox.innerHTML) {
      selectedResourceBox.innerHTML = ''
    }
    // append card to the selected box area
    selectedResourceBox.appendChild(document.createElement('hr'))
    selectedResourceBox.appendChild(clonedCard)
    // scroll into view
    selectedResourceBox.scrollIntoView({
      behavior: 'smooth',
      block: 'center',
      inline: 'nearest'
    })
  })

  // remove expanded class after 5 seconds, if it was added due to a card click event
  const removeSelectedResourceBox = () => {
    if (clonedCard.classList.contains('expanded')) {
      selectedResourceBox.innerHTML = ''
    }
  }
})