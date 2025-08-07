     
     const dummyUsers = [{ email: "test@example.com", password: "password123" }];

      const form = document.getElementById("authForm");
      const formTitle = document.getElementById("formTitle");
      const submitButton = document.getElementById("submitButton");
      const toggleMode = document.getElementById("toggleMode");
      const toggleText = document.getElementById("toggleText");
      const message = document.getElementById("message");
      const nameInput = document.getElementById("name");

      let isLogin = true;

      toggleMode.addEventListener("click", () => {
        isLogin = !isLogin;
        if (isLogin) {
          formTitle.textContent = "Welcome Back";
          submitButton.textContent = "Sign In";
          toggleText.textContent = "Don’t have an account?";
          toggleMode.textContent = "Sign up";
          nameInput.style.display = "none";
        } else {
          formTitle.textContent = "Create Account";
          submitButton.textContent = "Sign Up";
          toggleText.textContent = "Already have an account?";
          toggleMode.textContent = "Sign in";
          nameInput.style.display = "block";
        }
        message.textContent = "";
      });

      form.addEventListener("submit", (e) => {
        e.preventDefault();
        const email = document.getElementById("email").value.trim();
        const password = document.getElementById("password").value.trim();
        const name = document.getElementById("name").value.trim();

        if (!email || !password || (!isLogin && !name)) {
          message.style.color = "red";
          message.textContent = "Please fill all fields.";
          return;
        }

        if (isLogin) {
          const user = dummyUsers.find(u => u.email === email && u.password === password);
          if (user) {
            message.style.color = "green";
            message.textContent = "Login successful!";
            setTimeout(() => alert("Redirecting to dashboard..."), 1000);
          } else {
            message.style.color = "red";
            message.textContent = "Invalid credentials.";
          }
        } else {
          const exists = dummyUsers.find(u => u.email === email);
          if (exists) {
            message.style.color = "red";
            message.textContent = "User already exists.";
          } else {
            dummyUsers.push({ email, password });
            message.style.color = "green";
            message.textContent = `Welcome, ${name}! Account created.`;
            toggleMode.click();
          }
        }
      });
        function handleGoogleLogin(response) {
            const userObject = parseJwt(response.credential);
            const message = document.getElementById('message');

            message.style.color = "green";
            message.textContent = `Welcome, ${userObject.name}! Logged in with Google.`;

            setTimeout(() => {
              alert("Redirecting to dashboard...");
            }, 1000);
        }

        function parseJwt(token) {
          const base64Url = token.split('.')[1];
          const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
          const jsonPayload = decodeURIComponent(
            atob(base64)
              .split('')
              .map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
              .join('')
          );

          return JSON.parse(jsonPayload);
        }

