function previewLink(url, timeoutMillis = 5000) {
    return new Promise((resolve, reject) => {
        // Handle timeout
        const timeoutId = setTimeout(() => {
            reject(new Error('Request timed out'));
        }, timeoutMillis);

        // Fetch the URL
        fetch(url)
            .then(response => response.text())
            .then(html => {
                clearTimeout(timeoutId); // Clear the timeout

                const parser = new DOMParser();
                const soup = parser.parseFromString(html, 'text/html');

                const result = {
                    'title': extractMetaItem(soup, 'title'),
                    'description': extractMetaItem(soup, 'description'),
                    'image': extractMetaItem(soup, 'image')
                };

                if (result.title || result.description || result.image) {
                    resolve(result);
                } else {
                    reject(new Error('No metadata found'));
                }
            })
            .catch(error => {
                clearTimeout(timeoutId); // Clear the timeout
                reject(error);
            });
    });
}

function extractMetaItem(soup, name) {
    const metaTag = soup.querySelector(`meta[name="${name}"], meta[property="${name}"]`);
    return metaTag ? metaTag.getAttribute('content') : null;
}


window.addEventListener('DOMContentLoaded', async (e) => {
    const resources = document.querySelectorAll('.resource-card')

    for (const resource of resources) {
        const rtype = resource.dataset.rtype

        if (rtype === 'LINK') {
            const resourceURL = resource.querySelector(
                '.resource-link-summary .link-resource a').href

            if (!resourceURL) {
                continue;
            }

            // fetch data from url
            try {
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
            } catch (e) {
                console.error(e.message);
            }
        }
    }
})