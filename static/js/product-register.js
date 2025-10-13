// product-register.js
document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("product-form");
  const imageUrlInput = form.querySelector('input[name="image_url"]');
  const imageFileInput = form.querySelector('input[name="image_file"]');

  // 이미지 미리보기 요소 생성
  const preview = document.createElement("img");
  preview.style.maxWidth = "200px";
  preview.style.display = "block";
  preview.style.marginTop = "10px";
  imageFileInput.parentNode.appendChild(preview);

  // 이미지 미리보기 업데이트 함수
  function updatePreview() {
    const url = imageUrlInput.value.trim();
    const file = imageFileInput.files[0];

    if (url) {
      // URL이 있으면 URL 우선
      preview.src = url;
    } else if (file) {
      // 파일이 있으면 파일 표시
      const reader = new FileReader();
      reader.onload = function (event) {
        preview.src = event.target.result;
      };
      reader.readAsDataURL(file);
    } else {
      preview.src = "";
    }
  }

  // URL 입력 시
  imageUrlInput.addEventListener("input", () => {
    if (imageUrlInput.value.trim() !== "") {
      // 파일 입력 초기화
      imageFileInput.value = "";
    }
    updatePreview();
  });

  // 파일 선택 시
  imageFileInput.addEventListener("change", () => {
    if (imageFileInput.files.length > 0) {
      // URL 입력 초기화
      imageUrlInput.value = "";
    }
    updatePreview();
  });

  // 폼 제출 전 유효성 검사
  form.addEventListener("submit", (e) => {
    const sellerId = form.seller_id.value.trim();
    const name = form.name.value.trim();
    const price = form.price.value.trim();
    const region = form.region.value.trim();
    const condition = form.condition.value;

    if (!sellerId || !name || !price || !region || !condition) {
      e.preventDefault();
      alert("필수 항목을 모두 입력해주세요.");
      return;
    }

    // 이미지가 없으면 경고 (선택 사항)
    if (!imageUrlInput.value && !imageFileInput.files[0]) {
      e.preventDefault();
      alert("대표 사진을 URL이나 파일로 하나 선택해주세요.");
    }
  });
});
