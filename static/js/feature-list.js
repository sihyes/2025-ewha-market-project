window.onload = function() {
  var likeButtons = document.getElementsByClassName("like-btn");

  if (typeof wishedItems !== "undefined" && Array.isArray(wishedItems)) {
    for (var i = 0; i < likeButtons.length; i++) {
      var btn = likeButtons[i];
      var itemId = btn.dataset.itemId;

      if (wishedItems.includes(itemId)) {
        btn.style.backgroundColor = "pink";
        btn.textContent = "찜";
      }
    }
  }

  for (var i = 0; i < likeButtons.length; i++) {
    likeButtons[i].onclick = function() {
      var itemId = this.dataset.itemId; // ★ 버튼에 data-item-id 속성 필요
      var btn = this;

      fetch(`/toggle_wishlist/${itemId}`, { method: "POST" })
        .then(res => res.json())
        .then(data => {
          if (data.success) {
            if (data.wished) {
              btn.style.backgroundColor = "pink";
              btn.textContent = "찜";
            } else {
              btn.style.backgroundColor = "#f5f9f8";
              btn.textContent = "찜하기";
            }
          } else {
            alert(data.msg || "오류가 발생했습니다.");
          }
        })
        .catch(() => alert("서버 요청 실패 😢"));
    };
  }
};