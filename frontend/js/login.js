// Login page functionality with Supabase
document.addEventListener("DOMContentLoaded", function () {
  const loginForm = document.getElementById("loginForm");
  const emailInput = document.getElementById("loginEmail");
  const passwordInput = document.getElementById("loginPassword");
  const submitBtn = loginForm.querySelector(".submit-btn");
  const forgotPasswordLink = document.getElementById("forgotPasswordLink");

  // Check if user is already logged in
  checkAuthState();

  // Focus on email input when page loads
  emailInput.focus();

  // Handle login form submission
  loginForm.addEventListener("submit", async function (e) {
    e.preventDefault();

    const email = emailInput.value.trim();
    const password = passwordInput.value;

    // Basic validation
    if (!email || !password) {
      showMessage("Please fill in all fields", "error");
      return;
    }

    if (!isValidEmail(email)) {
      showMessage("Please enter a valid email address", "error");
      return;
    }

    // Show loading state
    setLoadingState(true);

    try {
      // Supabase authentication - changed from window.supabaseClient to window.supabase
      const { data, error } = await window.supabase.auth.signInWithPassword({
        email: email,
        password: password,
      });

      if (error) {
        throw error;
      }

      // Successful login
      showMessage("Login successful! Redirecting...", "success");

      // Redirect to dashboard
      setTimeout(() => {
        window.location.href = "dashboard.html";
      }, 1500);
    } catch (error) {
      console.error("Login error:", error);

      // Handle specific error messages
      let errorMessage = "Login failed. Please try again.";

      if (error.message.includes("Invalid login credentials")) {
        errorMessage = "Invalid email or password";
      } else if (error.message.includes("Email not confirmed")) {
        errorMessage = "Please check your email and confirm your account";
      } else if (error.message.includes("too many requests")) {
        errorMessage = "Too many login attempts. Please try again later.";
      }

      showMessage(errorMessage, "error");
    } finally {
      setLoadingState(false);
    }
  });

  // Handle forgot password link
  forgotPasswordLink.addEventListener("click", async function (e) {
    e.preventDefault();

    const email = emailInput.value.trim();

    if (!email || !isValidEmail(email)) {
      showMessage("Please enter a valid email address first", "error");
      emailInput.focus();
      return;
    }

    try {
      // Changed from window.supabaseClient to window.supabase
      const { error } = await window.supabase.auth.resetPasswordForEmail(
        email,
        {
          redirectTo: `${window.location.origin}/reset-password.html`,
        }
      );

      if (error) {
        throw error;
      }

      showMessage(`Password reset link sent to ${email}`, "success");
    } catch (error) {
      console.error("Password reset error:", error);
      showMessage("Failed to send reset email. Please try again.", "error");
    }
  });

  // Real-time email validation
  emailInput.addEventListener("blur", function () {
    const email = this.value.trim();
    if (email && !isValidEmail(email)) {
      showMessage("Please enter a valid email address", "error");
    } else {
      clearMessages();
    }
  });

  // Password input handling
  passwordInput.addEventListener("input", function () {
    clearMessages();
  });

  // Check authentication state
  async function checkAuthState() {
    try {
      // Changed from window.supabaseClient to window.supabase
      const {
        data: { user },
      } = await window.supabase.auth.getUser();

      if (user) {
        // User is already logged in, redirect to dashboard
        window.location.href = "dashboard.html";
      }
    } catch (error) {
      console.error("Auth check error:", error);
      // Continue with login page if there's an error
    }
  }

  // Helper Functions
  function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }

  function showMessage(message, type) {
    // Remove existing messages
    clearMessages();

    const messageDiv = document.createElement("div");
    messageDiv.className = `message ${type}`;
    messageDiv.textContent = message;

    // Insert message before the form
    loginForm.insertBefore(messageDiv, loginForm.firstChild);

    // Auto-remove error messages after 5 seconds
    if (type === "error") {
      setTimeout(() => {
        clearMessages();
      }, 5000);
    }
  }

  function clearMessages() {
    const existingMessages = loginForm.querySelectorAll(".message");
    existingMessages.forEach((msg) => msg.remove());
  }

  function setLoadingState(isLoading) {
    if (isLoading) {
      submitBtn.disabled = true;
      submitBtn.innerHTML = '<span class="spinner"></span>Signing In...';
    } else {
      submitBtn.disabled = false;
      submitBtn.innerHTML = "Sign In";
    }
  }

  // Handle Enter key on form inputs
  [emailInput, passwordInput].forEach((input) => {
    input.addEventListener("keypress", function (e) {
      if (e.key === "Enter") {
        loginForm.dispatchEvent(new Event("submit"));
      }
    });
  });
});
