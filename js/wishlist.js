document.addEventListener('DOMContentLoaded', function() {
  const wishlistContainer = document.getElementById('wishlistContainer');
  const wishlist = JSON.parse(localStorage.getItem('wishlist')) || [];

  if (wishlist.length === 0) {
    wishlistContainer.innerHTML = '<p>찜한 상품이 없습니다 😢</p>';
    return;
  }

  wishlist.forEach(item => {
    const card = document.createElement('div');
    card.classList.add('wishlist-item');
    card.innerHTML = `
      <img src="${item.image}" alt="${item.name}" />
      <div class="item-info">
        <p class="item-name">${item.name}</p>
        <p class="item-price">${item.price} 원</p>
      </div>
      <button class="wishlist-btn" data-name="${item.name}">
        <img src="{{ url_for('static', filename='img/heart-fill.svg') }}" alt="찜" />
      </button>
    `;
    wishlistContainer.appendChild(card);
  });

  // 찜 해제
  document.querySelectorAll('.wishlist-btn').forEach(btn => {
    btn.addEventListener('click', function() {
      const name = this.dataset.name;
      const updated = wishlist.filter(item => item.name !== name);
      localStorage.setItem('wishlist', JSON.stringify(updated));
      location.reload();
    });
  });
});