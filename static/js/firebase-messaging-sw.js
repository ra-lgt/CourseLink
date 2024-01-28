importScripts('https://www.gstatic.com/firebasejs/8.6.1/firebase-app.js');
importScripts('https://www.gstatic.com/firebasejs/8.6.1/firebase-messaging.js');


var firebaseConfig = {
    apiKey: "AIzaSyAiwvGBmyscjjekiRF2mcMlRYEW6Yu3tCU",
    authDomain: "course-link-2cdaf.firebaseapp.com",
    projectId: "course-link-2cdaf",
    storageBucket: "course-link-2cdaf.appspot.com",
    messagingSenderId: "58053067019",
    appId: "1:58053067019:web:9eec85b90de1aeb90c220e"
  };
  console.log(firebaseConfig)
  firebase.initializeApp(firebaseConfig);
  

  const messaging = firebase.messaging();