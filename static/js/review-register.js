function setRating(rating) {
    const ratingInput = document.getElementById('review-rating-value');
    if (ratingInput) ratingInput.value = rating;

    const stars = document.querySelectorAll('.star-btn');
    stars.forEach((star) => {
        const starValue = parseInt(star.getAttribute('data-rating'));
        if (starValue <= rating) {
            star.style.color = 'gold'; // 활성화 색상
        } else {
            star.style.color = 'gray'; // 비활성화 색상
        }
    });
}

function handleReviewSubmit(e) {
    e.preventDefault();
    const title = document.getElementById('review-title').value;
    const main = document.querySelector('main');
    const messageBox = document.createElement('div');

    messageBox.style.cssText = 'position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); background: #d4edda; color: #155724; padding: 20px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.2); z-index: 1000; text-align: center;';
    messageBox.innerHTML = `<h4>등록 완료</h4><p>"${title}" 리뷰가 성공적으로 등록되었습니다!</p>`;
    main.appendChild(messageBox);

    setTimeout(() => {
        messageBox.remove();
        document.getElementById('review-form').reset();
        setRating(5); 
    }, 1500);
}

document.addEventListener('DOMContentLoaded', () => {
    setRating(5);
    const reviewForm = document.getElementById('review-form');
    if (reviewForm) {
        reviewForm.addEventListener('submit', handleReviewSubmit);
    }
});