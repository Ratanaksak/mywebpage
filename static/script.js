let slideIndex = 0;
showSlides();

function showSlides() {
    let slides = document.querySelectorAll('.slide');
    slideIndex++;
    if (slideIndex > slides.length) {slideIndex = 1}
    document.querySelector('.slides').style.transform = `translateX(-${slideIndex - 1}00%)`; // Adjust slide position
    setTimeout(showSlides, 7000); // Change slide every 4 seconds (4000 milliseconds)
}

//function plusSlides(n) {
//    slideIndex += n;
//    showSlides();
//}
