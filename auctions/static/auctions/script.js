document.addEventListener('DOMContentLoaded', () => {
    let page = 2;
    let isLoading = false;

    const listingContainer = document.getElementById('listing-container');
    const loader = document.getElementById('loader'); 

    window.onscroll = async () => {
        if (window.innerHeight + window.scrollY >= document.body.offsetHeight) {
            await loadMore();
        }
    };

    const loadMore = async () => {
        if (isLoading) return; // Prevent multiple calls
        isLoading = true;
        loader.style.display = "block"; // Show loader during the request

        try {
            const response = await fetch(`/load-listings?page=${page}`);
            if (!response.ok) throw new Error("Failed to load listings");

            const { has_more, html } = await response.json(); 
            listingContainer.insertAdjacentHTML("beforeend", html);

            page++;
            isLoading = false;
            loader.style.display = "none";

            // Stop loading if no more data exists
            if (!has_more) {
                loader.style.display = "block";
                loader.textContent = "No more listings!";
                window.onscroll = null; // Disable further scrolling
            }
        } catch (error) {
            console.error(error);
            loader.textContent = "Failed to load more listings.";
            isLoading = false;
        }
    };
});

