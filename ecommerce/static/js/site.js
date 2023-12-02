
document.addEventListener('DOMContentLoaded', () => {
    // Get references to the login form and button
    var loginFormContainer = document.getElementById("login-form-container");
    var loginButton = document.getElementById("login-button");

    // Check if the login button exists
    if (loginButton) {
        // Show the login form when the button is clicked
        loginButton.addEventListener("click", function (event) {
            event.preventDefault();
            loginFormContainer.style.display = "block";
        });
    }

    const productsContainer = document.querySelector('.products-container');
    const scrollLeftButton = document.querySelector('.scroll-button.left');
    const scrollRightButton = document.querySelector('.scroll-button.right');
    const scrollAmount = 10; // Adjust this value for the desired scroll speed
    const maxWidth = 700;
    
    scrollLeftButton.style.display = 'none'; // Initially hide the left-scroll button
    
    function animateScroll(scrollTo) {
        const currentScroll = productsContainer.scrollLeft;
        const difference = scrollTo - currentScroll;
        const step = Math.sign(difference) * scrollAmount;
        
    
        console.log(`Current Scroll: ${currentScroll}`);
        console.log(`Scroll To: ${scrollTo}`);
        console.log(`Difference: ${difference}`);
        console.log(`Step: ${step}`);
    
        if (Math.abs(difference) <= Math.abs(step)) {
            productsContainer.scrollLeft = scrollTo;
        } else {
            productsContainer.scrollLeft += step;
    
            // Adjust the scroll direction based on scrollTo and currentScroll
            if (scrollTo < currentScroll && step > 0 ) {
                productsContainer.scrollLeft = scrollTo;
            } else if (scrollTo > currentScroll && step < 0) {
                productsContainer.scrollLeft = scrollTo;
            } else {
                requestAnimationFrame(() => animateScroll(scrollTo));
            }
        }
    }
    
    
    
    productsContainer.addEventListener('scroll', () => {
        if (productsContainer.scrollLeft > 0) {
            scrollLeftButton.style.display = 'flex'; // Show the left-scroll button
        } else {
            scrollLeftButton.style.display = 'none'; // Hide the left-scroll button
        }
    });
    
    scrollLeftButton.addEventListener('click', () => {
        const scrollTo = productsContainer.scrollLeft - 235; // Adjust the scroll distance as needed
        animateScroll(scrollTo);
    });
    
    scrollRightButton.addEventListener('click', () => {
        if (productsContainer.scrollLeft < maxWidth) {
        const scrollTo = productsContainer.scrollLeft + 235; // Adjust the scroll distance as needed
        animateScroll(scrollTo);
        }
    });
    

});
