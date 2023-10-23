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

const buildRoutine = () => {
  const out = Module.build(1);
  return JSON.parse(out);
};

const getTopicDescription = (index) => {
  const topics = [
    "scales",
    "chords",
    "arpeggios",
    "finger picking",
    "alternate picking",
    "ear training",
    "song practice",
  ];
  return topics[index];
};

const getCleanContainerElement = () => {
  const container = document.getElementById("container");
  container.innerHTML = "";
  return container;
};

// const getDates = numDays => {
//   let day = new Date();
//   const dates = [];
//   for (let index = 0; i < numDays; index++) {
//     dates.push(day);
//     day.setDate(day.getDate() + 1);
//   }
//   return dates;
// };

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

      const container = getCleanContainerElement();

      const outerList = document.createElement("ul");

      const routines = buildRoutine();

      let day = new Date();

      routines.forEach((routine,i ) => {
        const dates = get
        const outerListItem = document.createElement("li");

        outerListItem.innerText = day;

        const innerList = document.createElement("ul");

        routine.forEach((index) => {
          
          const innerListItem = document.createElement("li");

          innerListItem.innerText = getTopicDescription(index);

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
      console.log({ credential, user });
    });
  }
  
});
