import Menu from "./menu"
import AddDataOverlay from "./adminOverlay"
import { useNavigate } from "react-router-dom";
import { useAuth } from "../App";

export default function AdminView() {
  const { isAdmin } = useAuth();
  const navigate = useNavigate();

  if (!isAdmin) {
    navigate("/corporation")
  }

  return (
    <div className="App">
      <Menu />
      <AddDataOverlay />
    </div>
  )
}