import React from 'react';
import { cleanNotifications, showNotification } from '@mantine/notifications';
import { negaNotifProps } from './helpers';
import { useAuth } from '../App';

export default function LoginView() {
  const { isLoggedIn, axiosInstance, pageUrl } = useAuth();

  if (isLoggedIn) {
    window.location.replace(pageUrl + "/corporation")
  }

  const handleLogin = () => {
    axiosInstance.get("/login")
      .then(response => {
        const authURL = response.data;

        window.location.href = authURL;
      })
      .catch(error => {
        cleanNotifications()
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
