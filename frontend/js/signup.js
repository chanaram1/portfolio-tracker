// Signup page functionality with Supabase
document.addEventListener("DOMContentLoaded", function () {
  const signupForm = document.getElementById("signupForm");
  const nameInput = document.getElementById("signupName");
  const emailInput = document.getElementById("signupEmail");
  const passwordInput = document.getElementById("signupPassword");
  const confirmPasswordInput = document.getElementById("confirmPassword");
  const submitBtn = signupForm.querySelector(".submit-btn");

  // Check if user is already logged in
  checkAuthState();

  // Focus on name input when page loads
  nameInput.focus();

  // Handle signup form submission
  signupForm.addEventListener("submit", async function (e) {
    e.preventDefault();

    const name = nameInput.value.trim();
    const email = emailInput.value.trim();
    const password = passwordInput.value;
    const confirmPassword = confirmPasswordInput.value;

    // Validation
    if (!name || !email || !password || !confirmPassword) {
      showMessage("Please fill in all fields", "error");
      return;
    }

    if (name.length < 2) {
      showMessage("Name must be at least 2 characters long", "error");
      return;
    }

    if (!isValidEmail(email)) {
      showMessage("Please enter a valid email address", "error");
      return;
    }

    if (password.length < 6) {
      showMessage("Password must be at least 6 characters long", "error");
      return;
    }

    if (password !== confirmPassword) {
      showMessage("Passwords do not match", "error");
      return;
    }

    // Show loading state
    setLoadingState(true);

    try {
      // Supabase authentication - using window.supabase instead of window.supabaseClient
      const { data, error } = await window.supabase.auth.signUp({
        email: email,
        password: password,
        options: {
          data: {
            full_name: name,
            display_name: name,
          },
        },
      });

      if (error) {
        throw error;
      }

      // Check if email confirmation is required
      if (data.user && !data.user.email_confirmed_at) {
        showMessage(
          "Account created! Please check your email to verify your account before signing in.",
          "success"
        );

        // Redirect to login page after showing message
        setTimeout(() => {
          window.location.href = "login.html";
        }, 3000);
      } else {
        // Auto-confirmed (unlikely in production)
        showMessage("Account created successfully! Redirecting...", "success");
        setTimeout(() => {
          window.location.href = "dashboard.html";
        }, 2000);
      }
    } catch (error) {
      console.error("Signup error:", error);

      // Handle specific error messages
      let errorMessage = "Failed to create account. Please try again.";

      if (error.message.includes("User already registered")) {
        errorMessage =
          "An account with this email already exists. Try signing in instead.";
      } else if (error.message.includes("Password should be at least")) {
        errorMessage =
          "Password is too weak. Please choose a stronger password.";
      } else if (error.message.includes("Invalid email")) {
        errorMessage = "Invalid email address format";
      } else if (error.message.includes("signup is disabled")) {
        errorMessage = "Account registration is currently disabled";
      }

      showMessage(errorMessage, "error");
    } finally {
      setLoadingState(false);
    }
  });

  // Real-time validation
  nameInput.addEventListener("blur", function () {
    const name = this.value.trim();
    if (name && name.length < 2) {
      showMessage("Name must be at least 2 characters long", "error");
    } else {
      clearMessages();
    }
  });

  emailInput.addEventListener("blur", function () {
    const email = this.value.trim();
    if (email && !isValidEmail(email)) {
      showMessage("Please enter a valid email address", "error");
    } else {
      clearMessages();
    }
  });

  passwordInput.addEventListener("input", function () {
    const password = this.value;
    updatePasswordStrength(password);

    // Clear confirm password validation if it doesn't match
    if (confirmPasswordInput.value && confirmPasswordInput.value !== password) {
      confirmPasswordInput.setCustomValidity("Passwords do not match");
    } else {
      confirmPasswordInput.setCustomValidity("");
    }
  });

  confirmPasswordInput.addEventListener("input", function () {
    const password = passwordInput.value;
    const confirmPassword = this.value;

    if (confirmPassword && password !== confirmPassword) {
      showMessage("Passwords do not match", "error");
      this.setCustomValidity("Passwords do not match");
    } else {
      clearMessages();
      this.setCustomValidity("");
    }
  });

  // Check authentication state
  async function checkAuthState() {
    try {
      // Changed from window.supabaseClient to window.supabase
      const {
        data: { user },
      } = await window.supabase.auth.getUser();

      if (user && user.email_confirmed_at) {
        // User is already logged in and confirmed, redirect to dashboard
        window.location.href = "dashboard.html";
      }
    } catch (error) {
      console.error("Auth check error:", error);
      // Continue with signup page if there's an error
    }
  }

  // Helper Functions
  function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }

  function updatePasswordStrength(password) {
    // Clear previous messages
    clearMessages();

    if (password.length === 0) return;

    let strength = 0;
    let feedback = [];

    if (password.length >= 8) strength++;
    else feedback.push("at least 8 characters");

    if (/[a-z]/.test(password)) strength++;
    else feedback.push("lowercase letter");

    if (/[A-Z]/.test(password)) strength++;
    else feedback.push("uppercase letter");

    if (/[0-9]/.test(password)) strength++;
    else feedback.push("number");

    if (/[^A-Za-z0-9]/.test(password)) strength++;
    else feedback.push("special character");

    if (password.length >= 6 && strength >= 2) {
      // Acceptable password
      return;
    } else if (feedback.length > 0) {
      showMessage(`Password needs: ${feedback.join(", ")}`, "error");
    }
  }

  function showMessage(message, type) {
    // Remove existing messages
    clearMessages();

    const messageDiv = document.createElement("div");
    messageDiv.className = `message ${type}`;
    messageDiv.textContent = message;

    // Insert message before the form
    signupForm.insertBefore(messageDiv, signupForm.firstChild);

    // Auto-remove error messages after 5 seconds
    if (type === "error") {
      setTimeout(() => {
        clearMessages();
      }, 5000);
    }
  }

  function clearMessages() {
    const existingMessages = signupForm.querySelectorAll(".message");
    existingMessages.forEach((msg) => msg.remove());
  }

  function setLoadingState(isLoading) {
    if (isLoading) {
      submitBtn.disabled = true;
      submitBtn.innerHTML = '<span class="spinner"></span>Creating Account...';
    } else {
      submitBtn.disabled = false;
      submitBtn.innerHTML = "Create Account";
    }
  }

  // Handle Enter key on form inputs
  [nameInput, emailInput, passwordInput, confirmPasswordInput].forEach(
    (input) => {
      input.addEventListener("keypress", function (e) {
        if (e.key === "Enter") {
          signupForm.dispatchEvent(new Event("submit"));
        }
      });
    }
  );
});
