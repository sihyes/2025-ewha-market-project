function setRating(rating) {
    document.getElementById('review-rating-value').value = rating;
    const stars = document.querySelectorAll('.star-btn');
    stars.forEach((star, index) => {
        star.classList.toggle('selected', index < rating);
    });
}
function previewImage(event) {
    const file = event.target.files[0];
    const preview = document.getElementById('image-preview');

    if (file) {
        const reader = new FileReader();
        reader.onload = function (e) {
            preview.src = e.target.result;
            preview.style.display = 'block';
        };
        reader.readAsDataURL(file);
    }
    else {
        preview.src = '';
        preview.style.display = 'none';
    }
}