const reviewData = [
    {
        id: 1,
        title: "부드럽게 잘 발려요!", 
        writer: "김테스터",
        rating: 4, 
        content: "색상이 너무 예쁘고 촉촉해서 좋아요. 끈적임이 심하지 않고 부드럽게 잘 발립니다. 재구매 의사 있습니다!", 
        image: "static/img/review_lipgloss.jpg", 
        productName: "워터 틴트 립글로스 #코랄" 
    },
    {
        id: 2,
        title: "책 상태가 좋습니다", 
        writer: "박컴플레인",
        rating: 4,
        content: "필요했던 책인데 상태가 깔끔해서 만족합니다. 판매자님이 친절하세요. 다만 배송이 하루 늦어서 아쉬워요.",
        image: "static/img/review_book.jpg", 
        productName: "자바스크립트 바이블"
    },
    {
        id: 3,
        title: "꽤 시원해요!", 
        writer: "abc1234", 
        rating: 3,
        content: "생각보다 시끄럽지 않고 시원하네요! 휴대성이 좋아서 잘 사용 중입니다.\n다만 기기에 기스가 잘 생기는 게 아쉬워서 1점 깎았습니다", 
        image: "static/img/review_fan.jpg", 
        productName: "windpia 핸디 선풍기"
    }
];

function getStarRating(rating) {
    const fullStar = '★'.repeat(rating);
    const emptyStar = '☆'.repeat(5 - rating);
    return `${fullStar}${emptyStar}`;
}

function loadReviewList() {
    const container = document.getElementById('review-list-container');
    const countElement = document.getElementById('review-count');
    if (!container || !countElement) return;

    countElement.textContent = `${reviewData.length}개`;

    reviewData.forEach(review => {
        const card = document.createElement('div');
        card.className = 'review-card';
        card.onclick = () => {
            window.location.href = DETAIL_URL_PATTERN; 
        };
        card.innerHTML = `
            <img src="/${review.image}" alt="${review.title} 이미지" class="review-card-img">
            <div class="review-card-info">
                <h4>제목: ${review.title}</h4>
                <p>평점: ${getStarRating(review.rating)}</p>
            </div>
        `;
        container.appendChild(card);
    });
}

function loadReviewDetail() {
    const pathSegments = window.location.pathname.split('/');
    const reviewId = parseInt(pathSegments[pathSegments.length - 1]); 
    const review = reviewData.find(r => r.id === reviewId);
    
    if (review) {
        document.getElementById('detail-product-name').textContent = review.productName;
        document.getElementById('detail-title').textContent = review.title;
        document.getElementById('detail-rating').textContent = getStarRating(review.rating);
        document.getElementById('detail-image').src = `/${review.image}`; 
        document.getElementById('detail-image').alt = review.title;
        document.getElementById('detail-content').textContent = review.content;
        document.getElementById('detail-writer-id').textContent = review.writer;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const path = window.location.pathname;

    if (path === '/review-list') { 
        loadReviewList();
    } else if (path.includes('/detailed-review/')) {
        loadReviewDetail();
    }
});