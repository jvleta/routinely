import { initializeApp } from "https://www.gstatic.com/firebasejs/10.4.0/firebase-app.js";
import {
  getAuth,
  GoogleAuthProvider,
  signInWithPopup,
} from "https://www.gstatic.com/firebasejs/10.4.0/firebase-auth.js";

import {
  getFirestore,
  doc,
  getDoc,
  collection,
  setDoc,
} from "https://www.gstatic.com/firebasejs/10.4.0/firebase-firestore.js";

const firebaseConfig = {
  apiKey: "AIzaSyC-S1NgcxXANX4g4dnYCh_pt6wvjtA5KL8",
  authDomain: "routinely-6cc29.firebaseapp.com",
  projectId: "routinely-6cc29",
  storageBucket: "routinely-6cc29.appspot.com",
  messagingSenderId: "254697719173",
  appId: "1:254697719173:web:2813bd3f79b69274cbf0ec",
  measurementId: "G-FQPEHSM9Y1",
};

const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const provider = new GoogleAuthProvider();
console.log(auth);
signInWithPopup(auth, provider)
  .then((result) => {
    const credential = GoogleAuthProvider.credentialFromResult(result);
    const token = credential.accessToken;
    const user = result.user;
    console.log({ credential, token, user });
    (async () => {
      const db = getFirestore(app);
      const docRef = doc(db, "routines", user.uid);
      const docSnap = await getDoc(docRef);

      if (await docSnap.exists()) {
        console.log("Document data:", await docSnap.data());
      } else {
        console.log("No such document!");
        await setDoc(docRef, { message: "hi val!!!" });
      }
    })();
  })
  .catch((error) => {
    const errorCode = error.code;
    const errorMessage = error.message;
    const email = error.customData.email;
    const credential = GoogleAuthProvider.credentialFromError(error);
    console.log({ errorCode, errorMessage, email, credential });
  });
