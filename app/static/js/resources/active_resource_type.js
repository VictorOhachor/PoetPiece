const resourceTypes = document.querySelectorAll('.resource-types .resource-type')

const makeResourceTypeActive = () => {
  const queryString = window.location.search
  const params = new URLSearchParams(queryString)
  // get "type" param
  const type = params.get('type')
  if (!type) {
    resourceTypes[0].classList.add('resource-type__active')
    return
  }

  for (const r_type of resourceTypes) {
    if (r_type.id.toLowerCase() == type.toLowerCase()) {
      r_type.classList.add('resource-type__active')
      break
    }
  }
}

window.addEventListener('load', makeResourceTypeActive)