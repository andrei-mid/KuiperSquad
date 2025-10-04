
// Select the button and the star elements
const button = document.getElementById('startAnimation');
const spans = document.querySelectorAll('section span');
const heaterText = document.getElementById('titlu1');
const delay = ms => new Promise(resolve => setTimeout(resolve, ms));

// Function to stop existing star animations
function stopStarAnimations() {
    spans.forEach(span => {
        span.classList.add('stopped-animation');
    });
}

function startButtonFadeOut() {
    button.classList.add('animate'); // Apply the fade-out animation
    // Optionally, hide the button
    button.classList.add('hidden');
}

function startTitleAnimation() {
    heaterText.classList.add('fade-out');
    heaterText.classList.add('hidden');
}

button.addEventListener('click', async function() {
    stopStarAnimations();
    startButtonFadeOut();
    startTitleAnimation();
    
    await delay(2000); // Delay to allow the button and text fade out animations to start
    
    heaterText.textContent = 'Your journey begins here';
    heaterText.classList.remove('fade-out');
    heaterText.classList.add('fade-in');
    
    await delay(1500); 

    heaterText.classList.remove('fade-in');
    heaterText.classList.add('fade-out');

    await delay(1500); 
    
    heaterText.textContent = 'Are you ready to be amazed?';
    heaterText.classList.remove('fade-out');
    heaterText.classList.add('fade-in');

    await delay(1500); 

    heaterText.classList.remove('fade-in');
    heaterText.classList.add('fade-out');
    
    await delay(1500); // Wait for text to fade out before changing again
    
    heaterText.classList.remove('fade-out');
    heaterText.textContent = 'This is the beginng';
    heaterText.classList.add('fade-in');

    await delay(1500);

    window.location.href = "../html/index.html";
});

// To ensure that text changes occur in sequence
heaterText.addEventListener('animationend', () => {
    if (heaterText.classList.contains('fade-out')) {
        // Trigger additional animations or actions if needed
    }
});

let logoApasat = document.getElementById('logodiv');

logoApasat.addEventListener("click", () => {
    window.location.href = "../html/index.html";
});
