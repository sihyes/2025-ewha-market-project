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
