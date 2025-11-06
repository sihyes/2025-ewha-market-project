window.onload = function() {
  var likeButtons = document.getElementsByClassName("like-btn");

  for (var i = 0; i < likeButtons.length; i++) {
    likeButtons[i].onclick = function() {
      var itemId = this.dataset.itemId; // ★ 버튼에 data-item-id 속성 필요
      var btn = this;

      // 🔹 서버에 찜 상태 토글 요청
      fetch(`/toggle_wishlist/${itemId}`, { method: "POST" })
        .then(res => res.json())
        .then(data => {
          if (data.success) {
            if (data.wished) {
              // 🔸 서버에서 "찜 등록" 성공
              btn.style.backgroundColor = "pink";
              btn.textContent = "찜";
              alert("상품을 찜했습니다 💚");
            } else {
              // 🔸 서버에서 "찜 해제" 성공
              btn.style.backgroundColor = "#f5f9f8";
              btn.textContent = "찜하기";
              alert("찜하기를 취소했습니다 💔");

              // (선택) 찜 목록 화면에서는 바로 제거
              const itemEl = document.getElementById(`item-${itemId}`);
              if (itemEl) itemEl.remove();
            }
          } else {
            alert(data.msg || "오류가 발생했습니다.");
          }
        })
        .catch(() => alert("서버 요청 실패 😢"));
    };
  }
};
