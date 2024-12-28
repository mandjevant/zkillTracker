import './App.css';
import React, { useState, useEffect, createContext, useContext } from 'react';
import { Routes, Route } from 'react-router-dom';
import { MantineProvider } from '@mantine/core';
import CorporationView from './components/corporationView';
import AllianceView from './components/allianceView';
import MemberView from './components/memberView';
import AdminView from './components/adminView';
import LoginView from './components/loginView';
import { Notifications } from '@mantine/notifications';
import '@mantine/core/styles.css';
import '@mantine/dates/styles.css';
import '@mantine/charts/styles.css';
import axios from 'axios';
import LogOut from './components/logout';

const AuthContext = createContext();
export const useAuth = () => useContext(AuthContext)


export default function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [isAdmin, setIsAdmin] = useState(false);
  const [loggedInCharName, setLoggedInCharName] = useState("");

  useEffect(() => {
    axios.get("/check_logged_in")
      .then(response => {
        setIsLoggedIn(response.data.logged_in);
        setIsAdmin(response.data.is_admin);
        setLoggedInCharName(response.data.character_name);
      })
      .catch(error => {
        console.error("There was an error checking the login state: ", error);
      });
  }, []);

  useEffect(() => {
    if (isLoggedIn) {
      window.location.replace("http://localhost:3000/corporation")
    } else {
      window.location.replace("http://localhost:3000/")
    }
  }, [isLoggedIn])

  console.log("isLoggedIn", isLoggedIn)
  console.log("isAdmin", isAdmin)

  return (
    <MantineProvider defaultColorScheme="dark">
      <Notifications limit={5} zIndex={1000} />
      <AuthContext.Provider value={{ isLoggedIn, isAdmin, loggedInCharName, setIsLoggedIn, setIsAdmin, setLoggedInCharName }}>
        {isLoggedIn ? (
          isAdmin ? (
            <Routes>
              <Route path="/" element={<LoginView />} />
              <Route path="/corporation" element={<CorporationView />} />
              <Route path="/alliance" element={<AllianceView />} />
              <Route path="/members" element={<MemberView />} />
              <Route path="/admin" element={<AdminView />} />
            </Routes>
          ) : (
            <Routes>
              <Route path="/" element={<LoginView />} />
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