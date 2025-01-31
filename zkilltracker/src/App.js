import './App.css';
import React, { useState, useEffect, createContext, useContext } from 'react';
import { Routes, Route, useNavigate } from 'react-router-dom';
import { MantineProvider } from '@mantine/core';
import CorporationView from './components/corporationView';
import AllianceView from './components/allianceView';
import MemberView from './components/memberView';
import AdminView from './components/adminView';
import LoginView from './components/loginView';
import { cleanNotifications, Notifications, showNotification } from '@mantine/notifications';
import '@mantine/core/styles.css';
import '@mantine/dates/styles.css';
import '@mantine/charts/styles.css';
import axios from 'axios';
import LogOut from './components/logoutButton';
import { negaNotifProps, posiNotifProps } from './components/helpers';
import { urls } from './config'

const AuthContext = createContext();
export const useAuth = () => useContext(AuthContext)


export default function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [isAdmin, setIsAdmin] = useState(false);
  const [loggedInCharName, setLoggedInCharName] = useState("");
  const navigate = useNavigate();
  const axiosInstance = axios.create({
    baseURL: urls.baseApiUrl,
    withCredentials: true,
  })
  const pageUrl = urls.websiteUrl

  useEffect(() => {
    const currentRoute = window.location.href; 

    if (currentRoute.substr(currentRoute.length - 1) === "/") {
      axiosInstance.get("/login_status")
        .then((response) => {
          const data = response.data;
          setIsLoggedIn(data.isLoggedIn);
          setIsAdmin(data.isAdmin);
          setLoggedInCharName(data.characterName);
    
          if (data.isLoggedIn) {
            navigate("/corporation");
            cleanNotifications();
            showNotification({
              message: "Logged in!",
              ...posiNotifProps
            });
          } else {
            cleanNotifications();
            showNotification({
              message: "You are not approved to access the website.",
              ...negaNotifProps
            });
          }

        })
        .catch((error) => {
          console.error("There was an error fetching the login status:", error);
        });
      }
    }, [navigate, axiosInstance]);

  useEffect(() => {
    if (!isLoggedIn) {
      navigate("/");
    }
  }, [isLoggedIn, navigate, pageUrl]);

  return (
    <MantineProvider defaultColorScheme="dark">
      <Notifications limit={5} zIndex={1000} />
      <AuthContext.Provider value={{ isLoggedIn, isAdmin, loggedInCharName, setIsLoggedIn, setIsAdmin, setLoggedInCharName, axiosInstance, pageUrl }}>
        {isLoggedIn ? (
          isAdmin ? (
            <Routes>
              <Route path="/corporation" element={<CorporationView />} />
              <Route path="/alliance" element={<AllianceView />} />
              <Route path="/members" element={<MemberView />} />
              <Route path="/admin" element={<AdminView />} />
            </Routes>
          ) : (
            <Routes>
              <Route path="/corporation" element={<CorporationView />} />
              <Route path="/alliance" element={<AllianceView />} />
              <Route path="/members" element={<MemberView />} />
            </Routes>
          )
        ) : (
          <Routes>
            <Route path="/" element={<LoginView />} />
          </Routes>
        )}
        {isLoggedIn ? (
          <LogOut />
        ) : null }
      </AuthContext.Provider>
    </MantineProvider>
  );
}
