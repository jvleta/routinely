console.log("main");
import { initializeApp } from "https://www.gstatic.com/firebasejs/10.4.0/firebase-app.js";
import {
  getAuth,
  GoogleAuthProvider,
  signInWithPopup,
  onAuthStateChanged,
} from "https://www.gstatic.com/firebasejs/10.4.0/firebase-auth.js";

import {
  getFirestore,
  doc,
  getDoc,
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

onAuthStateChanged(auth, (user) => {
  if (user) {
    // User is signed in, see docs for a list of available properties
    // https://firebase.google.com/docs/reference/js/auth.user
    const uid = user.uid;

    (async () => {
      const db = getFirestore(app);
      const docRef = doc(db, "routines", uid);
      const docSnap = await getDoc(docRef);

      if (await docSnap.exists()) {
        console.log("Document data:", await docSnap.data());
      } else {
        console.log("No such document!");
        await setDoc(docRef, { message: "hi val!!!" });
      }

      const topics = [
        "scales",
        "chords",
        "arpeggios",
        "finger picking",
        "alternate picking",
        "ear training",
        "song practice",
      ];
      const container = document.getElementById("container");
      container.innerHTML = "";
      const outerList = document.createElement("ul");
      const out = Module.build(1);
      const routines = JSON.parse(out);
      let day = new Date();
      routines.forEach((routine) => {
        const outerListItem = document.createElement("li");
        outerListItem.innerText = day;
        const innerList = document.createElement("ul");
        routine.forEach((index) => {
          const innerListItem = document.createElement("li");
          innerListItem.innerText = topics[index];
          innerList.appendChild(innerListItem);
        });

        outerListItem.appendChild(innerList);
        outerList.appendChild(outerListItem);
        container.appendChild(outerList);
        day.setDate(day.getDate() + 1);
      });
    })();
  } else {
    const provider = new GoogleAuthProvider();
    signInWithPopup(auth, provider).then((result) => {
      const credential = GoogleAuthProvider.credentialFromResult(result);
      const user = result.user;
      console.log({credential, user});
    });
  }
});