import axios from "axios";
import { negaNotifProps } from './helpers';
import { Button } from "@mantine/core";
import { useAuth } from "../App";
import { showNotification } from "@mantine/notifications";


export default function LogOut() {
  const { loggedInCharName, setIsLoggedIn, setIsAdmin, setLoggedInCharName } = useAuth();

  function handleLogOut() {
    axios.get("/logout")
      .then(response => {
        setIsLoggedIn(response.data.logged_in);
        setIsAdmin(response.data.is_admin);
        setLoggedInCharName(response.data.character_name);

        setTimeout(() => {
          window.location.replace("http://localhost:3000/");
        }, 0);
      })
      .catch(error => {
        showNotification({
            message: "Could not process logout",
            ...negaNotifProps
          }
        )
        console.log("There was an error logging out: ", error)
      })
  }
  return (
    <Button
      className="logOutButton"
      variant="filled"
      onClick={handleLogOut}
    >
      Log out: {loggedInCharName}
    </Button>
  )
}
