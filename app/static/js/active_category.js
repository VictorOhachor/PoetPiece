const categoriesNames = document.querySelectorAll('.all-categories__name .category-name');
const paginationLinks = document.querySelectorAll('.pagination-container a');

const windowParams = new Proxy(new URLSearchParams(window.location.search), {
    get: (searchParams, prop) => searchParams.get(prop),
});

window.addEventListener('load', () => {
    for (const categoryName of categoriesNames) {
        // parse search string
        const categoryParams = new Proxy(new URLSearchParams(categoryName.search), {
            get: (searchParams, prop) => searchParams.get(prop),
        });

        if (location.pathname === categoryName.pathname &&
            windowParams.category === categoryParams.category
        ) {
            categoryName.style.borderBottom = '3px solid rgb(145, 21, 21)';
            categoryName.style.color = '#000';
        }
    }
})


for (const link of paginationLinks) {
    link.addEventListener('click', (e) => {
        if (windowParams.category &&
            !e.currentTarget.href.includes(`category=${windowParams.category}`)
        ) {
            e.preventDefault()

            const updatedUrl = `${e.currentTarget.href}&category=${windowParams.category}`
            location.href = updatedUrl
        }
    })
}