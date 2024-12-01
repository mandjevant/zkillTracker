import React, { useState } from "react";
import { NavLink } from 'react-router-dom'


export default function Menu(props) {
  const [isActive, setIsActive] = useState(false);

  const initMenus = [
    {
      menuId: 1,
      menuName: "Corporation",
      menuRef: "#corporation",
      view: "/corporationView",
    },
    {
      menuId: 2,
      menuName: "Compare corps",
      menuRef: "#comparecorps",
      view: "/compareCorpsView",
    },
    {
      menuId: 3,
      menuName: "Alliance",
      menuRef: "#alliance",
      view: "allianceView",
    },
  ];

  function switchActive() {
    setIsActive(!isActive);
  }

  return (
    <div className="menuHolder">
      <div className="hamburgerMenu" onClick={switchActive}>
        <span></span>
        <span></span>
        <span></span>
      </div>
      {isActive && (
        <div className="sideMenu">
          <ul id="menu">
            {initMenus.map((menu, index) => (
            //   <a href={menu.menuRef} onClick={() => setActiveView(menu.view)} key={index}>
                <li key={index}>
                    <NavLink to={menu.menuRef} className='navs'>
                        <label>{menu.menuName}</label>
                    </NavLink>
                </li>
            //   </a>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}