window.onload = function() {
  var likeButtons = document.getElementsByClassName("like-btn");
  for (var i = 0; i < likeButtons.length; i++) {
    likeButtons[i].onclick = function() {
      if (this.style.backgroundColor == "pink") {
        this.style.backgroundColor = "#f5f9f8";
        this.textContent = "찜하기"; 
        alert("찜하기를 취소했습니다 💔");
      } else {
        this.style.backgroundColor = "pink";
        this.textContent = "찜"; 
        alert("상품을 찜했습니다 💚");
      }
    };
  }
};
