// frontend/signup.js

// HTML에서 form 요소를 가져옵니다.
const signupForm = document.getElementById('signup-form');

// form에서 'submit' 이벤트가 발생했을 때 실행될 함수를 등록합니다.
signupForm.addEventListener('submit', async function(event) {
    // form의 기본 동작(페이지 새로고침)을 막습니다.
    event.preventDefault();

    // 각 input 요소에서 사용자가 입력한 값을 가져옵니다.
    const name = document.getElementById('name').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    // 백엔드 API로 보낼 데이터를 객체 형태로 만듭니다.
    const userData = {
        name: name,
        email: email,
        password: password
    };

    // fetch API를 사용해 백엔드에 POST 요청을 보냅니다.
    try {
        const response = await fetch('http://127.0.0.1:5000/api/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json' // 우리가 보내는 데이터가 JSON 형식임을 알려줍니다.
            },
            body: JSON.stringify(userData) // JavaScript 객체를 JSON 문자열로 변환합니다.
        });

        const result = await response.json(); // 서버의 응답을 JSON 형태로 파싱합니다.

        if (response.ok) {
            // HTTP 상태 코드가 200-299 사이일 경우 (성공)
            alert(result.message);
            // 성공 시 로그인 페이지로 이동하거나 다른 동작을 추가할 수 있습니다.
            // window.location.href = 'login.html';
        } else {
            // 그 외의 경우 (실패)
            alert(result.error);
        }
    } catch (error) {
        console.error('회원가입 요청 중 오류 발생:', error);
        alert('서버와 통신 중 오류가 발생했습니다.');
    }
});