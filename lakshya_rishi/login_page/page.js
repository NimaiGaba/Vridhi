// page.js

// Import Firebase initialized objects and functions
import {
    auth,
    db,
    firebaseOnAuthStateChanged,
    firebaseSignOut,
    firebaseCreateUserWithEmailAndPassword,
    firebaseSignInWithEmailAndPassword,
    firebaseDoc,
    firebaseSetDoc,
    firebaseGetDoc,
    firebaseSignInWithPopup,
    firebaseGoogleAuthProvider,
    firebaseUpdateProfile
} from './firebase-config.js';
import { GoogleAuthProvider, signInWithCredential } 
    from "https://www.gstatic.com/firebasejs/10.0.0/firebase-auth.js";
// Get references to HTML elements
const authBox = document.getElementById('authBox');
const formTitle = document.getElementById('formTitle');

const loginForm = document.getElementById('loginForm');
const loginEmailInput = document.getElementById('loginEmail');
const loginPasswordInput = document.getElementById('loginPassword');

const signupForm = document.getElementById('signupForm');
const signupFullNameInput = document.getElementById('signupFullName');
const signupEmailInput = document.getElementById('signupEmail');
const signupPasswordInput = document.getElementById('signupPassword');
const signupConfirmPasswordInput = document.getElementById('signupConfirmPassword');

const messageElement = document.getElementById('message');
const toggleModeButton = document.getElementById('toggleMode');
const toggleText = document.getElementById('toggleText');
const logoutButton = document.getElementById('logoutButton');

const googleLoginWrapper = document.querySelector('.google-login-wrapper');


// --- Helper Functions ---
function showMessage(msg, isError = false) {
    messageElement.textContent = msg;
    messageElement.style.color = isError ? 'red' : 'green';
}

function clearForms() {
    loginForm.reset();
    signupForm.reset();
    messageElement.textContent = ''; // Clear messages
}

// Function to update the UI based on authentication state
function updateUIForAuthState(user) {
    clearForms(); // Always clear forms when auth state changes

    if (user) {
        // User is logged in
        formTitle.textContent = `Welcome, ${user.email || user.displayName || 'User'}!`;
        loginForm.style.display = 'none';
        signupForm.style.display = 'none';
        toggleModeButton.style.display = 'none';
        toggleText.style.display = 'none';
        googleLoginWrapper.style.display = 'none'; // Hide Google button when logged in
        logoutButton.style.display = 'block'; // Show logout button
        showMessage('You are currently logged in.', false);

    } else {
        // User is logged out
        formTitle.textContent = 'Welcome Back'; // Default to Login view
        loginForm.style.display = 'block'; // Show login form
        signupForm.style.display = 'none'; // Hide signup form
        toggleModeButton.style.display = 'inline-block'; // Show toggle button
        toggleText.style.display = 'inline-block'; // Show toggle text
        googleLoginWrapper.style.display = 'block'; // Show Google button when logged out
        logoutButton.style.display = 'none'; // Hide logout button

        toggleModeButton.textContent = 'Sign up'; // Ensure button text is for switching to signup
        toggleText.textContent = 'Don’t have an account?'; // Ensure toggle text is for switching to signup
        showMessage(''); // Clear messages
    }
}

// IMPORTANT: Expose updateUIForAuthState to the global window object
// This allows handleGoogleLogin (which is global) to call it directly.
window.updateUIForAuthState = updateUIForAuthState;
// Expose showMessage as well for similar reasons or general utility
window.showMessage = showMessage;


// --- Event Listeners ---

// Toggle between Login and Signup forms
toggleModeButton.addEventListener('click', () => {
    clearForms(); // Clear both forms before switching

    if (loginForm.style.display === 'block') {
        // Currently showing login, switch to signup
        loginForm.style.display = 'none';
        signupForm.style.display = 'block';
        formTitle.textContent = 'Create Account';
        toggleModeButton.textContent = 'Sign In';
        toggleText.textContent = 'Already have an account?';
    } else {
        // Currently showing signup, switch to login
        loginForm.style.display = 'block';
        signupForm.style.display = 'none';
        formTitle.textContent = 'Welcome Back';
        toggleModeButton.textContent = 'Sign up';
        toggleText.textContent = 'Don’t have an account?';
    }
    showMessage(''); // Clear any messages on toggle
});

// Handle Login Form Submission
loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const email = loginEmailInput.value.trim();
    const password = loginPasswordInput.value.trim();

    if (!email || !password) {
        showMessage('Please enter both email and password.', true);
        return;
    }
    
    try {
        const userCredential = await firebaseSignInWithEmailAndPassword(auth, email, password);
        const user = userCredential.user;
        // Save display name in Firebase Auth
        window.location.href = `/after_login/frontend/UI.html`;
        showMessage(`Login successful! Welcome back, ${user.email}`, false);
        // UI update will be handled by onAuthStateChanged listener
    } catch (error) {
        const errorCode = error.code;
        const errorMessage = error.message;
        console.error("Login Error:", errorCode, errorMessage);
        switch (errorCode) {
            case 'auth/invalid-email':
            case 'auth/user-not-found':
            case 'auth/wrong-password':
                showMessage("Invalid email or password.", true);
                break;
            case 'auth/user-disabled':
                showMessage("Your account has been disabled.", true);
                break;
            case 'auth/network-request-failed':
                showMessage("Network error. Please check your internet connection.", true);
                break;
            default:
                showMessage(`Login failed: ${errorMessage}`, true);
                break;
        }
    }
});

