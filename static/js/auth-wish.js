function checkDuplicate() {
  const userId = document.getElementById('id-input').value;

  if (!userId) {
    alert("ID를 입력하세요!");
    return;
  }

  fetch(`/check_duplicate?id=${userId}`)
    .then(response => response.json())
    .then(data => {
      if (data.exists) {
        alert("이미 존재하는 아이디입니다.");
      } else {
        alert("사용 가능한 아이디입니다!");
      }
    })
    .catch(() => alert("서버 요청 중 오류가 발생했습니다."));
}

function toggleWishlist(itemId, btn){
  fetch(`/toggle_wishlist/${itemId}`, { method: "POST" })
    .then(res => res.json())
    .then(data => {
      if(data.success){
        if(data.wished){
          // 찜 등록 → 버튼 채워진 하트
          btn.classList.add("wished")
        } else {
          // 찜 해제 → 버튼 비운 하트
          btn.classList.remove("wished")
          // 화면에서 바로 제거
          const itemEl = document.getElementById(`item-${itemId}`);
          if(itemEl) itemEl.remove();
        }
      } else {
        alert(data.msg || "오류 발생");
      }
    })
    .catch(()=> alert("서버 요청 실패"))
}

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
        <img src="/static/img/heart-fill.svg" alt="찜" />
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