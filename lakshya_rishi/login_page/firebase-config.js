// firebase-config.js
import { updateProfile } from "https://www.gstatic.com/firebasejs/10.0.0/firebase-auth.js";

// Your web app's Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyAoTmtWnoIMho6af_FykYV-G0F4qzatVnM",
  authDomain: "stockscreener-265c2.firebaseapp.com",
  projectId: "stockscreener-265c2",
  storageBucket: "stockscreener-265c2.appspot.com",
  messagingSenderId: "232982857770",
  appId: "1:232982857770:web:89322466d1df0b5a8a5b53"
};

// Import necessary Firebase SDK functions
import { initializeApp } from "https://www.gstatic.com/firebasejs/10.0.0/firebase-app.js";
import {
  getAuth,
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
  onAuthStateChanged,
  signOut,
  GoogleAuthProvider,
  signInWithPopup
} from "https://www.gstatic.com/firebasejs/10.0.0/firebase-auth.js";
import {
  getFirestore,
  doc,
  setDoc,
  getDoc
} from "https://www.gstatic.com/firebasejs/10.0.0/firebase-firestore.js";

// Initialize the Firebase app
const app = initializeApp(firebaseConfig);

// Export the initialized Firebase service instances
export const auth = getAuth(app);
export const db = getFirestore(app);

// Export specific Firebase functions needed by other modules
export const firebaseGoogleAuthProvider = new GoogleAuthProvider();
firebaseGoogleAuthProvider.addScope('profile');
firebaseGoogleAuthProvider.addScope('email');

export const firebaseSignInWithPopup = signInWithPopup;
export const firebaseOnAuthStateChanged = onAuthStateChanged;
export const firebaseSignOut = signOut;
export const firebaseCreateUserWithEmailAndPassword = createUserWithEmailAndPassword;
export const firebaseSignInWithEmailAndPassword = signInWithEmailAndPassword;
export const firebaseDoc = doc;
export const firebaseSetDoc = setDoc;
export const firebaseGetDoc = getDoc;
export const firebaseUpdateProfile = updateProfile;
