const notificationMarkers = document.querySelectorAll('.unread-checkbox')

for (const marker of notificationMarkers) {
  marker.addEventListener('click', (e) => {
    e.preventDefault()

    // retrieve data attribute that contains the endpoint to visit in order
    // to mark a notification as read or unread
    const { markEndpoint } = e.currentTarget.dataset
    // visit endpoint
    window.location.pathname = markEndpoint
  })
}