// Handle Signup Form Submission
signupForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const fullName = signupFullNameInput.value.trim();
    const email = signupEmailInput.value.trim();
    const password = signupPasswordInput.value.trim();
    const confirmPassword = signupConfirmPasswordInput.value.trim();

    if (!fullName || !email || !password || !confirmPassword) {
        showMessage('Please fill in all fields.', true);
        return;
    }

    if (password.length < 6) {
        showMessage('Password should be at least 6 characters.', true);
        return;
    }

    if (password !== confirmPassword) {
        showMessage('Passwords do not match!', true);
        return;
    }

    try {
        const userCredential = await firebaseCreateUserWithEmailAndPassword(auth, email, password);
        const user = userCredential.user;
        await firebaseUpdateProfile(user, { displayName: fullName });
        // Store additional user data in Firestore
        await auth.currentUser.reload();

        await firebaseSetDoc(firebaseDoc(db, "users", user.uid), {
            email: user.email,
            fullName: fullName,
            createdAt: new Date().toISOString()
        });
        window.location.href = `/after_login/frontend/UI.html`;
        showMessage(`Registration successful! Welcome, ${user.email}`, false);
        clearForms();
        // Automatically switch back to login form after successful signup
        loginForm.style.display = 'block';
        signupForm.style.display = 'none';
        formTitle.textContent = 'Welcome Back';
        toggleModeButton.textContent = 'Sign up';
        toggleText.textContent = 'Don’t have an account?';
        showMessage('Account created. Please log in.', false);
        window.location.href = `/after_login/frontend/ui.html?name=${encodeURIComponent(fullName)}`;

    } catch (error) {
        const errorCode = error.code;
        const errorMessage = error.message;
        console.error("Signup Error:", errorCode, errorMessage);
        switch (errorCode) {
            case 'auth/email-already-in-use':
                showMessage("Email already in use. Please sign in or use a different email.", true);
                break;
            case 'auth/invalid-email':
                showMessage("Invalid email address.", true);
                break;
            case 'auth/weak-password':
                showMessage("Password should be at least 6 characters.", true);
                break;
            case 'auth/network-request-failed':
                showMessage("Network error. Please check your internet connection.", true);
                break;
            default:
                showMessage(`Registration failed: ${errorMessage}`, true);
                break;
        }
    }
});

// Handle Logout Button
logoutButton.addEventListener('click', async () => {
    try {
        await firebaseSignOut(auth);
        showMessage('Logged out successfully.', false);
        // UI update will be handled by onAuthStateChanged listener
    } catch (error) {
        console.error("Logout Error:", error);
        showMessage(`Logout failed: ${error.message}`, true);
    }
});

// --- Google Sign-In Integration (must be global for GSI client) ---
// --- Google Sign-In Integration ---


window.handleGoogleLogin = async () => {
  try {
    const result = await firebaseSignInWithPopup(auth, firebaseGoogleAuthProvider);
    console.log("Logged in:", result.user);
    window.location.href = "/after_login/frontend/UI.html";
  } catch (err) {
    console.error("Popup login failed:", err);
    alert("Google login failed: " + err.message);
  }
};
// firebaseOnAuthStateChanged(auth, async (user) => {
//     if (user) {
//         try {
//             const res = await fetch("/session-login", {
//                 method: "POST",
//                 headers: { "Content-Type": "application/json" },
//                 body: JSON.stringify({ email: user.email }),
//             });

//             if (res.ok) {
//                 window.location.href = "/dashboard";
//             } else {
//                 console.error("Session creation failed:", await res.text());
//             }
//         } catch (err) {
//             console.error("Error sending session login:", err);
//         }
//     }
// });



// --- Firebase Auth State Listener ---
// This is the primary mechanism to keep the UI in sync with the user's login status.
firebaseOnAuthStateChanged(auth, (user) => {
    if (user) {
        window.location.href = `/after_login/frontend/UI.html`;
    } else {
        updateUIForAuthState(null);
    }
});




// Initial check for auth state when the page loads
// This ensures correct UI display if a user is already logged in from a previous session
// (e.g., if they closed and reopened the tab).
// firebaseOnAuthStateChanged(auth, (user) => {
//     if (user) {
//         updateUIForAuthState(user);
//     } else {
//         updateUIForAuthState(null); // Explicitly pass null if no user
//     }
// });