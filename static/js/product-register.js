document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("product-form");
  form.addEventListener("submit", (e) => {
    const name = form.name.value.trim();
    const price = form.price.value.trim();
    const desc = form.description.value.trim();

    if (!name || !price || !desc) {
      e.preventDefault();
      alert("모든 필드를 입력해주세요.");
      return;
    }

    // 실제 서버에 POST 요청 시에는 여기서 데이터 전송
    console.log("상품명:", name);
    console.log("가격:", price);
    console.log("설명:", desc);
  });
});
