// Admin view
// - Refresh data button that refreshes kills&memberKills for current and past month.
// - Add data via a popup and nice selectors:
// 1. member using <characterID, characterName, corporationID>. Should return success
// 2. Corporation+months <corporationID> hits off input for corporation+months, should return success
// - File upload for alliance months after Shieks transposer
import Menu from "./menu"
import AddDataOverlay from "./adminOverlay"

export default function AdminView() {
  return (
    <div className="App">
      <Menu />
      <AddDataOverlay />
    </div>
  )
}