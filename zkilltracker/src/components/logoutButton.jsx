import { negaNotifProps } from './helpers';
import { Button } from "@mantine/core";
import { useAuth } from "../App";
import { cleanNotifications, showNotification } from "@mantine/notifications";
import { useNavigate } from "react-router-dom";


export default function LogOut() {
  const { loggedInCharName, setIsLoggedIn, setIsAdmin, setLoggedInCharName, axiosInstance } = useAuth();
  const navigate = useNavigate();

  function handleLogOut() {
    axiosInstance.get("/logout")
      .then(response => {
        setIsLoggedIn(response.data.isLoggedIn);
        setIsAdmin(response.data.isAdmin);
        setLoggedInCharName(response.data.character_name);

        navigate("/");
      })
      .catch(error => {
        cleanNotifications()
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
