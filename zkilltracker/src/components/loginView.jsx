import React, { useState } from 'react';
import axios from 'axios';
import { showNotification } from '@mantine/notifications';
import { negaNotifProps } from './helpers';
import { useAuth } from '../App';

export default function LoginView() {
  const [setLoggingIn] = useState(false);
  const { isLoggedIn } = useAuth();

  if (isLoggedIn) {
    window.location.replace("http://localhost:3000/corporation")
  }

  const handleLogin = () => {
    axios.get("/login")
      .then(response => {
        const authURL = response.data;
        setLoggingIn(true);

        window.location.href = authURL;
      })
      .catch(error => {
        showNotification({
          message: "Failed to log in.",
          ...negaNotifProps
        })
        console.log("Failed to log in", error)
      })
  };
  
  return (
    <div className="App">
      <div className="AppLogin">
        <button onClick={handleLogin}>Login with Eve Online</button>
      </div>
    </div>
  );
};
