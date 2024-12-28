import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { showNotification, cleanNotifications } from '@mantine/notifications';
import { negaNotifProps, posiNotifProps } from './helpers';
import { useAuth } from '../App';

export default function LoginView() {
  const [loggingIn, setLoggingIn] = useState(false);
  const { isLoggedIn, setIsLoggedIn, setIsAdmin, setLoggedInCharName } = useAuth();

  if (isLoggedIn) {
    window.location.replace("http://localhost:3000/corporation")
  }

  const handleLogin = () => {
    axios.get("/login")
      .then(response => {
        const authURL = response.data;
        setLoggingIn(true);

        const handle = window.open(authURL);

        if (!handle) {
          showNotification({
            message: "Failed to open login window.",
            ...negaNotifProps
          })
        };
      })
      .catch(error => {
        showNotification({
          message: "Failed to log in.",
          ...negaNotifProps
        })
        console.log("Failed to log in", error)
      })
  };
  
  useEffect(() => {
    if (isLoggedIn) {
      return
    }
    let interval;
    if (loggingIn) {
      interval = setInterval(() => {
        axios.get("/check_approval")
          .then(response => {
            if (response.data.status === "Done") {
              setLoggingIn(false);
              setIsLoggedIn(response.data.logged_in);
              setIsAdmin(response.data.is_admin);
              setLoggedInCharName(response.data.character_name);
              cleanNotifications();
              showNotification({
                message: "Logged in successfully!",
                ...posiNotifProps
              });
              clearInterval(interval);
              window.location.replace("http://localhost:3000/corporation")
            }
          })
          .catch(error => {
            setLoggingIn(false);
            cleanNotifications();
            showNotification({
              message: "Login unsuccessfull!",
              ...negaNotifProps
            });
            clearInterval(interval);
          });
      }, 500);
    }
    return () => clearInterval(interval);
  }, [loggingIn, isLoggedIn, setIsAdmin, setIsLoggedIn, setLoggedInCharName]);

  return (
    <div className="App">
      <div className="AppLogin">
        <button onClick={handleLogin}>Login with Eve Online</button>
      </div>
    </div>
  );
};
