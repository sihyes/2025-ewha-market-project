// product-register.js
document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("product-form");
  const imageUrlInput = form.querySelector('input[name="image_url"]');
  const imageFileInput = form.querySelector('input[name="image_file"]');

  // 미리보기 이미지 생성
  const preview = document.createElement("img");
  preview.style.maxWidth = "200px";
  preview.style.display = "block";
  preview.style.marginTop = "10px";
  imageFileInput.parentNode.appendChild(preview);

  // 미리보기 업데이트 함수
  function updatePreview() {
    const url = imageUrlInput.value.trim();
    const file = imageFileInput.files[0];

    if (url) {
      preview.src = url; // URL 우선
    } else if (file) {
      const reader = new FileReader();
      reader.onload = function (e) {
        preview.src = e.target.result;
      };
      reader.readAsDataURL(file);
    } else {
      preview.src = "";
    }
  }

  // URL 입력 시
  imageUrlInput.addEventListener("input", function () {
    if (imageUrlInput.value.trim() !== "") {
      imageFileInput.value = ""; // 파일 초기화
    }
    updatePreview();
  });

  // 파일 선택 시
  imageFileInput.addEventListener("change", function () {
    if (imageFileInput.files.length > 0) {
      imageUrlInput.value = ""; // URL 초기화
    }
    updatePreview();
  });

  // 폼 제출 전 유효성 체크
  form.addEventListener("submit", function (e) {
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

    if (!imageUrlInput.value && !imageFileInput.files[0]) {
      e.preventDefault();
      alert("대표 사진을 URL이나 파일로 하나 선택해주세요.");
    }
  });
});
