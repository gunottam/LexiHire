// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAuth } from 'firebase/auth';
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyBJ918Vsa6LdQGc7yHbjEbw0WhffP1rmZI",
  authDomain: "lexihire-a453d.firebaseapp.com",
  projectId: "lexihire-a453d",
  storageBucket: "lexihire-a453d.firebasestorage.app",
  messagingSenderId: "350877485429",
  appId: "1:350877485429:web:77d1bc9bf58b86cde82b3c"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
export const auth = getAuth();
export default app;