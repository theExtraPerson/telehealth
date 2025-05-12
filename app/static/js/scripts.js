/* Sending data through fetch API */
async function postData(url = "", data = {}) {
        const response = await fetch(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
        });
        return response.json(); // parses JSON response into native JavaScript objects
    }

// Password validation
  document.getElementById('registerForm').addEventListener('submit', function (e) {
    const pass = document.getElementById('password').value;
    const confirm = document.getElementById('confirm_password').value;
    if (pass !== confirm) {
      e.preventDefault();
      alert("Passwords do not match!");
    }
  });