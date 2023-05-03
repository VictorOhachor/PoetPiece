function extractMetaItem(soup, property) {
  // Extract a property from the Open Graph metadata of the given soup.
  let result = soup.querySelector(`meta[property="og:${property}"]`);
  if (!result) {
    // Try extracting from regular metadata instead.
    result = soup.querySelector(`meta[name="${property}"]`);
  }
  return result ? result.getAttribute('content') : '';
}

function previewLink(url) {
  // Get some metadata from a given URL.
  return fetch(url, { timeout: 1000 })
    .then(response => response.text())
    .then(html => {
      let parser = new DOMParser();
      let soup = parser.parseFromString(html, 'text/html');

      let result = {
        'title': extractMetaItem(soup, 'title'),
        'description': extractMetaItem(soup, 'description'),
        'image': extractMetaItem(soup, 'image')
      };

      if (result.title && result.description && result.image) {
        return result;
      }
    })
    .catch(error => {
      return null
    });
}

window.addEventListener('DOMContentLoaded', async (e) => {
  const resources = document.querySelectorAll('.resource-card')

  for (const resource of resources) {
    const rtype = resource.dataset.rtype
    
    if (rtype === 'LINK') {
      const resourceURL = resource.querySelector(
        '.resource-link-summary .link-resource a').href
      
      // fetch data from url
      const previewData = await previewLink(resourceURL)
      if (previewData) {
        const resourcePreview = document.querySelector('.resource-preview')
        const linkSummary = document.querySelector('.resource-link-summary')

        linkSummary.classList.add('hidden')
        resourcePreview.classList.remove('hidden')

        // populate resource preview for image
        const img = resourcePreview.querySelector('img')
        img.src = previewData.image
        img.alt = previewData.title

        // populate resource preview for title
        const title = resourcePreview.querySelector('.title')
        title.textContent = previewData.title

        // populate resource preview for description
        const desc = resourcePreview.querySelector('.description')
        desc.textContent = previewData.description
      }
    }
  }
})